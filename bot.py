import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
import datetime
import os

# Ana pencereyi oluştur
root = tk.Tk()
root.title("YOLUNU YORDAMINI V2")  # Başlık
root.geometry("800x600")  # Pencere boyutu
root.configure(bg='black')  # Arkaplan rengi

# Başlık etiketi
header_label = tk.Label(root, text="YOLUNU YORDAMINI V2", font=("Courier", 30), fg="purple", bg="black")
header_label.pack(pady=50)

# Kullanıcı adı
username_label = tk.Label(root, text="Kullanıcı Adı (T.C. Kimlik No vs.):", font=("Courier", 14), fg="green", bg="black")
username_label.pack(pady=10)
username_entry = tk.Entry(root, font=("Courier", 14), fg="green", bg="black", insertbackground="green")
username_entry.pack(pady=5)

# Şifre
password_label = tk.Label(root, text="Şifre:", font=("Courier", 14), fg="green", bg="black")
password_label.pack(pady=10)
password_entry = tk.Entry(root, font=("Courier", 14), fg="green", bg="black", show="*", insertbackground="green")
password_entry.pack(pady=5)

# Gün
day_label = tk.Label(root, text="Gün (örn: 29 Nisan 2025 Salı):", font=("Courier", 14), fg="green", bg="black")
day_label.pack(pady=10)
day_entry = tk.Entry(root, font=("Courier", 14), fg="green", bg="black", insertbackground="green")
day_entry.pack(pady=5)

# Seans
session_label = tk.Label(root, text="Seans (örn: 08:30 - 13:50):", font=("Courier", 14), fg="green", bg="black")
session_label.pack(pady=10)
session_entry = tk.Entry(root, font=("Courier", 14), fg="green", bg="black", insertbackground="green")
session_entry.pack(pady=5)

# Sandalye No
seat_label = tk.Label(root, text="Sandalye No:", font=("Courier", 14), fg="green", bg="black")
seat_label.pack(pady=10)
seat_entry = tk.Entry(root, font=("Courier", 14), fg="green", bg="black", insertbackground="green")
seat_entry.pack(pady=5)

