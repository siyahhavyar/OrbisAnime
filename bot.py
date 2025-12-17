import os
import requests
import random
import time
import json
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API, Client

# ==========================================
# AYARLAR (GITHUB SECRETS)
# ==========================================
API_KEY       = os.environ.get("API_KEY")
API_SECRET    = os.environ.get("API_SECRET")
ACCESS_TOKEN  = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")
GROQ_KEY      = os.environ.get("GROQ_KEY")

# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
def enhance_image(img_path):
    """Resmi indirip biraz daha kaliteli (HD) yapar."""
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
        print(f"⚠️ Görsel iyileştirme geçildi: {e}")
        return img_path

def ask_groq(prompt):
    """Groq AI'ya metin yazdırır."""
    if not GROQ_KEY:
        print("❌ HATA: GROQ_KEY bulunamadı!")
        return None
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8
        }
        
        # 30 saniye bekleme süresi tanıyalım
        res = requests.post(url, headers=headers, json=data, timeout=30)
        
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            print(f"❌ GROQ API Hatası ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        print(f"❌ Groq Bağlantı Hatası: {e}")
        return None

# ==========================================
# MOD 1: ANİME TANITIM (YEDEK VE ANA MOD)
# ==========================================
def mode_anime_spotlight():
    print("🎬 MOD 1: Anime Tanıtımı deneniyor...", flush=True)
    try:
        # Rate limit yememek için azıcık bekle
        time.sleep(2)
        
        # Rastgele sayfa
        page = random.randint(1, 10)
        url = f"https://api.jikan.moe/v4/top/anime?page={page}"
        resp = requests.get(url, timeout=20)
        
        if resp.status_code != 200:
            print(f"❌ Jikan API Hatası (Mod 1): {resp.status_code}")
            return None, None, None

        data = resp.json().get('data', [])
        if not data:
            print("❌ Jikan boş veri döndürdü.")
            return None, None, None
            
        item = random.choice(data)
        name = item.get('title_english') or item.get('title')
        img_url = item['images']['jpg']['large_image_url']
        synopsis = item.get('synopsis', 'No synopsis.')
        
        prompt = f"""
        Act as 'Orbis Anime'. Write a hype Twitter post for the anime: {name}.
        Synopsis: {synopsis[:500]}
        
        Rules:
        1. Start with Title in BOLD + Emoji.
        2. One hype paragraph.
        3. Rating: ⭐⭐⭐⭐⭐
        4. Hashtags: #{name.replace(' ','')} #Anime.
        """
        
        caption = ask_groq(prompt)
        return name, img_url, caption
        
    except Exception as e:
        print(f"❌ Mod 1 Çökme Hatası: {e}")
        return None, None, None

# ==========================================
# MOD 2: KARAKTER ANALİZİ
# ==========================================
def mode_character_showcase():
    print("👤 MOD 2: Karakter Analizi deneniyor...", flush=True)
    try:
        time.sleep(2)
        page = random.randint(1, 5)
        url = f"https://api.jikan.moe/v4/top/characters?page={page}"
        resp = requests.get(url, timeout=20)
        
        if resp.status_code != 200:
            print(f"❌ Jikan API Hatası (Mod 2): {resp.status_code}")
            return None, None, None
            
        data = resp.json().get('data', [])
        if not data: return None, None, None

        item = random.choice(data)
        name = item.get('name')
        img_url = item['images']['jpg']['image_url']
        about = item.get('about', 'Cool character.')
        
        prompt = f"""
        Act as 'Orbis Anime'. Tweet about character: {name}.
        Info: {about[:500]}
        Rules:
        1. "👤 CHARACTER SPOTLIGHT: {name}"
        2. Bullet points of traits.
        3. Hashtags.
        """
        
        caption = ask_groq(prompt)
        return name, img_url, caption
    except Exception as e:
        print(f"❌ Mod 2 Hata: {e}")
        return None, None, None

# ==========================================
# MOD 3: TOP 5 LISTE (Riskli Mod)
# ==========================================
def mode_top_5_list():
    print("📋 MOD 3: Top 5 Listesi deneniyor...", flush=True)
    try:
        genres = ["Horror", "Romance", "Action", "Isekai"]
        selected = random.choice(genres)
        
        # Jikan arama
        time.sleep(2)
        url = f"https://api.jikan.moe/v4/anime?q={selected}&limit=3&order_by=popularity"
        resp = requests.get(url, timeout=20)
        
        if resp.status_code != 200:
            print(f"❌ Jikan API Hatası (Mod 3): {resp.status_code}")
            return None, None, None
            
        data = resp.json().get('data', [])
        if not data: 
            print("❌ Mod 3 için veri bulunamadı.")
            return None, None, None
            
        cover_img = data[0]['images']['jpg']['large_image_url']
        
        prompt = f"""
        Act as 'Orbis Anime'. Create a "TOP 5 {selected.upper()} ANIME" list tweet.
        Just list 5 famous ones with emojis. Ask "Which is your fav?".
        """
        
        caption = ask_groq(prompt)
        return f"Top 5 {selected}", cover_img, caption
        
    except Exception as e:
        print(f"❌ Mod 3 Hata: {e}")
        return None, None, None

# ==========================================
# ANA ÇALIŞTIRMA BLOĞU
# ==========================================
if __name__ == "__main__":
    print("🚀 ORBIS ULTIMATE BAŞLATILIYOR...", flush=True)
    
    # 1. Deneme: Rastgele Mod Seç
    dice = random.randint(1, 100)
    name, img_url, caption = None, None, None
    
    if dice <= 40:
        name, img_url, caption = mode_anime_spotlight()
    elif dice <= 70:
        name, img_url, caption = mode_character_showcase()
    else:
        name, img_url, caption = mode_top_5_list()
        
    # 2. Deneme: Eğer ilk seçilen mod patladıysa (None döndüyse), GARANTİ MOD (Mod 1) çalıştır.
    if not name or not caption:
        print("\n⚠️ İlk mod başarısız oldu, YEDEK MOD (Anime Tanıtımı) devreye giriyor...")
        name, img_url, caption = mode_anime_spotlight()
        
    # 3. Paylaşım Kısmı
    if name and img_url and caption:
        print(f"\n✅ İÇERİK HAZIR: {name}")
        
        # Resmi İndir
        try:
            print("📥 Resim indiriliyor...")
            img_data = requests.get(img_url).content
            with open("temp.jpg", "wb") as f: f.write(img_data)
            final_img = enhance_image("temp.jpg")
        except Exception as e:
            print(f"❌ Resim indirme hatası: {e}")
            exit()

        # Twitter'a Gönder
        try:
            print("🔐 Twitter'a bağlanılıyor...")
            # V1 Auth (Medya için)
            auth = OAuthHandler(API_KEY, API_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
            api = API(auth)
            
            # V2 Client (Tweet için)
            client = Client(
                consumer_key=API_KEY,
                consumer_secret=API_SECRET,
                access_token=ACCESS_TOKEN,
                access_token_secret=ACCESS_SECRET
            )
            
            print("📤 Medya yükleniyor...")
            media = api.media_upload(filename=final_img)
            
            print("🐦 Tweet atılıyor...")
            client.create_tweet(text=caption, media_ids=[media.media_id])
            print("🎉 TWEET BAŞARIYLA ATILDI!")
            
        except Exception as e:
            print(f"\n❌ TWITTER HATASI: {e}")
            if "401" in str(e): print("👉 HATA: Keyler hatalı.")
            if "403" in str(e): print("👉 HATA: İzin yok. Access Token'ı Developer Portal'da 'Regenerate' yapıp GitHub'a eklemeyi unuttun!")
    else:
        print("\n❌❌ KRİTİK: İki mod da denendi ama içerik üretilemedi.")
        print("Olası sebepler: Jikan API çökmüş olabilir veya GROQ_KEY yanlış.")
