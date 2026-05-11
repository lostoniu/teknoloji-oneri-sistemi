import os
import re
import pandas as pd


TEKNOLOJI_DATASET = "teknoloji_urunleri_dataset.csv"
PC_PARTS_DATASET = "pc_parts_dataset.csv"


def temizle_yazi(x):
    x = str(x).strip().lower()
    x = x.replace("ı", "i")
    x = x.replace("İ", "i")
    x = x.replace("i̇", "i")
    x = x.replace("ğ", "g")
    x = x.replace("ü", "u")
    x = x.replace("ş", "s")
    x = x.replace("ö", "o")
    x = x.replace("ç", "c")
    return x


def fiyat_sayiya_cevir(fiyat):
    if pd.isna(fiyat):
        return 0

    fiyat = str(fiyat)
    fiyat = fiyat.replace("TL", "")
    fiyat = fiyat.replace("₺", "")
    fiyat = fiyat.replace(".", "")
    fiyat = fiyat.replace(",", "")
    fiyat = fiyat.strip()

    sayilar = "".join([c for c in fiyat if c.isdigit()])

    if sayilar == "":
        return 0

    return int(sayilar)


def ram_sayiya_cevir(ram):
    if pd.isna(ram):
        return 0

    sayilar = re.findall(r"\d+", str(ram))

    if not sayilar:
        return 0

    return max([int(s) for s in sayilar])


def sayi_al(deger):
    if pd.isna(deger):
        return 0

    sayilar = re.findall(r"\d+", str(deger))

    if not sayilar:
        return 0

    return max([int(s) for s in sayilar])


def metin(row, kolon):
    return str(row.get(kolon, "")).lower()


def kullanim_normalize(kullanim):
    k = temizle_yazi(kullanim)

    if "oyun" in k or "gaming" in k:
        return "oyun"

    if "video" in k or "edit" in k or "kurgu" in k:
        return "video_edit"

    if "tasarim" in k or "grafik" in k:
        return "tasarim"

    if "yazilim" in k or "kod" in k or "programlama" in k:
        return "yazilim"

    if "okul" in k or "ogrenci" in k or "ders" in k:
        return "okul"

    if "ofis" in k or "is" in k or "excel" in k or "word" in k:
        return "ofis"

    if "gunluk" in k or "normal" in k or "internet" in k:
        return "gunluk"

    if "spor" in k:
        return "spor"

    if "muzik" in k:
        return "muzik"

    if "kamera" in k or "fotograf" in k:
        return "kamera"

    return k


# =====================================================
# NORMAL TEKNOLOJİ DATASETİ
# =====================================================

def teknoloji_dataset_yukle():
    if not os.path.exists(TEKNOLOJI_DATASET):
        return pd.DataFrame()

    df = pd.read_csv(TEKNOLOJI_DATASET)

    if "Fiyat (TL)" in df.columns:
        df["FIYAT_SAYI"] = df["Fiyat (TL)"].apply(fiyat_sayiya_cevir)
    else:
        df["FIYAT_SAYI"] = 0

    if "RAM" in df.columns:
        df["RAM_SAYI"] = df["RAM"].apply(ram_sayiya_cevir)
    else:
        df["RAM_SAYI"] = 0

    return df


df = teknoloji_dataset_yukle()


def guclu_gpu_var_mi(row):
    gpu = metin(row, "GPU")
    return any(k in gpu for k in ["rtx", "gtx", "radeon rx", "rx", "arc"])


def dahili_gpu_mu(row):
    gpu = metin(row, "GPU")
    model = metin(row, "Model")

    return any(k in gpu for k in [
        "uhd", "iris", "dahili", "integrated", "paylaşımlı"
    ]) or "macbook air" in model


def islemci_guclu_mu(row):
    islemci = metin(row, "İşlemci")
    return any(k in islemci for k in [
        "i7", "i9", "ryzen 7", "ryzen 9", "m2", "m3", "m4"
    ])


def islemci_orta_mu(row):
    islemci = metin(row, "İşlemci")
    return any(k in islemci for k in [
        "i5", "ryzen 5", "m1", "m2"
    ])


def pil_iyi_mi(row):
    pil = str(row.get("Pil Ömrü", "")) + " " + str(row.get("Pil Ömrü (gün)", ""))
    sayilar = re.findall(r"\d+", pil)

    if not sayilar:
        return False

    return max([int(s) for s in sayilar]) >= 8


