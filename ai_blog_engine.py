import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time
import urllib.parse

# 1. 3개 도메인용 통합 보안 설정 불러오기
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    
    # 1번 방: 건강 포커스
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

# V8.1 핵심: 역할극 배제, 도메인별 핵심 객관적 목표 설정
blogs = {
    "건강 포커스": {
        "url": SITE1_URL, "media_url": SITE1_MEDIA, "user": SITE1_USER, "password": SITE1_PASS,
        "objective": "건강 및 웰빙 분야. 2026년 최신 의학 정보 및 데이터를 기반으로 객관적이고 검증된 사실만 작성할 것."
    },
    "경제 트렌드": {
        "url": SITE2_URL, "media_url": SITE2_MEDIA, "user": SITE2_USER, "password": SITE2_PASS,
        "objective": "경제 및 비즈니스 분야. 2026년 최신 시장 동향, 실물 지표, 수익화 데이터를 중심으로 명확하게 분석할 것."
    },
    "테크 리뷰": {
        "url": SITE3_URL, "media_url": SITE3_MEDIA, "user": SITE3_USER, "password": SITE3_PASS,
        "objective": "IT 및 테크놀로지 분야. 2026년 최신 기술 트렌드, AI 발전, 기기 스펙 등을 팩트 위주로 직관적으로 전달할 것."
    }
}

# 2. 사이드바 로그인
st.sidebar.title("🔐 관리자 인증")
pwd_input = st.sidebar.text_input("액세스 비번을 입력하세요", type="password")

if pwd_input == ADMIN_PASSWORD:
    st.title("🚀 AutoPress V8.1 멀티 엔진 가동소")
    st.info("키워드를 입력하면, 3개의 블로그 성격에 맞게 AI가 최신 팩트 기반으로 각색하여 동시 배달합니다.")
    
    main_keyword = st.text_input("통합 타겟 키워드 (예: 수면 부족)", "2026년 블로그 수익화")

    if st.button("🔥 3개 도메인 동시 전송 시작!", type="primary"):
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        progress_text = "V8.1 최신 정보 기반 배포 진행 중..."
        my_bar = st.progress(0, text=progress_text)
        sites = list(blogs.keys())
        
        for i, site_name in enumerate(sites):
            config = blogs[site_name]
            
            with st.spinner(f"🔄 [{i+1}/3] '{site_name}' 맞춤형 AI 썸네일 및 최신 본문 생성 중..."):
                try:
                    # 1. 썸네일 생성 로직 개편: 키워드 맞춤형 AI 이미지 무료 API 적용
                    image_prompt = f"high quality blog thumbnail, {main_keyword}, {site_name} concept, realistic, no text"
                    encoded_prompt = urllib.parse.quote(image_prompt)
                    image_api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=400&nologo=true"
                    
                    image_response = requests.get(image_api_url)
                    media_upload_response = requests.post(
                        config["media_url"],
                        headers={"Content-Disposition": f'attachment; filename="thumb_{i}.jpg"', "Content-Type": "image/jpeg"},
                        data=image_response.content,
                        auth=HTTPBasicAuth(config["user"], config["password"])
                    )
                    img_url = media_upload_response.json()["source_url"] if media_upload_response.status_code == 201 else ""
                    
                    # 2. 맞춤형 본문 작성 (2026년 팩트 및 GEO 구조화 최적화)
                    article_prompt = f"""키워드: [{main_keyword}]
도메인 방향성: {config['objective']}

위 키워드에 대해 구글 SEO 및 AI 검색 엔진(GEO)이 즉시 인용할 수 있도록 최적화된 블로그 포스팅을 작성해.
다음 지침을 엄격히 준수할 것:
1. 허구의 페르소나나 불필요한 인사말은 절대 포함하지 마.
2. 모든 정보는 2026년 현재 기준의 최신 트렌드와 팩트에 기반하여 작성해.
3. 서론 최상단에는 AI 모델들이 쉽게 요약본으로 긁어갈 수 있도록 2~3문장의 핵심 요약(TL;DR)을 배치해.
4. 모바일 가독성을 위해 H2, H3 태그를 나누고, 불릿 포인트(<ul>, <li>)와 굵은 글씨(<strong>)를 적극적으로 활용해.
5. 첫 줄은 무조건 'TITLE: [제목]' 형식으로 작성하고, 그다음 줄부터 HTML 본문을 작성해.
"""
                    article_res = model.generate_content(article_prompt)
                    text = article_res.text
                    
                    if "TITLE:" in text:
                        parts = text.split("TITLE:", 1)[1].split("\n", 1)
                        title_final = parts[0].strip()
                        body_text = parts[1].strip() if len(parts) > 1 else ""
                        content_final = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{body_text}'
                    else:
                        title_final = f"[{site_name}] {main_keyword} 최신 정보"
                        content_final = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{text.strip()}'
                        
                    # 3. 워드프레스 즉시 발행
                    payload = {"title": title_final, "content": content_final, "status": "publish"}
                    res = requests.post(config["url"], auth=HTTPBasicAuth(config["user"], config["password"]), json=payload)
                    
                    if res.status_code == 201:
                        st.write(f"✅ [{i+1}/3] **{site_name}** - 성공! (제목: {title_final})")
                    else:
                        st.error(f"❌ [{i+1}/3] {site_name} 실패: {res.text}")
                        
                except Exception as e:
                    st.error(f"❌ [{i+1}/3] {site_name} 에러: {e}")

            my_bar.progress((i + 1) / 3, text=progress_text)
            
            # API 호출 에러 방지를 위한 쿨다운 (30초)
            if i < 2:
                time.sleep(30)
                    
        st.balloons()
        st.success("🎉 V8.1 업데이트 완료! 맞춤형 썸네일과 GEO 최적화된 팩트 기반 포스팅이 배달되었습니다.")
else:
    st.title("🚀 AutoPress V8.1 멀티 엔진 가동소")
    st.info("왼쪽 사이드바에서 비밀번호를 입력하면 3개 도메인 통합 공장이 가동됩니다.")
