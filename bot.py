import os
import time
import requests
import random
import json
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API, Client

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GROQ_KEY      = os.getenv("GROQ_KEY")

# -----------------------------
# YARDIMCI: GROQ AI (METİN YAZARI)
# -----------------------------
def ask_groq(prompt):
    if not GROQ_KEY:
        print("UYARI: Groq Key yok.", flush=True)
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.85 # Biraz daha yaratıcı olsun
        }
        res = requests.post(url, headers=headers, json=data, timeout=20)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq Hata: {e}")
    return None

# -----------------------------
# YARDIMCI: GÖRSEL HD YAPMA
# -----------------------------
def enhance_image(img_path):
    try:
        img = Image.open(img_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        converter = ImageEnhance.Color(img)
        img = converter.enhance(1.25) # Renkleri biraz daha patlat
        img.save("final_image.jpg", quality=95)
        return "final_image.jpg"
    except:
        return img_path

# -----------------------------
# 1. İÇERİK ÜRETİCİ (SAMİMİ MOD)
# -----------------------------
def get_anime_content():
    print("🧠 Anime içeriği aranıyor...", flush=True)
    
    max_retries = 3
    for i in range(max_retries):
        try:
            page = random.randint(1, 10)
            url = f"https://api.jikan.moe/v4/top/anime?page={page}"
            resp = requests.get(url, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()['data']
                item = random.choice(data)
                
                name = item['title_english'] if item.get('title_english') else item['title']
                img_url = item['images']['jpg']['large_image_url']
                synopsis = item.get('synopsis', 'No info')[:1000] # Konuyu anlaması için daha çok veri
                genres = [g['name'] for g in item.get('genres', [])] # Türleri al
                
                # --- GÜNCELLENMİŞ PROMPT ---
                prompt = f"""
                Act as 'Orbis Anime', a passionate anime fan. 
                Task: Write a detailed, engaging Twitter post about the anime: {name}.
                
                Anime Context: {synopsis}
                Genres: {', '.join(genres)}
                
                Guidelines for Tone & Style:
                1. DO NOT be formal. Be friendly, enthusiastic, and sincere (like recommending to a best friend).
                2. Explain the PLOT clearly but make it sound exciting. What makes this anime special?
                3. Use emojis freely to match the vibe (e.g., ⚔️ for action, 🌸 for romance).
                4. Structure:
                   - Hook Line (Title + Emojis)
                   - The "Vibe" & Plot Summary (3-4 sentences)
                   - Why you should watch it (Personal verdict)
                   - Final Rating (e.g., 9/10 or Stars)
                
                Hashtag Rules:
                - Create 4-5 CUSTOM hashtags based on the specific genres and theme. 
                - Example: If it's Naruto, use #Ninja #Shonen #ActionAnime. 
                - ALWAYS include #{name.replace(' ','')} and #OrbisAnime.
                
                Output ONLY the tweet text.
                """
                caption = ask_groq(prompt)
                
                if caption:
                    return name, img_url, caption
            
            time.sleep(2)
        except Exception as e:
            print(f"Veri çekme hatası ({i+1}): {e}")
            time.sleep(2)
            
    return None, None, None

# -----------------------------
# 2. TWITTER POST (HİBRİT SİSTEM)
# -----------------------------
def post_to_twitter(img_url, caption):
    print("⬇️ Resim indiriliyor...", flush=True)
    try:
        img_data = requests.get(img_url).content
        with open("temp.jpg", "wb") as f:
            f.write(img_data)
        filename = enhance_image("temp.jpg")
    except Exception as e:
        print(f"Resim indirme hatası: {e}")
        return False

    print("🐦 Twitter'a bağlanılıyor...", flush=True)
    try:
        # V1.1 Auth (Resim Yüklemek İçin Şart)
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        
        media = api.media_upload(filename)
        print("✅ Resim yüklendi.")

        # V2 Tweet (Önce Modern Yöntem)
        try:
            client = Client(
                consumer_key=API_KEY,
                consumer_secret=API_SECRET,
                access_token=ACCESS_TOKEN,
                access_token_secret=ACCESS_SECRET
            )
            client.create_tweet(text=caption, media_ids=[media.media_id])
            print("🎉 TWEET ATILDI (Client Modu)!")
            return True
            
        except Exception as v2_error:
            print(f"⚠️ Client Modu Hata Verdi (Bu normal olabilir): {v2_error}")
            print("🔄 API Modu (Yedek) ile gönderiliyor...")
            
            # V1.1 Tweet (Yedek - Kesin Çözüm)
            api.update_status(status=caption, media_ids=[media.media_id])
            print("🎉 TWEET ATILDI (API Yedek Modu)!")
            return True

    except Exception as e:
        print(f"❌ Kritik Hata: {e}", flush=True)
        return False

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 ORBIS ANIME (SAMİMİ MOD) BAŞLIYOR...", flush=True)
    
    name, img_url, caption = get_anime_content()
    
    if name and img_url and caption:
        print("------------------------------------------------")
        print(f"🎯 Anime: {name}")
        print(f"📝 Açıklama Önizleme:\n{caption[:100]}...")
        print("------------------------------------------------")
        
        post_to_twitter(img_url, caption)
    else:
        print("⚠️ İçerik oluşturulamadı.")