def ekran_iyi_mi(row):
    ekran = metin(row, "Ekran")
    return any(k in ekran for k in [
        "oled", "retina", "2k", "4k", "ips", "120", "144", "165"
    ])


def ihtiyaca_uygun_mu(row, kategori, kullanim):
    ihtiyac = kullanim_normalize(kullanim)
    kategori = temizle_yazi(kategori)

    model = metin(row, "Model")
    segment = metin(row, "Segment")
    amac = metin(row, "Kullanım Amacı")
    ram = row.get("RAM_SAYI", 0)

    if ihtiyac == "":
        return True

    if kategori == "bilgisayar":

        if ihtiyac == "oyun":
            if "macbook" in model or dahili_gpu_mu(row):
                return False
            return guclu_gpu_var_mi(row) or "oyun" in amac or "gaming" in segment

        if ihtiyac == "video_edit":
            if ram < 16:
                return False
            if dahili_gpu_mu(row) and "macbook pro" not in model:
                return False
            return islemci_guclu_mu(row) or guclu_gpu_var_mi(row)

        if ihtiyac == "tasarim":
            if ram < 16:
                return False
            return ekran_iyi_mi(row) or guclu_gpu_var_mi(row)

        if ihtiyac == "yazilim":
            if ram < 8:
                return False
            return islemci_orta_mu(row) or islemci_guclu_mu(row)

        if ihtiyac in ["okul", "ofis", "gunluk"]:
            if "gaming" in segment or "oyun" in amac:
                return False
            return True

    return True


def urun_puani_hesapla(row, kategori, kullanim):
    puan = 0

    ihtiyac = kullanim_normalize(kullanim)
    kategori = temizle_yazi(kategori)

    segment = metin(row, "Segment")
    amac = metin(row, "Kullanım Amacı")
    gpu = metin(row, "GPU")
    model = metin(row, "Model")
    ram = row.get("RAM_SAYI", 0)

    if ihtiyac and ihtiyac in kullanim_normalize(amac):
        puan += 40

    if kategori == "bilgisayar":

        if ihtiyac == "oyun":
            if guclu_gpu_var_mi(row):
                puan += 80
            if "rtx 4090" in gpu or "rtx 4080" in gpu:
                puan += 60
            elif "rtx 4070" in gpu or "rtx 4060" in gpu:
                puan += 50
            elif "rtx 4050" in gpu or "rtx 3060" in gpu or "rtx 3050" in gpu:
                puan += 40

            if ram >= 32:
                puan += 35
            elif ram >= 16:
                puan += 25

            if islemci_guclu_mu(row):
                puan += 25

            if "macbook" in model or dahili_gpu_mu(row):
                puan -= 100

        elif ihtiyac == "video_edit":
            if ram >= 32:
                puan += 50
            elif ram >= 16:
                puan += 35
            if islemci_guclu_mu(row):
                puan += 40
            if guclu_gpu_var_mi(row):
                puan += 30
            if ekran_iyi_mi(row):
                puan += 25

        elif ihtiyac == "tasarim":
            if ekran_iyi_mi(row):
                puan += 45
            if ram >= 16:
                puan += 30
            if guclu_gpu_var_mi(row):
                puan += 30

        elif ihtiyac == "yazilim":
            if ram >= 32:
                puan += 45
            elif ram >= 16:
                puan += 35
            elif ram >= 8:
                puan += 20
            if islemci_guclu_mu(row):
                puan += 35
            elif islemci_orta_mu(row):
                puan += 25

        elif ihtiyac in ["okul", "ofis", "gunluk"]:
            if pil_iyi_mi(row):
                puan += 40
            if ram >= 8:
                puan += 20
            if "gaming" in segment or "oyun" in amac:
                puan -= 60

    if "üst" in segment or "amiral" in segment:
        puan += 10

    return puan


