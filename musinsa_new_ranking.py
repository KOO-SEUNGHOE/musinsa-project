from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    # 1. 무신사 메인 홈페이지 접속 (세션 확보)
    print("1. 무신사 메인 홈페이지 접속 중...")
    driver.get("https://www.musinsa.com/")
    time.sleep(3)

    # 2. 랭킹 페이지로 이동 (오버레이 막힘을 방지하기 위해 자바스크립트 클릭 사용)
    print("2. 랭킹 페이지로 이동 중...")
    ranking_menu = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '랭킹') or contains(@href, 'ranking')]"))
    )
    # 일반 .click() 대신 자바스크립트로 강제 클릭 실행
    driver.execute_script("arguments[0].click();", ranking_menu)
    time.sleep(3)

    # 3. 랭킹 페이지 내에서 'NEW' 탭 선택
    print("3. 'NEW' 랭킹 탭을 선택하는 중...")
    try:
        new_tab = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'NEW')] | //a[contains(text(), 'NEW')]"))
        )
        driver.execute_script("arguments[0].click();", new_tab)
        time.sleep(3)
    except Exception:
        print("탭 선택 우회 경로로 진입합니다.")
        driver.get("https://www.musinsa.com/main/musinsa/ranking")
        time.sleep(3)

    # 스크롤을 내려서 상품이 안전하게 로딩되도록 유도
    driver.execute_script("window.scrollTo(0, 2000);")
    time.sleep(3)

    # 4. TOP 100 상품 데이터 추출
    print("4. TOP 100 상품 데이터를 수집하고 있습니다...")
    product_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/products/']")))
    items = [link.find_element(By.XPATH, "./..") for link in product_links]
    
    products = []
    seen_titles = set()
    
    for item in items:
        try:
            text = item.text.strip()
            if not text:
                continue
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) >= 2:
                brand = lines[0]
                price = next((line for line in lines if '원' in line or ',' in line), "가격 정보 없음")
                title = next((line for line in lines if line != brand and line != price and len(line) > 2), "상품명 없음")
                
                if title not in seen_titles and title != "상품명 없음":
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
    print(f"\n수집 성공! 총 {len(df)}개의 NEW 랭킹 상품을 가져왔습니다.")
    print(df.head(10))
    
    if len(df) > 0:
        df.to_csv("musinsa_new_ranking_top100.csv", index=False, encoding="utf-8-sig")
        print("데이터가 'musinsa_new_ranking_top100.csv' 파일로 저장되었습니다.")
    else:
        print("수집된 데이터가 없습니다.")

finally:
    driver.quit()