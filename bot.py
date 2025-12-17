import os
import time
import requests
import random
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API, Client

# ==========================================
# GITHUB SECRETS (Değiştirme)
# ==========================================
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GROQ_KEY      = os.getenv("GROQ_KEY")

# ==========================================
# YARDIMCI: GROQ AI
# ==========================================
def ask_groq(prompt):
    if not GROQ_KEY: return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8
        }
        res = requests.post(url, headers=headers, json=data, timeout=20)
        return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else None
    except: return None

# ==========================================
# YARDIMCI: GÖRSEL HD
# ==========================================
def enhance_image(img_path):
    try:
        img = Image.open(img_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        img.save("final_image.jpg", quality=95)
        return "final_image.jpg"
    except: return img_path

# ==========================================
# İÇERİK SEÇİCİ
# ==========================================
def get_anime_content():
    print("🧠 İçerik hazırlanıyor...", flush=True)
    try:
        # Rate limit yememek için rastgelelik
        page = random.randint(1, 10)
        resp = requests.get(f"https://api.jikan.moe/v4/top/anime?page={page}", timeout=15)
        if resp.status_code != 200: return None, None, None
        
        item = random.choice(resp.json()['data'])
        name = item['title_english'] or item['title']
        img_url = item['images']['jpg']['large_image_url']
        synopsis = item.get('synopsis', 'Awesome anime.')[:800]
        genres = [g['name'] for g in item.get('genres', [])]
        
        prompt = f"""
        Act as 'Orbis Anime'. Write a friendly, hype tweet about: {name}.
        Context: {synopsis}
        Genres: {', '.join(genres)}
        
        Rules:
        1. Start with Title + Emoji.
        2. Friendly, enthusiastic tone.
        3. Explain the plot simply.
        4. Hashtags: #{name.replace(' ','')} {' '.join(['#'+g for g in genres[:3]])} #Anime
        Output ONLY the tweet text.
        """
        caption = ask_groq(prompt)
        return name, img_url, caption
    except Exception as e:
        print(f"Hata: {e}")
        return None, None, None

# ==========================================
# TWITTER PAYLAŞIM (SADECE V2)
# ==========================================
def post_to_twitter(img_url, caption):
    print("⬇️ Resim indiriliyor...", flush=True)
    try:
        with open("temp.jpg", "wb") as f:
            f.write(requests.get(img_url).content)
        filename = enhance_image("temp.jpg")
    except: return

    print("🐦 Twitter'a yükleniyor...", flush=True)
    try:
        # 1. MEDYA YÜKLEME (V1.1 - Burası çalışıyor demiştin)
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        media = api.media_upload(filename)
        print("✅ Resim yüklendi (ID alındı).")
        
        # 2. TWEET ATMA (V2 - Sadece buraya odaklanacağız)
        client = Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        response = client.create_tweet(text=caption, media_ids=[media.media_id])
        print(f"🎉 TWEET BAŞARIYLA ATILDI! ID: {response.data['id']}")
        
    except Exception as e:
        print("\n❌ TWEET HATASI (V2):")
        print(e)
        print("-" * 30)
        print("EĞER BURADA '403 FORBIDDEN' GÖRÜYORSAN:")
        print("Developer Portal'da bu App, bir 'Project'in içinde görünse bile bağlantısı kopmuş olabilir.")
        print("ÇÖZÜM: Yeni bir Proje oluştur ve App'i onun içine taşı.")

if __name__ == "__main__":
    name, img_url, caption = get_anime_content()
    if name:
        post_to_twitter(img_url, caption)
    else:
        print("⚠️ İçerik oluşmadı.")
