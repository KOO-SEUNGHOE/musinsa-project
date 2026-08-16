import pandas as pd

# 1. 수집한 CSV 파일 불러오기
df = pd.read_csv("musinsa_new_ranking_top100.csv")

print(f"정제 전 데이터 총 개수: {len(df)}개")

# 2. 노이즈 데이터 필터링 조건 작성
# - 가격이 '가격 정보 없음'인 행 제거
df_clean = df[df['Price'] != '가격 정보 없음'].copy()

# - Brand 컬럼이 숫자로만 이루어진 경우(랭킹 배너 등) 제거
# 숫자로 변환 가능한지 체크하는 함수
def is_not_number(val):
    return not str(val).isdigit()

df_clean = df_clean[df_clean['Brand'].apply(is_not_number)]

# 3. 랭크(Rank) 번호 재정렬 (1부터 순서대로)
df_clean['Rank'] = range(1, len(df_clean) + 1)
df_clean = df_clean.reset_index(drop=True)

print(f"정제 후 순수 상품 데이터 개수: {len(df_clean)}개")
print(df_clean.head(10))

# 4. 정제된 데이터 새로 저장
df_clean.to_csv("musinsa_new_ranking_cleaned.csv", index=False, encoding="utf-8-sig")