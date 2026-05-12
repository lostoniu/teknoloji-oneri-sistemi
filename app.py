import os
import json
import random
import pandas as pd
import streamlit as st
import psycopg2

from recommender import (
    urun_oner,
    chatbot_metnini_anla,
    aciklama_uret,
)

from anything_client import llm_analiz_et, llm_sohbet_et

from auth import (
    register_user,
    verify_user,
    login_user,
    sifre_sifirlama_kodu_gonder,
    sifreyi_guncelle
)


st.set_page_config(
    page_title="Akıllı Teknoloji Ürünleri Öneri Sistemi",
    page_icon="🤖",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 3px solid #9700bd;
}

h1, h2, h3, h4 {
    color: #ffffff !important;
}

p, label, span, div {
    color: #ffffff;
}

.stButton button {
    background-color: #ee8713;
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    padding: 0.6rem 1rem;
}

.stButton button:hover {
    background-color: #ff9f2d;
    color: white;
    border: 1px solid #57a4fb;
}

[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #57a4fb !important;
}

.stTextInput input {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 10px;
    border: 1px solid #57a4fb;
}

.stChatInput textarea {
    background-color: #111827 !important;
    color: white !important;
}

div[data-testid="stAlert"] {
    background-color: #1e293b;
    border-left: 6px solid #ee8713;
    border-radius: 12px;
}

.product-card {
    background-color: #111827;
    border: 2px solid #57a4fb;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
}

.product-title {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
}

.badge-blue {
    background-color: #57a4fb;
    color: #0f172a;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: bold;
}

.badge-purple {
    background-color: #9700bd;
    color: white;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: bold;
}

.badge-orange {
    background-color: #ee8713;
    color: white;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: bold;
}

hr {
    border: 1px solid #9700bd;
}
</style>
""", unsafe_allow_html=True)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )


def safe_json_dumps(data):
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except Exception:
        return "{}"


def favori_ekle(user_id, product_type, product_name, product_data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO favorites (user_id, product_type, product_name, product_data)
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                str(product_type),
                str(product_name),
                safe_json_dumps(product_data)
            )
        )

        conn.commit()
        cur.close()
        conn.close()

        return True, "Ürün favorilere eklendi."

    except Exception as e:
        return False, f"Favori ekleme hatası: {e}"


def favorileri_getir(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT product_name, product_type
            FROM favorites
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 20
            """,
            (user_id,)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    except Exception:
        return []


def sistemi_kaydet(user_id, build_name, build_data, total_price):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO saved_builds (user_id, build_name, build_data, total_price)
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                str(build_name),
                safe_json_dumps(build_data),
                int(float(total_price))
            )
        )

        conn.commit()
        cur.close()
        conn.close()

        return True, "Toplama bilgisayar sistemi kaydedildi."

    except Exception as e:
        return False, f"Sistem kaydetme hatası: {e}"


