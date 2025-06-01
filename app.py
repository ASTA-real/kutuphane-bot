import customtkinter as ctk
import json
import os
from tkinter import messagebox
from bot import rezervasyon_yap
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

KATLAR = ["1", "zemin", "bodrum"]
SEANSLAR = [
    "08:30 - 13:50",
    "14:00 - 19:50",
    "20:00 - 23:50"
]

class KullaniciYonetimApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Rezarvasyon Katili")
        self.geometry("650x550")

        self.kullanicilar = []
        self.secilen_kullanicilar = set()
        self.tarih_index = 0

        self.dosya_yolu = "kullanicilar.json"
        self.kullanicilari_yukle()

        self.kullanici_listbox = ctk.CTkScrollableFrame(self, width=430, height=300)
        self.kullanici_listbox.grid(row=0, column=0, rowspan=6, padx=10, pady=10)

        self.checkboxlar = []
        self.checkbox_guncelle()

        # Giriş alanları
        self.entry_isim = ctk.CTkEntry(self, placeholder_text="İsim")
        self.entry_isim.grid(row=0, column=1, padx=10, pady=5)

        self.entry_tc = ctk.CTkEntry(self, placeholder_text="Tc")
        self.entry_tc.grid(row=1, column=1, padx=10, pady=5)

        self.entry_sifre = ctk.CTkEntry(self, placeholder_text="Şifre", show="*")
        self.entry_sifre.grid(row=2, column=1, padx=10, pady=5)

        self.optionmenu_kat = ctk.CTkOptionMenu(self, values=KATLAR)
        self.optionmenu_kat.set("Kat Seç")
        self.optionmenu_kat.grid(row=3, column=1, padx=10, pady=5)

        self.optionmenu_seans = ctk.CTkOptionMenu(self, values=SEANSLAR)
        self.optionmenu_seans.set("Seans Seç")
        self.optionmenu_seans.grid(row=4, column=1, padx=10, pady=5)

        self.optionmenu_tarih = ctk.CTkOptionMenu(self, values=self.bugunun_sonraki_gunleri())
        self.optionmenu_tarih.set("Tarih Seç")
        self.optionmenu_tarih.grid(row=5, column=1, padx=10, pady=5)

        self.tarih_navigasyon = ctk.CTkFrame(self)
        self.tarih_navigasyon.grid(row=5, column=0, padx=10, pady=5)

        self.btn_onceki_hafta = ctk.CTkButton(self.tarih_navigasyon, text="←", width=30, command=self.onceki_hafta)
        self.btn_onceki_hafta.pack(side="left", padx=5)

        self.btn_sonraki_hafta = ctk.CTkButton(self.tarih_navigasyon, text="→", width=30, command=self.sonraki_hafta)
        self.btn_sonraki_hafta.pack(side="left", padx=5)

        self.entry_sandalye = ctk.CTkEntry(self, placeholder_text="Sandalye")
        self.entry_sandalye.grid(row=6, column=1, padx=10, pady=5)

        self.optionmenu_toplu_tarih = ctk.CTkOptionMenu(self, values=self.bugunun_sonraki_gunleri())
        self.optionmenu_toplu_tarih.set("Tarih Seç")
        self.optionmenu_toplu_tarih.grid(row=7, column=0, padx=10, pady=5)

        self.btn_toplu_tarih = ctk.CTkButton(self, text="Toplu Tarih Güncelle", command=self.toplu_tarih_guncelle)
        self.btn_toplu_tarih.grid(row=7, column=1, padx=10, pady=5)

        self.btn_ekle = ctk.CTkButton(self, text="Ekle", command=self.kullanici_ekle)
        self.btn_ekle.grid(row=8, column=0, padx=10, pady=5)

        self.btn_sil = ctk.CTkButton(self, text="Sil", command=self.kullanici_sil)
        self.btn_sil.grid(row=8, column=1, padx=10, pady=5)

        self.btn_guncelle = ctk.CTkButton(self, text="Güncelle", command=self.kullanici_guncelle)
        self.btn_guncelle.grid(row=9, column=0, padx=10, pady=5)

        self.btn_baslat = ctk.CTkButton(self, text="Botu Başlat", command=self.bot_baslat)
        self.btn_baslat.grid(row=9, column=1, padx=10, pady=5)

    def bugunun_sonraki_gunleri(self, n=7):
        baslangic = datetime.today() + timedelta(days=self.tarih_index * 7)
        return [(baslangic + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n)]

    def onceki_hafta(self):
        self.tarih_index -= 1
        self.tarih_seceneklerini_guncelle()

    def sonraki_hafta(self):
        self.tarih_index += 1
        self.tarih_seceneklerini_guncelle()

    def tarih_seceneklerini_guncelle(self):
        yeni_tarihler = self.bugunun_sonraki_gunleri()
        self.optionmenu_tarih.configure(values=yeni_tarihler)
        self.optionmenu_toplu_tarih.configure(values=yeni_tarihler)
        self.optionmenu_tarih.set("Tarih Seç")
        self.optionmenu_toplu_tarih.set("Tarih Seç")

    def checkbox_guncelle(self):
        for cb in self.checkboxlar:
            cb.destroy()
        self.checkboxlar = []
        self.checkbox_vars = []

        for i, kullanici in enumerate(self.kullanicilar):
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(
                self.kullanici_listbox,
                text=f"{i+1}) {kullanici.get('isim', '')} - {kullanici['tc']} - {kullanici['kat']} - {kullanici['seans']} - {kullanici['tarih']} - {kullanici['sandalye']}",
                variable=var
            )
            cb.pack(anchor="w")
            self.checkboxlar.append(cb)
            self.checkbox_vars.append(var)

    def kullanicilari_yukle(self):
        if os.path.exists(self.dosya_yolu):
            with open(self.dosya_yolu, "r") as f:
                self.kullanicilar = json.load(f)

    def kullanicilari_kaydet(self):
        with open(self.dosya_yolu, "w") as f:
            json.dump(self.kullanicilar, f, indent=2)

    def kullanici_ekle(self):
        yeni = {
            "isim": self.entry_isim.get(),
            "tc": self.entry_tc.get(),
            "sifre": self.entry_sifre.get(),
            "kat": self.optionmenu_kat.get(),
            "seans": self.optionmenu_seans.get(),
            "tarih": self.optionmenu_tarih.get(),
            "sandalye": self.entry_sandalye.get()
        }
        self.kullanicilar.append(yeni)
        self.kullanicilari_kaydet()
        self.checkbox_guncelle()

    def kullanici_sil(self):
        secilenler = [i for i, var in enumerate(self.checkbox_vars) if var.get()]
        for i in sorted(secilenler, reverse=True):
            del self.kullanicilar[i]
        self.kullanicilari_kaydet()
        self.checkbox_guncelle()

    def kullanici_guncelle(self):
        secilenler = [i for i, var in enumerate(self.checkbox_vars) if var.get()]
        if not secilenler:
            messagebox.showinfo("Uyarı", "Güncellenecek kullanıcı seçilmedi.")
            return

        i = secilenler[0]
        self.kullanicilar[i] = {
            "isim": self.entry_isim.get(),
            "tc": self.entry_tc.get(),
            "sifre": self.entry_sifre.get(),
            "kat": self.optionmenu_kat.get(),
            "seans": self.optionmenu_seans.get(),
            "tarih": self.optionmenu_tarih.get(),
            "sandalye": self.entry_sandalye.get()
        }
        self.kullanicilari_kaydet()
        self.checkbox_guncelle()

    def toplu_tarih_guncelle(self):
        yeni_tarih = self.optionmenu_toplu_tarih.get()
        for k in self.kullanicilar:
            k["tarih"] = yeni_tarih
        self.kullanicilari_kaydet()
        self.checkbox_guncelle()
        messagebox.showinfo("Başarılı", f"Tüm kullanıcıların tarihi {yeni_tarih} olarak güncellendi.")

    def bot_baslat(self):
        secilenler = [i for i, var in enumerate(self.checkbox_vars) if var.get()]
        if not secilenler:
            messagebox.showinfo("Uyarı", "Botu başlatmak için kullanıcı seçin.")
            return

        for i in secilenler:
            rezervasyon_yap(self.kullanicilar[i])

if __name__ == "__main__":
    app = KullaniciYonetimApp()
    app.mainloop()
