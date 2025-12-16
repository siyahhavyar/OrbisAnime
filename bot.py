import os
import requests
import random
import json
import time
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API, Client

# ==========================================
# ŞİFRELER (GITHUB SECRETS'TEN)
# ==========================================
API_KEY       = os.environ["API_KEY"]
API_SECRET    = os.environ["API_SECRET"]
ACCESS_TOKEN  = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]
GROQ_KEY      = os.environ["GROQ_KEY"]

# ==========================================
# YARDIMCI: GÖRSEL İYİLEŞTİRME (HD)
# ==========================================
def enhance_image(img_path):
    try:
        img = Image.open(img_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        converter = ImageEnhance.Color(img)
        img = converter.enhance(1.3) # Biraz daha canlı
        converter = ImageEnhance.Contrast(img)
        img = converter.enhance(1.1)
        output_name = "orbis_hd.jpg"
        img.save(output_name, quality=95)
        return output_name
    except: return img_path

# ==========================================
# MOD 1: ANİME TANITIM (DETAYLI & EMOJİLİ)
# ==========================================
def mode_anime_spotlight():
    print("🎬 MOD 1: Anime Tanıtımı Hazırlanıyor...", flush=True)
    try:
        # Rastgele popüler bir anime seç
        page = random.randint(1, 15)
        url = f"https://api.jikan.moe/v4/top/anime?page={page}"
        resp = requests.get(url, timeout=20).json()
        item = random.choice(resp['data'])
        
        name = item['title_english'] if item['title_english'] else item['title']
        img_url = item['images']['jpg']['large_image_url']
        synopsis = item['synopsis']
        
        # Groq ile uzun ve tatlı bir tanıtım yazdır
        prompt = f"""
        Act as 'Orbis Anime', a popular anime influencer.
        Topic: {name} (Anime)
        Context: {synopsis[:800]}
        
        Task: Write a detailed, engaging Twitter post.
        
        Guidelines:
        1. Start with the Anime Title in BOLD/Uppercase with cool emojis (✨🎥).
        2. Write a paragraph explaining WHY it is unique and worth watching. Focus on plot + vibe.
        3. Use a friendly, enthusiastic tone (use emojis like 🌸, 🔥, 🗡️, 🍱).
        4. Mention the Genre (e.g., Horror, Romance).
        5. End with a "Rating: ⭐⭐⭐⭐⭐" style verdict.
        6. Use 5-6 relevant hashtags including #{name.replace(' ','')} and #AnimeRecommendation.
        
        Output ONLY the tweet text.
        """
        caption = ask_groq(prompt)
        return name, img_url, caption
    except Exception as e:
        print(f"Hata Mod 1: {e}")
        return None, None, None

# ==========================================
# MOD 2: KARAKTER ANALİZİ (GÜNLÜK YILDIZ)
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
        about = item['about']
        
        prompt = f"""
        Act as 'Orbis Anime'.
        Topic: Character Profile - {name}
        Context: {about[:800]}
        
        Task: Write a character analysis tweet.
        
        Guidelines:
        1. Header: "👤 CHARACTER SPOTLIGHT: {name}"
        2. List their key traits/powers/personality in bullet points (•).
        3. Explain why fans love (or hate) them.
        4. Use emojis matching the character's vibe.
        5. Hashtags: #{name.replace(' ','')} #AnimeCharacter.
        
        Output ONLY the tweet text.
        """
        caption = ask_groq(prompt)
        return name, img_url, caption
    except Exception as e:
        print(f"Hata Mod 2: {e}")
        return None, None, None

# ==========================================
# MOD 3: TOP 5 LİSTESİ (KONSEPT)
# ==========================================
def mode_top_5_list():
    print("📋 MOD 3: Top 5 Listesi Hazırlanıyor...", flush=True)
    try:
        # Rastgele bir tür seç (Korku, Romantik, Aksiyon...)
        genres = ["Horror", "Romance", "Psychological", "Cyberpunk", "Isekai", "Dark Fantasy", "School Life"]
        selected_genre = random.choice(genres)
        
        # O türden 5 anime bulmak zor olabilir, o yüzden Groq'a listeyi hazırlatacağız
        # Görsel olarak "Generic" bir anime görseli veya türü temsil eden bir şey kullanabiliriz
        # Şimdilik Jikan'dan o türde rastgele bir anime resmi alıp kapak yapacağız
        
        # O türden bir resim bulmak için arama yapalım
        search_url = f"https://api.jikan.moe/v4/anime?q={selected_genre}&limit=1"
        resp = requests.get(search_url).json()
        cover_img = resp['data'][0]['images']['jpg']['large_image_url']
        
        prompt = f"""
        Act as 'Orbis Anime'.
        Task: Create a "TOP 5 {selected_genre.upper()} ANIME YOU MUST WATCH" list for Twitter.
        
        Guidelines:
        1. Headline: "🏆 TOP 5 {selected_genre.upper()} ANIME" with emojis.
        2. List 5 distinct, high-quality anime in that genre.
        3. For each, give a tiny 1-sentence reason why (e.g., "1. Berserk - Pure darkness 🌑").
        4. Ask followers: "Which one is your favorite?"
        5. Hashtags: #{selected_genre}Anime #Top5Anime.
        
        Output ONLY the tweet text.
        """
        caption = ask_groq(prompt)
        return f"Top 5 {selected_genre}", cover_img, caption
        
    except Exception as e:
        print(f"Hata Mod 3: {e}")
        return None, None, None

# ==========================================
# YARDIMCI: GROQ İLE KONUŞMA
# ==========================================
def ask_groq(prompt):
    if len(GROQ_KEY) < 5: return "Error: No API Key"
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
        res = requests.post(url, headers=headers, json=data, timeout=20)
        return res.json()['choices'][0]['message']['content']
    except: return "Error generating text."

# ==========================================
# ANA KONTROL VE PAYLAŞIM
# ==========================================
if __name__ == "__main__":
    print("🚀 ORBIS ULTIMATE BAŞLIYOR...", flush=True)
    
    # MOD SEÇİMİ (Rastgele ama ağırlıklı)
    # %50 Anime Tanıtımı, %30 Karakter, %20 Liste
    dice = random.randint(1, 100)
    
    if dice <= 50:
        name, img_url, caption = mode_anime_spotlight()
    elif dice <= 80:
        name, img_url, caption = mode_character_showcase()
    else:
        name, img_url, caption = mode_top_5_list()
        
    if name and img_url and caption:
        print(f"✅ Seçilen Mod İçeriği: {name}")
        
        # Resmi İndir ve HD Yap
        img_data = requests.get(img_url).content
        with open("temp.jpg", "wb") as f: f.write(img_data)
        final_img = enhance_image("temp.jpg")
        
        # Twitter'a Yükle
        try:
            auth = OAuthHandler(API_KEY, API_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
            api = API(auth)
            client = Client(consumer_key=API_KEY, consumer_secret=API_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
            
            media = api.media_upload(final_img)
            client.create_tweet(text=caption, media_ids=[media.media_id])
            print("🐦 TWEET ATILDI!")
        except Exception as e:
            print(f"❌ Tweet Hatası: {e}")
    else:
        print("⚠️ İçerik oluşturulamadı.")
