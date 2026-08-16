import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
# ★ 핵심: 화면 없는 서버 환경에서 돌리기 위한 필수 옵션들
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    print("무신사 NEW 랭킹 페이지 접속 중 (Headless 모드)...")
    driver.get("https://www.musinsa.com/")
    time.sleep(3)

    # 랭킹 메뉴 강제 이동
    ranking_menu = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '랭킹') or contains(@href, 'ranking')]")))
    driver.execute_script("arguments[0].click();", ranking_menu)
    time.sleep(3)

    try:
        new_tab = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'NEW')] | //a[contains(text(), 'NEW')]")))
        driver.execute_script("arguments[0].click();", new_tab)
        time.sleep(3)
    except Exception:
        driver.get("https://www.musinsa.com/main/musinsa/ranking")
        time.sleep(3)

    driver.execute_script("window.scrollTo(0, 2000);")
    time.sleep(3)

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
    print(f"수집 성공! 총 {len(df)}개 상품.")
    
    if len(df) > 0:
        df.to_csv("musinsa_new_ranking_top100.csv", index=False, encoding="utf-8-sig")
        print("CSV 파일 저장 완료.")

finally:
    driver.quit()