def urun_oner(kategori, min_butce, max_butce, min_ram, siralama, kullanim=""):
    if df.empty:
        return pd.DataFrame()

    filtre = df[
        (df["Kategori"].astype(str).apply(temizle_yazi) == temizle_yazi(kategori)) &
        (df["FIYAT_SAYI"] >= min_butce) &
        (df["FIYAT_SAYI"] <= max_butce)
    ].copy()

    if temizle_yazi(kategori) in ["bilgisayar", "telefon", "tablet"]:
        filtre = filtre[filtre["RAM_SAYI"] >= min_ram]

    if kullanim:
        filtre = filtre[
            filtre.apply(lambda row: ihtiyaca_uygun_mu(row, kategori, kullanim), axis=1)
        ].copy()

    filtre["ONERI_PUANI"] = filtre.apply(
        lambda row: urun_puani_hesapla(row, kategori, kullanim),
        axis=1
    )

    if "Model" in filtre.columns:
        filtre = filtre.drop_duplicates(subset=["Model"], keep="first")

    if siralama == "Ucuzdan pahalıya":
        filtre = filtre.sort_values(
            by=["ONERI_PUANI", "FIYAT_SAYI"],
            ascending=[False, True]
        )
    else:
        filtre = filtre.sort_values(
            by=["ONERI_PUANI", "FIYAT_SAYI"],
            ascending=[False, False]
        )

    return filtre.head(30)


# =====================================================
# TOPLAMA PC DATASETİ
# =====================================================

def pc_dataset_yukle():
    if not os.path.exists(PC_PARTS_DATASET):
        return pd.DataFrame()

    pc = pd.read_csv(PC_PARTS_DATASET)

    gerekli_kolonlar = [
        "Kategori",
        "Alt_Kategori",
        "Marka",
        "Model",
        "Fiyat_TL",
        "Segment",
        "Kullanim_Amaci",
        "Soket",
        "RAM_Tipi",
        "Watt",
        "Kapasite",
        "Uyumluluk",
        "Puan",
        "Yorum_Sayisi",
        "RGB",
        "Boyut",
        "Cozunurluk",
        "VRAM",
        "Kaynak"
    ]

    for kolon in gerekli_kolonlar:
        if kolon not in pc.columns:
            pc[kolon] = ""

    pc["Fiyat_TL"] = pc["Fiyat_TL"].apply(fiyat_sayiya_cevir)
    pc["Puan"] = pd.to_numeric(pc["Puan"], errors="coerce").fillna(0)
    pc["Yorum_Sayisi"] = pd.to_numeric(pc["Yorum_Sayisi"], errors="coerce").fillna(0)

    return pc


pc_df = pc_dataset_yukle()


def pc_alt_kategorileri_getir():
    if pc_df.empty:
        return ["Dataset bulunamadı"]

    siralama = [
        "İşlemci",
        "Ekran Kartı",
        "Anakart",
        "RAM",
        "SSD",
        "HDD",
        "Güç Kaynağı",
        "Kasa",
        "Soğutucu",
        "Monitör",
        "Klavye",
        "Mouse"
    ]

    mevcut = list(pc_df["Alt_Kategori"].dropna().unique())

    sonuc = []

    for s in siralama:
        for m in mevcut:
            if temizle_yazi(s) == temizle_yazi(m):
                sonuc.append(m)

    for m in mevcut:
        if m not in sonuc:
            sonuc.append(m)

    return sonuc


def pc_parcalari_filtrele(alt_kategori):
    if pc_df.empty:
        return pd.DataFrame()

    filtre = pc_df[
        pc_df["Alt_Kategori"].apply(temizle_yazi) == temizle_yazi(alt_kategori)
    ].copy()

    filtre = filtre.drop_duplicates(
        subset=["Alt_Kategori", "Marka", "Model"],
        keep="first"
    )

    return filtre


