import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time, urllib.parse, os, feedparser

def get_env_secrets():
    """GitHub Secrets에서 정보를 가져와 사이트 설정을 구성합니다."""
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
                "cta_text": "최신 건강 리포트 확인하기"
            },
            {
                "name": "경제 트렌드",
                "url": os.environ.get("SITE2_URL"),
                "media": os.environ.get("SITE2_MEDIA"),
                "user": os.environ.get("SITE2_USER"),
                "pass": os.environ.get("SITE2_PASS"),
                "color": "#1A237E",
                "objective": "2026년 글로벌 시장 지표 및 수익화 전략 분석 포스팅.",
                "cta_text": "실시간 경제 지표 분석보기"
            },
            {
                "name": "넥스트 테크 웨이브",
                "url": os.environ.get("SITE3_URL"),
                "media": os.environ.get("SITE3_MEDIA"),
                "user": os.environ.get("SITE3_USER"),
                "pass": os.environ.get("SITE3_PASS"),
                "color": "#6200EE",
                "objective": "2026년 최신 AI 및 신기술 트렌드 테크 분석 포스팅.",
                "cta_text": "신기술 인사이트 더보기"
            }
        ]
    }

def get_realtime_commercial_keyword(api_key):
    """실시간 뉴스 중 수익성이 높은 키워드를 추출합니다."""
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_titles = [entry.title for entry in feed.entries[:12]]
    combined_titles = " | ".join(news_titles)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""다음 뉴스 리스트 중에서 건강, 경제, 테크 블로그에서 '구매 결정'이나 '솔루션 비교'가 일어날 법한 상업적 가치가 높은 키워드 1개를 선정해줘. 
    단순 나열보다 '비용', '수익', '추천'과 연결될 수 있는 주제여야 해. 단어만 딱 하나 출력해.
    뉴스: {combined_titles}"""
    
    response = model.generate_content(prompt)
    return response.text.strip()

def run_auto_post():
    secrets = get_env_secrets()
    if not secrets["GEMINI_API_KEY"]:
        print("❌ API 키가 설정되지 않았습니다.")
        return

    main_keyword = get_realtime_commercial_keyword(secrets["GEMINI_API_KEY"])
    print(f"💰 선정된 고단가 키워드: {main_keyword}")
    
    model = genai.GenerativeModel('gemini-2.5-flash')

    for site in secrets["SITES"]:
        try:
            # 1. 썸네일 생성
            img_prompt = urllib.parse.quote(f"high quality professional blog thumbnail, {main_keyword}, {site['name']} theme")
            img_url = f"https://image.pollinations.ai/prompt/{img_prompt}?width=800&height=450&nologo=true"
            img_data = requests.get(img_url).content
            
            media_res = requests.post(
                site["media"],
                headers={"Content-Disposition": 'attachment; filename="thumb.jpg"', "Content-Type": "image/jpeg"},
                data=img_data,
                auth=HTTPBasicAuth(site["user"], site["pass"])
            )
            final_img_url = media_res.json().get("source_url", "")

            # 2. 본문 생성 (수익 최적화 프롬프트)
            article_prompt = f"""키워드 [{main_keyword}]에 대해 {site['objective']}를 작성해.
            - TITLE: [제목] 형식 필수.
            - 상단에 <blockquote>를 활용한 3줄 핵심 요약(TL;DR) 포함.
            - 중간에 2026년 통계나 비교 데이터를 담은 <table>을 반드시 포함.
            - 가독성을 위해 H2, H3 태그와 <ul> 리스트를 적극 활용.
            - 마지막에 [전문가 Insight] 섹션을 <div style="background:#f8f9fa; padding:15px; border-left:5px solid {site['color']};">로 감싸서 작성.
            """
            
            res = model.generate_content(article_prompt).text
            title = res.split("TITLE:")[1].split("\n")[0].strip() if "TITLE:" in res else f"[{main_keyword}] 2026 심층 리포트"
            
            # 3. 수익화 장치 조립
            site_home = site["url"].split("/wp-json")[0]
            internal_link = f'<div style="border:1px solid #eee; padding:15px; margin:20px 0;"><strong>📍 함께 보면 좋은 글:</strong> <a href="{site_home}" style="color:{site["color"]}; text-decoration:none;">2026 {main_keyword} 시장 변화와 대응 전략</a></div>'
            cta_button = f'<div style="text-align:center; margin:40px 0;"><a href="{site_home}" style="background:{site["color"]}; color:white; padding:18px 35px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block;">{site["cta_text"]}</a></div>'
            
            content = f'<img src="{final_img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n{res}\n{internal_link}\n{cta_button}'
            
            # 4. 발행
            requests.post(
                site["url"],
                auth=HTTPBasicAuth(site["user"], site["pass"]),
                json={"title": title, "content": content, "status": "publish"}
            )
            print(f"✅ {site['name']} 수익 최적화 발행 완료")
            time.sleep(10)
            
        except Exception as e:
            print(f"❌ {site['name']} 실패: {e}")

if __name__ == "__main__":
    run_auto_post()
