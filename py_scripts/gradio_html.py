import asyncio
from py_scripts.crawler_detail import *
from py_scripts.crawler_detail_async import *
from py_scripts.groq_analysis import *
from py_scripts.rag import *

def format_search_result_html(results, query, search_number, page, page_size=50):
    result_count = len(results)
    total_pages = (result_count - 1) // page_size + 1
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, result_count)

    if result_count == 0:
        return '<div class="result-box">沒有找到符合條件的食譜，請嘗試其他關鍵字。</div>'

    result_message = f"實際找到 {result_count} 筆結果（搜尋條件為 {search_number} 筆），顯示第 {page+1} 頁（共 {total_pages} 頁）。"
    html = [
        f'<div class="result-box">'
        f'<h2>搜尋關鍵字: <b>{query}</b></h2>'
        f'<p>{result_message}</p><br>'
    ]

    for item in results[start_idx:end_idx]:
        name = item.get("recipe_name", "")
        link = item.get("recipe_link", "#")
        img  = item.get("image_url", "")
        tags = item.get("tags", [])

        tags_html = ""
        if tags:
            badges = "".join(f'<span class="tag-badge">{t}</span>' for t in tags)
            tags_html = f'<div class="result-tags">{badges}</div>'

        html.append(f'''
        <div class="result-item">
            <img class="result-thumb" src="{img}" alt="{name}">
            <div class="result-info">
                <h3 class="result-title">{name}</h3>
                {tags_html}
                <a class="result-link" href="{link}" target="_blank" rel="noopener noreferrer">連結</a>
            </div>
        </div>
        ''')

    html.append("</div>")
    return "\n".join(html)

