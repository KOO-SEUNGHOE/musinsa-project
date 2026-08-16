import requests
from bs4 import BeautifulSoup
import pandas as pd

# 무신사 랭킹 페이지 (실시간 랭킹)
url = "https://www.musinsa.com/ranking/best"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 상품 정보 리스트 추출
products = []
items = soup.select(".list_item") # 무신사 랭킹 리스트 클래스 선택

for item in items:
    rank = item.select_one(".rank_num")
    brand = item.select_one(".item_title")
    title = item.select_one(".list_info > a")
    price = item.select_one(".price")
    
    if rank and brand and title and price:
        products.append({
            "Rank": rank.text.strip(),
            "Brand": brand.text.strip(),
            "Title": title.text.strip(),
            "Price": price.text.strip().replace(",", "").replace("원", "")
        })

# 데이터프레임으로 변환
df_musinsa = pd.DataFrame(products)
print(df_musinsa.head())

# CSV로 저장 (분석용)
df_musinsa.to_csv("musinsa_ranking.csv", index=False, encoding="utf-8-sig")