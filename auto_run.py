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
                "objective": "2026년 최신 의학 정보 및 데이터 기반 팩트 중심 건강 포스팅."
            },
            {
                "name": "경제 트렌드",
                "url": os.environ.get("SITE2_URL"),
                "media": os.environ.get("SITE2_MEDIA"),
                "user": os.environ.get("SITE2_USER"),
                "pass": os.environ.get("SITE2_PASS"),
                "color": "#1A237E",
                "objective": "2026년 글로벌 시장 지표 및 수익화 전략 분석 포스팅."
            },
            {
                "name": "넥스트 테크 웨이브",
                "url": os.environ.get("SITE3_URL"),
                "media": os.environ.get("SITE3_MEDIA"),
                "user": os.environ.get("SITE3_USER"),
                "pass": os.environ.get("SITE3_PASS"),
                "color": "#6200EE",
                "objective": "2026년 최신 AI 및 신기술 트렌드 테크 분석 포스팅."
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
            
            # 3. GrowWeb.me 백링크 섹션 (SEO 외부 링크)
            growweb_banner = '''
            <div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; margin: 40px 0; background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);">
                <p style="margin: 0 0 6px 0; font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px;">POWERED BY AI MARKETING TOOLS</p>
                <h4 style="margin: 0 0 10px 0; font-size: 18px; color: #1a1a2e;">
                    <a href="https://www.growweb.me/" target="_blank" rel="noopener" style="color: #4f46e5; text-decoration: none;">GrowWeb.me</a>
                    — AI 마케팅 운영 도구
                </h4>
                <p style="margin: 0 0 16px 0; font-size: 14px; color: #555; line-height: 1.7;">
                    GEO·SEO 진단, 경쟁사 분석, AI 언급율(Share of Voice) 측정까지 — 시니어 마케터의 직관을 AI가 보조합니다. 9가지 도구 전부 <strong>완전 무료</strong>.
                </p>
                <a href="https://www.growweb.me/" target="_blank" rel="noopener"
                   style="display: inline-block; background: #4f46e5; color: white; padding: 10px 24px; border-radius: 8px; font-size: 14px; font-weight: bold; text-decoration: none;">
                    무료로 시작하기 →
                </a>
            </div>
            '''

            # 4. 최종 HTML 조립
            content = f'<img src="{final_img_url}" style="width:100%; border-radius:12px; margin-bottom:25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">\n{res}\n{growweb_banner}'
            
            # 5. 워드프레스 발행
            requests.post(
                site["url"],
                auth=HTTPBasicAuth(site["user"], site["pass"]),
                json={"title": title, "content": content, "status": "publish"}
            )
            print(f"✅ {site['name']} V10 수익 최적화 발행 완료")
            time.sleep(15) # 과부하 방지
            
        except Exception as e:
            print(f"❌ {site['name']} 시스템 에러: {e}")

if __name__ == "__main__":
    run_auto_post_v10()
