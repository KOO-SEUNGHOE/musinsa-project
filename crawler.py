import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

try:
    print("무신사 전체 실시간 랭킹 페이지 접속 중...")
    url = "https://www.musinsa.com/main/musinsa/ranking?gf=A&storeCode=musinsa&sectionId=199&contentsId=&categoryCode=000&ageBand=AGE_BAND_ALL&subPan=product"
    driver.get(url)
    time.sleep(5)

    # 100개 상품이 완전히 렌더링되도록 스크롤 실행
    for i in range(15):
        driver.execute_script(f"window.scrollTo(0, {i * 800});")
        time.sleep(1)

    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    
    products = []
    seen_urls = set()

    # 노이즈 문구 필터링 키워드 (급상승, 판매, 구매 등 완전 제거)
    ignore_keywords = ["급상승", "단독", "품절임박", "쿠폰", "도착보장", "구매", "판매", "보는 중", "적립", "무료배송", "후기"]

    for link in links:
        href = link.get_attribute("href")
        if not href or href in seen_urls:
            continue

        try:
            card = link.find_element(By.XPATH, "./ancestor::li | ./ancestor::div[contains(@class, 'goods')] | ./ancestor::div[contains(@class, 'item')] | ./..")
            text = card.text.strip()
            if not text:
                continue

            lines = [l.strip() for l in text.split('\n') if l.strip()]

            # 1. 단순 숫자(순위), 배지 문구, 단독 할인율(%) 필터링
            clean_lines = []
            for line in lines:
                if line.isdigit():  # 순위 숫자 (1, 2, 3...) 제거
                    continue
                if re.match(r'^\d+%$', line):  # '28%' 등 단독 할인율 제거
                    continue
                if any(kw in line for kw in ignore_keywords):  # '급상승', '판매 2.4천개' 등 제거
                    continue
                clean_lines.append(line)

            # 2. 가격('원' 문맥) 찾기 및 추출
            price = None
            price_line_idx = -1
            for idx, line in enumerate(clean_lines):
                match = re.search(r'([\d,]+원)', line)
                if match:
                    price = match.group(1)  # '70,560원' 형태만 정밀 추출
                    price_line_idx = idx
                    break

            if not price or price_line_idx == -1:
                continue

            # 3. 가격 표시 이전 줄들을 브랜드와 상품명으로 분리
            info_lines = clean_lines[:price_line_idx]
            if len(info_lines) >= 2:
                brand = info_lines[0]
                title = " ".join(info_lines[1:])
            elif len(info_lines) == 1:
                brand = info_lines[0]
                title = info_lines[0]
            else:
                continue

            if brand and title:
                seen_urls.add(href)
                products.append({
                    "Rank": len(products) + 1,
                    "Brand": brand,
                    "Title": title,
                    "Price": price
                })

            if len(products) >= 100:
                break

        except Exception:
            continue

    df = pd.DataFrame(products)
    print(f"수집 성공! 총 {len(df)}개 상품.")
    if len(df) > 0:
        df.to_csv("musinsa_new_ranking_top100.csv", index=False, encoding="utf-8-sig")
        print("CSV 파일 저장 완료.")

finally:
    driver.quit()