import requests
from bs4 import BeautifulSoup
import json
import os
import datetime
from collections import defaultdict
import asyncio
import aiohttp
from py_scripts.crawler_detail import parse_chinese_number, format_ingredients

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}

base_url = "https://icook.tw"

async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            print(f"無法取得食譜: {url} 狀態碼: {response.status}")
            return None  # 或拋出例外，視需求而定
        text = await response.text()
        return text

async def parse_recipe_detail_async(session, link, img_url_small):
    print(f"Processing: {link}")
    html = await fetch(session, link)
    if html is None:
        # 頁面無法取得，回傳 None 或其他適當值
        return None
    
    root = BeautifulSoup(html, "html.parser")

    title = root.find("title")

    if "愛料理上找不到您要的頁面喔～" in title.get_text(strip=True):
        print(f"無法取得食譜: {link} 找不到頁面")
        return None

    name = root.find("h1", id="recipe-name")
    is_vip = name.find("title")
    if is_vip and is_vip.get_text(strip=True) == "VIP 專屬":
        print(f"VIP 專屬食譜: {link}")
        return None

    username = root.find("div", class_="author-name")
    user_stats = root.find_all("span", class_="author-stat")
    for stat in user_stats:
        text = stat.get_text(strip=True)
        if "食譜" in text:
            try:
                user_recipe_str = stat.find("span", class_="stat-num").get_text(strip=True)
                user_recipe = parse_chinese_number(user_recipe_str)
                if user_recipe is None:
                    print(f"無法取得或轉換食譜數字: {user_recipe_str}")
            except AttributeError:
                user_recipe = None
                print("無法取得食譜數字: 無資料")
        elif "粉絲" in text:
            try:
                user_fans_str = stat.find("span", class_="stat-num").get_text(strip=True)
                user_fans = parse_chinese_number(user_fans_str)
                if user_fans is None:
                    print(f"無法取得或轉換粉絲數字: {user_fans_str}")
            except AttributeError:
                user_fans = None
                print("無法取得粉絲數字: 無資料")
    try:
        image_url = root.find("div", class_="ratio-container ratio-container-custom").find("img").get("src", None)
    except:
        image_url = img_url_small

    description = root.find("section", class_="description")
    tags = root.find_all("li", class_="tag")
    tag_list = [tag.get_text(strip=True).replace("#", "") for tag in tags]
    left_block = root.find("span", class_="stat-left")
    if left_block and "說讚" in left_block.get_text(strip=True):
        like_text = left_block.get_text(strip=True).split("說讚")[0].strip()
        like_count = parse_chinese_number(like_text)
        if like_count is None:
            print(f"無法將 '{like_text}' 轉換為整數")
    right_block = root.find("span", class_="stat-right")
    if right_block:
        right_block_stat = right_block.find_all("a", class_="stat")
        for stat in right_block_stat:
            if "一起做" in stat.get_text(strip=True):
                together_text = stat.get_text(strip=True).split("一起做")[0].strip()
                together_count = parse_chinese_number(together_text)
                if together_count is None:
                    print(f"無法將 '{together_text}' 轉換為整數")
            elif "留言" in stat.get_text(strip=True):
                comment_text = stat.get_text(strip=True).split("留言")[0].strip()
                comment_count = parse_chinese_number(comment_text)
                if comment_count is None:
                    print(f"無法將 '{comment_text}' 轉換為整數")

    ingredient_list = []
    ingredients = root.find_all("li", class_="ingredient")
    for ingredient in ingredients:
        try:
            ingredient_name = ingredient.find("div", class_="ingredient-name")
            ingredient_amount = ingredient.find("div", class_="ingredient-unit")
            ingredient_group = ingredient.parent.parent.find("div", class_="group-name")
            ingredient_dic = {
                "name": ingredient_name.get_text(strip=True) if ingredient_name else None,
                "amount": ingredient_amount.get_text(strip=True) if ingredient_amount else None,
                "group": ingredient_group.get_text(strip=True) if ingredient_group else None
            }
            ingredient_list.append(ingredient_dic)
        except AttributeError:
            print(f"無法取得食材名稱或數量: {ingredient}")
            continue

    steps_dic = {}
    steps = root.find_all("li", class_="recipe-details-step-item")
    for count, step in enumerate(steps, start=1):
        try:
            step_text = step.find("p", class_="recipe-step-description-content").get_text(strip=True)
            steps_dic[count] = step_text
        except AttributeError:
            print(f"無法取得步驟描述: {step}")
            continue
        

    metas = root.find("div", class_="recipe-detail-metas")
    view_str = metas.find("div")
    try:
        if "瀏覽" in view_str.get_text(strip=True):
            view_str = view_str.get_text(strip=True).split("瀏覽")[0].strip()
            view_count = parse_chinese_number(view_str)
            if view_count is None:
                print(f"無法將 '{together_text}' 轉換為整數")
    except Exception as e:
        view_count = None
        print(f"錯誤: {e}")
    date = metas.find("time")['datetime']

    recipe = {
        "recipe_name": name.get_text(strip=True) if name else None,
        "recipe_link": link,
        "user_name": username.get_text(strip=True) if username else None,
        "user_recipe": user_recipe if 'user_recipe' in locals() else 0,
        "user_fans": user_fans if 'user_fans' in locals() else 0,
        "image_url": image_url if 'image_url' in locals() else None,
        "description": description.get_text(strip=True) if description else None,
        "tags": tag_list if tag_list else [],
        "like_count": like_count if 'like_count' in locals() else 0,
        "together_count": together_count if 'together_count' in locals() else 0,
        "comment_count": comment_count if 'comment_count' in locals() else 0,
        "ingredients": ingredient_list if ingredient_list else [],
        'ingredients_context' : format_ingredients(ingredient_list),
        "steps": steps_dic if steps_dic else {},
        "view_count": view_count if 'view_count' in locals() else 0,
        "date": date if date else None,
    }
    print(recipe)
    return recipe

