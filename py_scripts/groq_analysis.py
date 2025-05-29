import getpass
import os
from groq import Groq
import re

client = Groq()
model_name = "llama3-8b-8192"

def set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

def generate_true_false(recipe, question):
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


    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=1
    )

    # 模型輸出
    raw_output = response.choices[0].message.content.strip().lower()

    # 使用正則式尋找 "true" 或 "false"
    match = re.search(r'\b(true|false)\b', raw_output)

    if match:
        print(f"【{recipe['recipe_name']}】: {match.group(1)}")
        return match.group(1)
    else:
        print("⚠️ match 失敗")
        return "false"

def generate(recipe, question):
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


    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=300
    )

    thoughts = response.choices[0].message.content
    return thoughts

def rewrite_answer(question, first_generation):
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

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=300
    )

    thoughts = response.choices[0].message.content
    return thoughts

def generate_result(recipe, question):
    print("=====================================")
    print(f"🔍分析食譜: {recipe['recipe_name']}\n")
    first_genreation = generate(recipe, question)
    print("💭初步依據食譜的回答:")
    print(first_genreation)
    
    result = rewrite_answer(question, first_genreation)
    print("\n✨精簡後的回答:")
    print(result)
    
    return result

if __name__ == "__main__":

    # 確保環境變數已設置
    api_key = input("請輸入 Groq Api Key: ")
    client = Groq(api_key=api_key)
    print("可用model:")
    models = client.models.list()
    for model in models.data:
        print(model.id)