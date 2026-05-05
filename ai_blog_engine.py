import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai

# ==========================================
# 1. 보안 설정 (Secrets에서 불러오기)
# 웹 배포 시 이 정보들은 Streamlit 관리자 화면에서 별도로 설정합니다.
# ==========================================
try:
    WP_URL = st.secrets["WP_URL"]
    WP_MEDIA_URL = st.secrets["WP_MEDIA_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_PASSWORD = st.secrets["WP_PASSWORD"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"] # 접속 비밀번호 추가
except:
    st.error("⚠️ Secrets 설정이 필요합니다. 로컬 테스트 중이라면 설정 파일(secrets.toml)을 확인하세요.")
    st.stop()

# ==========================================
# 2. 웹 접속 보안 (간이 로그인)
# ==========================================
st.sidebar.title("🔐 관리자 인증")
pwd_input = st.sidebar.text_input("액세스 비번을 입력하세요", type="password")

if pwd_input != ADMIN_PASSWORD:
    st.warning("비밀번호를 입력해야 엔진이 활성화됩니다.")
    st.stop()

# --- 이 아래부터는 기존 엔진 로직과 동일합니다 ---
st.title("🌐 AI 블로그 플랫폼 (Web Version)")
# (기존 생성 및 발행 로직 생략 - 실제 코드에서는 그대로 유지됨)