# İşlem butonu
def submit_form():
    # Kullanıcıdan verileri al
    KULLANICI_ADI = username_entry.get()
    SIFRE = password_entry.get()
    GUN = day_entry.get()
    SEANS = session_entry.get()
    SANDALYE_NO = int(seat_entry.get())

    # WebDriver ayarları (Headless modda)
    options = Options()
    options.add_argument("--headless")  # Tarayıcıyı görünmez yap
    options.add_argument("--window-size=1920,1080")  # Görüntü hatası olmasın
    options.add_argument("--disable-gpu")  # GPU hatası olmasın diye
    options.add_argument("--no-sandbox")  # Bazı sistemlerde sandbox hatası
    options.add_argument("--disable-dev-shm-usage")  # Memory sorunları için

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    # Siteye git
    driver.get("https://kutuphane.umraniye.bel.tr/rezervasyon/?p=2&dil=0&islem=giris")

    # Çerezleri kabul et
    try:
        cerez_onay_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btn.btn-primary.mx-3.okudum")))
        cerez_onay_button.click()
        print("✅ Çerez ve Aydınlatma metnini kabul ettiniz.")
    except Exception as e:
        print("⚠️ Çerez butonunda hata:", e)

    # Kullanıcı adı ve şifre gir
    kullanici_adi_input = wait.until(EC.presence_of_element_located((By.NAME, "kullanici")))
    kullanici_adi_input.send_keys(KULLANICI_ADI)

    sifre_input = driver.find_element(By.NAME, "sifre")
    sifre_input.send_keys(SIFRE)

    # CAPTCHA çözümü
    try:
        captcha_resmi = driver.find_element(By.CLASS_NAME, "captcha")
        captcha_resmi.screenshot("captcha.png")
        print("📷 CAPTCHA kaydedildi: captcha.png dosyasını açıyorum...")
        os.system("start captcha.png")  # Windows'ta aç
    except Exception as e:
        print("❌ CAPTCHA resmi bulunamadı:", e)

    captcha_kodu = input("Ekrandaki CAPTCHA kodunu gir: ")

    captcha_input = driver.find_element(By.NAME, "code_girisForm")
    captcha_input.send_keys(captcha_kodu)

    # Giriş butonuna tıkla
    try:
        btn_giris = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Giriş Yap")]')))
        ActionChains(driver).move_to_element(btn_giris).click().perform()
        print("✅ Giriş yapılıyor...")
    except Exception as e:
        print("❌ Giriş butonunda hata:", e)

    # Modal pencereyi kapat (varsa)
    try:
        modal_kapat = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Tamam')]")))
        modal_kapat.click()
        print("✅ Modal pencere kapatıldı.")
    except:
        print("⚠️ Modal pencere yok, devam ediliyor.")

    # Rezervasyon sekmesine git
    try:
        rezervasyon_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Rezervasyon")))
        rezervasyon_link.click()
        print("✅ Rezervasyon sekmesine geçildi.")
    except Exception as e:
        print("❌ Rezervasyon sekmesine geçerken hata:", e)

    # Kullanıcıdan alınan GUN bilgisini tarih değerine çevirelim
    gun_ilk_parca = GUN.split(' ')[0]  # gün numarası
    ay_isim = GUN.split(' ')[1]        # ay ismi
    yil = GUN.split(' ')[2]            # yıl

    # Türkçe ayları İngilizceye çevir
    aylar = {
        'Ocak': '01',
        'Şubat': '02',
        'Mart': '03',
        'Nisan': '04',
        'Mayıs': '05',
        'Haziran': '06',
        'Temmuz': '07',
        'Ağustos': '08',
        'Eylül': '09',
        'Ekim': '10',
        'Kasım': '11',
        'Aralık': '12'
    }

    ay_numarasi = aylar.get(ay_isim)

    tarih_value = f"{yil}-{ay_numarasi}-{gun_ilk_parca.zfill(2)}"  # örnek: 2025-04-30

    # Şimdi sitede bu tarih var mı kontrol edeceğiz
    try:
        tarih_select_element = wait.until(EC.presence_of_element_located((By.NAME, "tarih")))

        mevcut_tarihler = [option.get_attribute("value") for option in tarih_select_element.find_elements(By.TAG_NAME, "option")]

        if tarih_value not in mevcut_tarihler:
            # Eğer yoksa JavaScript ile yeni bir option ekle
            script = f'''
            var select = document.getElementsByName('tarih')[0];
            var option = document.createElement('option');
            option.value = "{tarih_value}";
            option.text = "{GUN}";
            select.appendChild(option);
            '''
            driver.execute_script(script)
            print(f"✅ {GUN} tarihi dropdown'a eklendi!")
        else:
            print(f"✅ {GUN} zaten dropdown'da mevcut.")
    except Exception as e:
        print(f"❌ Tarih kontrolünde hata: {e}")

    # Kat seçimi
    try:
        kat_select_element = wait.until(EC.element_to_be_clickable((By.NAME, "salon")))
        select_kat = Select(kat_select_element)
        select_kat.select_by_visible_text("ZEMİN KAT [FA]")
        print("✅ Kat seçildi.")
    except Exception as e:
        print("❌ Kat seçerken hata:", e)

    # Tarih seçimi
    try:
        # Tarih dropdown'unu bul
        tarih_select_element = wait.until(EC.element_to_be_clickable((By.NAME, "tarih")))

        # Tarihi ekleyelim
        driver.execute_script('''var option = document.createElement("option");
                                 option.value = "2025-04-30";
                                 option.text = "30 Nisan 2025 Çarşamba";
                                 arguments[0].appendChild(option);''', tarih_select_element)
        print(f"✅ {GUN} tarihi dropdown'a eklendi!")

        # Dropdown'da tarihi seçelim
        select_tarih = Select(tarih_select_element)
        select_tarih.select_by_visible_text(GUN)
        print("✅ Tarih seçildi.")
    except Exception as e:
        print(f"❌ Tarih seçerken hata: {e}")

    # Seans seçimi
    try:
        seans_select_element = wait.until(EC.presence_of_element_located((By.NAME, "seans")))
        select_seans = Select(seans_select_element)
        wait.until(lambda driver: len(select_seans.options) > 1)
        select_seans.select_by_visible_text(SEANS)
        print("✅ Seans seçildi.")
    except Exception as e:
        print("❌ Seans seçerken hata:", e)

    # Sandalye seçimi
    try:
        sandalye = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//span[contains(@class, 'sandalye') and text()='{SANDALYE_NO}']"))
        )
        sandalye.click()
        print(f"✅ {SANDALYE_NO} numaralı sandalye seçildi.")
    except Exception as e:
        print("❌ Sandalye seçerken hata:", e)

    # EVET butonuna tıklama
    try:
        evet_butonu = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "evet")))
        evet_butonu.click()
        print("✅ EVET butonuna tıklandı.")

        print("\n" + "=" * 50)
        print(f"{KULLANICI_ADI} için rezervasyon tamamlandı.")
        print(f"Tarih: {GUN}")
        print(f"Seans: {SEANS}")
        print(f"Sandalye No: {SANDALYE_NO}")
        print("=" * 50)

        messagebox.showinfo("Başarı", f"{KULLANICI_ADI} için rezervasyon başarıyla tamamlandı.")
    except Exception as e:
        print("❌ EVET butonuna tıklarken hata:", e)

    # Bitince tarayıcıyı kapat
    time.sleep(5)
    driver.quit()

# Butona tıklandığında işlemi başlat
submit_button = tk.Button(root, text="Rezervasyonu Tamamla", font=("Courier", 16), bg="purple", fg="green", command=submit_form)
submit_button.pack(pady=50)

# Ana pencereyi çalıştır
root.mainloop()
