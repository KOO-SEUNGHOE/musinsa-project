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
    print("무신사 전체 실시간 랭킹 페이지 접속 중...")
    driver.get("https://www.musinsa.com/main/musinsa/ranking?gf=A&storeCode=musinsa&sectionId=199&contentsId=&categoryCode=000&ageBand=AGE_BAND_ALL&subPan=product")
    time.sleep(5)

    # 100위까지 상품이 DOM에 완전히 로드되도록 스크롤을 여유 있게 반복 실행
    for _ in range(8):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)

    # 상품 카드를 담고 있는 가장 핵심적인 컨테이너들을 탐색
    # 무신사 랭킹 리스트의 개별 아이템 요소를 직접 타겟팅합니다.
    items = driver.find_elements(By.CSS_SELECTOR, "div.sc-1v37d32-0, li.li_box, div.piece-common, article")
    
    # 만약 위 셀렉터로 안 잡히면 상품 이미지나 링크를 품고 있는 부모 li/div를 정밀 타겟팅
    if len(items) < 10:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
        items = [link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'goods')] | ./ancestor::li") for link in links]

    products = []
    seen_titles = set()
    
    for idx, item in enumerate(items, 1):
        try:
            text = item.text.strip()
            if not text:
                continue
                
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            # 불필요한 태그/텍스트 필터링
            filtered = []
            for l in lines:
                if l in ["급상승", "단독", "품절임박", "쿠폰"] or "%" in l or "명이 보는 중" in l or "도착보장" in l:
                    continue
                if l.isdigit() and 1 <= int(l) <= 100:  # 순위 숫자 자체는 제외
                    continue
                filtered.append(l)
                
            if len(filtered) >= 3:
                brand = filtered[0]
                # 가격 정보(원 혹은 콤마가 포함된 문자열) 찾기
                price_idx = next((i for i, l in enumerate(filtered) if '원' in l or ',' in l), None)
                
                if price_idx is not None:
                    price = filtered[price_idx]
                    # 브랜드와 가격 사이의 텍스트들을 조합하여 상품명 완성
                    title_candidates = filtered[1:price_idx]
                    title = " ".join(title_candidates) if title_candidates else filtered[1]
                else:
                    price = "가격 정보 없음"
                    title = filtered[1]
                
                if title and title not in seen_titles and "원" not in title:
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