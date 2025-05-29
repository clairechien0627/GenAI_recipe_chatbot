import json
from typing import List, TypedDict
from pydantic import BaseModel, Field
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import init_chat_model
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import START, END, StateGraph

model_name = "llama3-8b-8192"
def meta_func(obj: dict, seq_num: int) -> dict:
    return {
        "seq_num":            seq_num,
        "recipe_name":        obj.get("recipe_name", ""),
        "recipe_link":        obj.get("recipe_link", ""),
        "image_url":          obj.get("image_url", ""),
        "user_recipe_count":  int(obj.get("user_recipe", 0)),
        "user_fans_count":    int(obj.get("user_fans", 0)),
        "view_count":         int(obj.get("view_count", 0)),
        "like_count":         int(obj.get("like_count", 0)),
        "together_count":     int(obj.get("together_count", 0)),
        "comment_count":      int(obj.get("comment_count", 0)),
        "date":               str(obj.get("date", "")),
    }

def build_docs_from_list(path: List[dict]) -> List[Document]:
    docs = []
    for i, obj in enumerate(path):
        content_parts = [
            f"食譜名稱: {obj.get('recipe_name', '')}",
            f"描述: {obj.get('description', '')}",
            f"標籤: {', '.join(obj.get('tags', []))}",
            "食材:",
            "\n".join(
                f"  - {ing.get('name', '')}：{ing.get('amount', '')}"
                for ing in (obj.get("ingredients") or [])
            ),
            "步驟:",
            "\n".join(
                f"  {k}. {v}"
                for k, v in sorted((obj.get("steps") or {}).items(), key=lambda x: int(x[0]))
            ),
        ]
        page_content = "\n".join(content_parts)
        metadata = meta_func(obj, seq_num=i)
        docs.append(Document(page_content=page_content, metadata=metadata))
    return docs


def docs_store_chroma(docs: List[Document]) -> Chroma:
    # splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        # persist_directory="./recipe_chroma_db",
        collection_name="recipes"
    )
    print("✨ 已存入資料筆數進入向量資料庫：", vectordb._collection.count())
    return vectordb

class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[str]

# 定義結構化評分模型
class RecipeRatingItem(BaseModel):
    title: str = Field(..., description="食譜名稱")
    score: int = Field(..., ge=1, le=3, description="食譜評分，1 到 3 分")
    reason: str = Field(..., description="給出這個評分的簡短理由")
    image_url: str = Field("", description="食譜圖片的網址")
    recipe_link: str = Field("", description="食譜原始連結")

    class Config:
        extra = "allow"

class RecipeRatings(BaseModel):
    ratings: List[RecipeRatingItem]

def build_workflow(vectorstore: Chroma, k: int):
    llm = init_chat_model(model_name, model_provider="groq")
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})  # 取前 k 筆

    system_prompt = """
    你是一位專業的食譜分析師，熟悉各類食材與烹飪技巧。  
    請根據使用者提供的條件，為檢索到的每道食譜打分（1~3 分，1 代表不符合，2 代表部分符合，3 代表符合），並簡要說明打分的理由。  
    只要有關聯都屬於部分符合，對於符合條件不必太嚴謹。
    分數越高代表越符合條件，不須分析與條件無關的內容。  
    請只回傳 JSON 格式，內容包含 title（食譜名稱）、score（分數）、reason（理由）。  
    請使用繁體中文回答理由。
    """

    user_prompt = """
    以下是使用者的評分條件：{question}

    請根據這些條件，閱讀以下食譜內容並進行評分，並給出簡短理由。
    （1~3 分，1 代表不符合，2 代表部分符合，3 代表符合）
    分數越高代表越符合條件，不須分析與條件無關的內容：

    {recipe_content}

    請只回傳 JSON 格式，內容包含score（分數）、reason（理由）。  
    請使用繁體中文回答理由。
    """

    # 評分用 Prompt
    rating_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])

    rating_chain = rating_prompt | llm.with_structured_output(RecipeRatingItem)

    workflow = StateGraph(GraphState)

    def retrieve(state):
        print("---檢索文件中---")
        question = state["question"]
        documents = retriever.invoke(question)
        return {"documents": documents, "question": question}

    def generate(state):
        print("---評分中---")
        documents = state["documents"]
        ratings = []

        for doc in documents:
            recipe_content = doc.page_content
            title = doc.metadata.get("recipe_name", "未知食譜")
            image_url = doc.metadata.get("image_url", "")
            recipe_link = doc.metadata.get("recipe_link", "")  # 取得連結

            try:
                result = rating_chain.invoke({
                    "title": title,
                    "recipe_content": recipe_content,
                    "question": state["question"]
                })

                if isinstance(result, RecipeRatingItem):
                    result = result.model_copy(update={
                        "title": title,
                        "image_url": image_url,
                        "recipe_link": recipe_link
                    })
                elif isinstance(result, dict):
                    result.setdefault("reason", "模型未提供理由")
                    result = RecipeRatingItem(
                        title=title,
                        image_url=image_url,
                        recipe_link=recipe_link,
                        **result
                    )

                ratings.append(result)

            except Exception as e:
                print("評分失敗：", e)
                ratings.append(RecipeRatingItem(
                    title=title,
                    score=0,
                    reason="模型評分失敗，無法提供理由。",
                    image_url=image_url,
                    recipe_link=recipe_link
                ))


            print(f"【{title}】")
            print(f"⭐ 評分：{result.score}")
            print(f"💬 理由：{result.reason}")
            print("=====================================")

        return {
            "documents": documents,
            "question": state["question"],
            "generation": RecipeRatings(ratings=ratings).model_dump()
        }



    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
