import os
import requests
import random
import json
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API, Client

# ==========================================
# GITHUB SECRETS'TEN ŞİFRELERİ ÇEKME
# ==========================================
API_KEY       = os.environ["API_KEY"]
API_SECRET    = os.environ["API_SECRET"]
ACCESS_TOKEN  = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]
GROQ_KEY      = os.environ["GROQ_KEY"]

# ==========================================
# 1. ORBIS ANIME BULUCU
# ==========================================
def get_random_anime_content():
    print("🇯🇵 Orbis Arşivi taranıyor...", flush=True)
    mode = random.choice(["anime", "character"])
    try:
        random_page = random.randint(1, 10)
        if mode == "anime":
            url = f"https://api.jikan.moe/v4/top/anime?page={random_page}"
            resp = requests.get(url, timeout=20).json()
            item = random.choice(resp['data'])
            name = item.get('title_english', item['title'])
            img_url = item['images']['jpg']['large_image_url'] 
            desc = item.get('synopsis', 'A masterpiece of animation.')
        else: 
            url = f"https://api.jikan.moe/v4/top/characters?page={random_page}"
            resp = requests.get(url, timeout=20).json()
            item = random.choice(resp['data'])
            name = item['name']
            img_url = item['images']['jpg']['image_url']
            desc = item.get('about', 'A legendary anime character.')

        if not img_url or "default" in img_url: return None, None, None, None
        print(f"🎯 Bulunan Eser: {name}", flush=True)
        return name, img_url, desc, mode
    except Exception as e:
        print(f"⚠️ Veri hatası: {e}")
        return None, None, None, None

# ==========================================
# 2. HD EFEKTİ
# ==========================================
def enhance_image(img_path):
    print("✨ Görsel restore ediliyor...", flush=True)
    try:
        img = Image.open(img_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        converter = ImageEnhance.Color(img)
        img = converter.enhance(1.25) 
        converter = ImageEnhance.Contrast(img)
        img = converter.enhance(1.1) 
        output_name = "orbis_hd.jpg"
        img.save(output_name, quality=95)
        return output_name
    except: return img_path

# ==========================================
# 3. KÜRATÖR (GROQ)
# ==========================================
def generate_commentary(name, desc, mode):
    print("🧠 Yapay Zeka notu hazırlıyor...", flush=True)
    if len(GROQ_KEY) > 5:
        try:
            prompt = f"""
            Act as 'Orbis Anime', a professional Anime Curator on Twitter.
            TOPIC: {name} (Type: {mode})
            CONTEXT: {desc[:600]}...
            TASK: Write a sophisticated tweet.
            RULES:
            1. Start with the name in uppercase.
            2. Share a deep insight or a 'Did you know' fact.
            3. Tone: Respectful, Artistic, Nostalgic.
            4. Max 280 characters logic.
            5. End with 3 relevant hashtags.
            Output ONLY the tweet text.
            """
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
            res = requests.post(url, headers=headers, json=data, timeout=20)
            if res.status_code == 200: return res.json()['choices'][0]['message']['content']
        except: pass
    return f"🎬 ORBIS ARCHIVE: {name}\n\n#Anime #{name.replace(' ','')}"

# ==========================================
# 4. PAYLAŞIM
# ==========================================
def post_to_twitter(img_path, caption):
    print("📸 Twitter'a yükleniyor...", flush=True)
    try:
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        client = Client(consumer_key=API_KEY, consumer_secret=API_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
        media = api.media_upload(img_path)
        client.create_tweet(text=caption, media_ids=[media.media_id])
        print("🐦 TWEET BAŞARIYLA ATILDI!", flush=True)
        return True
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")
        return False

# ==========================================
# ANA ÇALIŞTIRMA
# ==========================================
if __name__ == "__main__":
    print("🚀 ORBIS ANIME GITHUB ACTION BAŞLIYOR...", flush=True)
    # 3 kere deneme hakkı verelim
    for _ in range(3):
        name, img_url, desc, mode = get_random_anime_content()
        if name and img_url:
            img_data = requests.get(img_url).content
            with open("temp.jpg", "wb") as f: f.write(img_data)
            final_img = enhance_image("temp.jpg")
            caption = generate_commentary(name, desc, mode)
            print(f"📝 Tweet: {caption}")
            if post_to_twitter(final_img, caption):
                break # Başarılıysa döngüden çık
            else:
                print("Hata oluştu, tekrar deneniyor...")
        time.sleep(10)
