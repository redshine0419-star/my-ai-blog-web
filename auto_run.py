import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time, urllib.parse, os, feedparser

def get_env_secrets():
    """3개 도메인의 환경변수 및 디자인/수익화 속성 정의"""
    return {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "SITES": [
            {
                "name": "건강 포커스",
                "url": os.environ.get("SITE1_URL"),
                "media": os.environ.get("SITE1_MEDIA"),
                "user": os.environ.get("SITE1_USER"),
                "pass": os.environ.get("SITE1_PASS"),
                "color": "#00A86B",
                "objective": "2026년 최신 의학 정보 및 데이터 기반 팩트 중심 건강 포스팅.",
                "cta_text": "🔥 가장 인기 있는 건강 리포트 보기"
            },
            {
                "name": "경제 트렌드",
                "url": os.environ.get("SITE2_URL"),
                "media": os.environ.get("SITE2_MEDIA"),
                "user": os.environ.get("SITE2_USER"),
                "pass": os.environ.get("SITE2_PASS"),
                "color": "#1A237E",
                "objective": "2026년 글로벌 시장 지표 및 수익화 전략 분석 포스팅.",
                "cta_text": "📈 실시간 경제 지표 분석 더보기"
            },
            {
                "name": "넥스트 테크 웨이브",
                "url": os.environ.get("SITE3_URL"),
                "media": os.environ.get("SITE3_MEDIA"),
                "user": os.environ.get("SITE3_USER"),
                "pass": os.environ.get("SITE3_PASS"),
                "color": "#6200EE",
                "objective": "2026년 최신 AI 및 신기술 트렌드 테크 분석 포스팅.",
                "cta_text": "🚀 신기술 핵심 인사이트 확인하기"
            }
        ]
    }

def get_realtime_commercial_keyword(api_key):
    """실시간 구글 뉴스에서 '구매, 비용, 비교, 트렌드' 등 상업적(고단가) 키워드 1개 추출"""
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_titles = [entry.title for entry in feed.entries[:15]]
    combined_titles = " | ".join(news_titles)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""다음 2026년 실시간 주요 뉴스 리스트 중에서, 블로그 방문자가 '비용 비교', '구매 결정', '투자 전략' 등 상업적인 액션을 취할 확률이 가장 높은(광고 단가가 높은) 핵심 주제 1개만 선정해. 
    단순 정보가 아니라 '솔루션 제안'이나 '수익 창출'과 직결되는 단어여야 해. 딱 한 단어(혹은 짧은 명사형)로만 출력해.
    뉴스 리스트: {combined_titles}"""
    
    response = model.generate_content(prompt)
    return response.text.strip()

def run_auto_post_v10():
    secrets = get_env_secrets()
    if not secrets["GEMINI_API_KEY"]:
        print("❌ API 키 오류: 환경 변수를 확인하세요.")
        return

    main_keyword = get_realtime_commercial_keyword(secrets["GEMINI_API_KEY"])
    print(f"💰 [V10 가동] 타겟팅된 고단가 키워드: {main_keyword}")
    
    model = genai.GenerativeModel('gemini-2.5-flash')

    for site in secrets["SITES"]:
        try:
            # 1. 썸네일 AI 자동 생성 (고품질 프롬프트)
            img_prompt = urllib.parse.quote(f"high end professional editorial blog thumbnail, {main_keyword}, {site['name']} theme, vector art")
            img_url = f"https://image.pollinations.ai/prompt/{img_prompt}?width=800&height=450&nologo=true"
            img_data = requests.get(img_url).content
            
            media_res = requests.post(
                site["media"],
                headers={"Content-Disposition": 'attachment; filename="cover.jpg"', "Content-Type": "image/jpeg"},
                data=img_data,
                auth=HTTPBasicAuth(site["user"], site["pass"])
            )
            final_img_url = media_res.json().get("source_url", "")

            # 2. PV 극대화 및 광고 배치 최적화 프롬프트
            article_prompt = f"""키워드 [{main_keyword}]에 대해 {site['objective']}를 작성해. 아래 구조를 100% 지켜:
            - TITLE: [제목] (클릭을 유발하는 상업적/구체적 수치가 들어간 제목)
            - 서론: 인사말 없이 바로 본론 시작.
            - 핵심 요약: <blockquote> 태그를 사용해 3줄 요약(TL;DR) 작성 (GEO 최적화).
            - (이 주석을 HTML에 그대로 넣어줘)
            - 본문 중간: 2026년 데이터나 비용 비교를 담은 <table>을 반드시 1개 이상 포함.
            - 소제목: H2, H3 태그를 3개 이상 사용하여 시각적 피로도 최소화.
            - 마무리: <div style="background:#f8f9fa; padding:15px; border-left:5px solid {site['color']};"> 태그로 감싼 [전문가 인사이트] 박스 작성.
            """
            
            res = model.generate_content(article_prompt).text
            title = res.split("TITLE:")[1].split("\n")[0].strip() if "TITLE:" in res else f"[{main_keyword}] 2026 완벽 분석 리포트"
            
            # 3. 무인 수익화 장치 조립 (체류 시간 증대 및 내부 순환 링크)
            site_home = site["url"].split("/wp-json")[0]
            
            # 중간 내부 링크 유도 (PV 상승)
            internal_link = f'''
            <div style="border: 1px dashed {site['color']}; border-radius: 8px; padding: 20px; margin: 30px 0; background-color: #fafafa;">
                <h3 style="margin-top: 0; color: {site['color']}; fontSize: 18px;">💡 연관 인사이트</h3>
                <p style="margin-bottom: 0;">이 글을 읽은 분들이 가장 많이 클릭한 <strong>최신 트렌드 분석</strong>도 함께 확인해 보세요.</p>
                <a href="{site_home}" style="color: {site['color']}; text-decoration: underline; font-weight: bold; display: block; margin-top: 10px;">👉 관련 글 리스트 보러 가기</a>
            </div>
            '''
            
            # 최종 CTA 버튼 (블로그 홈/카테고리로 유도하여 추가 탐색 유발)
            cta_button = f'''
            <div style="text-align:center; margin: 50px 0;">
                <a href="{site_home}" style="background-color:{site['color']}; color:white; padding: 18px 40px; border-radius: 50px; text-decoration:none; font-weight:bold; font-size: 1.1em; display:inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease;">
                    {site["cta_text"]}
                </a>
            </div>
            '''
            
            # 4. 최종 HTML 조립
            content = f'<img src="{final_img_url}" style="width:100%; border-radius:12px; margin-bottom:25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">\n{res}\n{internal_link}\n{cta_button}'
            
            # 5. 워드프레스 발행
            requests.post(
                site["url"],
                auth=HTTPBasicAuth(site["user"], site["pass"]),
                json={"title": title, "content": content, "status": "publish"}
            )
            print(f"✅ {site['name']} V10 수익 최적화 발행 완료 (Main: {site_home})")
            time.sleep(15) # 과부하 방지
            
        except Exception as e:
            print(f"❌ {site['name']} 시스템 에러: {e}")

if __name__ == "__main__":
    run_auto_post_v10()
