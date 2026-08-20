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

    # 100개 상품이 완전히 렌더링되도록 촘촘하게 스크롤 실행
    for i in range(15):
        driver.execute_script(f"window.scrollTo(0, {i * 600});")
        time.sleep(0.8)

    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    
    products = []
    seen_urls = set()

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

            # 1. 가격 추출 ('원'과 숫자가 포함된 행)
            prices = [l for l in lines if '원' in l and any(c.isdigit() for c in l)]
            if not prices:
                continue
            price = prices[-1]  # 최종 할인가 선택

            # 2. 노이즈 및 할인율(%) 필터링
            noise_keywords = ["급상승", "단독", "품절임박", "쿠폰", "보는 중", "도착보장", "구매", "적립", "무료배송", "할인"]
            clean_lines = []
            for line in lines:
                if line.isdigit():  # 순위 숫자/ID 제거
                    continue
                if re.match(r'^\d+%$', line):  # '16%', '30%' 등 할인율 제거
                    continue
                if any(kw in line for kw in noise_keywords):
                    continue
                if '원' in line:
                    continue
                clean_lines.append(line)

            # 3. 브랜드 및 상품명 정밀 분리
            if len(clean_lines) >= 2:
                brand = clean_lines[0]
                title = " ".join(clean_lines[1:])
            elif len(clean_lines) == 1:
                brand = "무신사"
                title = clean_lines[0]
            else:
                continue

            # 상단 광고나 랭킹 외 상품 방지 (브랜드명과 상품명이 정상 분리된 경우만)
            if brand and title and title != brand:
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