import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai

# 1. 보안 설정 불러오기
try:
    WP_URL = st.secrets["WP_URL"]
    WP_MEDIA_URL = st.secrets["WP_MEDIA_URL"]
    WP_USER = st.secrets["WP_USER"]
    WP_PASSWORD = st.secrets["WP_PASSWORD"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Streamlit Settings > Secrets 설정을 먼저 완료해주세요.")
    st.stop()

# 2. 사이드바 로그인
st.sidebar.title("🔐 관리자 인증")
pwd_input = st.sidebar.text_input("액세스 비번을 입력하세요", type="password")

# 비밀번호 검증
if pwd_input == ADMIN_PASSWORD:
    # --- 인증 성공 시 보여줄 메인 화면 ---
    st.title("🌐 AI 블로그 플랫폼 (Web Version)")
    
    keyword = st.text_input("타겟 키워드", "2026년 블로그 수익화 트렌드")

    if st.button("✨ 고품질 SEO 초안 & 썸네일 생성하기", type="primary"):
        with st.spinner("AI가 작동 중입니다..."):
            try:
                # 이미지 및 글 생성 로직 (V4와 동일)
                image_response = requests.get("https://picsum.photos/800/400")
                media_upload_response = requests.post(
                    WP_MEDIA_URL,
                    headers={"Content-Disposition": 'attachment; filename="thumb.jpg"', "Content-Type": "image/jpeg"},
                    data=image_response.content,
                    auth=HTTPBasicAuth(WP_USER, WP_PASSWORD)
                )
                img_url = media_upload_response.json()["source_url"] if media_upload_response.status_code == 201 else ""
                
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(f"{keyword}에 대해 SEO 최적화 블로그 포스팅을 HTML로 써줘. TITLE: 포함.")
                
                text = response.text
                if "TITLE:" in text:
                    parts = text.split("TITLE:", 1)[1].split("\n", 1)
                    st.session_state['t'] = parts[0].strip()
                    st.session_state['c'] = f'<img src="{img_url}" style="width:100%;">\n\n' + parts[1].strip()
                st.success("생성 완료!")
            except Exception as e:
                st.error(f"오류: {e}")

    # 검수 및 발행 부분
    title_final = st.text_input("최종 제목", st.session_state.get('t', ''))
    content_final = st.text_area("최종 본문", st.session_state.get('c', ''), height=300)

    if st.button("🚀 워드프레스로 발행"):
        res = requests.post(WP_URL, auth=HTTPBasicAuth(WP_USER, WP_PASSWORD), json={"title": title_final, "content": content_final, "status": "publish"})
        if res.status_code == 201:
            st.success("발행 성공!")
            st.balloons()
else:
    # 인증 실패 시
    st.title("🌐 AI 블로그 플랫폼 (Web Version)")
    st.info("왼쪽 사이드바에서 비밀번호를 입력하면 엔진이 활성화됩니다.")
