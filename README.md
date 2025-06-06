# GenAI\_recipe\_chatbot

## 摘要

* **爬蟲功能（蒐集食譜資訊）**：

上網搜尋食譜名稱，並依據使用者提供的限制，爬取食譜的詳細資訊供後續分析。

* **對話機器人功能（純語言模型）**：

透過語言模型處理使用者輸入，能針對使用者選取的食譜回答相關問題。模型會獲得食譜的詳細資料，並進行詳細的分析以回答使用者的問題。主要目的是快速了解食譜資訊。

* **檢索系統功能（RAG 架構）**：

採用 RAG 技術，先從食譜資料庫中檢索最相關內容，再結合語言模型生成回答。每個食譜都會根據使用者的條件進行評分，並給出評分背後的理由。主要目的是使用不同於網站的搜尋方式，更加多元的去找尋使用者有興趣的食譜。

## 🕸️ 爬蟲

**爬取來源**：[愛料理](https://icook.tw/)

**目的**：透過查詢蒐集網站上的食譜資訊。


### 📄 食譜資訊範例

```json
{
  "recipe_name": "聖誕曲奇餅乾",
  "recipe_link": "https://icook.tw/recipes/471112",
  "user_name": "Iris玩轉廚房",
  "user_recipe": 42,
  "user_fans": 96,
  "image_url": "https://imageproxy.icook.network/fit?background=255%2C255%2C255&height=800&nocrop=false&stripmeta=true&type=auto&url=http%3A%2F%2Ftokyo-kitchen.icook.tw.s3.amazonaws.com%2Fuploads%2Frecipe%2Fcover%2F471112%2Ff05766f1340b18ba.jpg&width=800",
  "description": "描述聖誕節到了，來個應景又可愛的節慶餅乾吧！",
  "tags": [
    "聖誕餅乾",
    "烘焙",
    "甜點",
    "家庭烘焙",
    "餅乾製作",
    "烤箱食譜",
    "手工餅乾",
    "節慶食譜"
  ],
  "like_count": 32,
  "together_count": 0,
  "comment_count": 1,
  "ingredients": [
    { "name": "低筋麵粉", "amount": "150克", "group": null },
    { "name": "糖粉", "amount": "40克", "group": null },
    { "name": "無鹽奶油", "amount": "80克", "group": null },
    { "name": "蛋", "amount": "0.5顆", "group": null },
    { "name": "可可粉", "amount": "3克", "group": null },
    { "name": "抹茶粉", "amount": "3克", "group": null }
  ],
  "ingredients_context": "1. 低筋麵粉 : 150克\n2. 糖粉 : 40克\n3. 無鹽奶油 : 80克\n4. 蛋 : 0.5顆\n5. 可可粉 : 3克\n6. 抹茶粉 : 3克\n",
  "steps": {
    "1": "糖粉過篩",
    "2": "加入室溫軟化的無鹽奶油",
    "3": "先將糖粉和無鹽奶油略微混合後，用打蛋器打至蓬鬆",
    "4": "加入蛋",
    "5": "打發至吸收",
    "6": "加入過篩的低筋麵粉",
    "7": "將麵糰混合均勻",
    "8": "麵糰分成3等份",
    "9": "1份麵糰加入過篩的抹茶粉混合成糰",
    "10": "1份麵糰加入過篩的可可粉混合成糰",
    "11": "完成3種顏色的麵糰",
    "12": "將麵糰放在塑膠袋內桿成約0.3公分厚，於冰箱冷藏30分鐘",
    "13": "餅乾模撒少許低筋麵粉防沾，然後在麵糰上壓出形狀後，置於烤盤上",
    "14": "烤箱以140度預熱10分鐘後，將餅乾烘烤10分鐘，再將烤盤前後翻轉，續烤10分鐘。",
    "15": "餅乾完成"
  },
  "view_count": 4092,
  "date": "2024-12-26"
}
```

### 📄 食譜格式介紹

| 欄位名稱                   | 資料型態                                | 簡短說明                |
| ---------------------- | ----------------------------------- | ------------------- |
| `recipe_name`          | string                              | 食譜名稱                |
| `recipe_link`          | string(URL)                         | 食譜的網址連結             |
| `user_name`            | string                              | 食譜作者名稱              |
| `user_recipe`          | integer                             | 作者發佈的食譜數量           |
| `user_fans`            | integer                             | 作者的粉絲數              |
| `image_url`            | string(URL)                         | 食譜圖片的網址             |
| `description`          | string or null                      | 食譜簡短描述，可為空          |
| `tags`                 | list of strings                     | 食譜相關標籤              |
| `like_count`           | integer                             | 食譜被按讚的次數            |
| `together_count`       | integer                             | 食譜參與「一起做」的人數          |
| `comment_count`        | integer                             | 食譜留言數               |
| `ingredients`          | list of objects                     | 食材清單，每個物件包含名稱、數量、分組 |
| `ingredients[].name`   | string                              | 食材名稱                |
| `ingredients[].amount` | string                              | 食材用量                |
| `ingredients[].group`  | string or null                      | 食材所屬分組（例如：若無可為 null）   |
| `ingredients_context`  | string                              | 食材詳細文字說明（ingredients的純文字版本）   |
| `steps`                | object (key: string, value: string) | 製作步驟，鍵為步驟序號，值為步驟描述  |
| `view_count`           | integer                             | 食譜被瀏覽次數             |
| `date`                 | string (YYYY-MM-DD)                 | 食譜發佈日期，格式為年-月-日     |




## 🟢 對話機器人功能一：是非題判斷（True/False）

使用者可以針對食譜內容提出「是」或「否」的問題，例如「這個食譜需要用到烤箱嗎？」「裡面有加雞蛋嗎？」等。

系統會根據食譜資料（包含名稱、描述、食材、步驟、觀看數、作者資訊等），利用語言模型判斷問題，最後回傳「**true**」或「**false**」作為答案。

### Generator for true or false
在 `system_prompt` 與 `user_prompt` 中都提出限制避免輸出其他關內容。

```python
system_prompt = """
    你是一位專業且經驗豐富的廚師，擅長分析各類食譜的材料、製作步驟與烹飪技巧。  
    請根據我提供的條件與資訊，判斷並回答「true」或「false」，以明確回應該問題。  
    回答時請僅輸出「true」或「false」。請勿輸出其他文字，不要加上任何解釋。
    """

    user_prompt = f"""
    以下是我要你分析的食譜內容:
    食譜名稱: {recipe['recipe_name']}
    食譜連結: {recipe['recipe_link']}
    食譜作者: {recipe['user_name']}
    食譜作者食譜數量: {recipe['user_recipe']}
    食譜作者粉絲數量: {recipe['user_fans']}
    食譜圖片: {recipe['image_url']}
    食譜描述: {recipe['description']}
    食譜標籤: {recipe['tags']}
    食譜喜歡數: {recipe['like_count']}
    食譜一起做數: {recipe['together_count']}
    食譜留言數: {recipe['comment_count']}
    食譜食材:
    {recipe['ingredients_context']}
    食譜步驟: {recipe['steps']}
    食譜觀看數: {recipe['view_count']}
    食譜日期: {recipe['date']}

    請根據這些資訊，回答問題:
    {question}

    請只回覆「true」或「false」，其他任何文字都是錯誤的。
    """
```
另外再額外限制 `max_token` 數量至 `1`
```python
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0,
    max_tokens=1
)
```

此功能特點如下：

* **回答快速**：只輸出 `true` 或 `false`，處理效率高，無需額外分析。
* **適合回答簡單的問題**：對於明確且具體的判斷題，如是否使用某種材料、是否包含特定步驟，能快速做出判斷。


## 🟣 對話機器人功能二：簡答題分析（Short Answer）

這個功能適合需要更詳細說明的問題，例如「這道食譜用了哪些材料？」或「食譜中需要用到幾顆雞蛋？」等。

我們使用兩階段式 `CoT` 的方式回答，幫助我們可以更簡短且明確地回答問題：

1. **初步回答**：根據食譜內容與問題，產出一段繁體中文的完整回覆，說明理由、步驟或細節。
2. **答案精簡**：將初步回覆進行語言修正（如英文詞轉換為繁體中文），最終輸出一句清晰簡短的回答。

### Generator
基於食譜資訊生成的回答。

單純的直接回答會容易出現一些不好的答案，如英文內容，多餘的解釋，提及非問題的食譜內容，所以使用兩階段的回答來避免這些情況。
```python
system_prompt = """
  你是一位擅長分析食譜的專業廚師，對各類料理的材料、製作步驟與烹飪技巧非常熟悉。
  請根據我提供的條件與資訊，給出明確且詳細的食譜分析結果。
  無論我提出何種要求或描述何種情境，你都需依據條件提供專業的建議與解說。
  回答時請使用繁體中文。
  """

user_prompt = f"""
    以下是我要你分析的食譜內容:
    食譜名稱: {recipe['recipe_name']}
    食譜連結: {recipe['recipe_link']}
    食譜作者: {recipe['user_name']}
    食譜作者食譜數量: {recipe['user_recipe']}
    食譜作者粉絲數量: {recipe['user_fans']}
    食譜圖片: {recipe['image_url']}
    食譜描述: {recipe['description']}
    食譜標籤: {recipe['tags']}
    食譜喜歡數: {recipe['like_count']}
    食譜一起做數: {recipe['together_count']}
    食譜留言數: {recipe['comment_count']}
    食譜食材:
    {recipe['ingredients_context']}
    食譜步驟: {recipe['steps']}
    食譜觀看數: {recipe['view_count']}
    食譜日期: {recipe['date']}

    請根據這些資訊，回答問題:
    {question}

    回答時請使用繁體中文。
    """
```
### Rewriter
基於 `generater` 生成的回答再進行重新分析，統整併精簡回答，避免亢長的答案，也使回答的格式叫回統一。

`system_prompt` 使用 `few-shot` 舉出幾個在實驗過程中出現的較為不好的 `generater` 輸出內容，並使用人工修正的方式給出實際範例告訴 `rewriter` 應該要怎麼改進會比較好。

最後發現使用 `few-shot` 能夠非常有效的讓 `rewriter` 寫出格式較為統一的答案。
```python
system_prompt = """
    你是一位擅長精簡答案的統整專家。
    你會獲得一個問題與AI所產出的答案，答案能會出現不正確的語言(如英文)、回答中斷、或是無法理解的內容。
    你需要根據問題與答案，將不正確的語言修正為繁體中文，並且將答案進行精簡與統整。
    請將答案中的不必要的內容刪除，並且保留最重要的資訊，且請勿虛構答案。
    輸出時不要使用換行，請使用標點符號來分隔就行，不要使用markdown格式。
    請確認輸出必須是繁體中文。

    例如:
    問題: 需要烤箱嗎?
    答案: 根據提供的食譜內容，食譜中明確地指出步驟14為烤箱烘烤，溫度為140度，時間為20分鐘，而餅乾完成後並未進行其他加工或 tratamiento。 因此，我可以確定食譜需要烤箱。
    
    精簡輸出: 需要烤箱，步驟14中指出需烤箱烘烤，溫度為140度，時間為20分鐘。

    問題: 有巧克力嗎?
    答案: 根據提供的食譜內容，沒有任何巧克力出現。在這個雪球曲奇餅乾的食譜中，主要的材料是奶油、糖粉、 粟粉、低筋麵粉。這些材料用於製造麵糰，最後形成雪球曲奇餅乾，並灑上糖霜。但是，沒有任何巧克力相關的食材或步驟出現。
    
    精簡輸出: 沒有巧克力。

    問題: 需要什麼材料?
    答案: 
    根據提供的食譜內容，所需的材料如下：
    1. 奶油：125克
    2. 糖粉：40克
    3. 粟粉：110克
    4. 低筋麵粉：90克
    總的來說，這個食譜需要四種主要材料：奶油、糖粉、粟粉和低筋麵粉。

    精簡輸出: 奶油125克、糖粉40克、粟粉110克、低筋麵粉90克。
    """

user_prompt = f"""
    題目:
    {question}

    AI的回答:
    {first_generation}

    請將不正確的語言修正為繁體中文，並且將答案進行精簡與統整。
    請直接輸出最後精簡完的答案，捨棄掉與題目無關的相關描述，無須輸出問題。
    若發現問題是與食譜無關的問題，請直接回覆「問題與食譜無關」。
    請確認輸出必須是繁體中文。
    """
```

此功能特點如下：

* 確保輸出為繁體中文。
* 精簡重整可使內容更易閱讀、排版整齊。
* 能辨別與食譜無關的問題，並回覆「問題與食譜無關」，避免語言模型亂回答。


## 🔍 RAG 檢索功能介紹

使用 `RAG` 能根據使用者輸入的條件或問題，從數千筆食譜資料中自動找出最相關的幾道食譜，以供後續進行分析與評分。
### 核心流程

1. **資料轉換為向量（Embedding）**

   每一筆食譜資料，只保留**食譜名稱、描述、標籤、食材與步驟**被整理成純文字格式（`page_content`），並將其餘的欄位（例如觀看數、作者資訊、連結等）會被儲存在 `metadata` 以提供後續的資料提取，最後將所有內容包裝成 `Document`。
   
   使用 `HuggingFaceEmbeddings` 模型（`all-mpnet-base-v2`）將文本轉換成向量。

    ```python
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    ```

2. **建立向量資料庫（Vector Store）**

    轉換後的向量會儲存在 `Chroma` 向量資料庫中。

    ```python
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        # persist_directory="./recipe_chroma_db",
        collection_name="recipes"
    )
    ```


3. **語意檢索（Semantic Search）**

    當使用者輸入條件後，系統會自動將輸入問題轉成向量。

    接著與資料庫中所有食譜的向量進行比對，**找出前 `k` 筆最相關的食譜**。

    ```python
    llm = init_chat_model(model, model_provider="groq")
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    ```

4. **返回高相關度結果**

    找到的食譜將作為後續語言模型的輸入，進行更多的詳細分析。

---
### 輸出格式限制
`score` 與 `reason`為語言模型的輸出內容，`title` 、 `image_url` 與 `recipe_link` 則從 `meta_data` 中取出。

```python
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
```
提取方式：
```python
recipe_content = doc.page_content
title = doc.metadata.get("recipe_name", "未知食譜")
image_url = doc.metadata.get("image_url", "")
recipe_link = doc.metadata.get("recipe_link", "")
```
---
### Generator
針對每個食譜內容與使用者條件進行打分與簡短的理由說明。

打分規則：
* 1分 (不符合條件)
* 2分 (部分符合條件)
* 3分 (完全符合條件)

```python
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
```

#### 技術細節與優勢

不同於原本 `愛料理` 的關鍵字搜尋，`RAG` 系統可以幫助我們找到更多元的食譜 (避免總是搜尋到網頁上固定的前幾個食譜)，且能分析食譜細節內容，找到更符合使用者需求的食譜。


## 🖼️ 介面介紹

### 🔍 搜尋網址

#### 📥 輸入框

* **輸入關鍵字**：輸入您想查詢的食譜名稱（如：餅乾、蛋糕）。
* **搜尋數量設定**：可自訂搜尋的食譜數量。
* **進階搜尋條件**：可依據讚數、留言數、瀏覽數等篩選符合條件的食譜。
* **作者條件篩選**：可依作者的食譜數與粉絲數進行過濾。

<div align="center">
  <img src="./img/search_interface.png" alt="搜尋介面"/>
</div>

#### 📤 輸出框

每頁顯示 50 筆食譜，透過「上一頁 / 下一頁」按鈕瀏覽。

<div align="center">
  <img src="./img/search_result.png" alt="搜尋結果"/>
</div>

---

### 🤖 對話機器人

#### 🔹 選擇食譜
從搜尋結果中點選一個或多個食譜進行分析。

#### 🔹 是非題
輸入「是或否」類型的問題，系統將根據食譜內容判斷答案，輸出至符合條件與不符合條件的輸出條件框。

<div align="center"> <img src="./img/true_false_interface.png" alt="是非題輸入介面"/> </div> 

<div align="center"> <img src="./img/true_false_result.png" alt="是非題結果畫面"/> </div>

#### 🔹 簡答
輸入開放性問題，系統將回覆相關資訊。

<div align="center"> <img src="./img/chat_interface.png" alt="簡答輸入介面"/> </div>

<div align="center"> <img src="./img/chat_result.png" alt="簡答結果畫面"/> </div>


---

### 🔎 檢索食譜

#### 📥 輸入框

* **向量資料儲存**：可將目前的食譜集建立向量庫並重複使用。
* **向量化檢索功能**：支援根據語意條件（如：用到水果的食譜）找出最相關的食譜。
* **可自訂檢索數量**：可設定每次檢索回傳的相關食譜筆數。

<div align="center">
  <img src="./img/rag_interface.png" alt="RAG 輸入介面"/>
</div>

#### 📤 輸出框

系統會回傳：

* 與查詢條件最相關的食譜清單

* 每道食譜的評分與評分理由

<div align="center">
  <img src="./img/rag_result.png" alt="RAG 檢索結果"/>
</div>



## 🛑 困難


### 🤖 對話機器人

1. 對於 true/false 的判斷，語言模型無須花過多的時間，然而簡答題使用了 `CoT` 的方式，輸出的 `token` 數量也較多，建議一次選取少於10個食譜，否則會需要等待非常多的時間。

2. 嘗試過使用非同步的方式呼叫，然而卻會受到 `Qroq` 每分鐘的可處理的請求與 `token` 數量限制。


### 🔎 RAG檢索系統

1. 存入向量庫時會花較多時間，通常需要5~10分鐘。
2. 使用向量查詢的方法不見得就能夠提取到目標食譜，且使用語言模型進行評分的方式可能標準不一，還是需對照評分理由來確認較為準確。


## 參考資料

* [Chroma](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
* [Build a Retrieval Augmented Generation (RAG) App: Part 1](https://python.langchain.com/docs/tutorials/rag/)
* [Build a Retrieval Augmented Generation (RAG) App: Part 2](https://python.langchain.com/docs/tutorials/qa_chat_history/)
* [Adaptive RAG](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/)