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

    # 100개 상품이 모두 로드되도록 스크롤을 충분히 내립니다.
    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # 상품 상세로 가는 고유 링크들을 모두 수집
    product_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    
    seen_urls = set()
    unique_cards = []
    
    # 중복 링크를 제거하고 각 상품의 개별 카드 영역을 안전하게 추출
    for link in product_links:
        href = link.get_attribute("href")
        if href and href not in seen_urls:
            seen_urls.add(href)
            try:
                # 합집합 연산자(|)를 쓰지 않고 안전하게 부모 요소를 탐색합니다.
                card = link.find_element(By.XPATH, "./parent::*")
                # 만약 부모가 너무 좁거나 넓으면 한 단계 위를 타겟팅
                try:
                    card = card.find_element(By.XPATH, "./parent::*")
                except:
                    pass
                unique_cards.append(card)
            except:
                continue

    products = []
    seen_titles = set()
    current_rank = 1
    
    for card in unique_cards:
        try:
            text = card.text.strip()
            if not text:
                continue
                
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            # 불필요한 메타 텍스트 필터링
            filtered = []
            for l in lines:
                if l in ["급상승", "단독", "품절임박", "쿠폰"] or "%" in l or "명이 보는 중" in l or "도착보장" in l or "판매" in l:
                    continue
                if l.isdigit() and 1 <= int(l) <= 100:
                    continue
                filtered.append(l)
                
            if len(filtered) >= 2:
                brand = filtered[0]
                price_idx = next((i for i, l in enumerate(filtered) if '원' in l or ',' in l), None)
                
                if price_idx is not None:
                    price = filtered[price_idx]
                    title_candidates = [l for l in filtered[1:price_idx] if l != brand and len(l) > 1]
                    title = title_candidates[0] if title_candidates else filtered[1]
                else:
                    price = "가격 정보 없음"
                    title = filtered[1]
                
                # 유효한 상품명이고 중복되지 않은 경우에만 추가
                if title and title != brand and "원" not in title and title not in seen_titles:
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