def pc_ihtiyac_puani(row, kullanim=""):
    puan = 0
    ihtiyac = kullanim_normalize(kullanim)

    alt = temizle_yazi(row.get("Alt_Kategori", ""))
    segment = temizle_yazi(row.get("Segment", ""))
    amac = temizle_yazi(row.get("Kullanim_Amaci", ""))
    model = temizle_yazi(row.get("Model", ""))
    vram = sayi_al(row.get("VRAM", 0))
    watt = sayi_al(row.get("Watt", 0))
    kapasite = sayi_al(row.get("Kapasite", 0))
    hz = sayi_al(row.get("Cozunurluk", 0))

    puan += float(row.get("Puan", 0)) * 8
    puan += min(float(row.get("Yorum_Sayisi", 0)) / 100, 20)

    if ihtiyac == "oyun":
        if "oyun" in amac or "gaming" in amac:
            puan += 50
        if "ust" in segment or "performans" in segment:
            puan += 35

        if alt == "ekran karti":
            puan += 60
            if vram >= 16:
                puan += 35
            elif vram >= 12:
                puan += 25
            elif vram >= 8:
                puan += 18

        if alt == "monitor" and hz >= 144:
            puan += 25

        if alt in ["klavye", "mouse"]:
            if "gaming" in model or "oyun" in amac:
                puan += 20

    elif ihtiyac in ["video_edit", "tasarim"]:
        if "profesyonel" in amac or "tasarim" in amac or "edit" in amac:
            puan += 50

        if alt == "islemci":
            puan += 35

        if alt == "ram" and kapasite >= 32:
            puan += 35

        if alt == "ssd" and kapasite >= 1000:
            puan += 30

        if alt == "ekran karti" and vram >= 12:
            puan += 25

    elif ihtiyac == "yazilim":
        if alt == "islemci":
            puan += 30
        if alt == "ram" and kapasite >= 32:
            puan += 35
        elif alt == "ram" and kapasite >= 16:
            puan += 25
        if alt == "ssd":
            puan += 25

    else:
        if "orta" in segment:
            puan += 20
        if "giris" in segment:
            puan += 10
        if "fiyat" in segment:
            puan += 20

    if alt == "guc kaynagi" and watt >= 650:
        puan += 20

    return puan


def pc_parca_oner(alt_kategori, min_butce, max_butce, siralama, kullanim=""):
    if pc_df.empty:
        return pd.DataFrame()

    if alt_kategori == "Dataset bulunamadı":
        return pd.DataFrame()

    filtre = pc_df[
        (pc_df["Alt_Kategori"].apply(temizle_yazi) == temizle_yazi(alt_kategori)) &
        (pc_df["Fiyat_TL"] >= min_butce) &
        (pc_df["Fiyat_TL"] <= max_butce)
    ].copy()

    filtre["ONERI_PUANI"] = filtre.apply(
        lambda row: pc_ihtiyac_puani(row, kullanim),
        axis=1
    )

    filtre = filtre.drop_duplicates(
        subset=["Alt_Kategori", "Marka", "Model"],
        keep="first"
    )

    if siralama == "Ucuzdan pahalıya":
        filtre = filtre.sort_values(
            by=["ONERI_PUANI", "Fiyat_TL"],
            ascending=[False, True]
        )
    else:
        filtre = filtre.sort_values(
            by=["ONERI_PUANI", "Fiyat_TL"],
            ascending=[False, False]
        )

    return filtre.head(30)


def soket_bul(row):
    return str(row.get("Soket", "")).strip()


def ram_tipi_bul(row):
    return str(row.get("RAM_Tipi", "")).strip()


def uygun_satir_sec(filtre, hedef_fiyat, kullanim="", ekstra_kosul=None):
    if filtre.empty:
        return None

    secenekler = filtre.copy()

    if ekstra_kosul is not None:
        secenekler = secenekler[secenekler.apply(ekstra_kosul, axis=1)].copy()

    if secenekler.empty:
        return None

    secenekler["ONERI_PUANI"] = secenekler.apply(
        lambda row: pc_ihtiyac_puani(row, kullanim),
        axis=1
    )

    secenekler["HEDEF_FARK"] = (secenekler["Fiyat_TL"] - hedef_fiyat).abs()

    secenekler = secenekler.sort_values(
        by=["ONERI_PUANI", "HEDEF_FARK", "Fiyat_TL"],
        ascending=[False, True, True]
    )

    return secenekler.iloc[0]


def sistem_butce_oranlari(kullanim):
    ihtiyac = kullanim_normalize(kullanim)

    if ihtiyac == "oyun":
        return {
            "İşlemci": 0.16,
            "Ekran Kartı": 0.34,
            "Anakart": 0.09,
            "RAM": 0.08,
            "SSD": 0.07,
            "Güç Kaynağı": 0.07,
            "Kasa": 0.05,
            "Soğutucu": 0.04,
            "Monitör": 0.12,
            "Klavye": 0.03,
            "Mouse": 0.03,
        }

    if ihtiyac in ["video_edit", "tasarim"]:
        return {
            "İşlemci": 0.22,
            "Ekran Kartı": 0.25,
            "Anakart": 0.09,
            "RAM": 0.11,
            "SSD": 0.10,
            "Güç Kaynağı": 0.07,
            "Kasa": 0.05,
            "Soğutucu": 0.05,
            "Monitör": 0.13,
            "Klavye": 0.02,
            "Mouse": 0.02,
        }

    return {
        "İşlemci": 0.20,
        "Ekran Kartı": 0.20,
        "Anakart": 0.10,
        "RAM": 0.10,
        "SSD": 0.09,
        "Güç Kaynağı": 0.08,
        "Kasa": 0.07,
        "Soğutucu": 0.05,
        "Monitör": 0.13,
        "Klavye": 0.04,
        "Mouse": 0.04,
    }


