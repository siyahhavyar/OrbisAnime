import os
import requests
import random
import time
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API

# ==========================================
# AYARLAR (GITHUB SECRETS)
# ==========================================
API_KEY       = os.environ.get("API_KEY")
API_SECRET    = os.environ.get("API_SECRET")
ACCESS_TOKEN  = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")
GROQ_KEY      = os.environ.get("GROQ_KEY")

# ==========================================
# YARDIMCI: RESİM İYİLEŞTİRME
# ==========================================
def enhance_image(img_path):
    try:
        img = Image.open(img_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        output_name = "orbis_hd.jpg"
        img.save(output_name, quality=95)
        return output_name
    except: return img_path

# ==========================================
# YARDIMCI: GROQ AI
# ==========================================
def ask_groq(prompt):
    if not GROQ_KEY: return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(url, headers=headers, json=data, timeout=30)
        return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else None
    except: return None

# ==========================================
# MOD: ANİME SEÇİCİ (BASİTLEŞTİRİLMİŞ)
# ==========================================
def get_content():
    try:
        # Rastgele bir anime çek
        page = random.randint(1, 10)
        resp = requests.get(f"https://api.jikan.moe/v4/top/anime?page={page}", timeout=20)
        item = random.choice(resp.json()['data'])
        
        name = item['title_english'] or item['title']
        img_url = item['images']['jpg']['large_image_url']
        synopsis = item.get('synopsis', 'No info')[:500]
        
        prompt = f"""
        Act as 'Orbis Anime'. Write a short, hype tweet for: {name}.
        Use emojis. Add hashtags #{name.replace(' ','')} #Anime.
        """
        caption = ask_groq(prompt)
        return name, img_url, caption
    except Exception as e:
        print(f"İçerik hatası: {e}")
        return None, None, None

# ==========================================
# ANA İŞLEM
# ==========================================
if __name__ == "__main__":
    print("🚀 ORBIS BAŞLIYOR (V1.1 MODU)...")
    
    # 1. İçerik Hazırla
    name, img_url, caption = get_content()
    
    if name and caption:
        print(f"✅ İçerik: {name}")
        
        # 2. Resmi İndir
        with open("temp.jpg", "wb") as f:
            f.write(requests.get(img_url).content)
        final_img = enhance_image("temp.jpg")
        
        # 3. Twitter'a Bağlan ve Paylaş
        try:
            auth = OAuthHandler(API_KEY, API_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
            api = API(auth)
            
            print("📤 Resim yükleniyor (V1.1)...")
            media = api.media_upload(filename=final_img)
            print("✅ Resim yüklendi!")
            
            print("🐦 Tweet atılıyor (V1.1 update_status)...")
            # BURASI DEĞİŞTİ: Client yerine API kullanıyoruz
            api.update_status(status=caption, media_ids=[media.media_id])
            
            print("🎉 TWEET BAŞARIYLA ATILDI! (Sonunda)")
            
        except Exception as e:
            print(f"\n❌ HATA: {e}")
            if "403" in str(e):
                print("⚠️ HATA NOTU: Eğer yine 403 alıyorsan, GitHub'daki şifrelerin gerçekten güncellenip güncellenmediğini kontrol etmemiz lazım.")
                # Şifrenin doğru yüklendiğini (göstermeden) test edelim
                print(f"Debug: API_KEY yüklenmiş mi? {'EVET' if API_KEY else 'HAYIR'}")
                print(f"Debug: ACCESS_TOKEN yüklenmiş mi? {'EVET' if ACCESS_TOKEN else 'HAYIR'}")
    else:
        print("⚠️ İçerik üretilemedi.")
