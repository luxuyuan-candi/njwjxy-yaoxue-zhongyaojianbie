import os
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import quote
import time

def download_360_images(keyword, limit=100, save_dir='data/zhongyao_360'):
    os.makedirs(save_dir, exist_ok=True)
    count = 0
    page = 1

    print(f"\n🔍 开始爬取：{keyword}（目标 {limit} 张）")

    while count < limit:
        url = f"https://image.so.com/j?q={quote(keyword)}&pn=60&sn={(page - 1) * 60}"
        print("URL:", url)
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = requests.get(url, headers=headers, timeout=10).json()
            img_list = resp.get("list", [])
            if not img_list:
                print("⚠️ 没有更多图片了")
                break

            for img in img_list:
                if count >= limit:
                    break
                img_url = img.get("qhimg_url") or img.get("img")
                if not img_url:
                    continue

                try:
                    img_data = requests.get(img_url, timeout=10).content
                    image = Image.open(BytesIO(img_data)).convert("RGB")
                    image = image.resize((299, 299))
                    image.save(os.path.join(save_dir, f"{keyword.replace(' ', '_')}_360_{count+1}.jpg"), "JPEG", quality=95)
                    print(f"[{count+1}] ✅ 下载：{img_url}")
                    count += 1
                except Exception as e:
                    print(f"❌ 跳过图片：{e}")
            page += 1
            time.sleep(1)

        except Exception as e:
            print(f"请求失败：{e}")
            break

    print(f"✅ 共保存 {count} 张图片\n")

# 示例关键词：天麻、枸杞、白果、当归...
zhongyao_list = [
    "血竭",
    "青皮", "黄柏", "海藻", "全蝎", "炙甘草", "冬虫夏草", "青礞石", "紫苏梗", "葛根", "瓜蒌皮",
    "金果榄", "仙茅", "青蒿", "乌梢蛇", "防己", "羌活", "菊花", "龙胆", "罗汉果", "何首乌",
]
for i in zhongyao_list:
    save_dir = f"data/{i}"
    download_360_images(f"{i} 中药", limit=1000, save_dir=save_dir)
    time.sleep(10)