def kayitli_sistemleri_getir(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT build_name, total_price
            FROM saved_builds
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 20
            """,
            (user_id,)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    except Exception:
        return []


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "sonuc" not in st.session_state:
    st.session_state.sonuc = None

if "pc_build" not in st.session_state:
    st.session_state.pc_build = None

if "pc_builds" not in st.session_state:
    st.session_state.pc_builds = []

if "selected_pc_build_index" not in st.session_state:
    st.session_state.selected_pc_build_index = 0

if "aktif_mod" not in st.session_state:
    st.session_state.aktif_mod = None

if "kategori" not in st.session_state:
    st.session_state.kategori = "Telefon"

if "min_butce" not in st.session_state:
    st.session_state.min_butce = 0

if "max_butce" not in st.session_state:
    st.session_state.max_butce = 30000

if "min_ram" not in st.session_state:
    st.session_state.min_ram = 0

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []

if "pc_random_seed" not in st.session_state:
    st.session_state.pc_random_seed = 1


@st.cache_data
def ev_esyalari_yukle():
    dosya = "elektronik_ev_esyalari_dataset.csv"

    if not os.path.exists(dosya):
        return pd.DataFrame()

    df = pd.read_csv(dosya)

    df["Fiyat_TL"] = pd.to_numeric(df["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
    df["Puan"] = pd.to_numeric(df["Puan"], errors="coerce").fillna(0)
    df["Yorum_Sayisi"] = pd.to_numeric(df["Yorum_Sayisi"], errors="coerce").fillna(0).astype(int)
    df["Garanti_Ay"] = pd.to_numeric(df["Garanti_Ay"], errors="coerce").fillna(0).astype(int)

    return df


@st.cache_data
def pc_dataset_yukle():
    dosya = "pc_parts_dataset.csv"

    if not os.path.exists(dosya):
        return pd.DataFrame()

    df = pd.read_csv(dosya)

    if "Fiyat_TL" in df.columns:
        df["Fiyat_TL"] = pd.to_numeric(df["Fiyat_TL"], errors="coerce").fillna(0).astype(int)

    if "Puan" in df.columns:
        df["Puan"] = pd.to_numeric(df["Puan"], errors="coerce").fillna(0)

    if "Yorum_Sayisi" in df.columns:
        df["Yorum_Sayisi"] = pd.to_numeric(df["Yorum_Sayisi"], errors="coerce").fillna(0).astype(int)

    return df


ev_df = ev_esyalari_yukle()
pc_df = pc_dataset_yukle()


def fiyat_formatla(deger):
    try:
        return f"{int(float(deger)):,}".replace(",", ".") + " TL"
    except Exception:
        return str(deger)


def veri_getir(row, kolon):
    if kolon in row.index and str(row[kolon]) != "nan":
        return row[kolon]
    return "Yok"


def sayisal_filtre_degeri(seri):
    return seri.astype(str).str.extract(r"(\d+)")[0].fillna(0).astype(int)


def sayi_cek(deger):
    try:
        if pd.isna(deger):
            return 0

        bulunan = pd.Series([str(deger)]).str.extract(r"(\d+)")[0].iloc[0]

        if pd.isna(bulunan):
            return 0

        return int(bulunan)

    except Exception:
        return 0


def ev_ana_kategorileri_getir():
    if ev_df.empty:
        return ["Dataset bulunamadı"]

    return sorted(ev_df["Ana_Kategori"].dropna().unique())


def ev_alt_kategorileri_getir():
    if ev_df.empty:
        return ["Dataset bulunamadı"]

    return sorted(ev_df["Alt_Kategori"].dropna().unique())


def siralama_uygula(df, siralama, fiyat_kolon=None, puan_kolon=None, yorum_kolon=None, ram_kolon=None):
    if df is None or df.empty:
        return df

    sonuc = df.copy()

    if siralama == "En Düşük Fiyat":
        if fiyat_kolon and fiyat_kolon in sonuc.columns:
            sonuc = sonuc.sort_values(by=fiyat_kolon, ascending=True)

    elif siralama == "En Yüksek Fiyat":
        if fiyat_kolon and fiyat_kolon in sonuc.columns:
            sonuc = sonuc.sort_values(by=fiyat_kolon, ascending=False)

    elif siralama == "Teknik Puan":
        if puan_kolon and puan_kolon in sonuc.columns:
            sonuc = sonuc.sort_values(by=puan_kolon, ascending=False)

    elif siralama == "Yorum Sayısı":
        if yorum_kolon and yorum_kolon in sonuc.columns:
            sonuc = sonuc.sort_values(by=yorum_kolon, ascending=False)

    elif siralama == "Bellek / RAM":
        if ram_kolon and ram_kolon in sonuc.columns:
            ramlar = sonuc[ram_kolon].astype(str).str.extract(r"(\d+)")[0]
            ramlar = pd.to_numeric(ramlar, errors="coerce").fillna(0).astype(int)
            sonuc = sonuc.assign(_ram_sort=ramlar)
            sonuc = sonuc.sort_values(by="_ram_sort", ascending=False)
            sonuc = sonuc.drop(columns=["_ram_sort"])

    elif siralama == "Akıllı Sıralama":
        if puan_kolon and puan_kolon in sonuc.columns and fiyat_kolon and fiyat_kolon in sonuc.columns:
            fiyat = pd.to_numeric(sonuc[fiyat_kolon], errors="coerce").fillna(0)
            puan = pd.to_numeric(sonuc[puan_kolon], errors="coerce").fillna(0)
            sonuc = sonuc.assign(_akilli=(puan * 1000) - (fiyat / 1000))
            sonuc = sonuc.sort_values(by="_akilli", ascending=False)
            sonuc = sonuc.drop(columns=["_akilli"])

        elif puan_kolon and puan_kolon in sonuc.columns:
            sonuc = sonuc.sort_values(by=puan_kolon, ascending=False)

    elif siralama == "Popülerlik":
        if yorum_kolon and yorum_kolon in sonuc.columns:
            sonuc = sonuc.sort_values(by=yorum_kolon, ascending=False)
        elif puan_kolon and puan_kolon in sonuc.columns:
            sonuc = sonuc.sort_values(by=puan_kolon, ascending=False)

    return sonuc


def pc_parcalari_getir(alt_kategori, min_butce=0, max_butce=250000):
    if pc_df.empty:
        return pd.DataFrame()

    sonuc = pc_df[
        (pc_df["Alt_Kategori"].astype(str) == alt_kategori) &
        (pc_df["Fiyat_TL"] >= min_butce) &
        (pc_df["Fiyat_TL"] <= max_butce)
    ].copy()

    return sonuc


def pc_parca_filtrele(
    alt_kategori,
    min_butce,
    max_butce,
    soket,
    ram_tipi,
    min_vram,
    min_kapasite,
    min_watt,
    rgb,
    siralama
):
    sonuc = pc_parcalari_getir(alt_kategori, min_butce, max_butce)

    if sonuc.empty:
        return sonuc

    if soket != "Farketmez" and "Soket" in sonuc.columns:
        sonuc = sonuc[sonuc["Soket"].astype(str).str.upper() == soket.upper()]

    if ram_tipi != "Farketmez" and "RAM_Tipi" in sonuc.columns:
        sonuc = sonuc[sonuc["RAM_Tipi"].astype(str).str.upper() == ram_tipi.upper()]

    if min_vram != "Farketmez" and "VRAM" in sonuc.columns:
        sonuc = sonuc[sayisal_filtre_degeri(sonuc["VRAM"]) >= int(min_vram)]

    if min_kapasite != "Farketmez" and "Kapasite" in sonuc.columns:
        sonuc = sonuc[sayisal_filtre_degeri(sonuc["Kapasite"]) >= int(min_kapasite)]

    if min_watt != "Farketmez" and "Watt" in sonuc.columns:
        sonuc = sonuc[sayisal_filtre_degeri(sonuc["Watt"]) >= int(min_watt)]

    if rgb != "Farketmez" and "RGB" in sonuc.columns:
        sonuc = sonuc[sonuc["RGB"].astype(str).str.lower() == rgb.lower()]

    sonuc = siralama_uygula(
        sonuc,
        siralama,
        fiyat_kolon="Fiyat_TL",
        puan_kolon="Puan",
        yorum_kolon="Yorum_Sayisi"
    )

    return sonuc.head(50)


def pc_random_sec(df, seed):
    if df is None or df.empty:
        return None

    sonuc = df.copy()

    if "Puan" in sonuc.columns:
        sonuc = sonuc.sort_values(by="Puan", ascending=False)

    havuz = sonuc.head(20)

    if havuz.empty:
        return None

    rnd = random.Random(seed)
    secilen_index = rnd.choice(list(havuz.index))

    return havuz.loc[secilen_index]


def pc_aday_sec(adaylar, hedef_fiyat, seed):
    if adaylar is None or adaylar.empty:
        return None

    sonuc = adaylar.copy()
    sonuc["Fiyat_TL"] = pd.to_numeric(sonuc["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
    sonuc = sonuc[sonuc["Fiyat_TL"] > 0]

    if sonuc.empty:
        return None

    sonuc = sonuc.assign(_fark=(sonuc["Fiyat_TL"] - hedef_fiyat).abs())
    sonuc = sonuc.sort_values(by=["_fark", "Puan"], ascending=[True, False]) if "Puan" in sonuc.columns else sonuc.sort_values(by="_fark")

    havuz = sonuc.head(8)
    rnd = random.Random(seed)
    secilen_index = rnd.choice(list(havuz.index))

    return havuz.loc[secilen_index].drop(labels=["_fark"], errors="ignore")


def tek_pc_sistem_adayi_olustur(min_butce, max_butce, hedef_fiyat, kullanim, seed):
    if pc_df.empty:
        return None

    rnd = random.Random(seed)

    oranlar = {
        "İşlemci": 0.18,
        "Anakart": 0.12,
        "RAM": 0.10,
        "Ekran Kartı": 0.35,
        "SSD": 0.08,
        "Güç Kaynağı": 0.07,
        "Kasa": 0.05,
        "Soğutucu": 0.05
    }

    parcalar = {}

    cpu_hedef = int(hedef_fiyat * oranlar["İşlemci"] * rnd.uniform(0.75, 1.25))
    islemciler = pc_parcalari_getir("İşlemci", 0, max_butce)

    if kullanim and not islemciler.empty and "Kullanim_Amaci" in islemciler.columns:
        filtre = islemciler[
            islemciler["Kullanim_Amaci"].astype(str).str.lower().str.contains(kullanim.lower(), na=False)
        ]
        if not filtre.empty:
            islemciler = filtre

    islemci = pc_aday_sec(islemciler, cpu_hedef, seed + 10)

    if islemci is None:
        return None

    parcalar["İşlemci"] = islemci
    soket = str(islemci.get("Soket", ""))
    ram_tipi = str(islemci.get("RAM_Tipi", ""))

    gpu_hedef = int(hedef_fiyat * oranlar["Ekran Kartı"] * rnd.uniform(0.75, 1.25))
    ekran_kartlari = pc_parcalari_getir("Ekran Kartı", 0, max_butce)

    if kullanim and not ekran_kartlari.empty and "Kullanim_Amaci" in ekran_kartlari.columns:
        filtre = ekran_kartlari[
            ekran_kartlari["Kullanim_Amaci"].astype(str).str.lower().str.contains(kullanim.lower(), na=False)
        ]
        if not filtre.empty:
            ekran_kartlari = filtre

    ekran_karti = pc_aday_sec(ekran_kartlari, gpu_hedef, seed + 20)

    if ekran_karti is None:
        return None

    parcalar["Ekran Kartı"] = ekran_karti

    anakart_hedef = int(hedef_fiyat * oranlar["Anakart"] * rnd.uniform(0.75, 1.25))
    anakartlar = pc_parcalari_getir("Anakart", 0, max_butce)

    if not anakartlar.empty and "Soket" in anakartlar.columns and soket:
        filtre = anakartlar[anakartlar["Soket"].astype(str) == soket]
        if not filtre.empty:
            anakartlar = filtre

    if not anakartlar.empty and "RAM_Tipi" in anakartlar.columns and ram_tipi:
        filtre = anakartlar[anakartlar["RAM_Tipi"].astype(str) == ram_tipi]
        if not filtre.empty:
            anakartlar = filtre

    anakart = pc_aday_sec(anakartlar, anakart_hedef, seed + 30)

    if anakart is None:
        return None

    parcalar["Anakart"] = anakart

    ram_hedef = int(hedef_fiyat * oranlar["RAM"] * rnd.uniform(0.75, 1.25))
    ramler = pc_parcalari_getir("RAM", 0, max_butce)

    if not ramler.empty and "RAM_Tipi" in ramler.columns and ram_tipi:
        filtre = ramler[ramler["RAM_Tipi"].astype(str) == ram_tipi]
        if not filtre.empty:
            ramler = filtre

    ram = pc_aday_sec(ramler, ram_hedef, seed + 40)

    if ram is None:
        return None

    parcalar["RAM"] = ram

    ssd_hedef = int(hedef_fiyat * oranlar["SSD"] * rnd.uniform(0.75, 1.25))
    ssd = pc_aday_sec(pc_parcalari_getir("SSD", 0, max_butce), ssd_hedef, seed + 50)

    if ssd is None:
        return None

    parcalar["SSD"] = ssd

    psu_hedef = int(hedef_fiyat * oranlar["Güç Kaynağı"] * rnd.uniform(0.75, 1.25))
    psular = pc_parcalari_getir("Güç Kaynağı", 0, max_butce)
    min_psu = 500
    gpu_watt = sayi_cek(ekran_karti.get("Watt", 0))

    if gpu_watt > 0:
        min_psu = max(500, gpu_watt + 250)

    if not psular.empty and "Watt" in psular.columns:
        psular = psular[sayisal_filtre_degeri(psular["Watt"]) >= min_psu]

    psu = pc_aday_sec(psular, psu_hedef, seed + 60)

    if psu is None:
        return None

    parcalar["Güç Kaynağı"] = psu

    kasa_hedef = int(hedef_fiyat * oranlar["Kasa"] * rnd.uniform(0.75, 1.25))
    kasa = pc_aday_sec(pc_parcalari_getir("Kasa", 0, max_butce), kasa_hedef, seed + 70)

    if kasa is None:
        return None

    parcalar["Kasa"] = kasa

    sogutucu_hedef = int(hedef_fiyat * oranlar["Soğutucu"] * rnd.uniform(0.75, 1.25))
    sogutucular = pc_parcalari_getir("Soğutucu", 0, max_butce)

    if not sogutucular.empty and "Soket" in sogutucular.columns and soket:
        filtre = sogutucular[sogutucular["Soket"].astype(str).str.contains(soket, na=False)]
        if not filtre.empty:
            sogutucular = filtre

    sogutucu = pc_aday_sec(sogutucular, sogutucu_hedef, seed + 80)

    if sogutucu is None:
        return None

    parcalar["Soğutucu"] = sogutucu

    toplam = sum(int(row.get("Fiyat_TL", 0)) for row in parcalar.values())

    if toplam < min_butce or toplam > max_butce:
        return None

    imza = "|".join([
        str(row.get("Marka", "")) + " " + str(row.get("Model", ""))
        for row in parcalar.values()
    ])

    return {
        "basarili": True,
        "mesaj": "Bütçe aralığına uygun sistem oluşturuldu.",
        "parcalar": parcalar,
        "toplam_fiyat": toplam,
        "min_butce": min_butce,
        "max_butce": max_butce,
        "butce": max_butce,
        "hedef_fiyat": hedef_fiyat,
        "soket": soket,
        "ram_tipi": ram_tipi,
        "imza": imza
    }


def besli_pc_sistem_olustur(min_butce, max_butce, kullanim, seed):
    if pc_df.empty:
        return []

    hedefler = [
        min_butce,
        int(min_butce + ((max_butce - min_butce) * 0.25)),
        int(min_butce + ((max_butce - min_butce) * 0.50)),
        int(min_butce + ((max_butce - min_butce) * 0.75)),
        max_butce
    ]

    adaylar = []
    gorulen_imzalar = set()

    for hedef_index, hedef in enumerate(hedefler):
        for deneme in range(250):
            sistem = tek_pc_sistem_adayi_olustur(
                min_butce=min_butce,
                max_butce=max_butce,
                hedef_fiyat=hedef,
                kullanim=kullanim,
                seed=seed + (hedef_index * 10000) + deneme
            )

            if sistem is None:
                continue

            imza = sistem.get("imza", "")
            if imza in gorulen_imzalar:
                continue

            gorulen_imzalar.add(imza)
            sistem["hedef_index"] = hedef_index
            sistem["hedef_farki"] = abs(int(sistem["toplam_fiyat"]) - int(hedef))
            adaylar.append(sistem)

    secilenler = []
    kullanilan_imzalar = set()

    for hedef_index, hedef in enumerate(hedefler):
        uygunlar = [
            s for s in adaylar
            if s.get("imza") not in kullanilan_imzalar
        ]

        if not uygunlar:
            continue

        uygunlar = sorted(
            uygunlar,
            key=lambda x: abs(int(x["toplam_fiyat"]) - int(hedef))
        )

        secilen = uygunlar[0]
        secilen["isim"] = f"Sistem {hedef_index + 1}"
        secilenler.append(secilen)
        kullanilan_imzalar.add(secilen.get("imza"))

    secilenler = sorted(secilenler, key=lambda x: int(x["toplam_fiyat"]))

    for i, sistem in enumerate(secilenler[:5]):
        sistem["isim"] = f"Sistem {i + 1}"

    return secilenler[:5]


def uyumlu_pc_sistem_topla(max_butce, kullanim, seed):
    sistemler = besli_pc_sistem_olustur(0, max_butce, kullanim, seed)
    if sistemler:
        return sistemler[0]
    return {
        "basarili": False,
        "mesaj": "Bu bütçeye uygun sistem oluşturulamadı.",
        "parcalar": {},
        "toplam_fiyat": 0,
        "butce": max_butce
    }


def ev_esyasi_oner(
    ana_kategori,
    alt_kategori,
    min_butce,
    max_butce,
    siralama,
    kullanim,
    min_puan,
    enerji_sinifi,
    kaynak_site,
    min_watt="Farketmez",
    min_emis="Farketmez",
    min_hazne="Farketmez",
    wifi="Farketmez",
    rgb="Farketmez",
    min_garanti="Farketmez",
    stok="Farketmez"
):
    if ev_df.empty:
        return pd.DataFrame()

    sonuc = ev_df[
        (ev_df["Fiyat_TL"] >= min_butce) &
        (ev_df["Fiyat_TL"] <= max_butce)
    ].copy()

    if ana_kategori != "Tümü":
        sonuc = sonuc[sonuc["Ana_Kategori"].astype(str) == ana_kategori]

    if alt_kategori != "Tümü":
        sonuc = sonuc[sonuc["Alt_Kategori"].astype(str) == alt_kategori]

    if kullanim:
        sonuc = sonuc[
            sonuc["Kullanim_Amaci"].astype(str).str.lower().str.contains(kullanim.lower(), na=False)
            |
            sonuc["Ozellikler"].astype(str).str.lower().str.contains(kullanim.lower(), na=False)
        ]

    if min_puan > 0:
        sonuc = sonuc[sonuc["Puan"] >= min_puan]

    if enerji_sinifi != "Farketmez":
        sonuc = sonuc[sonuc["Enerji_Sinifi"].astype(str) == enerji_sinifi]

    if kaynak_site != "Farketmez":
        sonuc = sonuc[sonuc["Kaynak_Site"].astype(str) == kaynak_site]

    if min_watt != "Farketmez":
        wattlar = sonuc["Ozellikler"].astype(str).str.extract(r"(\d+)\s*W")[0]
        wattlar = pd.to_numeric(wattlar, errors="coerce").fillna(0).astype(int)
        sonuc = sonuc[wattlar >= int(min_watt)]

    if min_emis != "Farketmez":
        emisler = sonuc["Ozellikler"].astype(str).str.extract(r"(\d+)\s*Pa")[0]
        emisler = pd.to_numeric(emisler, errors="coerce").fillna(0).astype(int)
        sonuc = sonuc[emisler >= int(min_emis)]

    if min_hazne != "Farketmez":
        hazneler = sonuc["Ozellikler"].astype(str).str.extract(r"(\d+)\s*L")[0]
        hazneler = pd.to_numeric(hazneler, errors="coerce").fillna(0).astype(int)
        sonuc = sonuc[hazneler >= int(min_hazne)]

    if wifi != "Farketmez":
        if wifi == "Var":
            sonuc = sonuc[
                sonuc["Ozellikler"].astype(str).str.lower().str.contains("wi-fi|wifi", na=False)
            ]
        else:
            sonuc = sonuc[
                ~sonuc["Ozellikler"].astype(str).str.lower().str.contains("wi-fi|wifi", na=False)
            ]

    if rgb != "Farketmez":
        if rgb == "Var":
            sonuc = sonuc[
                sonuc["Ozellikler"].astype(str).str.lower().str.contains("rgb|ışık|isik", na=False)
            ]
        else:
            sonuc = sonuc[
                ~sonuc["Ozellikler"].astype(str).str.lower().str.contains("rgb|ışık|isik", na=False)
            ]

    if min_garanti != "Farketmez":
        sonuc = sonuc[sonuc["Garanti_Ay"] >= int(min_garanti)]

    if stok != "Farketmez":
        sonuc = sonuc[sonuc["Stok_Durumu"].astype(str) == stok]

    sonuc = sonuc.drop_duplicates(subset=["Marka", "Model"], keep="first")

    sonuc = siralama_uygula(
        sonuc,
        siralama,
        fiyat_kolon="Fiyat_TL",
        puan_kolon="Puan",
        yorum_kolon="Yorum_Sayisi"
    )

    return sonuc.head(50)


def auth_screen():
    st.title("🤖 Akıllı Teknoloji Ürünleri Öneri Sistemi")
    st.write("Uygulamayı kullanmak için giriş yapmalı veya kayıt olmalısın.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Giriş Yap",
        "Kayıt Ol",
        "Mail Doğrula",
        "Şifremi Unuttum"
    ])

    with tab1:
        st.subheader("Giriş Yap")

        login_input = st.text_input(
            "Kullanıcı adı / E-posta",
            key="login_input"
        )

        login_password = st.text_input(
            "Şifre",
            type="password",
            key="login_password"
        )

        if st.button("Giriş Yap", key="login_button"):
            if login_input.strip() == "" or login_password.strip() == "":
                st.error("Kullanıcı adı/e-posta ve şifre boş bırakılamaz.")
            else:
                success, message, user = login_user(login_input, login_password)

                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with tab2:
        st.subheader("Kayıt Ol")

        username = st.text_input("Kullanıcı adı", key="register_username")
        email = st.text_input("E-posta", key="register_email")
        password = st.text_input("Şifre", type="password", key="register_password")
        password_again = st.text_input("Şifre tekrar", type="password", key="register_password_again")

        if st.button("Kayıt Ol", key="register_button"):
            if username.strip() == "" or email.strip() == "" or password.strip() == "":
                st.error("Lütfen tüm alanları doldur.")
            elif password != password_again:
                st.error("Şifreler aynı değil.")
            elif "@" not in email or "." not in email:
                st.error("Geçerli bir e-posta adresi gir.")
            else:
                success, message = register_user(username, email, password)

                if success:
                    st.success(message)
                    st.info("Mail Doğrula sekmesinden 5 haneli kodu gir.")
                else:
                    st.error(message)

    with tab3:
        st.subheader("Mail Doğrula")

        email = st.text_input("E-posta", key="verify_email")
        code = st.text_input("5 haneli doğrulama kodu", max_chars=5, key="verify_code")

        if st.button("Doğrula", key="verify_button"):
            if email.strip() == "" or code.strip() == "":
                st.error("E-posta ve doğrulama kodu boş bırakılamaz.")
            elif len(code) != 5:
                st.error("Kod 5 haneli olmalıdır.")
            else:
                success, message = verify_user(email, code)

                if success:
                    st.success(message)
                else:
                    st.error(message)

    with tab4:
        st.subheader("Şifremi Unuttum")

        forgot_email = st.text_input("Kayıtlı e-posta", key="forgot_email")

        if st.button("Şifre Sıfırlama Kodu Gönder", key="forgot_send_button"):
            if forgot_email.strip() == "":
                st.error("E-posta boş bırakılamaz.")
            else:
                success, message = sifre_sifirlama_kodu_gonder(forgot_email)

                if success:
                    st.success(message)
                else:
                    st.error(message)

        reset_code = st.text_input(
            "Mailden gelen 5 haneli kod",
            max_chars=5,
            key="reset_code"
        )

        new_password = st.text_input(
            "Yeni şifre",
            type="password",
            key="new_password"
        )

        new_password_again = st.text_input(
            "Yeni şifre tekrar",
            type="password",
            key="new_password_again"
        )

        if st.button("Şifreyi Güncelle", key="reset_password_button"):
            if forgot_email.strip() == "" or reset_code.strip() == "" or new_password.strip() == "":
                st.error("Tüm alanları doldur.")
            elif len(reset_code) != 5:
                st.error("Kod 5 haneli olmalıdır.")
            elif new_password != new_password_again:
                st.error("Yeni şifreler aynı değil.")
            else:
                success, message = sifreyi_guncelle(
                    forgot_email,
                    reset_code,
                    new_password
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)


def pc_parca_karti(row):
    st.markdown(f"""
<div class="product-card">
<div class="product-title">🧩 {veri_getir(row, 'Marka')} {veri_getir(row, 'Model')}</div><br>
<span class="badge-orange">💰 {fiyat_formatla(veri_getir(row, 'Fiyat_TL'))}</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Alt_Kategori')}</span>
<span class="badge-purple">⭐ {veri_getir(row, 'Puan')}</span>
<br><br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanim_Amaci')}<br>
🔌 <b>Soket:</b> {veri_getir(row, 'Soket')}<br>
🧠 <b>RAM Tipi:</b> {veri_getir(row, 'RAM_Tipi')}<br>
⚡ <b>Watt:</b> {veri_getir(row, 'Watt')}<br>
💾 <b>Kapasite:</b> {veri_getir(row, 'Kapasite')}<br>
🔗 <b>Uyumluluk:</b> {veri_getir(row, 'Uyumluluk')}<br>
💬 <b>Yorum Sayısı:</b> {veri_getir(row, 'Yorum_Sayisi')}<br>
🌈 <b>RGB:</b> {veri_getir(row, 'RGB')}<br>
📏 <b>Boyut:</b> {veri_getir(row, 'Boyut')}<br>
🖥️ <b>Çözünürlük:</b> {veri_getir(row, 'Cozunurluk')}<br>
🎮 <b>VRAM:</b> {veri_getir(row, 'VRAM')}<br>
📚 <b>Kaynak:</b> {veri_getir(row, 'Kaynak')}
</div>
""", unsafe_allow_html=True)


def ev_karti(row):
    st.markdown(f"""
<div class="product-card">
<div class="product-title">🏠 {veri_getir(row, 'Marka')} {veri_getir(row, 'Model')}</div><br>
<span class="badge-orange">💰 {fiyat_formatla(veri_getir(row, 'Fiyat_TL'))}</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Alt_Kategori')}</span>
<span class="badge-purple">⭐ {veri_getir(row, 'Puan')}</span>
<br><br>
📂 <b>Ana Kategori:</b> {veri_getir(row, 'Ana_Kategori')}<br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanim_Amaci')}<br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
⚙️ <b>Özellikler:</b> {veri_getir(row, 'Ozellikler')}<br>
🔋 <b>Enerji Sınıfı:</b> {veri_getir(row, 'Enerji_Sinifi')}<br>
🎨 <b>Renk:</b> {veri_getir(row, 'Renk')}<br>
🛡️ <b>Garanti:</b> {veri_getir(row, 'Garanti_Ay')} ay<br>
💬 <b>Yorum Sayısı:</b> {veri_getir(row, 'Yorum_Sayisi')}<br>
📦 <b>Stok:</b> {veri_getir(row, 'Stok_Durumu')}<br>
🛒 <b>Kaynak Site:</b> {veri_getir(row, 'Kaynak_Site')}
</div>
""", unsafe_allow_html=True)


st.sidebar.markdown("### 🧪 Test Modu")

if st.sidebar.button("Test Kullanıcısı Olarak Gir", key="test_login_button"):
    st.session_state.logged_in = True
    st.session_state.user = {
        "id": 0,
        "username": "test_user",
        "email": "test@example.com"
    }
    st.rerun()

if not st.session_state.logged_in:
    auth_screen()
    st.stop()


col_title, col_chat = st.columns([5, 1])

with col_title:
    st.title("🤖 Akıllı Teknoloji Ürünleri Öneri Sistemi")

with col_chat:
    with st.popover("💬 Chatbot"):
        st.subheader("Ürün Asistanı")

        chatbot_siralama = st.selectbox(
            "Sonuç sıralaması",
            [
                "Akıllı Sıralama",
                "Popülerlik",
                "Teknik Puan",
                "En Düşük Fiyat",
                "En Yüksek Fiyat",
                "Yorum Sayısı",
                "Bellek / RAM"
            ],
            key="chatbot_siralama_select"
        )

        for mesaj in st.session_state.mesajlar:
            with st.chat_message(mesaj["rol"]):
                st.write(mesaj["icerik"])

        kullanici_mesaji = st.chat_input(
            "Örnek: 50000 TL bütçem var, oyun için toplama bilgisayar istiyorum"
        )

        if kullanici_mesaji:
            st.session_state.mesajlar.append({
                "rol": "user",
                "icerik": kullanici_mesaji
            })

            chat_kategori, chat_min_butce, chat_max_butce, chat_ram, chat_kullanim = chatbot_metnini_anla(
                kullanici_mesaji
            )

            mesaj_lower = kullanici_mesaji.lower()

            if any(k in mesaj_lower for k in [
                "süpürge", "supurge", "airfryer", "kahve", "klima", "ütü", "utu",
                "kettle", "blender", "ev eşyası", "ev esyasi", "çay makinesi", "cay makinesi",
                "robot", "dikey süpürge", "hava temizleyici", "vantilatör", "kombi"
            ]):
                chat_kategori = "Elektronik Ev Eşyaları"

            llm_cevap = "İsteğini anladım. Aşağıda kriterlerine göre önerileri hazırladım."
            llm_sonuc = None
            urun_istegi_var = True

            try:
                gelen_llm_cevap = llm_sohbet_et(kullanici_mesaji)
                gelen_llm_sonuc = llm_analiz_et(kullanici_mesaji)

                if gelen_llm_cevap:
                    llm_cevap = gelen_llm_cevap

                if gelen_llm_sonuc is not None:
                    llm_sonuc = gelen_llm_sonuc
                    urun_istegi_var = bool(llm_sonuc.get("urun_istegi_var", True))

            except Exception:
                pass

            if llm_sonuc is not None:
                chat_kategori = llm_sonuc.get("kategori", chat_kategori)
                chat_min_butce = int(llm_sonuc.get("min_butce", chat_min_butce))
                chat_max_butce = int(llm_sonuc.get("max_butce", chat_max_butce))
                chat_ram = int(llm_sonuc.get("ram", chat_ram))
                chat_kullanim = llm_sonuc.get("kullanim", chat_kullanim)

                if "toplama" in mesaj_lower or "parça" in mesaj_lower or "parca" in mesaj_lower:
                    chat_kategori = "Toplama Bilgisayar"

            if urun_istegi_var:
                if chat_kategori == "Toplama Bilgisayar":
                    st.session_state.aktif_mod = "pc_build"
                    st.session_state.sonuc = None
                    st.session_state.pc_build = uyumlu_pc_sistem_topla(
                        max_butce=chat_max_butce,
                        kullanim=chat_kullanim,
                        seed=st.session_state.pc_random_seed
                    )

                    bot_mesaji = f"{llm_cevap}\n\nAnladığım kriterler: Toplama Bilgisayar, bütçe: {chat_min_butce}-{chat_max_butce} TL."

                elif chat_kategori == "Elektronik Ev Eşyaları":
                    st.session_state.aktif_mod = "ev_esyalari"
                    st.session_state.pc_build = None
                    st.session_state.pc_builds = []
                    st.session_state.sonuc = ev_esyasi_oner(
                        ana_kategori="Tümü",
                        alt_kategori="Tümü",
                        min_butce=chat_min_butce,
                        max_butce=chat_max_butce,
                        siralama=chatbot_siralama,
                        kullanim="",
                        min_puan=0,
                        enerji_sinifi="Farketmez",
                        kaynak_site="Farketmez"
                    )

                    bot_mesaji = f"{llm_cevap}\n\nAnladığım kriterler: Elektronik Ev Eşyaları, bütçe: {chat_min_butce}-{chat_max_butce} TL."

                else:
                    st.session_state.aktif_mod = "chatbot"
                    st.session_state.pc_build = None
                    st.session_state.pc_builds = []
                    st.session_state.sonuc = urun_oner(
                        chat_kategori,
                        chat_min_butce,
                        chat_max_butce,
                        chat_ram,
                        chatbot_siralama,
                        chat_kullanim
                    )

                    st.session_state.sonuc = siralama_uygula(
                        st.session_state.sonuc,
                        chatbot_siralama,
                        fiyat_kolon="FIYAT_SAYI",
                        puan_kolon="ONERI_PUANI",
                        ram_kolon="RAM"
                    )

                    bot_mesaji = f"{llm_cevap}\n\nAnladığım kriterler: {chat_kategori}, {chat_min_butce}-{chat_max_butce} TL."

            else:
                bot_mesaji = llm_cevap

            st.session_state.mesajlar.append({
                "rol": "assistant",
                "icerik": bot_mesaji
            })

            st.rerun()

        if st.button("Sohbeti Temizle", key="clear_chat_button"):
            st.session_state.mesajlar = []
            st.session_state.sonuc = None
            st.session_state.pc_build = None
            st.rerun()


st.write(
    "Bu sistem; hazır teknoloji ürünleri, toplama bilgisayar parçaları ve elektronik ev eşyaları için "
    "bütçe ve kullanım amacına göre öneri sunar."
)

st.sidebar.write(f"👤 Kullanıcı: {st.session_state.user['username']}")

if st.sidebar.button("Çıkış Yap", key="logout_button"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


st.sidebar.markdown("---")

with st.sidebar.expander("⭐ Favorilerim", expanded=False):
    favoriler = favorileri_getir(st.session_state.user["id"])

    if len(favoriler) == 0:
        st.write("Henüz favori yok.")
    else:
        for fav_name, fav_type in favoriler:
            st.write(f"⭐ {fav_name} ({fav_type})")

with st.sidebar.expander("💾 Kaydedilen Sistemlerim", expanded=False):
    sistemler = kayitli_sistemleri_getir(st.session_state.user["id"])

    if len(sistemler) == 0:
        st.write("Henüz kayıtlı sistem yok.")
    else:
        for build_name, total_price in sistemler:
            st.write(f"🖥️ {build_name} - {fiyat_formatla(total_price)}")


st.sidebar.markdown("---")
st.sidebar.header("Kullanıcı Gereksinimleri")

kategori = st.sidebar.selectbox(
    "Ürün Kategorisi",
    [
        "Telefon",
        "Bilgisayar",
        "Tablet",
        "Kulaklık",
        "Akıllı Saat / Bileklik",
        "Toplama Bilgisayar",
        "Elektronik Ev Eşyaları"
    ]
)

butce_araligi = st.sidebar.slider(
    "Bütçe Aralığı (TL)",
    min_value=100,
    max_value=250000,
    value=(10000, 30000),
    step=100
)

min_butce = butce_araligi[0]
max_butce = butce_araligi[1]

siralama = st.sidebar.selectbox(
    "Listeyi Sırala",
    [
        "Akıllı Sıralama",
        "Popülerlik",
        "Teknik Puan",
        "En Düşük Fiyat",
        "En Yüksek Fiyat",
        "Yorum Sayısı",
        "Bellek / RAM"
    ]
)

kullanim = st.sidebar.selectbox(
    "Kullanım Amacı",
    [
        "",
        "Oyun",
        "Okul",
        "Ofis",
        "Yazılım",
        "Tasarım",
        "Video Edit",
        "Günlük",
        "Ev Temizliği",
        "Pratik Yemek",
        "Akıllı Ev",
        "Alerji",
        "Hava Kalitesi",
        "Güvenlik"
    ]
)

min_ram = 0

ev_ana_kategori = None
ev_alt_kategori = None
ev_min_puan = 0.0
ev_enerji = "Farketmez"
ev_site = "Farketmez"
ev_min_watt = "Farketmez"
ev_min_emis = "Farketmez"
ev_min_hazne = "Farketmez"
ev_wifi = "Farketmez"
ev_rgb = "Farketmez"
ev_garanti = "Farketmez"
ev_stok = "Farketmez"


if kategori == "Toplama Bilgisayar":
    st.sidebar.markdown("### 🧩 Toplama Bilgisayar Modu")

    pc_mod = st.sidebar.radio(
        "Ne yapmak istiyorsun?",
        [
            "Parçaları tek tek incele",
            "Bütçeye göre uyumlu sistem topla"
        ],
        key="pc_mod_radio"
    )

    if pc_mod == "Parçaları tek tek incele":
        st.sidebar.info("Parça başlıklarını aç, seçimlerini yap, en alttaki butonla sonuçları getir.")

        with st.sidebar.expander("İşlemci"):
            soket_cpu = st.selectbox(
                "Soket",
                ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"],
                key="cpu_soket"
            )

        with st.sidebar.expander("Anakart"):
            soket_mb = st.selectbox(
                "Soket",
                ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"],
                key="mb_soket"
            )

            ramtip_mb = st.selectbox(
                "RAM Tipi",
                ["Farketmez", "DDR4", "DDR5"],
                key="mb_ramtip"
            )

        with st.sidebar.expander("RAM"):
            ramtip_ram = st.selectbox(
                "RAM Tipi",
                ["Farketmez", "DDR4", "DDR5"],
                key="ram_ramtip"
            )

            rgb_ram = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="ram_rgb"
            )

        with st.sidebar.expander("Ekran Kartı"):
            min_vram_gpu = st.selectbox(
                "Minimum VRAM",
                ["Farketmez", "4", "6", "8", "12", "16"],
                key="gpu_vram"
            )

        with st.sidebar.expander("SSD"):
            min_kapasite_ssd = st.selectbox(
                "Minimum Kapasite",
                ["Farketmez", "500", "1000", "2000", "4000"],
                key="ssd_capacity"
            )

        with st.sidebar.expander("HDD"):
            min_kapasite_hdd = st.selectbox(
                "Minimum Kapasite",
                ["Farketmez", "500", "1000", "2000", "4000"],
                key="hdd_capacity"
            )

        with st.sidebar.expander("Güç Kaynağı"):
            min_watt_psu = st.selectbox(
                "Minimum Watt",
                ["Farketmez", "500", "600", "650", "750", "850", "1000"],
                key="psu_watt"
            )

        with st.sidebar.expander("Kasa"):
            rgb_kasa = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="case_rgb"
            )

        with st.sidebar.expander("Soğutucu"):
            soket_cooler = st.selectbox(
                "Soket",
                ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"],
                key="cooler_soket"
            )

            rgb_cooler = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="cooler_rgb"
            )

        with st.sidebar.expander("Monitör"):
            monitor_rgb = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="monitor_rgb"
            )

        with st.sidebar.expander("Klavye"):
            rgb_keyboard = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="keyboard_rgb"
            )

        with st.sidebar.expander("Mouse"):
            rgb_mouse = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="mouse_rgb"
            )

        st.sidebar.markdown("---")

        if st.sidebar.button("🔎 Seçimlerime Göre Önerilenleri Getir", key="pc_all_parts_filter_button"):
            sonuc_listesi = []

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "İşlemci",
                    min_butce,
                    max_butce,
                    soket_cpu,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Anakart",
                    min_butce,
                    max_butce,
                    soket_mb,
                    ramtip_mb,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "RAM",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    ramtip_ram,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    rgb_ram,
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Ekran Kartı",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    min_vram_gpu,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "SSD",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    min_kapasite_ssd,
                    "Farketmez",
                    "Farketmez",
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "HDD",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    min_kapasite_hdd,
                    "Farketmez",
                    "Farketmez",
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Güç Kaynağı",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    min_watt_psu,
                    "Farketmez",
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Kasa",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    rgb_kasa,
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Soğutucu",
                    min_butce,
                    max_butce,
                    soket_cooler,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    rgb_cooler,
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Monitör",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    monitor_rgb,
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Klavye",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    rgb_keyboard,
                    siralama
                )
            )

            sonuc_listesi.append(
                pc_parca_filtrele(
                    "Mouse",
                    min_butce,
                    max_butce,
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    "Farketmez",
                    rgb_mouse,
                    siralama
                )
            )

            temiz_liste = [df for df in sonuc_listesi if df is not None and not df.empty]

            if len(temiz_liste) > 0:
                st.session_state.sonuc = pd.concat(temiz_liste, ignore_index=True)
            else:
                st.session_state.sonuc = pd.DataFrame()

            st.session_state.aktif_mod = "pc_parca"
            st.session_state.pc_build = None
            st.session_state.pc_builds = []
            st.rerun()

    else:
        if st.sidebar.button("🖥️ Sistem Topla", key="build_pc_button"):
            st.session_state.aktif_mod = "pc_build"
            st.session_state.pc_build = None
            st.session_state.pc_builds = besli_pc_sistem_olustur(
                min_butce=min_butce,
                max_butce=max_butce,
                kullanim=kullanim,
                seed=st.session_state.pc_random_seed
            )
            st.session_state.selected_pc_build_index = 0
            st.session_state.sonuc = None
            st.rerun()


elif kategori == "Elektronik Ev Eşyaları":
    st.sidebar.markdown("### 🏠 Elektronik Ev Eşyaları")

    ana_kategoriler = ["Tümü"] + ev_ana_kategorileri_getir()
    ev_ana_kategori = st.sidebar.selectbox("Ana Kategori", ana_kategoriler)

    if ev_ana_kategori == "Tümü":
        alt_kategoriler = ["Tümü"] + ev_alt_kategorileri_getir()
    else:
        alt_kategoriler = ["Tümü"] + sorted(
            ev_df[ev_df["Ana_Kategori"] == ev_ana_kategori]["Alt_Kategori"].dropna().unique()
        )

    ev_alt_kategori = st.sidebar.selectbox("Alt Kategori", alt_kategoriler)

    ev_min_puan = st.sidebar.slider(
        "Minimum Puan",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.1
    )

    ev_enerji = st.sidebar.selectbox(
        "Enerji Sınıfı",
        ["Farketmez", "A+++", "A++", "A+", "A", "B", "C", "Belirtilmemiş"]
    )

    ev_site = st.sidebar.selectbox(
        "Kaynak Site",
        ["Farketmez", "Hepsiburada", "Trendyol", "Teknosa", "MediaMarkt", "Vatan Bilgisayar", "Amazon Türkiye", "n11"]
    )

    ev_min_watt = st.sidebar.selectbox(
        "Minimum Watt",
        ["Farketmez", "500", "800", "1000", "1200", "1500", "1800", "2000", "2200", "2500", "3000"]
    )

    ev_min_emis = st.sidebar.selectbox(
        "Minimum Emiş Gücü / Pa",
        ["Farketmez", "1000", "2000", "3000", "4000", "5000", "6000", "7000"]
    )

    ev_min_hazne = st.sidebar.selectbox(
        "Minimum Hazne / Litre",
        ["Farketmez", "1", "2", "3", "4", "5", "6", "7", "8"]
    )

    ev_wifi = st.sidebar.selectbox(
        "Wi-Fi",
        ["Farketmez", "Var", "Yok"]
    )

    ev_rgb = st.sidebar.selectbox(
        "RGB / Işık",
        ["Farketmez", "Var", "Yok"]
    )

    ev_garanti = st.sidebar.selectbox(
        "Minimum Garanti",
        ["Farketmez", "12", "24", "36"]
    )

    ev_stok = st.sidebar.selectbox(
        "Stok Durumu",
        ["Farketmez", "Stokta var", "Az stok", "Kampanyalı", "Hızlı teslimat"]
    )


else:
    min_ram = st.sidebar.selectbox(
        "Minimum RAM",
        [0, 2, 4, 6, 8, 12, 16, 24, 32, 64],
        index=3
    )


st.sidebar.markdown("---")

if kategori != "Toplama Bilgisayar":
    if st.sidebar.button("Öneri Getir", key="oneri_getir_button"):
        st.session_state.pc_build = None
        st.session_state.sonuc = None

        if kategori == "Elektronik Ev Eşyaları":
            st.session_state.aktif_mod = "ev_esyalari"
            st.session_state.sonuc = ev_esyasi_oner(
                ana_kategori=ev_ana_kategori,
                alt_kategori=ev_alt_kategori,
                min_butce=min_butce,
                max_butce=max_butce,
                siralama=siralama,
                kullanim=kullanim,
                min_puan=ev_min_puan,
                enerji_sinifi=ev_enerji,
                kaynak_site=ev_site,
                min_watt=ev_min_watt,
                min_emis=ev_min_emis,
                min_hazne=ev_min_hazne,
                wifi=ev_wifi,
                rgb=ev_rgb,
                min_garanti=ev_garanti,
                stok=ev_stok
            )

        else:
            st.session_state.aktif_mod = "panel"
            sonuc = urun_oner(
                kategori,
                min_butce,
                max_butce,
                min_ram,
                siralama,
                kullanim
            )

            sonuc = siralama_uygula(
                sonuc,
                siralama,
                fiyat_kolon="FIYAT_SAYI",
                puan_kolon="ONERI_PUANI",
                ram_kolon="RAM"
            )

            st.session_state.sonuc = sonuc

        st.session_state.kategori = kategori
        st.session_state.min_butce = min_butce
        st.session_state.max_butce = max_butce
        st.session_state.min_ram = min_ram
        st.rerun()


st.markdown("---")


if st.session_state.aktif_mod == "pc_build":
    st.subheader("🖥️ Bütçeye Göre 5 Farklı Uyumlu Toplama Bilgisayar Sistemi")

    builds = st.session_state.get("pc_builds", [])

    if not builds:
        st.warning("Bu bütçe aralığında uygun sistem bulunamadı. Bütçe aralığını biraz genişletip tekrar deneyebilirsin.")

    else:
        st.info(
            "Aşağıda aynı bütçe aralığına göre 5 farklı sistem oluşturuldu. "
            "Sistem 1 aralıktaki en uygun fiyatlı seçeneğe, Sistem 5 ise en yüksek fiyatlı seçeneğe yakın sıralanır."
        )

        buton_kolonlari = st.columns(len(builds))

        for i, build_item in enumerate(builds):
            with buton_kolonlari[i]:
                if st.button(
                    f"{build_item.get('isim', 'Sistem')} {fiyat_formatla(build_item.get('toplam_fiyat', 0))}",
                    key=f"select_pc_build_{i}"
                ):
                    st.session_state.selected_pc_build_index = i
                    st.rerun()

        secili_index = st.session_state.get("selected_pc_build_index", 0)

        if secili_index >= len(builds):
            secili_index = 0
            st.session_state.selected_pc_build_index = 0

        build = builds[secili_index]

        st.markdown(f"## Seçili Sistem: {build.get('isim', f'Sistem {secili_index + 1}')}")

        st.success(
            f"Toplam sistem fiyatı: {fiyat_formatla(build.get('toplam_fiyat', 0))} "
            f"/ Bütçe aralığı: {fiyat_formatla(build.get('min_butce', min_butce))} - {fiyat_formatla(build.get('max_butce', max_butce))}"
        )

        col_a, col_b = st.columns([1, 1])

        with col_a:
            sistem_adi = st.text_input(
                "Bu sistemi kaydetmek için isim ver",
                value=f"Benim Toplama Bilgisayarım - {build.get('isim', f'Sistem {secili_index + 1}')}",
                key="save_build_name"
            )

            if st.button("💾 Bu Sistemi Kaydet", key="save_build_button"):
                success, message = sistemi_kaydet(
                    st.session_state.user["id"],
                    sistem_adi,
                    build,
                    build.get("toplam_fiyat", 0)
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

        with col_b:
            if st.button("🔄 5 Sistemi Değiştir", key="change_build_button"):
                st.session_state.pc_random_seed += 1
                st.session_state.pc_build = None
                st.session_state.pc_builds = besli_pc_sistem_olustur(
                    min_butce=min_butce,
                    max_butce=max_butce,
                    kullanim=kullanim,
                    seed=st.session_state.pc_random_seed
                )
                st.session_state.selected_pc_build_index = 0
                st.rerun()

        for parca_adi, row in build.get("parcalar", {}).items():
            st.markdown(f"## {parca_adi}")
            pc_parca_karti(row)


elif st.session_state.aktif_mod == "pc_parca":
    st.subheader("🧩 Seçimlere Göre Önerilen Toplama Bilgisayar Parçaları")

    sonuc = st.session_state.sonuc

    if sonuc is None:
        st.info("Soldan parça başlıklarını açıp seçim yapabilirsin.")

    elif sonuc.empty:
        st.warning("Bu kriterlere uygun parça bulunamadı.")

    else:
        st.success(f"{len(sonuc)} parça bulundu.")

        if "Alt_Kategori" in sonuc.columns:
            for alt_kategori_adi in sonuc["Alt_Kategori"].dropna().unique():
                st.markdown(f"## {alt_kategori_adi}")

                alt_df = sonuc[sonuc["Alt_Kategori"] == alt_kategori_adi]

                for index, row in alt_df.iterrows():
                    pc_parca_karti(row)

                    if st.button("⭐ Favorilere Ekle", key=f"fav_pc_{alt_kategori_adi}_{index}"):
                        product_name = f"{veri_getir(row, 'Marka')} {veri_getir(row, 'Model')}"

                        success, message = favori_ekle(
                            st.session_state.user["id"],
                            "Toplama Bilgisayar Parçası",
                            product_name,
                            row.to_dict()
                        )

                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        else:
            for index, row in sonuc.iterrows():
                pc_parca_karti(row)


elif st.session_state.aktif_mod == "ev_esyalari":
    st.subheader("🏠 Elektronik Ev Eşyaları")

    sonuc = st.session_state.sonuc

    if ev_df.empty:
        st.error("elektronik_ev_esyalari_dataset.csv bulunamadı.")

    elif sonuc is None:
        st.info("Soldan elektronik ev eşyası filtrelerini seçip öneri alabilirsin.")

    elif sonuc.empty:
        st.warning("Bu kriterlere uygun elektronik ev eşyası bulunamadı.")

    else:
        st.success(f"{len(sonuc)} ürün bulundu.")

        for index, row in sonuc.iterrows():
            ev_karti(row)

            if st.button("⭐ Favorilere Ekle", key=f"fav_ev_{index}"):
                product_name = f"{veri_getir(row, 'Marka')} {veri_getir(row, 'Model')}"

                success, message = favori_ekle(
                    st.session_state.user["id"],
                    "Elektronik Ev Eşyası",
                    product_name,
                    row.to_dict()
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)


else:
    st.subheader("🔎 Önerilen Ürünler")

    if st.session_state.sonuc is None:
        st.info("Soldaki panelden filtreleme yapabilir veya sağ üstteki chatbot butonuna basarak isteğini yazabilirsin.")

    else:
        sonuc = st.session_state.sonuc

        if sonuc.empty:
            st.warning("Bu kriterlere uygun ürün bulunamadı.")

        else:
            st.success(f"{len(sonuc)} ürün bulundu.")

            for index, row in sonuc.iterrows():
                st.markdown(f"""
<div class="product-card">
<div class="product-title">📦 {veri_getir(row, 'Model')}</div><br>
<span class="badge-orange">💰 {veri_getir(row, 'FIYAT_SAYI')} TL</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Kategori')}</span>
<span class="badge-purple">⭐ {veri_getir(row, 'ONERI_PUANI')}</span>
<br><br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanım Amacı')}<br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
⚙️ <b>İşlemci:</b> {veri_getir(row, 'İşlemci')}<br>
🧠 <b>RAM:</b> {veri_getir(row, 'RAM')}<br>
💾 <b>Depolama:</b> {veri_getir(row, 'Depolama')}<br>
🎮 <b>GPU:</b> {veri_getir(row, 'GPU')}<br>
🖥️ <b>Ekran:</b> {veri_getir(row, 'Ekran')}<br>
</div>
""", unsafe_allow_html=True)

                if st.button("⭐ Favorilere Ekle", key=f"fav_normal_{index}"):
                    product_name = str(veri_getir(row, "Model"))

                    success, message = favori_ekle(
                        st.session_state.user["id"],
                        str(veri_getir(row, "Kategori")),
                        product_name,
                        row.to_dict()
                    )

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

                aciklama = aciklama_uret(
                    row,
                    st.session_state.kategori,
                    st.session_state.min_butce,
                    st.session_state.max_butce,
                    st.session_state.min_ram
                )

                st.info(aciklama)