# bot.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from PIL import Image, ImageOps
import pytesseract

KAT_KODLARI = {
    "1": "80",
    "bodrum": "81",
    "zemin": "82"
}

SEANS_KODLARI = {
    "08:30 - 13:50": "08%3A30+-+13%3A50",
    "14:00 - 19:50": "14%3A00+-+19%3A50",
    "20:00 - 23:50": "20%3A00+-+23%3A50"
}

def rezervasyon_yap(kullanici):
    print(f"\n🚀 {kullanici['tc']} için rezervasyon başlatılıyor...")

    kat_kodu = KAT_KODLARI.get(kullanici["kat"])
    seans_kodu = SEANS_KODLARI.get(kullanici["seans"])
    rezervasyon_url = f"https://kutuphane.umraniye.bel.tr/rezervasyon/?p=1&dil=0&salon={kat_kodu}&seans={seans_kodu}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://kutuphane.umraniye.bel.tr/rezervasyon/?p=2&dil=0&islem=giris")
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.okudum"))).click()
        except: pass

        wait.until(EC.presence_of_element_located((By.NAME, "kullanici"))).send_keys(kullanici["tc"])
        driver.find_element(By.NAME, "sifre").send_keys(kullanici["sifre"])

        for deneme in range(1, 6):
            print(f"🔁 CAPTCHA denemesi {deneme}...")

            captcha_element = driver.find_element(By.CLASS_NAME, "captcha")
            captcha_element.screenshot("captcha.png")

            img = Image.open("captcha.png")
            gray = ImageOps.grayscale(img)
            inverted = ImageOps.invert(gray)
            captcha_code = pytesseract.image_to_string(inverted, config="--psm 8 -c tessedit_char_whitelist=0123456789").strip()
            print("🧩 CAPTCHA çözüldü:", captcha_code)

            driver.find_element(By.NAME, "code_girisForm").clear()
            driver.find_element(By.NAME, "code_girisForm").send_keys(captcha_code)
            driver.find_element(By.XPATH, '//button[contains(text(), "Giriş Yap")]').click()
            time.sleep(2)

            try:
                kapat_buton = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "kapat") and contains(text(), "Kapat")]'))
                )
                kapat_buton.click()
                print("❌ CAPTCHA hatalı, tekrar deneniyor...")
                time.sleep(1)
            except:
                print("✅ Giriş başarılı!")
                break
        else:
            print("❌ CAPTCHA 5 kez yanlış. Kullanıcı atlandı.")
            return

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Tamam')]"))).click()
        except: pass

        driver.get(rezervasyon_url)
        print("✅ Rezervasyon sayfasına gidildi.")

        try:
            tarih_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "tarih")))
            mevcut_tarihler = [opt.get_attribute("value") for opt in tarih_dropdown.find_elements(By.TAG_NAME, "option")]

            if kullanici["tarih"] not in mevcut_tarihler:
                driver.execute_script(f'''
                    var select = document.getElementsByName('tarih')[0];
                    var opt = document.createElement('option');
                    opt.value = "{kullanici["tarih"]}";
                    opt.text = "{kullanici["tarih"]} (manuel)";
                    select.appendChild(opt);
                ''')
                print(f"🆕 Tarih eklendi: {kullanici['tarih']}")

            Select(tarih_dropdown).select_by_value(kullanici["tarih"])
            print(f"📅 Tarih seçildi: {kullanici['tarih']}")
            time.sleep(3)
        except Exception as e:
            print("❌ Tarih seçme hatası:", e)

        try:
            sandalye = wait.until(EC.element_to_be_clickable((
                By.XPATH, f"//span[contains(@class, 'sandalye') and text()='{kullanici['sandalye']}']")))
            sandalye.click()
            print(f"💺 {kullanici['sandalye']} numaralı sandalye seçildi.")
        except Exception as e:
            print("❌ Sandalye seçme hatası:", e)

        try:
            evet_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "evet")))
            evet_btn.click()
            print("🎉 Rezervasyon tamamlandı!")
        except Exception as e:
            print("❌ EVET butonu hatası:", e)

    finally:
        time.sleep(5)
        driver.quit()
