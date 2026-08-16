import streamlit as st
import pandas as pd
from collections import Counter
import re
import matplotlib.pyplot as plt

# 윈도우 환경 한글 폰트 깨짐 방지
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(page_title="무신사 NEW 랭킹 트렌드 대시보드", page_icon="🛍️", layout="wide")

st.title("🛍️ 무신사 NEW 랭킹 트렌드 분석 대시보드")
st.markdown("크롤링한 실시간 무신사 NEW 랭킹 데이터를 바탕으로 가격 통계와 트렌드 키워드를 한눈에 확인할 수 있는 대시보드입니다.")

# 1. 데이터 불러오기 및 전처리 함수
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("musinsa_new_ranking_top100.csv")
    except FileNotFoundError:
        return None
    
    # 노이즈 및 결측치 전처리
    df = df[df['Price'] != '가격 정보 없음'].copy()
    df = df[~df['Brand'].astype(str).str.isdigit()].copy()
    
    # 가격 정수형 변환
    def clean_price(price_str):
        if pd.isna(price_str):
            return 0
        cleaned = str(price_str).replace("원", "").replace(",", "").strip()
        digits = "".join([c for c in cleaned if c.isdigit()])
        return int(digits) if digits else 0

    df['Price_Num'] = df['Price'].apply(clean_price)
    
    # Rank를 깔끔하게 1부터 순차적으로 재부여
    df['Rank'] = range(1, len(df) + 1)
    df = df.reset_index(drop=True)
    
    return df

df = load_data()

if df is None or df.empty:
    st.error("데이터 파일('musinsa_new_ranking_top100.csv')을 찾을 수 없거나 데이터가 비어 있습니다.")
else:
    # 사이드바 설정 (필터 기능)
    st.sidebar.header("🔍 검색 및 필터")
    selected_brand = st.sidebar.selectbox("브랜드 선택", ["전체"] + sorted(df['Brand'].unique().tolist()))
    
    filtered_df = df if selected_brand == "전체" else df[df['Brand'] == selected_brand]

    # 상단 핵심 지표 (Metric) 카드 출력
    col1, col2, col3 = st.columns(3)
    col1.metric("분석된 총 상품 수", f"{len(filtered_df)}개")
    col2.metric("평균 판매 가격", f"{filtered_df['Price_Num'].mean():,.0f}원")
    col3.metric("최고가 상품 가격", f"{filtered_df['Price_Num'].max():,.0f}원")

    st.markdown("---")

    # 레이아웃 분할 (좌: 키워드 분석 / 우: 브랜드 분포)
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("🔥 상위 트렌드 키워드")
        all_titles = " ".join(filtered_df['Title'].dropna().tolist())
        cleaned_text = re.sub(r'[^가-힣a-zA-Z\s]', ' ', all_titles)
        words = [w for w in cleaned_text.split() if len(w) > 1]
        word_counts = Counter(words)
        top_keywords = pd.DataFrame(word_counts.most_common(10), columns=['Keyword', 'Count'])
        
        # Matplotlib을 이용한 깔끔한 한글 지원 바 차트
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(top_keywords['Keyword'], top_keywords['Count'], color='#ff5722')
        ax.set_title("키워드별 빈도수", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with right_col:
        st.subheader("🏢 상위 등장 브랜드 분포")
        brand_top = filtered_df['Brand'].value_counts().head(10).reset_index()
        brand_top.columns = ['Brand', 'Count']
        
        # Matplotlib을 이용한 브랜드 바 차트
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.bar(brand_top['Brand'], brand_top['Count'], color='#2196f3')
        ax2.set_title("브랜드별 상품 수", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    st.markdown("---")
    
    # 하단 원본 데이터 테이블 출력
    st.subheader("📋 수집된 상품 상세 데이터")
    st.dataframe(filtered_df[['Rank', 'Brand', 'Title', 'Price']], use_container_width=True)