async def search_recipes_link_async(session, link):
    html = await fetch(session, link)
    root = BeautifulSoup(html, "html.parser")

    links = []
    recipe_items = root.find_all("li", class_="browse-recipe-item")
    for item in recipe_items:
        link = base_url + item.find("a", class_="browse-recipe-link")["href"]
        img_url_small = item.find("img")["data-src"]
        links.append([link, img_url_small])
        print(link)

    next_page = root.find("li", class_="pagination-tab page--next")
    next_url = None
    if next_page:
        next_url = base_url + next_page.find("a")["href"]

    return links, next_url

async def async_search_recipes(
    text_input, search_number,
    like_on, like_min, like_max,
    together_on, together_min, together_max,
    comment_on, comment_min, comment_max,
    view_on, view_min, view_max,
    recipe_on, recipe_min, recipe_max,
    fans_on, fans_min, fans_max,
):
    async with aiohttp.ClientSession() as session:
        search_recipe = text_input
        search_url = f"https://icook.tw/search/{search_recipe}"
        recipes = []
        seen_links = set()

        while len(recipes) < search_number:
            if search_url is None:
                break

            # 非同步的搜尋連結函式，需你自行實作
            recipe_links, search_url = await search_recipes_link_async(session, search_url)

            if recipe_links is None:
                break

            # 建立多個非同步任務同時抓取食譜細節
            tasks = []
            for link, img_url_small in recipe_links:
                if len(recipes) + len(tasks) >= search_number:
                    break
                if link in seen_links:
                    continue
                # 非同步抓取詳細資料
                tasks.append(parse_recipe_detail_async(session, link, img_url_small))

            results = await asyncio.gather(*tasks)

            for recipe in results:
                if recipe is None:
                    continue

                # 篩選條件
                if like_on and (recipe["like_count"] < like_min or recipe["like_count"] > like_max):
                    continue
                if together_on and (recipe["together_count"] < together_min or recipe["together_count"] > together_max):
                    continue
                if comment_on and (recipe["comment_count"] < comment_min or recipe["comment_count"] > comment_max):
                    continue
                if view_on and (recipe["view_count"] < view_min or recipe["view_count"] > view_max):
                    continue
                if recipe_on and (recipe["user_recipe"] < recipe_min or recipe["user_recipe"] > recipe_max):
                    continue
                if fans_on and (recipe["user_fans"] < fans_min or recipe["user_fans"] > fans_max):
                    continue

                if recipe["recipe_link"] in seen_links:
                    continue

                recipes.append(recipe)
                seen_links.add(recipe["recipe_link"])

        return recipes