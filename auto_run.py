import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time
import urllib.parse
import os
import feedparser

def get_env_secrets():
    return {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "SITES": [
            {
                "name": "건강 포커스",
                "url": os.environ.get("SITE1_URL"),
                "media": os.environ.get("SITE1_MEDIA"),
                "user": os.environ.get("SITE1_USER"),
                "pass": os.environ.get("SITE1_PASS"),
                "color": "#00A86B", # 메디컬 그린
                "objective": "2026년 최신 의학 정보 및 데이터 기반 팩트 중심 건강 포스팅.",
                "cta_text": "실시간 건강 지표 확인하기"
            },
            {
                "name": "경제 트렌드",
                "url": os.environ.get("SITE2_URL"),
                "media": os.environ.get("SITE2_MEDIA"),
                "user": os.environ.get("SITE2_USER"),
                "pass": os.environ.get("SITE2_PASS"),
                "color": "#1A237E", # 네이비 블루
                "objective": "2026년 글로벌 시장 지표 및 수익화 전략 분석 포스팅.",
                "cta_text": "오늘의 주요 경제 지표 보기"
            },
            {
                "name": "테크 리뷰",
                "url": os.environ.get("SITE3_URL"),
                "media": os.environ.get("SITE3_MEDIA"),
                "user": os.environ.get("SITE3_USER"),
                "pass": os.environ.get("SITE3_PASS"),
                "color": "#6200EE", # 일렉트릭 퍼플
                "objective": "2026년 최신 AI 및 신기술 트렌드 테크 분석 포스팅.",
                "cta_text": "최신 테크 트렌드 리포트 받기"
            }
        ]
    }

def get_realtime_keyword(api_key):
    # 구글 뉴스 RSS (대한민국 주요 뉴스)
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_titles = [entry.title for entry in feed.entries[:10]]
    combined_titles = " | ".join(news_titles)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"다음 실시간 뉴스들 중에서 건강, 경제, 테크 블로그에서 다루기 좋은 가장 핫한 주제를 선정해 딱 한 단어로 키워드만 말해줘. 뉴스 리스트: {combined_titles}"
    
    response = model.generate_content(prompt)
    return response.text.strip()

def run_auto_post():
    secrets = get_env_secrets()
    main_keyword = get_realtime_keyword(secrets["GEMINI_API_KEY"])
    print(f"🎯 선정된 실시간 키워드: {main_keyword}")
    
    model = genai.GenerativeModel('gemini-2.5-flash')

    for site in secrets["SITES"]:
        try:
            # 1. 썸네일 생성
            img_prompt = urllib.parse.quote(f"high quality blog thumbnail, {main_keyword}, {site['name']} concept, minimal design")
            img_url = f"https://image.pollinations.ai/prompt/{img_prompt}?width=800&height=450&nologo=true"
            img_data = requests.get(img_url).content
            
            media_res = requests.post(
                site["media"],
                headers={"Content-Disposition": f'attachment; filename="thumb.jpg"', "Content-Type": "image/jpeg"},
                data=img_data,
                auth=HTTPBasicAuth(site["user"], site["pass"])
            )
            final_img_url = media_res.json().get("source_url", "")

            # 2. GEO 최적화 본문 생성 (TL;DR, 리스트, CTA 버튼 포함)
            article_prompt = f"""키워드 [{main_keyword}]에 대해 {site['objective']}를 작성해.
            - 2026년 최신 정보 기반. 인사말 절대 금지.
            - TITLE: [제목] 형식 필수.
            - 상단에 '핵심 요약(TL;DR)' 박스를 HTML <blockquote> 태그로 포함해.
            - 모바일 가독성을 위해 H2, H3, <ul> 리스트를 적극 활용해.
            - 글 하단에 '더 알아보기' 클릭을 유도하는 CTA 버튼을 HTML로 만들어 추가해.
            - 글 끝에 '이 정보가 도움이 되셨다면 다른 관련 글도 확인해보세요' 문구를 포함해.
            """
            
            res = model.generate_content(article_prompt).text
            title = res.split("TITLE:")[1].split("\n")[0].strip() if "TITLE:" in res else f"[{main_keyword}] 최신 리포트"
            
            # 본문 가공 (이미지 + 내용 + CTA 버튼 스타일링)
            cta_button = f'<div style="text-align:center; margin:40px 0;"><a href="#" style="background:{site['color']}; color:white; padding:18px 35px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:18px; display:inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">{site["cta_text"]}</a></div>'
            content = f'<img src="{final_img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">\n{res}\n{cta_button}'
            
            requests.post(site["url"], auth=HTTPBasicAuth(site["user"], site["pass"]), json={"title": title, "content": content, "status": "publish"})
            print(f"✅ {site['name']} 발행 완료")
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ {site['name']} 에러: {e}")

if __name__ == "__main__":
    run_auto_post()
