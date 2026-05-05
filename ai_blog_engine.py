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
    st.title("🌐 AI 블로그 플랫폼 (Web Version)")
    
    keyword = st.text_input("타겟 키워드", "2026년 블로그 수익화 트렌드")

    if st.button("✨ 고품질 SEO 초안 & 썸네일 생성하기", type="primary"):
        with st.spinner("AI가 작동 중입니다... (약 15~20초 소요)"):
            try:
                # 이미지 업로드 로직
                image_response = requests.get("https://picsum.photos/800/400")
                media_upload_response = requests.post(
                    WP_MEDIA_URL,
                    headers={"Content-Disposition": 'attachment; filename="thumb.jpg"', "Content-Type": "image/jpeg"},
                    data=image_response.content,
                    auth=HTTPBasicAuth(WP_USER, WP_PASSWORD)
                )
                img_url = media_upload_response.json()["source_url"] if media_upload_response.status_code == 201 else ""
                
                # AI 글쓰기 로직
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash') 
                
                prompt = f"[{keyword}]에 대해 구글 SEO 최적화된 블로그 포스팅을 작성해줘. 첫 줄은 무조건 'TITLE: [제목]' 형식으로 쓰고, 그 다음 줄부터 본문을 HTML 태그(<p>, <h2>, <strong> 등)로 작성해."
                response = model.generate_content(prompt)
                
                text = response.text
                
                # 🔥 [핵심 수정] AI가 말을 안 들었을 때를 대비한 안전장치 추가!
                if "TITLE:" in text:
                    parts = text.split("TITLE:", 1)[1].split("\n", 1)
                    st.session_state['t'] = parts[0].strip()
                    body_text = parts[1].strip() if len(parts) > 1 else ""
                    st.session_state['c'] = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{body_text}'
                else:
                    # AI가 TITLE: 이라는 단어를 안 썼어도, 전체 텍스트를 억지로 본문에 집어넣음
                    st.session_state['t'] = f"{keyword} - AI 작성 초안"
                    st.session_state['c'] = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{text.strip()}'
                    
                st.success("🎉 생성 완료! 아래에서 내용을 확인하세요.")
            except Exception as e:
                st.error(f"❌ 오류: {e}")

    # 검수 및 발행 부분
    title_final = st.text_input("최종 제목", st.session_state.get('t', ''))
    content_final = st.text_area("최종 본문 (HTML 확인)", st.session_state.get('c', ''), height=300)
    
    if st.session_state.get('c', ''):
        with st.expander("👀 웹사이트에 어떻게 보일지 미리보기"):
            st.markdown(st.session_state['c'], unsafe_allow_html=True)

    post_status = st.selectbox("발행 상태", ["draft", "publish"])

    if st.button("🚀 워드프레스로 발행"):
        payload = {"title": title_final, "content": content_final, "status": post_status}
        res = requests.post(WP_URL, auth=HTTPBasicAuth(WP_USER, WP_PASSWORD), json=payload)
        if res.status_code == 201:
            st.success(f"🎉 워드프레스 발행 성공! ({post_status})")
            st.balloons()
        else:
            st.error(f"❌ 발행 실패: {res.text}")
else:
    st.title("🌐 AI 블로그 플랫폼")
    st.info("왼쪽 사이드바에서 비밀번호를 입력하면 엔진이 활성화됩니다.")