def parca_adi_bul(istenen):
    for alt in pc_alt_kategorileri_getir():
        if temizle_yazi(alt) == temizle_yazi(istenen):
            return alt
    return istenen


def secilecek_parca_listesi(max_butce):
    if max_butce < 35000:
        return [
            "İşlemci",
            "Ekran Kartı",
            "Anakart",
            "RAM",
            "SSD",
            "Güç Kaynağı",
            "Kasa",
            "Soğutucu",
        ]

    return [
        "İşlemci",
        "Ekran Kartı",
        "Anakart",
        "RAM",
        "SSD",
        "Güç Kaynağı",
        "Kasa",
        "Soğutucu",
        "Monitör",
        "Klavye",
        "Mouse",
    ]


def pc_sistem_topla(max_butce, kullanim="", min_butce=0):
    if pc_df.empty:
        return {
            "basarili": False,
            "mesaj": "pc_parts_dataset.csv bulunamadı. Dosyayı app.py ile aynı klasöre koy."
        }

    max_butce = int(max_butce)
    min_butce = int(min_butce)

    if max_butce <= 0:
        return {
            "basarili": False,
            "mesaj": "Geçerli bir bütçe girilmedi."
        }

    oranlar = sistem_butce_oranlari(kullanim)
    parca_listesi = secilecek_parca_listesi(max_butce)

    parcalar = {}

    islemci_adi = parca_adi_bul("İşlemci")
    anakart_adi = parca_adi_bul("Anakart")
    ram_adi = parca_adi_bul("RAM")

    islemciler = pc_parcalari_filtrele(islemci_adi)

    if islemciler.empty:
        return {
            "basarili": False,
            "mesaj": "CSV içinde İşlemci kategorisi bulunamadı. Alt_Kategori sütununda İşlemci yazmalı."
        }

    cpu = uygun_satir_sec(
        islemciler,
        max_butce * oranlar.get("İşlemci", 0.18),
        kullanim
    )

    if cpu is None:
        return {
            "basarili": False,
            "mesaj": "Uygun işlemci bulunamadı."
        }

    parcalar["İşlemci"] = cpu
    cpu_soket = soket_bul(cpu)

    anakartlar = pc_parcalari_filtrele(anakart_adi)

    def anakart_kosul(row):
        anakart_soket = soket_bul(row)
        if cpu_soket == "" or cpu_soket.lower() == "nan":
            return True
        return temizle_yazi(anakart_soket) == temizle_yazi(cpu_soket)

    anakart = uygun_satir_sec(
        anakartlar,
        max_butce * oranlar.get("Anakart", 0.10),
        kullanim,
        anakart_kosul
    )

    if anakart is None:
        anakart = uygun_satir_sec(
            anakartlar,
            max_butce * oranlar.get("Anakart", 0.10),
            kullanim
        )

    if anakart is None:
        return {
            "basarili": False,
            "mesaj": "Uygun anakart bulunamadı."
        }

    parcalar["Anakart"] = anakart

    sistem_soket = soket_bul(anakart)
    sistem_ram_tipi = ram_tipi_bul(anakart)

    ramler = pc_parcalari_filtrele(ram_adi)

    def ram_kosul(row):
        ram_tipi = ram_tipi_bul(row)
        if sistem_ram_tipi == "" or sistem_ram_tipi.lower() == "nan":
            return True
        return temizle_yazi(ram_tipi) == temizle_yazi(sistem_ram_tipi)

    ram = uygun_satir_sec(
        ramler,
        max_butce * oranlar.get("RAM", 0.09),
        kullanim,
        ram_kosul
    )

    if ram is None:
        ram = uygun_satir_sec(
            ramler,
            max_butce * oranlar.get("RAM", 0.09),
            kullanim
        )

    if ram is None:
        return {
            "basarili": False,
            "mesaj": "Uygun RAM bulunamadı."
        }

    parcalar["RAM"] = ram

    for parca in parca_listesi:
        if parca in ["İşlemci", "Anakart", "RAM"]:
            continue

        gercek_ad = parca_adi_bul(parca)
        filtre = pc_parcalari_filtrele(gercek_ad)

        if filtre.empty:
            continue

        ekstra_kosul = None

        if parca == "Güç Kaynağı":
            def psu_kosul(row):
                watt = sayi_al(row.get("Watt", 0))
                if kullanim_normalize(kullanim) == "oyun":
                    return watt >= 650
                return watt >= 500

            ekstra_kosul = psu_kosul

        if parca == "SSD":
            def ssd_kosul(row):
                kapasite = sayi_al(row.get("Kapasite", 0))
                return kapasite >= 500

            ekstra_kosul = ssd_kosul

        secilen = uygun_satir_sec(
            filtre,
            max_butce * oranlar.get(parca, 0.08),
            kullanim,
            ekstra_kosul
        )

        if secilen is not None:
            parcalar[parca] = secilen

    toplam = sum([int(row["Fiyat_TL"]) for row in parcalar.values()])

    deneme = 0

    while toplam > max_butce and deneme < 30:
        deneme += 1

        pahali_parca = max(
            parcalar,
            key=lambda k: int(parcalar[k]["Fiyat_TL"])
        )

        mevcut = parcalar[pahali_parca]
        filtre = pc_parcalari_filtrele(parca_adi_bul(pahali_parca))

        daha_ucuz = filtre[
            filtre["Fiyat_TL"] < int(mevcut["Fiyat_TL"])
        ].copy()

        if pahali_parca == "Anakart" and sistem_soket:
            daha_ucuz = daha_ucuz[
                daha_ucuz["Soket"].apply(temizle_yazi) == temizle_yazi(sistem_soket)
            ]

        if pahali_parca == "RAM" and sistem_ram_tipi:
            daha_ucuz = daha_ucuz[
                daha_ucuz["RAM_Tipi"].apply(temizle_yazi) == temizle_yazi(sistem_ram_tipi)
            ]

        if daha_ucuz.empty:
            break

        daha_ucuz["ONERI_PUANI"] = daha_ucuz.apply(
            lambda row: pc_ihtiyac_puani(row, kullanim),
            axis=1
        )

        daha_ucuz = daha_ucuz.sort_values(
            by=["ONERI_PUANI", "Fiyat_TL"],
            ascending=[False, False]
        )

        parcalar[pahali_parca] = daha_ucuz.iloc[0]

        toplam = sum([int(row["Fiyat_TL"]) for row in parcalar.values()])

    if toplam > max_butce:
        return {
            "basarili": False,
            "mesaj": f"Bu bütçeyle sistem oluşturulamadı. En yakın sistem {toplam} TL tuttu.",
            "toplam_fiyat": toplam,
            "butce": max_butce,
            "parcalar": parcalar,
        }

    return {
        "basarili": True,
        "toplam_fiyat": toplam,
        "butce": max_butce,
        "kullanim": kullanim,
        "parcalar": parcalar,
        "soket": sistem_soket,
        "ram_tipi": sistem_ram_tipi,
        "monitor_dahil": "Monitör" in parcalar,
        "cevre_birimleri_dahil": "Klavye" in parcalar and "Mouse" in parcalar,
    }


