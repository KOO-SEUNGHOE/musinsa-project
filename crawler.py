import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
wait = WebDriverWait(driver, 15)

try:
    print("무신사 랭킹 페이지 접속 중...")
    driver.get("https://www.musinsa.com/main/musinsa/ranking?goodsKinds=NEW")
    time.sleep(5)

    # 페이지 전체 로딩 및 렌더링을 위해 스크롤을 여러 번 내립니다.
    driver.execute_script("window.scrollTo(0, 1500);")
    time.sleep(3)

    # 상품 카드 영역을 정확히 지정 (상품 이미지나 링크가 포함된 개별 카드 박스)
    # 무신사 랭킹 리스트의 상품 카드들을 감싸는 태그들을 탐색합니다.
    product_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.sc-1v37d32-0, div[class*='goodsItem'], a[href*='/products/']")))
    
    products = []
    seen_titles = set()
    
    for card in product_cards:
        try:
            # 만약 a 태그를 직접 잡았다면 부모 카드 영역으로 이동
            if card.tag_name == 'a':
                item = card.find_element(By.XPATH, "./..")
            else:
                item = card

            text = item.text.strip()
            if not text:
                continue
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            filtered_lines = []
            for line in lines:
                if line.isdigit() and int(line) <= 100:
                    continue
                if line in ["급상승", "단독", "품절임박"] or "판매" in line or "%" in line:
                    continue
                filtered_lines.append(line)
            
            if len(filtered_lines) >= 2:
                brand = filtered_lines[0]
                price = next((line for line in filtered_lines if '원' in line or ',' in line), "가격 정보 없음")
                title = next((line for line in filtered_lines if line != brand and line != price and len(line) > 1), "상품명 없음")
                
                if title not in seen_titles and title != "상품명 없음" and "원" not in title:
                    seen_titles.add(title)
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