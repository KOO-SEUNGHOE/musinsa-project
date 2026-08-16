from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

options = Options()
# 봇 탐지 우회 설정 유지
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

print("무신사 페이지에 접속 중입니다...")
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.musinsa.com/main/musinsa/recommend?gf=A")
    
    # 페이지 동적 로딩을 위해 충분히 대기 및 스크롤
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 1500);")
    time.sleep(3)

    wait = WebDriverWait(driver, 10)
    
    # 1차 시도: 상품 링크(/products/)를 포함하는 부모 카드 요소들을 탐색
    print("상품 데이터를 수집하고 있습니다...")
    try:
        # 상품 상세 페이지로 가는 링크가 포함된 카드 영역 수집
        product_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
        items = [link.find_element(By.XPATH, "./..") for link in product_links] # 부모 요소 추출
    except Exception:
        # 실패 시 일반적인 블록 요소 탐색
        items = driver.find_elements(By.CSS_SELECTOR, "div[class*='item'], div[class*='goods']")

    products = []
    for item in items:
        try:
            text = item.text.strip()
            if not text:
                continue
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # 텍스트 라인에서 브랜드, 상품명, 가격 추출
            if len(lines) >= 2:
                brand = lines[0]
                # 가격 형태를 가진 문자열 탐색
                price = next((line for line in lines if '원' in line or ',' in line), "가격 정보 없음")
                # 가격이 아닌 첫 번째 긴 텍스트를 상품명으로 지정
                title = next((line for line in lines if line != brand and line != price and len(line) > 2), "상품명 없음")
                
                if brand and title:
                    products.append({
                        "Brand": brand,
                        "Title": title,
                        "Price": price
                    })
        except Exception:
            continue

    df = pd.DataFrame(products)
    # 중복 제거 및 빈 값 정제
    df = df.drop_duplicates(subset=['Title']).reset_index(drop=True)
    
    print(f"\n수집 성공! 총 {len(df)}개의 유효 상품 데이터를 가져왔습니다.")
    print(df.head(10))
    
    if len(df) > 0:
        df.to_csv("musinsa_recommend_selenium.csv", index=False, encoding="utf-8-sig")
        print("데이터가 'musinsa_recommend_selenium.csv' 파일로 저장되었습니다.")
    else:
        print("수집된 데이터가 없습니다. 페이지 구조를 다시 확인해야 합니다.")

finally:
    driver.quit()