def pc_sistem_aciklama_uret(build):
    if not build or not build.get("basarili", False):
        return "Sistem oluşturulamadı."

    toplam = build.get("toplam_fiyat", 0)
    butce = build.get("butce", 0)
    kullanim = kullanim_normalize(build.get("kullanim", ""))

    aciklama = []

    aciklama.append(
        f"Sistem toplam {toplam} TL tutuyor ve {butce} TL bütçeyi aşmıyor."
    )

    soket = build.get("soket", "")
    ram_tipi = build.get("ram_tipi", "")

    if soket:
        aciklama.append(f"İşlemci ve anakart {soket} soketine göre uyumlu seçildi.")

    if ram_tipi:
        aciklama.append(f"RAM, anakart ile uyumlu olacak şekilde {ram_tipi} seçildi.")

    if kullanim == "oyun":
        aciklama.append("Oyun için ekran kartına daha fazla bütçe ayrıldı.")

    elif kullanim in ["video_edit", "tasarim"]:
        aciklama.append("Tasarım/video edit için işlemci, RAM, SSD ve ekran kartı dengeli seçildi.")

    elif kullanim == "yazilim":
        aciklama.append("Yazılım için işlemci, RAM ve SSD önceliklendirildi.")

    else:
        aciklama.append("Genel kullanım için fiyat/performans dengesi gözetildi.")

    if build.get("monitor_dahil", False):
        aciklama.append("Bütçe yeterli olduğu için monitör de dahil edildi.")
    else:
        aciklama.append("Bütçe düşük olduğu için kasa içi temel parçalar seçildi.")

    return " ".join(aciklama)


