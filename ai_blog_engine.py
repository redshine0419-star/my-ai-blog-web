import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time

# 1. 3개 도메인용 통합 보안 설정 불러오기
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    
    # 1번 방: 건강 포커스 (본부)
    SITE1_URL = st.secrets["SITE1_URL"]
    SITE1_MEDIA = st.secrets["SITE1_MEDIA"]
    SITE1_USER = st.secrets["SITE1_USER"]
    SITE1_PASS = st.secrets["SITE1_PASS"]
    
    # 2번 방: 경제 트렌드
    SITE2_URL = st.secrets["SITE2_URL"] 
    SITE2_MEDIA = st.secrets["SITE2_MEDIA"]
    SITE2_USER = st.secrets["SITE2_USER"]
    SITE2_PASS = st.secrets["SITE2_PASS"]
    
    # 3번 방: 테크 리뷰
    SITE3_URL = st.secrets["SITE3_URL"] 
    SITE3_MEDIA = st.secrets["SITE3_MEDIA"]
    SITE3_USER = st.secrets["SITE3_USER"]
    SITE3_PASS = st.secrets["SITE3_PASS"]
    
except Exception as e:
    st.error(f"⚠️ Streamlit Secrets 설정 누락: {e}")
    st.stop()

# V8 핵심: 도메인별 페르소나 매핑 사전
blogs = {
    "건강 포커스": {
        "url": SITE1_URL,
        "media_url": SITE1_MEDIA,
        "user": SITE1_USER,
        "password": SITE1_PASS,
        "persona": "너는 10년 차 건강/의학 전문 에디터야. 신뢰감 있고 전문적인 톤으로 건강, 웰빙, 인체에 미치는 영향에 초점을 맞춰 작성해줘."
    },
    "경제 트렌드": {
        "url": SITE2_URL,
        "media_url": SITE2_MEDIA,
        "user": SITE2_USER,
        "password": SITE2_PASS,
        "persona": "너는 날카로운 경제 분석가야. 최신 트렌드, 데이터, 시장의 흐름과 수익화 관점에서 명확하게 작성해줘."
    },
    "테크 리뷰": {
        "url": SITE3_URL,
        "media_url": SITE3_MEDIA,
        "user": SITE3_USER,
        "password": SITE3_PASS,
        "persona": "너는 IT/테크 인플루언서야. 관련 기술 동향, 도구 활용법 등을 직관적이고 트렌디하게 작성해줘."
    }
}

# 2. 사이드바 로그인
st.sidebar.title("🔐 관리자 인증")
pwd_input = st.sidebar.text_input("액세스 비번을 입력하세요", type="password")

if pwd_input == ADMIN_PASSWORD:
    st.title("🚀 AutoPress V8 멀티 엔진 가동소")
    st.info("키워드를 입력하면, 3개의 블로그 성격에 맞게 AI가 내용을 각색하여 동시 배달합니다.")
    
    main_keyword = st.text_input("통합 타겟 키워드 (예: 수면 부족)", "2026년 블로그 수익화")

    if st.button("🔥 3개 도메인 동시 전송 시작!", type="primary"):
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        progress_text = "V8 엔진 멀티사이트 배포 진행 중..."
        my_bar = st.progress(0, text=progress_text)
        
        sites = list(blogs.keys())
        
        for i, site_name in enumerate(sites):
            config = blogs[site_name]
            
            with st.spinner(f"🔄 [{i+1}/3] '{site_name}' 페르소나를 적용하여 작성 중..."):
                try:
                    # 1. 이미지 생성 (각 사이트마다 다른 이미지가 배정되도록 seed 적용)
                    image_response = requests.get(f"https://picsum.photos/seed/{main_keyword}_{i}/800/400")
                    media_upload_response = requests.post(
                        config["media_url"],
                        headers={"Content-Disposition": f'attachment; filename="thumb_{i}.jpg"', "Content-Type": "image/jpeg"},
                        data=image_response.content,
                        auth=HTTPBasicAuth(config["user"], config["password"])
                    )
                    img_url = media_upload_response.json()["source_url"] if media_upload_response.status_code == 201 else ""
                    
                    # 2. 맞춤형 본문 작성 (페르소나 융합)
                    article_prompt = f"키워드: [{main_keyword}]\n\n{config['persona']}\n위 키워드에 대해 구글 SEO 최적화된 블로그 포스팅을 작성해. 첫 줄은 무조건 'TITLE: [제목]' 형식으로 쓰고, 그 다음 줄부터 본문을 HTML 태그로 작성해."
                    article_res = model.generate_content(article_prompt)
                    text = article_res.text
                    
                    if "TITLE:" in text:
                        parts = text.split("TITLE:", 1)[1].split("\n", 1)
                        title_final = parts[0].strip()
                        body_text = parts[1].strip() if len(parts) > 1 else ""
                        content_final = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{body_text}'
                    else:
                        title_final = f"[{site_name}] {main_keyword} 가이드"
                        content_final = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{text.strip()}'
                        
                    # 3. 워드프레스 즉시 발행 (각기 다른 사이트이므로 동시 발행 무방)
                    payload = {
                        "title": title_final,
                        "content": content_final,
                        "status": "publish"
                    }
                    res = requests.post(config["url"], auth=HTTPBasicAuth(config["user"], config["password"]), json=payload)
                    
                    if res.status_code == 201:
                        st.write(f"✅ [{i+1}/3] **{site_name}** - 배달 성공! (제목: {title_final})")
                    else:
                        st.error(f"❌ [{i+1}/3] {site_name} 배달 실패: {res.text}")
                        
                except Exception as e:
                    st.error(f"❌ [{i+1}/3] {site_name} 작업 중 오류 발생: {e}")

            my_bar.progress((i + 1) / 3, text=progress_text)
            
            # API 429 에러 방어를 위한 대기 시간 (사이트 간 이동 시 엔진 냉각)
            if i < 2:
                with st.spinner("🚦 구글 AI 서버 냉각 중 (30초 대기)..."):
                    time.sleep(30)
                    
        st.balloons()
        st.success("🎉 V8 멀티 엔진 가동 완료! 3개의 멀티사이트에 각각의 맞춤형 포스팅이 완벽하게 적재되었습니다.")
else:
    st.title("🚀 AutoPress V8 멀티 엔진 가동소")
    st.info("왼쪽 사이드바에서 비밀번호를 입력하면 3개 도메인 통합 공장이 가동됩니다.")
