from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import requests
import os
import time
from io import BytesIO
from urllib.parse import quote

def download_sogou_images_selenium(keyword, limit=200, save_dir="data/sogou_images"):
    os.makedirs(save_dir, exist_ok=True)

    options = Options()
    options.add_argument('--headless')  # 不打开浏览器窗口
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    url = f"https://pic.sogou.com/pics?query={quote(keyword)}"
    driver.get(url)

    print(f"🔍 搜索：{url}")
    image_urls = set()
    scroll_times = 0

    while len(image_urls) < limit and scroll_times < 50:
        # 模拟滚动以触发加载
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        imgs = driver.find_elements(By.TAG_NAME, 'img')
        for img in imgs:
            src = img.get_attribute('src')
            if src and src.startswith('http') and '.gif' not in src:
                image_urls.add(src)
        scroll_times += 1

    print(f"📷 获取图片链接数量：{len(image_urls)}")

    driver.quit()

    # 下载图片
    count = 0
    for src in image_urls:
        if count >= limit:
            break
        try:
            img_data = requests.get(src, timeout=10).content
            img = Image.open(BytesIO(img_data)).convert("RGB")
            img = img.resize((299, 299))
            img.save(f"{save_dir}/{keyword.replace(' ', '_')}_sogou_{count + 1}.jpg", "JPEG", quality=95)
            print(f"[{count + 1}] ✅ 下载：{src}")
            count += 1
        except Exception as e:
            print(f"❌ 跳过图片：{e}")

    print(f"✅ 下载完成，共保存 {count} 张图片")

# 示例使用
save_dir = "data/鹿角_sogou"
download_sogou_images_selenium("鹿角 中药", limit=1000, save_dir=save_dir)
