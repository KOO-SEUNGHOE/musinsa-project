import time
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
    time.sleep(4)

    # 100개 상품이 DOM에 렌더링되도록 구간별로 천천히 스크롤
    for i in range(12):
        driver.execute_script(f"window.scrollTo(0, {i * 700});")
        time.sleep(1)

    # 상품 링크 수집
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    
    products = []
    seen_urls = set()

    for link in links:
        href = link.get_attribute("href")
        if not href or href in seen_urls:
            continue
        
        try:
            # 부모 요소 추출
            card = link.find_element(By.XPATH, "./ancestor::li | ./ancestor::div[contains(@class, 'item')] | ./..")
            raw_lines = [t.strip() for t in card.text.split('\n') if t.strip()]
            
            # Pure 숫자(ID, 순위 등) 및 마케팅 텍스트 완전 제거
            clean_lines = []
            for line in raw_lines:
                if line.isdigit():  # '1014', '1' 등 순수 숫자는 무조건 제어
                    continue
                if any(kw in line for kw in ["급상승", "단독", "품절임박", "쿠폰", "명이 보는 중", "도착보장", "판매"]):
                    continue
                clean_lines.append(line)

            # 가격('원' 포함)을 기준으로 구조 분리
            price = next((l for l in clean_lines if '원' in l), None)
            if not price:
                continue

            # 가격이 아닌 나머지 텍스트 추출 (브랜드 / 상품명)
            text_tokens = [l for l in clean_lines if '원' not in l]
            
            if len(text_tokens) >= 2:
                brand = text_tokens[0]
                title = " ".join(text_tokens[1:])
            elif len(text_tokens) == 1:
                brand = "무신사"
                title = text_tokens[0]
            else:
                continue

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
    print(f"수집 완료: 총 {len(df)}개")
    df.to_csv("musinsa_new_ranking_top100.csv", index=False, encoding="utf-8-sig")

finally:
    driver.quit()