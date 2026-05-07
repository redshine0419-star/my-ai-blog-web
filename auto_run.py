import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time
import urllib.parse
import os

# GitHub Secrets에서 환경변수 로드
def get_env_secrets():
    return {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "SITE1": {
            "url": os.environ.get("SITE1_URL"),
            "media": os.environ.get("SITE1_MEDIA"),
            "user": os.environ.get("SITE1_USER"),
            "pass": os.environ.get("SITE1_PASS"),
            "objective": "건강 및 웰빙 분야. 2026년 최신 의학 정보 기반 팩트 포스팅."
        },
        "SITE2": {
            "url": os.environ.get("SITE2_URL"),
            "media": os.environ.get("SITE2_MEDIA"),
            "user": os.environ.get("SITE2_USER"),
            "pass": os.environ.get("SITE2_PASS"),
            "objective": "경제 및 비즈니스 분야. 2026년 최신 시장 동향 분석 포스팅."
        },
        "SITE3": {
            "url": os.environ.get("SITE3_URL"),
            "media": os.environ.get("SITE3_MEDIA"),
            "user": os.environ.get("SITE3_USER"),
            "pass": os.environ.get("SITE3_PASS"),
            "objective": "IT 및 테크 리뷰. 2026년 최신 기술 트렌드 기반 팩트 포스팅."
        }
    }

def run_auto_post():
    secrets = get_env_secrets()
    genai.configure(api_key=secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # 오늘의 키워드 생성
    kw_res = model.generate_content("2026년 현재 대중이 가장 관심 있어 할 건강, 경제, 테크 통합 키워드 1개만 단어로 추천해줘.")
    main_keyword = kw_res.text.strip()
    print(f"🎯 오늘의 키워드: {main_keyword}")

    for i in range(1, 4):
        site = secrets[f"SITE{i}"]
        try:
            # 이미지 생성
            img_prompt = urllib.parse.quote(f"high quality blog thumbnail, {main_keyword}, realistic")
            img_url = f"https://image.pollinations.ai/prompt/{img_prompt}?width=800&height=400&nologo=true"
            img_data = requests.get(img_url).content
            
            # 워드프레스 미디어 업로드
            media_res = requests.post(
                site["media"],
                headers={"Content-Disposition": f'attachment; filename="thumb_{i}.jpg"', "Content-Type": "image/jpeg"},
                data=img_data,
                auth=HTTPBasicAuth(site["user"], site["pass"])
            )
            final_img_url = media_res.json().get("source_url", "")

            # 본문 생성 및 발행
            prompt = f"키워드 [{main_keyword}]에 대해 {site['objective']}에 맞춰 2026년 최신 팩트 기반 블로그 글을 HTML로 작성해. 인사말 금지, TITLE: [제목] 형식 필수."
            article = model.generate_content(prompt).text
            
            title = article.split("TITLE:")[1].split("\n")[0].strip() if "TITLE:" in article else f"[{main_keyword}] 최신 리포트"
            content = f'<img src="{final_img_url}" style="width:100%;">{article}'
            
            requests.post(site["url"], auth=HTTPBasicAuth(site["user"], site["pass"]), json={"title": title, "content": content, "status": "publish"})
            print(f"✅ 사이트 {i} 발행 완료")
            time.sleep(30)
        except Exception as e:
            print(f"❌ 사이트 {i} 에러: {e}")

if __name__ == "__main__":
    run_auto_post()
