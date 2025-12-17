import os
import requests
import random
import time
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API, Client

# ==========================================
# AYARLAR VE KEYLER
# ==========================================
# Eğer bilgisayarında test ediyorsan bu satırları kendi keylerinle doldurabilirsin.
# GitHub Actions'da çalışıyorsa os.environ kalsın.
API_KEY       = os.environ.get("API_KEY")
API_SECRET    = os.environ.get("API_SECRET")
ACCESS_TOKEN  = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")
GROQ_KEY      = os.environ.get("GROQ_KEY")

# ==========================================
# YARDIMCI: GÖRSEL İYİLEŞTİRME (HD)
# ==========================================
def enhance_image(img_path):
    try:
        img = Image.open(img_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        converter = ImageEnhance.Color(img)
        img = converter.enhance(1.3)
        converter = ImageEnhance.Contrast(img)
        img = converter.enhance(1.1)
        output_name = "orbis_hd.jpg"
        img.save(output_name, quality=95)
        return output_name
    except Exception as e:
        print(f"⚠️ Görsel iyileştirme hatası: {e}")
        return img_path

# ==========================================
# MOD 1: ANİME TANITIM
# ==========================================
def mode_anime_spotlight():
    print("🎬 MOD 1: Anime Tanıtımı Hazırlanıyor...", flush=True)
    try:
        page = random.randint(1, 15)
        url = f"https://api.jikan.moe/v4/top/anime?page={page}"
        resp = requests.get(url, timeout=20).json()
        item = random.choice(resp['data'])
        
        name = item['title_english'] if item.get('title_english') else item['title']
        img_url = item['images']['jpg']['large_image_url']
        synopsis = item['synopsis'] if item['synopsis'] else "No synopsis available."
        
        prompt = f"""
        Act as 'Orbis Anime', a popular anime influencer.
        Topic: {name} (Anime)
        Context: {synopsis[:800]}
        
        Task: Write a detailed, engaging Twitter post.
        Guidelines:
        1. Start with the Anime Title in BOLD/Uppercase with cool emojis.
        2. Write a paragraph explaining WHY it is unique.
        3. Use a friendly, enthusiastic tone.
        4. Mention the Genre.
        5. End with a "Rating: ⭐⭐⭐⭐⭐" style verdict.
        6. Use 5-6 relevant hashtags including #{name.replace(' ','')} and #AnimeRecommendation.
        Output ONLY the tweet text.
        """
        caption = ask_groq(prompt)
        return name, img_url, caption
    except Exception as e:
        print(f"❌ Hata Mod 1: {e}")
        return None, None, None

# ==========================================
# MOD 2: KARAKTER ANALİZİ
# ==========================================
def mode_character_showcase():
    print("👤 MOD 2: Karakter Analizi Hazırlanıyor...", flush=True)
    try:
        page = random.randint(1, 10)
        url = f"https://api.jikan.moe/v4/top/characters?page={page}"
        resp = requests.get(url, timeout=20).json()
        item = random.choice(resp['data'])
        
        name = item['name']
        img_url = item['images']['jpg']['image_url']
        about = item['about'] if item['about'] else "Gizemli bir karakter."
        
        prompt = f"""
        Act as 'Orbis Anime'.
        Topic: Character Profile - {name}
        Context: {about[:800]}
        Task: Write a character analysis tweet.
        Guidelines:
        1. Header: "👤 CHARACTER SPOTLIGHT: {name}"
        2. List key traits in bullet points (•).
        3. Explain why fans love them.
        4. Use emojis matching the character's vibe.
        5. Hashtags: #{name.replace(' ','')} #AnimeCharacter.
        Output ONLY the tweet text.
        """
        caption = ask_groq(prompt)
        return name, img_url, caption
    except Exception as e:
        print(f"❌ Hata Mod 2: {e}")
        return None, None, None

# ==========================================
# MOD 3: TOP 5 LİSTESİ
# ==========================================
def mode_top_5_list():
    print("📋 MOD 3: Top 5 Listesi Hazırlanıyor...", flush=True)
    try:
        genres = ["Horror", "Romance", "Psychological", "Cyberpunk", "Isekai", "Dark Fantasy"]
        selected_genre = random.choice(genres)
        
        search_url = f"https://api.jikan.moe/v4/anime?q={selected_genre}&limit=1"
        resp = requests.get(search_url).json()
        if resp['data']:
            cover_img = resp['data'][0]['images']['jpg']['large_image_url']
        else:
            return None, None, None
        
        prompt = f"""
        Act as 'Orbis Anime'.
        Task: Create a "TOP 5 {selected_genre.upper()} ANIME" list for Twitter.
        Guidelines:
        1. Headline: "🏆 TOP 5 {selected_genre.upper()} ANIME" with emojis.
        2. List 5 distinct, high-quality anime.
        3. For each, give a tiny 1-sentence reason why.
        4. Ask followers: "Which one is your favorite?"
        5. Hashtags: #{selected_genre}Anime #Top5Anime.
        Output ONLY the tweet text.
        """
        caption = ask_groq(prompt)
        return f"Top 5 {selected_genre}", cover_img, caption
    except Exception as e:
        print(f"❌ Hata Mod 3: {e}")
        return None, None, None

# ==========================================
# YARDIMCI: GROQ İLE KONUŞMA
# ==========================================
def ask_groq(prompt):
    if not GROQ_KEY: return "Error: No API Key for Groq"
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
        res = requests.post(url, headers=headers, json=data, timeout=20)
        
        if res.status_code != 200:
            print(f"Groq Hatası: {res.text}")
            return "İçerik üretilemedi."
            
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating text: {e}"

# ==========================================
# ANA KONTROL VE PAYLAŞIM
# ==========================================
if __name__ == "__main__":
    print("🚀 ORBIS ULTIMATE BAŞLIYOR...", flush=True)
    
    # Zar At
    dice = random.randint(1, 100)
    if dice <= 50:
        name, img_url, caption = mode_anime_spotlight()
    elif dice <= 80:
        name, img_url, caption = mode_character_showcase()
    else:
        name, img_url, caption = mode_top_5_list()
        
    if name and img_url and caption:
        print(f"✅ Seçilen Mod İçeriği: {name}")
        
        # Resmi İndir
        try:
            img_data = requests.get(img_url).content
            with open("temp.jpg", "wb") as f: f.write(img_data)
            final_img = enhance_image("temp.jpg")
        except Exception as e:
            print(f"❌ Resim indirme hatası: {e}")
            exit()

        # Twitter Bağlantısı
        try:
            # V1.1 Auth (Medya yüklemek için)
            auth = OAuthHandler(API_KEY, API_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
            api = API(auth, wait_on_rate_limit=True)
            
            # V2 Client (Tweet atmak için)
            client = Client(
                consumer_key=API_KEY, 
                consumer_secret=API_SECRET, 
                access_token=ACCESS_TOKEN, 
                access_token_secret=ACCESS_SECRET
            )
            
            print("📤 Resim yükleniyor...")
            # 1. Adım: Resmi Yükle (V1.1 API)
            media = api.media_upload(filename=final_img)
            media_id = media.media_id
            print(f"✅ Resim yüklendi! ID: {media_id}")
            
            print("🐦 Tweet gönderiliyor...")
            # 2. Adım: Tweeti Oluştur (V2 API)
            response = client.create_tweet(text=caption, media_ids=[media_id])
            print(f"🎉 BAŞARILI! Tweet ID: {response.data['id']}")
            
        except Exception as e:
            print("\n❌ TWEET ATILAMADI!")
            print(f"Hata Detayı: {e}")
            print("-" * 30)
            print("🔴 ÇÖZÜM İPUCU: Eğer '403 Forbidden' alıyorsan:")
            print("1. Twitter Developer Portal'da 'User authentication settings' kısmına git.")
            print("2. İzinleri 'Read and Write' yap.")
            print("3. MUTLAKA 'Regenerate Token' yapıp yeni keyleri kullan.")
            
    else:
        print("⚠️ İçerik oluşturulamadı, API yanıt vermedi.")