def update_search_page(page, recipes, direction, query, search_number):
    if len(recipes) == 0:
        return '<div class="result-box">⚠️ 尚未有可顯示的搜尋結果。</div>', 0

    if direction == "prev":
        page = max(0, page - 1)
    elif direction == "next":
        page = min((len(recipes) - 1) // 50, page + 1)

    html = format_search_result_html(recipes, query, search_number, page)
    return html, page


def get_recipe_block(recipes, page, per_page=100):
    total_pages = (len(recipes) - 1) // per_page + 1
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    end = start + per_page
    html = f'<div class="pagination-info">頁數：{page + 1} / {total_pages}</div>'
    html += '<div class="image-gallery">'

    for idx, r in enumerate(recipes[start:end]):
        real_idx = start + idx
        html += f'''
        <div class="image-option" data-index="{real_idx}">
          <img src="{r['image_url']}" width="100" alt="{r['recipe_name']}" loading="lazy" />
          <div>{r['recipe_name']}</div>
        </div>
        '''
    html += '</div>'
    return html

def update_recipe_page(page, recipes, direction):
    if len(recipes) == 0:
        return '<div class="image-gallery">⚠️ 尚未有可顯示的搜尋結果。</div>', 0
    
    if direction == "prev":
        page = max(0, page - 1)
    elif direction == "next":
        page = min((len(recipes) - 1) // 100, page + 1)
    html = get_recipe_block(recipes, page)
    return html, page


def dummy_search(
    text_input, search_number,
    like_on, like_min, like_max,
    together_on, together_min, together_max,
    comment_on, comment_min, comment_max,
    view_on, view_min, view_max,
    recipe_on, recipe_min, recipe_max,
    fans_on, fans_min, fans_max,
):
    def check_range(on, min_val, max_val, name):
        if on:
            if min_val is None or max_val is None:
                return f"⚠️ 請完整填寫{name}的最小值與最大值"
            try:
                min_num = float(min_val)
                max_num = float(max_val)
            except ValueError:
                return f"⚠️ {name}的最小值與最大值必須是數字"
            if min_num > max_num:
                return f"⚠️ {name}的最小值不可大於最大值"
        return None

    for on, min_v, max_v, label in [
        (like_on, like_min, like_max, "讚數"),
        (together_on, together_min, together_max, "一起做數"),
        (comment_on, comment_min, comment_max, "留言數"),
        (view_on, view_min, view_max, "瀏覽數"),
        (recipe_on, recipe_min, recipe_max, "作者食譜數"),
        (fans_on, fans_min, fans_max, "作者粉絲數"),
    ]:
        msg = check_range(on, min_v, max_v, label)
        if msg:
            return msg, "", []

    try:
        search_num = int(search_number)
        if search_num <= 0:
            return "⚠️ 搜尋數量必須為大於0的整數", "", []
    except Exception:
        return "⚠️ 搜尋數量必須為整數", "", []

    search_results = asyncio.run(async_search_recipes(
        text_input, search_num,
        like_on=like_on, like_min=like_min, like_max=like_max,
        together_on=together_on, together_min=together_min, together_max=together_max,
        comment_on=comment_on, comment_min=comment_min, comment_max=comment_max,
        view_on=view_on, view_min=view_min, view_max=view_max,
        recipe_on=recipe_on, recipe_min=recipe_min, recipe_max=recipe_max,
        fans_on=fans_on, fans_min=fans_min, fans_max=fans_max
    ))

    if len(search_results) == 0:
        return '<div class="result-box">沒有找到符合條件的食譜，請嘗試其他關鍵字。</div>', '', []

    page = 0
    html = format_search_result_html(search_results, text_input, search_number, page)

    return html, get_recipe_block(search_results, page), search_results, page

def handle_true_false_question(selected_indexes_str, question, recipes):
    if not selected_indexes_str.strip():
        return "⚠️ 請先選擇至少一個食譜。"

    try:
        selected_indexes = [int(i) for i in selected_indexes_str.split(",") if i.strip().isdigit()]
    except:
        return "⚠️ 解析選取資料失敗"

    selected_recipes = [recipes[i] for i in selected_indexes if 0 <= i < len(recipes)]

    if not selected_recipes:
        return "⚠️ 找不到選取的食譜"

    true_items = []
    false_items = []
    

    answers = []
    for r in selected_recipes:
        try:
            answer = generate_true_false(r, question)  # 同步呼叫
        except Exception as e:
            print(f"錯誤：{e}")
            answer = "false"
        answers.append(answer)

    for r, answer in zip(selected_recipes, answers):
        block = f'''
        <div class="match-item">
            <img class="match-thumb" src="{r['image_url']}" alt="{r['recipe_name']}">
            <div class="match-info">
                <h3 class="match-title">
                    <a href="{r['recipe_link']}" target="_blank">{r['recipe_name']}</a>
                </h3>
            </div>
        </div>
        '''

        if answer.strip().lower() == "true":
            true_items.append(block)
        else:
            false_items.append(block)

    output_html = ['<div class="match-group">']

    if true_items:
        output_html.append('''
        <div class="match-section match-true">
            <h2 class="match-header">✅ 符合條件的食譜</h2>
            <div class="true-false-image">
                <div class="items-container">
        ''')
        output_html.extend(true_items)
        output_html.append('''
                </div>
            </div>
        </div>
        ''')

    if false_items:
        output_html.append('''
        <div class="match-section match-false">
            <h2 class="match-header">❌ 不符合條件的食譜</h2>
            <div class="true-false-image">
                <div class="items-container">
        ''')
        output_html.extend(false_items)
        output_html.append('''
                </div>
            </div>
        </div>
        ''')

    output_html.append('</div>')

    return "\n".join(output_html)

def handle_chat_question(selected_indexes_str, question, recipes):
    if not selected_indexes_str.strip():
        return "⚠️ 請先選擇至少一個食譜。"

    try:
        selected_indexes = [int(i) for i in selected_indexes_str.split(",") if i.strip().isdigit()]
    except:
        return "⚠️ 解析選取資料失敗"

    selected_recipes = [recipes[i] for i in selected_indexes if 0 <= i < len(recipes)]

    if not selected_recipes:
        return "⚠️ 找不到選取的食譜"

    output_html = ['<div class="chat-box">']
    
    answers = []
    for r in selected_recipes:
        try:
            answer = generate_result(r, question)  # 同步呼叫
        except Exception as e:
            print(f"錯誤：{e}")
            answer = "⚠️ 無法輸出回覆"
        answers.append(answer)

    for r, answer in zip(selected_recipes, answers):
        output_html.append(f"""
        <div class="chat-item">
            <img class="chat-thumb" src="{r['image_url']}" alt="{r['recipe_name']}">
            <div class="chat-info">
                <h3 class="chat-title">
                    <a href="{r['recipe_link']}" target="_blank">{r['recipe_name']}</a>
                </h3>
                <div class="chat-desc">{answer}</div>
            </div>
        </div>
        """)

    output_html.append("</div>")
    return "\n".join(output_html)

def store_vectorstore(data_list):
    if not data_list:
        return "⚠️ 請先搜索食譜", None
    docs = build_docs_from_list(data_list)
    vectorstore = docs_store_chroma(docs)
    return f"✅ 已存入資料進入向量資料庫：{vectorstore._collection.count()}筆" , vectorstore

def handle_rag_question(question, vectorstore, k=20):
    if vectorstore is None:
        return "⚠️ 尚未建立檢索庫，請先點擊「存入檢索庫」"
    
    if not question.strip():
        return "⚠️ 請輸入問題"

    app = build_workflow(vectorstore, int(k))
    result = app.invoke({"question": question})

    ratings = result.get("generation", {}).get("ratings", [])
    if not ratings:
        return "⚠️ 沒有取得任何評分結果"

    output_html = ['<div class="rag-box">']
    for item in ratings:
        title = item.get("title", "未知食譜")
        score = item.get("score", "無評分")
        image_url = item.get("image_url", "")
        reason = item.get('reason', '無理由說明')
        link = item.get('recipe_link', '無理由說明')

        output_html.append(f"""
        <div class="rag-item">
            <img class="rag-thumb" src="{image_url}" alt="{title}">
            <div class="rag-info">
                <h3 class="rag-title">
                    <a href="{link}" target="_blank">{title}</a>
                </h3>
                <div class="rag-desc">
                    ⭐ 評分：{score} <br>
                    💬 理由：{reason}
                </div>
            </div>
        </div>
        """)


    output_html.append("</div>")
    return "\n".join(output_html)
