import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time
from datetime import datetime, timedelta

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

# 비밀번호 검증 성공 시
if pwd_input == ADMIN_PASSWORD:
    st.title("🚀 AI 블로그 대량 자동화 플랫폼 (V7)")
    st.info("메인 키워드를 입력하면, AI가 연관 키워드 3개를 뽑아 2시간 간격으로 예약 발행합니다.")
    
    main_keyword = st.text_input("메인 타겟 키워드 (예: 직장인 부업)", "2026년 블로그 수익화")

    if st.button("🔥 3개 연속 생성 및 예약 발행 시작!", type="primary"):
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        # [단계 1] 꼬리 키워드 3개 자동 추출
        with st.spinner("🧠 AI가 트래픽이 터질 꼬리 키워드 3개를 분석 중입니다..."):
            try:
                kw_prompt = f"[{main_keyword}]와 관련된 구글 검색량은 많고 경쟁은 적은 세부(꼬리) 키워드 딱 3개만 콤마(,)로 구분해서 텍스트로만 출력해. (예: 직장인 블로그 수익, 티스토리 애드센스 승인, 워드프레스 초기 비용)"
                kw_response = model.generate_content(kw_prompt)
                
                # 콤마로 분리하고 앞뒤 공백 제거 후 3개만 리스트에 담기
                keywords = [k.strip() for k in kw_response.text.split(",") if k.strip()][:3]
                
                if len(keywords) < 3:
                    keywords = [f"{main_keyword} 기초", f"{main_keyword} 심화", f"{main_keyword} 실전"] # 오류 방지용 기본값
                    
                st.success(f"🎯 추출된 타겟 키워드: {', '.join(keywords)}")
                time.sleep(15) # 키워드를 뽑고 나서 다음 글쓰기로 넘어가기 전 15초 대기
            except Exception as e:
                st.error(f"키워드 추출 실패: {e}")
                st.stop()

        # [단계 2] 3개 포스팅 루프 생성 및 예약 발행
        progress_text = "자동 생성 및 워드프레스 배달 진행 중..."
        my_bar = st.progress(0, text=progress_text)
        
        for i, target_kw in enumerate(keywords):
            with st.spinner(f"🔄 [{i+1}/3] '{target_kw}' 주제로 글을 쓰고 이미지를 업로드 중입니다..."):
                try:
                    # 1. 이미지 생성 및 업로드
                    image_response = requests.get("https://picsum.photos/800/400")
                    media_upload_response = requests.post(
                        WP_MEDIA_URL,
                        headers={"Content-Disposition": f'attachment; filename="thumb_{i}.jpg"', "Content-Type": "image/jpeg"},
                        data=image_response.content,
                        auth=HTTPBasicAuth(WP_USER, WP_PASSWORD)
                    )
                    img_url = media_upload_response.json()["source_url"] if media_upload_response.status_code == 201 else ""
                    
                    # 2. 본문 작성
                    article_prompt = f"[{target_kw}]에 대해 구글 SEO 최적화된 블로그 포스팅을 작성해줘. 첫 줄은 무조건 'TITLE: [제목]' 형식으로 쓰고, 그 다음 줄부터 본문을 HTML 태그로 작성해."
                    article_res = model.generate_content(article_prompt)
                    text = article_res.text
                    
                    if "TITLE:" in text:
                        parts = text.split("TITLE:", 1)[1].split("\n", 1)
                        title_final = parts[0].strip()
                        body_text = parts[1].strip() if len(parts) > 1 else ""
                        content_final = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{body_text}'
                    else:
                        title_final = f"{target_kw} 완벽 가이드"
                        content_final = f'<img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n\n{text.strip()}'
                        
                    # 3. 예약 시간 계산 (국제 표준시 GMT 기준)
                    # 첫 번째 글(i=0)은 즉시(0시간), 두 번째 글(i=1)은 2시간 뒤, 세 번째 글(i=2)은 4시간 뒤
                    pub_time_gmt = datetime.utcnow() + timedelta(hours=2*i)
                    iso_time_gmt = pub_time_gmt.strftime("%Y-%m-%dT%H:%M:%S")
                    
                    # 워드프레스 정책: 미래 시간이면 status를 'future'로 해야 함. 첫 글은 'publish'.
                    post_status = "publish" if i == 0 else "future"
                    
                    # 4. 워드프레스 발행
                    payload = {
                        "title": title_final,
                        "content": content_final,
                        "status": post_status,
                        "date_gmt": iso_time_gmt
                    }
                    res = requests.post(WP_URL, auth=HTTPBasicAuth(WP_USER, WP_PASSWORD), json=payload)
                    
                    if res.status_code == 201:
                        st.write(f"✅ [{i+1}/3] **{title_final}** - 배달 성공! (상태: {post_status})")
                    else:
                        st.error(f"❌ [{i+1}/3] 배달 실패: {res.text}")
                        
                except Exception as e:
                    st.error(f"❌ [{i+1}/3] 작업 중 오류 발생: {e}")

            # 프로그레스 바 업데이트
            my_bar.progress((i + 1) / 3, text=progress_text)
            
            # 429 에러 방지를 위한 핵심 로직 (마지막 글을 쓰고 나서는 쉴 필요 없음)
            if i < 2:
            with st.spinner("🚦 구글 AI 서버 무료 제한 방어 중 (45초 대기)..."):
            time.sleep(45)
                    
        st.balloons()
        st.success("🎉 대량 생성 및 예약 발행이 완벽하게 끝났습니다! 워드프레스 관리자 창에서 [예약됨] 상태를 확인해 보세요.")
else:
    st.title("🚀 AI 블로그 대량 자동화 플랫폼")
    st.info("왼쪽 사이드바에서 비밀번호를 입력하면 공장이 가동됩니다.")