# =====================================================
# CHATBOT ANALİZ
# =====================================================

def chatbot_metnini_anla(metin):
    metin_kucuk = temizle_yazi(metin)

    kategori = None
    min_butce = 0
    max_butce = 30000
    min_ram = 0
    kullanim = ""

    if "toplama" in metin_kucuk or "parca" in metin_kucuk or "masaustu" in metin_kucuk:
        kategori = "Toplama Bilgisayar"
    elif "telefon" in metin_kucuk:
        kategori = "Telefon"
    elif "bilgisayar" in metin_kucuk or "laptop" in metin_kucuk:
        kategori = "Bilgisayar"
    elif "tablet" in metin_kucuk:
        kategori = "Tablet"
    elif "kulaklik" in metin_kucuk:
        kategori = "Kulaklık"
    elif "saat" in metin_kucuk or "bileklik" in metin_kucuk:
        kategori = "Akıllı Saat / Bileklik"

    if "oyun" in metin_kucuk or "gaming" in metin_kucuk:
        kullanim = "Oyun"
    elif "video" in metin_kucuk or "edit" in metin_kucuk:
        kullanim = "Video Edit"
    elif "yazilim" in metin_kucuk or "kod" in metin_kucuk:
        kullanim = "Yazılım"
    elif "tasarim" in metin_kucuk or "grafik" in metin_kucuk:
        kullanim = "Tasarım"
    elif "okul" in metin_kucuk or "ogrenci" in metin_kucuk:
        kullanim = "Okul"
    elif "ofis" in metin_kucuk:
        kullanim = "Ofis"
    elif "gunluk" in metin_kucuk:
        kullanim = "Günlük"

    aralik = re.search(
        r"(\d[\d\.\,]*)\s*(bin|tl|₺|lira)?\s*[-–]\s*(\d[\d\.\,]*)\s*(bin|tl|₺|lira)?",
        metin_kucuk
    )

    if aralik:
        s1 = aralik.group(1).replace(".", "").replace(",", "")
        s2 = aralik.group(3).replace(".", "").replace(",", "")

        min_butce = int(s1)
        max_butce = int(s2)

        if aralik.group(2) == "bin" and min_butce < 1000:
            min_butce *= 1000

        if aralik.group(4) == "bin" and max_butce < 1000:
            max_butce *= 1000

    else:
        butce_eslesme = re.search(r"(\d[\d\.\,]*)\s*(tl|₺|lira|bin)", metin_kucuk)

        if butce_eslesme:
            sayi = int(butce_eslesme.group(1).replace(".", "").replace(",", ""))

            if "bin" in butce_eslesme.group(2) and sayi < 1000:
                sayi *= 1000

            max_butce = sayi

    ram_eslesme = re.search(r"(\d+)\s*(gb)?\s*ram", metin_kucuk)

    if ram_eslesme:
        min_ram = int(ram_eslesme.group(1))

    if kategori is None:
        kategori = "Telefon"

    return kategori, min_butce, max_butce, min_ram, kullanim


def aciklama_uret(row, kategori, min_butce, max_butce, min_ram):
    aciklamalar = []

    fiyat = row.get("FIYAT_SAYI", 0)

    if min_butce <= fiyat <= max_butce:
        aciklamalar.append("belirlenen fiyat aralığına uygun")

    if temizle_yazi(kategori) in ["bilgisayar", "telefon", "tablet"]:
        ram = row.get("RAM_SAYI", 0)

        if ram >= min_ram:
            aciklamalar.append(f"{ram} GB RAM ihtiyacını karşılıyor")

    puan = row.get("ONERI_PUANI", 0)

    if puan > 0:
        aciklamalar.append(f"kullanıcı ihtiyacına göre {puan} puan aldı")

    if len(aciklamalar) == 0:
        return "Bu ürün kriterlere yakın olduğu için önerildi."

    return "Bu ürün " + ", ".join(aciklamalar) + " olduğu için önerildi."