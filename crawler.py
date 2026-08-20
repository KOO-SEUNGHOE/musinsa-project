import requests
import json
import pandas as pd

# 무신사 내부 랭킹 API 엔드포인트
url = "https://api.musinsa.com/api2/dp/v1/plp/goods/ranking?storeCode=musinsa&sectionId=199&categoryCode=000&page=1&size=100"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.musinsa.com/"
}

try:
    print("무신사 랭킹 API 직접 호출 중...")
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        # API 응답 구조에서 상품 리스트 추출
        goods_list = data.get("data", {}).get("list", [])
        
        products = []
        for idx, item in enumerate(goods_list[:100], 1):
            products.append({
                "Rank": idx,
                "Brand": item.get("brandName", ""),
                "Title": item.get("goodsName", ""),
                "Price": f"{item.get('price', 0):,}원"
            })
            
        df = pd.DataFrame(products)
        print(f"수집 성공! 총 {len(df)}개 상품.")
        df.to_csv("musinsa_new_ranking_top100.csv", index=False, encoding="utf-8-sig")
        print("CSV 파일 저장 완료.")
    else:
        print(f"API 호출 실패 (상태 코드: {response.status_code})")

except Exception as e:
    print(f"에러 발생: {e}")