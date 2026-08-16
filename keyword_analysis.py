import pandas as pd
from collections import Counter
import re

# 1. 데이터 불러오기 (이미 저장된 크롤링 파일 활용)
try:
    df = pd.read_csv("musinsa_new_ranking_top100.csv")
except FileNotFoundError:
    print("오류: 'musinsa_new_ranking_top100.csv' 파일이 없습니다. 크롤링을 먼저 진행해주세요.")
    exit()

# 노이즈 데이터 전처리
df = df[df['Price'] != '가격 정보 없음'].copy()
df = df[~df['Brand'].astype(str).str.isdigit()]

# 2. 텍스트 정제 및 단어 추출 (상품명 분석)
all_titles = " ".join(df['Title'].dropna().tolist())

# 특수문자 및 기호 제거 (한글, 영문, 공백만 남기기)
cleaned_text = re.sub(r'[^가-힣a-zA-Z\s]', ' ', all_titles)

# 단어 단위로 쪼개기
words = cleaned_text.split()

# 의미없는 짧은 단어나 조사 등 제외 (2글자 이상만 추출)
filtered_words = [word for word in words if len(word) > 1]

# 3. 가장 많이 등장한 상위 키워드 추출
word_counts = Counter(filtered_words)
top_keywords = word_counts.most_common(10)

print("========================================")
print("     [ 무신사 NEW 상품명 트렌드 키워드 TOP 10 ]")
print("========================================")
for word, count in top_keywords:
    print(f"• {word}: {count}회")