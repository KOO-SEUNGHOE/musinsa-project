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
    print("무신사 전체 랭킹 페이지 접속 중...")
    # 사용자가 보여주신 정확한 전체 랭킹 메인 URL
    driver.get("https://www.musinsa.com/main/musinsa/ranking?goodsKinds=NEW")
    time.sleep(5)

    # 100개 상품이 모두 렌더링되도록 스크롤을 충분히 내립니다.
    for _ in range(6):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # 상품 링크를 기준으로 각 카드 요소를 모두 수집
    product_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/products/']")))
    
    products = []
    seen_titles = set()
    current_rank = 1
    
    for link in product_links:
        try:
            card = link.find_element(By.XPATH, "./..")
            text = card.text.strip()
            if not text:
                continue
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # 뱃지 및 불필요한 메타 텍스트 제거
            valid_lines = []
            for l in lines:
                if l in ["급상승", "단독", "품절임박"] or "판매" in l or "%" in l:
                    continue
                # 카드 내부에 포함된 순위 숫자(1~100)는 건너뜁니다.
                if l.isdigit() and 1 <= int(l) <= 100:
                    continue
                valid_lines.append(l)
            
            if len(valid_lines) >= 2:
                brand = valid_lines[0]
                price = next((l for l in valid_lines if '원' in l or ',' in l), "가격 정보 없음")
                
                title_candidates = [l for l in valid_lines if l != brand and l != price and len(l) > 1]
                title = title_candidates[0] if title_candidates else "상품명 없음"
                
                if title not in seen_titles and title != "상품명 없음" and "원" not in title:
                    seen_titles.add(title)
                    products.append({
                        "Rank": current_rank,
                        "Brand": brand,
                        "Title": title,
                        "Price": price
                    })
                    current_rank += 1
            
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