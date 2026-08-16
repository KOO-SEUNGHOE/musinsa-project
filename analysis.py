import pandas as pd

# 1. 수집한 CSV 파일 불러오기
df = pd.read_csv("musinsa_recommend_selenium.csv")

print(f"=== 데이터 요약 (총 {len(df)}개 상품) ===")
print(df.info())
print("\n")

# 2. 가격 데이터 정제 (문자열 '원', ',' 제거 후 숫자로 변환)
# 가격 정보가 없는 경우를 대비해 예외 처리 포함
def clean_price(price_str):
    if pd.isna(price_str):
        return 0
    cleaned = str(price_str).replace("원", "").replace(",", "").strip()
    # 숫자만 추출
    digits = "".join([c for c in cleaned if c.isdigit()])
    return int(digits) if digits else 0

df['Price_Num'] = df['Price'].apply(clean_price)

# 3. 주요 분석 지표 출력
print("=== [1] 가격대 통계 ===")
print(f"평균 가격: {df['Price_Num'].mean():,.0f}원")
print(f"최고가 상품: {df.loc[df['Price_Num'].idxmax()]['Title']} ({df['Price_Num'].max():,.0f}원)")
print(f"최저가 상품: {df.loc[df['Price_Num'].idxmin()]['Title']} ({df['Price_Num'].min():,.0f}원)")
print("\n")

print("=== [2] 상위 브랜드 분포 ===")
brand_counts = df['Brand'].value_counts().head(5)
print(brand_counts)