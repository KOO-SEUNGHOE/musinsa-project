import pandas as pd

# 1. 저장해 둔 CSV 파일 직접 불러오기
try:
    df = pd.read_csv("musinsa_new_ranking_top100.csv")
except FileNotFoundError:
    print("오류: 'musinsa_new_ranking_top100.csv' 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
    exit()

# 2. 노이즈 데이터 자동 전처리 (가격 정보가 없거나 브랜드가 숫자인 행 제거)
df = df[df['Price'] != '가격 정보 없음'].copy()
df = df[~df['Brand'].astype(str).str.isdigit()]

# 3. 가격 데이터 정수형(int)으로 변환
def clean_price(price_str):
    if pd.isna(price_str):
        return 0
    cleaned = str(price_str).replace("원", "").replace(",", "").strip()
    digits = "".join([c for c in cleaned if c.isdigit()])
    return int(digits) if digits else 0

df['Price_Num'] = df['Price'].apply(clean_price)

# 4. 주요 인사이트 통계 출력
print("========================================")
print("       [ 무신사 NEW 랭킹 데이터 분석 ]      ")
print("========================================")
print(f"• 총 분석 상품 수: {len(df)}개")
print(f"• 전체 평균 가격: {df['Price_Num'].mean():,.0f}원")
print(f"• 가장 비싼 상품: {df.loc[df['Price_Num'].idxmax()]['Title']} ({df['Price_Num'].max():,.0f}원)")
print(f"• 가장 저렴한 상품: {df.loc[df['Price_Num'].idxmin()]['Title']} ({df['Price_Num'].min():,.0f}원)")
print("\n[상위 등장 브랜드 TOP 5]")
print(df['Brand'].value_counts().head(5))