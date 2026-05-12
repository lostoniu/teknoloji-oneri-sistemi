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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #111827 48%, #1e1b4b 100%);
    color: #ffffff;
}

section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.96);
    border-right: 1px solid rgba(139, 92, 246, 0.45);
    box-shadow: 8px 0 30px rgba(0, 0, 0, 0.22);
}

h1, h2, h3, h4 {
    color: #ffffff !important;
    letter-spacing: -0.02em;
}

p, label, span, div {
    color: #ffffff;
}

.stButton button {
    background: linear-gradient(135deg, #f59e0b 0%, #ee8713 100%);
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 800;
    padding: 0.65rem 1rem;
    transition: all 0.22s ease;
    box-shadow: 0 10px 22px rgba(238, 135, 19, 0.18);
}

.stButton button:hover {
    background: linear-gradient(135deg, #ffb347 0%, #f97316 100%);
    color: white;
    transform: translateY(-2px);
    border: 1px solid rgba(87, 164, 251, 0.7);
}

[data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input {
    background-color: rgba(17, 24, 39, 0.94) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(87, 164, 251, 0.75) !important;
}

.stChatInput textarea {
    background-color: rgba(17, 24, 39, 0.96) !important;
    color: white !important;
    border-radius: 14px !important;
}

div[data-testid="stAlert"] {
    background-color: rgba(30, 41, 59, 0.95);
    border-left: 6px solid #f59e0b;
    border-radius: 14px;
}

.product-card {
    background: #f8f5f0;
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 16px 34px rgba(0, 0, 0, 0.18);
    transition: all 0.24s ease;
}

.product-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 22px 45px rgba(0, 0, 0, 0.24), 0 0 0 1px rgba(87, 164, 251, 0.25);
}

.product-card, .product-card div, .product-card p, .product-card b {
    color: #111827 !important;
}

.product-title {
    font-size: 21px;
    font-weight: 900;
    color: #111827 !important;
}

.badge-blue {
    background-color: #57a4fb;
    color: #0f172a !important;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
}

.badge-purple {
    background-color: #8b5cf6;
    color: white !important;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
}

.badge-orange {
    background-color: #ee8713;
    color: white !important;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
}

.system-card {
    background: rgba(248, 245, 240, 0.98);
    border: 1px solid rgba(139, 92, 246, 0.38);
    border-radius: 22px;
    padding: 18px;
    min-height: 138px;
    box-shadow: 0 18px 38px rgba(0, 0, 0, 0.20);
    transition: all 0.22s ease;
}

.system-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 22px 46px rgba(0, 0, 0, 0.26), 0 0 0 1px rgba(87, 164, 251, 0.25);
}

.system-card, .system-card div, .system-card span, .system-card b {
    color: #111827 !important;
}

.system-title {
    font-size: 19px;
    font-weight: 900;
    color: #111827 !important;
}

.system-price {
    font-size: 22px;
    font-weight: 900;
    color: #4c1d95 !important;
    margin-top: 6px;
}

.system-chip {
    display: inline-block;
    margin-top: 10px;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 900;
    color: white !important;
}

.chip-1 { background: #10b981; }
.chip-2 { background: #57a4fb; color: #0f172a !important; }
.chip-3 { background: #8b5cf6; }
.chip-4 { background: #f59e0b; }
.chip-5 { background: #ef4444; }

.summary-box {
    background: rgba(248, 245, 240, 0.98);
    border: 1px solid rgba(87, 164, 251, 0.35);
    border-radius: 22px;
    padding: 20px;
    margin: 16px 0 20px 0;
    box-shadow: 0 18px 38px rgba(0,0,0,0.18);
}

.summary-box, .summary-box div, .summary-box b {
    color: #111827 !important;
}

hr {
    border: 1px solid rgba(139, 92, 246, 0.45);
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
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


def marka_listesi_getir(df, kategori_kolon=None, kategori_deger=None, ikinci_kolon=None, ikinci_deger=None):
    if df is None or df.empty or "Marka" not in df.columns:
        return ["Farketmez"]

    sonuc = df.copy()

    if kategori_kolon and kategori_deger and kategori_deger not in [None, "Tümü", "Farketmez"]:
        if kategori_kolon in sonuc.columns:
            sonuc = sonuc[sonuc[kategori_kolon].astype(str) == str(kategori_deger)]

    if ikinci_kolon and ikinci_deger and ikinci_deger not in [None, "Tümü", "Farketmez"]:
        if ikinci_kolon in sonuc.columns:
            sonuc = sonuc[sonuc[ikinci_kolon].astype(str) == str(ikinci_deger)]

    markalar = sorted(sonuc["Marka"].dropna().astype(str).unique())
    temiz_markalar = []

    for marka in markalar:
        if marka.strip() != "" and marka.lower() != "nan":
            temiz_markalar.append(marka)

    return ["Farketmez"] + temiz_markalar


def fiyat_karsilastirma_html(df, row, site_kolon, fiyat_kolon="Fiyat_TL", max_satir=5):
    if df is None or df.empty or "Model" not in df.columns or fiyat_kolon not in df.columns:
        return ""

    model = str(veri_getir(row, "Model"))
    marka = str(veri_getir(row, "Marka"))

    if model in ["", "Yok", "nan"]:
        return ""

    ayni_urunler = df[df["Model"].astype(str) == model].copy()

    if ayni_urunler.empty and "Marka" in df.columns:
        ayni_urunler = df[
            (df["Marka"].astype(str) == marka) &
            (df["Model"].astype(str).str.contains(model[:20], na=False, regex=False))
        ].copy()

    if ayni_urunler.empty:
        return ""

    ayni_urunler[fiyat_kolon] = pd.to_numeric(ayni_urunler[fiyat_kolon], errors="coerce").fillna(0).astype(int)
    ayni_urunler = ayni_urunler[ayni_urunler[fiyat_kolon] > 0]
    ayni_urunler = ayni_urunler.sort_values(by=fiyat_kolon, ascending=True)

    if ayni_urunler.empty:
        return ""

    satirlar = []
    for _, item in ayni_urunler.head(max_satir).iterrows():
        site = item.get(site_kolon, "Bilinmeyen Site") if site_kolon in item.index else "Bilinmeyen Site"
        fiyat = fiyat_formatla(item.get(fiyat_kolon, 0))
        satirlar.append(f"<li><b>{site}</b>: {fiyat}</li>")

    baslik = "Fiyat Kaynağı" if len(satirlar) <= 1 else "Fiyat Karşılaştırması"

    return (
        '<br>'
        '<div style="background:#fff7ed; border:1px solid #fed7aa; border-radius:14px; padding:12px; margin-top:12px; color:#111827 !important;">'
        f'<b>🛒 {baslik}</b>'
        '<ul style="margin-top:8px; margin-bottom:0; padding-left:20px; color:#111827 !important;">'
        + ''.join(satirlar) +
        '</ul></div>'
    )


def modelden_marka_tahmin(model):
    if pd.isna(model):
        return "Bilinmiyor"

    metin = str(model).strip()
    if metin == "":
        return "Bilinmiyor"

    bilinen_markalar = [
        "Apple", "Samsung", "Xiaomi", "Huawei", "Honor", "Oppo", "Vivo", "Realme", "OnePlus",
        "Lenovo", "HP", "Dell", "Asus", "Acer", "MSI", "Monster", "Casper",
        "Sony", "JBL", "Anker", "Logitech", "Razer", "SteelSeries", "Sennheiser", "Philips"
    ]

    metin_lower = metin.lower()
    for marka in bilinen_markalar:
        if marka.lower() in metin_lower:
            return marka

    return metin.split()[0]


def normal_urun_marka_listesi(kategori):
    try:
        dosya = "teknoloji_urunleri_dataset.csv"
        if not os.path.exists(dosya):
            return ["Farketmez"]

        df = pd.read_csv(dosya, usecols=["Kategori", "Model"])
        df = df[df["Kategori"].astype(str) == str(kategori)]

        if df.empty:
            return ["Farketmez"]

        markalar = sorted(df["Model"].apply(modelden_marka_tahmin).dropna().astype(str).unique())
        markalar = [m for m in markalar if m and m != "Bilinmiyor" and m.lower() != "nan"]

        return ["Farketmez"] + markalar

    except Exception:
        return ["Farketmez"]


def normal_urun_marka_filtrele(df, marka):
    if df is None or df.empty or marka == "Farketmez" or "Model" not in df.columns:
        return df

    sonuc = df.copy()
    sonuc = sonuc[sonuc["Model"].apply(modelden_marka_tahmin).astype(str) == str(marka)]
    return sonuc


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
    marka,
    siralama
):
    sonuc = pc_parcalari_getir(alt_kategori, min_butce, max_butce)

    if sonuc.empty:
        return sonuc

    if marka != "Farketmez" and "Marka" in sonuc.columns:
        sonuc = sonuc[sonuc["Marka"].astype(str) == str(marka)]

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
    if "Puan" in sonuc.columns:
        sonuc = sonuc.sort_values(by=["_fark", "Puan"], ascending=[True, False])
    else:
        sonuc = sonuc.sort_values(by="_fark")

    havuz = sonuc.head(10)
    rnd = random.Random(seed)
    secilen_index = rnd.choice(list(havuz.index))

    return havuz.loc[secilen_index].drop(labels=["_fark"], errors="ignore")


# HIZLI SİSTEM ÜRETİCİ
# Eski yavaş kodun yerine tek seferde havuz hazırlayıp 5 sistemi hızlı üretir.
def fiyat_hedefine_yakin_satir(df, hedef, varyasyon=0):
    if df is None or df.empty:
        return None

    aday = df.copy()
    aday["Fiyat_TL"] = pd.to_numeric(aday["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
    aday = aday[aday["Fiyat_TL"] > 0]

    if aday.empty:
        return None

    aday = aday.assign(_fark=(aday["Fiyat_TL"] - int(hedef)).abs())

    if "Puan" in aday.columns:
        aday = aday.sort_values(by=["_fark", "Puan"], ascending=[True, False])
    else:
        aday = aday.sort_values(by=["_fark", "Fiyat_TL"], ascending=[True, True])

    siralar = list(aday.index)
    secilecek_sira = min(abs(int(varyasyon)), len(siralar) - 1)
    return aday.loc[siralar[secilecek_sira]].drop(labels=["_fark"], errors="ignore")


def pc_havuzu_fast(alt_kategori, max_butce, kullanim=""):
    if pc_df.empty:
        return pd.DataFrame()

    df = pc_df[
        (pc_df["Alt_Kategori"].astype(str) == alt_kategori) &
        (pc_df["Fiyat_TL"] > 0) &
        (pc_df["Fiyat_TL"] <= max_butce)
    ].copy()

    if df.empty:
        return df

    if alt_kategori in ["İşlemci", "Ekran Kartı"] and kullanim and "Kullanim_Amaci" in df.columns:
        filtre = df[
            df["Kullanim_Amaci"]
            .astype(str)
            .str.lower()
            .str.contains(kullanim.lower(), na=False)
        ]
        if not filtre.empty:
            df = filtre

    df = df.drop_duplicates(subset=["Marka", "Model"], keep="first")
    df = df.sort_values(by="Fiyat_TL", ascending=True).reset_index(drop=True)
    return df


def uyumlu_havuz_filtrele(df, kategori, soket=None, ram_tipi=None, min_psu=0):
    if df is None or df.empty:
        return pd.DataFrame()

    sonuc = df.copy()

    if kategori == "Anakart":
        if soket and "Soket" in sonuc.columns:
            filtre = sonuc[sonuc["Soket"].astype(str) == str(soket)]
            if not filtre.empty:
                sonuc = filtre

        if ram_tipi and "RAM_Tipi" in sonuc.columns:
            filtre = sonuc[sonuc["RAM_Tipi"].astype(str) == str(ram_tipi)]
            if not filtre.empty:
                sonuc = filtre

    if kategori == "RAM":
        if ram_tipi and "RAM_Tipi" in sonuc.columns:
            filtre = sonuc[sonuc["RAM_Tipi"].astype(str) == str(ram_tipi)]
            if not filtre.empty:
                sonuc = filtre

    if kategori == "Güç Kaynağı":
        if min_psu > 0 and "Watt" in sonuc.columns:
            filtre = sonuc[sayisal_filtre_degeri(sonuc["Watt"]) >= int(min_psu)]
            if not filtre.empty:
                sonuc = filtre

    if kategori == "Soğutucu":
        if soket and "Soket" in sonuc.columns:
            filtre = sonuc[sonuc["Soket"].astype(str).str.contains(str(soket), na=False)]
            if not filtre.empty:
                sonuc = filtre

    return sonuc.sort_values(by="Fiyat_TL", ascending=True).reset_index(drop=True)


def sistem_toplam_fiyat(parcalar):
    return sum(int(row.get("Fiyat_TL", 0)) for row in parcalar.values())


def sistem_imza(parcalar):
    return "|".join([
        str(row.get("Marka", "")) + " " + str(row.get("Model", ""))
        for row in parcalar.values()
    ])


def sistemi_butceye_yaklastir(parcalar, havuzlar, min_butce, max_butce, hedef_fiyat):
    # En fazla 10 ucuz/pahalı değişim yapar. Sonsuz döngü yok, hızlı çalışır.
    for _ in range(10):
        toplam = sistem_toplam_fiyat(parcalar)

        if min_butce <= toplam <= max_butce:
            return parcalar

        degisimler = []

        for kategori, mevcut in parcalar.items():
            mevcut_fiyat = int(mevcut.get("Fiyat_TL", 0))
            havuz = havuzlar.get(kategori, pd.DataFrame())

            if havuz is None or havuz.empty:
                continue

            if toplam < min_butce:
                adaylar = havuz[havuz["Fiyat_TL"] > mevcut_fiyat].copy()
                if adaylar.empty:
                    continue

                adaylar = adaylar.assign(
                    _yeni_toplam=toplam - mevcut_fiyat + adaylar["Fiyat_TL"]
                )
                adaylar = adaylar[adaylar["_yeni_toplam"] <= max_butce]

                if adaylar.empty:
                    continue

                adaylar = adaylar.assign(_fark=(adaylar["_yeni_toplam"] - hedef_fiyat).abs())
                aday = adaylar.sort_values(by="_fark").iloc[0]
                degisimler.append((abs(int(aday["_yeni_toplam"]) - hedef_fiyat), kategori, aday.drop(labels=["_yeni_toplam", "_fark"], errors="ignore")))

            else:
                adaylar = havuz[havuz["Fiyat_TL"] < mevcut_fiyat].copy()
                if adaylar.empty:
                    continue

                adaylar = adaylar.assign(
                    _yeni_toplam=toplam - mevcut_fiyat + adaylar["Fiyat_TL"]
                )
                adaylar = adaylar[adaylar["_yeni_toplam"] >= min_butce]

                if adaylar.empty:
                    continue

                adaylar = adaylar.assign(_fark=(adaylar["_yeni_toplam"] - hedef_fiyat).abs())
                aday = adaylar.sort_values(by="_fark").iloc[0]
                degisimler.append((abs(int(aday["_yeni_toplam"]) - hedef_fiyat), kategori, aday.drop(labels=["_yeni_toplam", "_fark"], errors="ignore")))

        if not degisimler:
            return parcalar

        degisimler = sorted(degisimler, key=lambda x: x[0])
        _, kategori, yeni_parca = degisimler[0]
        parcalar[kategori] = yeni_parca

    return parcalar


def tek_sistem_fast_olustur(min_butce, max_butce, hedef_fiyat, kullanim, seed, ana_havuzlar, varyasyon):
    oranlar = {
        "İşlemci": 0.18,
        "Ekran Kartı": 0.35,
        "Anakart": 0.12,
        "RAM": 0.10,
        "SSD": 0.08,
        "Güç Kaynağı": 0.07,
        "Kasa": 0.05,
        "Soğutucu": 0.05
    }

    parcalar = {}

    islemci = fiyat_hedefine_yakin_satir(
        ana_havuzlar.get("İşlemci", pd.DataFrame()),
        hedef_fiyat * oranlar["İşlemci"],
        varyasyon
    )
    if islemci is None:
        return None

    parcalar["İşlemci"] = islemci
    soket = str(islemci.get("Soket", ""))
    ram_tipi = str(islemci.get("RAM_Tipi", ""))

    ekran_karti = fiyat_hedefine_yakin_satir(
        ana_havuzlar.get("Ekran Kartı", pd.DataFrame()),
        hedef_fiyat * oranlar["Ekran Kartı"],
        varyasyon
    )
    if ekran_karti is None:
        return None

    parcalar["Ekran Kartı"] = ekran_karti

    gpu_watt = sayi_cek(ekran_karti.get("Watt", 0))
    min_psu = max(500, gpu_watt + 250) if gpu_watt > 0 else 500

    uyumlu_havuzlar = {
        "İşlemci": ana_havuzlar.get("İşlemci", pd.DataFrame()),
        "Ekran Kartı": ana_havuzlar.get("Ekran Kartı", pd.DataFrame()),
    }

    for kategori in ["Anakart", "RAM", "SSD", "Güç Kaynağı", "Kasa", "Soğutucu"]:
        uyumlu_havuzlar[kategori] = uyumlu_havuz_filtrele(
            ana_havuzlar.get(kategori, pd.DataFrame()),
            kategori,
            soket=soket,
            ram_tipi=ram_tipi,
            min_psu=min_psu
        )

        secilen = fiyat_hedefine_yakin_satir(
            uyumlu_havuzlar[kategori],
            hedef_fiyat * oranlar[kategori],
            varyasyon
        )

        if secilen is None:
            return None

        parcalar[kategori] = secilen

    parcalar = sistemi_butceye_yaklastir(
        parcalar=parcalar,
        havuzlar=uyumlu_havuzlar,
        min_butce=min_butce,
        max_butce=max_butce,
        hedef_fiyat=hedef_fiyat
    )

    toplam = sistem_toplam_fiyat(parcalar)

    if toplam < min_butce or toplam > max_butce:
        return None

    return {
        "basarili": True,
        "mesaj": "Bütçe aralığına uygun sistem oluşturuldu.",
        "parcalar": parcalar,
        "toplam_fiyat": toplam,
        "min_butce": min_butce,
        "max_butce": max_butce,
        "butce": max_butce,
        "hedef_fiyat": hedef_fiyat,
        "imza": sistem_imza(parcalar)
    }


def besli_pc_sistem_olustur(min_butce, max_butce, kullanim, seed):
    if pc_df.empty:
        return []

    kategoriler = [
        "İşlemci",
        "Ekran Kartı",
        "Anakart",
        "RAM",
        "SSD",
        "Güç Kaynağı",
        "Kasa",
        "Soğutucu"
    ]

    # En büyük hız kazancı burada: CSV her sistem için tekrar tekrar filtrelenmez.
    ana_havuzlar = {
        kategori: pc_havuzu_fast(kategori, max_butce, kullanim)
        for kategori in kategoriler
    }

    hedefler = [
        int(min_butce),
        int(min_butce + ((max_butce - min_butce) * 0.25)),
        int(min_butce + ((max_butce - min_butce) * 0.50)),
        int(min_butce + ((max_butce - min_butce) * 0.75)),
        int(max_butce)
    ]

    sistemler = []
    imzalar = set()

    for i, hedef in enumerate(hedefler):
        secilen = None

        # 100-200 deneme yok. En fazla 6 varyasyon, hızlı.
        for varyasyon in range(6):
            sistem = tek_sistem_fast_olustur(
                min_butce=min_butce,
                max_butce=max_butce,
                hedef_fiyat=hedef,
                kullanim=kullanim,
                seed=seed,
                ana_havuzlar=ana_havuzlar,
                varyasyon=(i * 2) + varyasyon
            )

            if sistem is None:
                continue

            if sistem["imza"] in imzalar:
                continue

            secilen = sistem
            break

        if secilen is not None:
            sistemler.append(secilen)
            imzalar.add(secilen["imza"])

    sistemler = sorted(sistemler, key=lambda x: int(x["toplam_fiyat"]))

    for i, sistem in enumerate(sistemler):
        sistem["isim"] = f"Sistem {i + 1}"

    return sistemler[:5]


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
    stok="Farketmez",
    marka="Farketmez"
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

    if marka != "Farketmez" and "Marka" in sonuc.columns:
        sonuc = sonuc[sonuc["Marka"].astype(str) == str(marka)]

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
    fiyat_karsilastirma = fiyat_karsilastirma_html(pc_df, row, "Kaynak")

    st.markdown(f"""
<div class="product-card">
<div class="product-title">🧩 {veri_getir(row, 'Marka')} {veri_getir(row, 'Model')}</div><br>
<span class="badge-orange">💰 {fiyat_formatla(veri_getir(row, 'Fiyat_TL'))}</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Alt_Kategori')}</span>
<span class="badge-purple">⭐ {veri_getir(row, 'Puan')}</span>
<br><br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanim_Amaci')}<br>
🏷️ <b>Marka:</b> {veri_getir(row, 'Marka')}<br>
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
{fiyat_karsilastirma}
</div>
""", unsafe_allow_html=True)


def ev_karti(row):
    fiyat_karsilastirma = fiyat_karsilastirma_html(ev_df, row, "Kaynak_Site")

    st.markdown(f"""
<div class="product-card">
<div class="product-title">🏠 {veri_getir(row, 'Marka')} {veri_getir(row, 'Model')}</div><br>
<span class="badge-orange">💰 {fiyat_formatla(veri_getir(row, 'Fiyat_TL'))}</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Alt_Kategori')}</span>
<span class="badge-purple">⭐ {veri_getir(row, 'Puan')}</span>
<br><br>
📂 <b>Ana Kategori:</b> {veri_getir(row, 'Ana_Kategori')}<br>
🏷️ <b>Marka:</b> {veri_getir(row, 'Marka')}<br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanim_Amaci')}<br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
⚙️ <b>Özellikler:</b> {veri_getir(row, 'Ozellikler')}<br>
🔋 <b>Enerji Sınıfı:</b> {veri_getir(row, 'Enerji_Sinifi')}<br>
🎨 <b>Renk:</b> {veri_getir(row, 'Renk')}<br>
🛡️ <b>Garanti:</b> {veri_getir(row, 'Garanti_Ay')} ay<br>
💬 <b>Yorum Sayısı:</b> {veri_getir(row, 'Yorum_Sayisi')}<br>
📦 <b>Stok:</b> {veri_getir(row, 'Stok_Durumu')}<br>
🛒 <b>Kaynak Site:</b> {veri_getir(row, 'Kaynak_Site')}
{fiyat_karsilastirma}
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
                    st.session_state.pc_build = None
                    st.session_state.pc_builds = besli_pc_sistem_olustur(
                        min_butce=chat_min_butce,
                        max_butce=chat_max_butce,
                        kullanim=chat_kullanim,
                        seed=st.session_state.pc_random_seed
                    )
                    st.session_state.selected_pc_build_index = 0

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
                        kaynak_site="Farketmez",
                        marka="Farketmez"
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
ev_marka = "Farketmez"
normal_marka = "Farketmez"


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
            marka_cpu = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "İşlemci"),
                key="cpu_marka"
            )

            soket_cpu = st.selectbox(
                "Soket",
                ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"],
                key="cpu_soket"
            )

        with st.sidebar.expander("Anakart"):
            marka_mb = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Anakart"),
                key="mb_marka"
            )

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
            marka_ram = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "RAM"),
                key="ram_marka"
            )

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
            marka_gpu = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Ekran Kartı"),
                key="gpu_marka"
            )

            min_vram_gpu = st.selectbox(
                "Minimum VRAM",
                ["Farketmez", "4", "6", "8", "12", "16"],
                key="gpu_vram"
            )

        with st.sidebar.expander("SSD"):
            marka_ssd = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "SSD"),
                key="ssd_marka"
            )

            min_kapasite_ssd = st.selectbox(
                "Minimum Kapasite",
                ["Farketmez", "500", "1000", "2000", "4000"],
                key="ssd_capacity"
            )

        with st.sidebar.expander("HDD"):
            marka_hdd = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "HDD"),
                key="hdd_marka"
            )

            min_kapasite_hdd = st.selectbox(
                "Minimum Kapasite",
                ["Farketmez", "500", "1000", "2000", "4000"],
                key="hdd_capacity"
            )

        with st.sidebar.expander("Güç Kaynağı"):
            marka_psu = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Güç Kaynağı"),
                key="psu_marka"
            )

            min_watt_psu = st.selectbox(
                "Minimum Watt",
                ["Farketmez", "500", "600", "650", "750", "850", "1000"],
                key="psu_watt"
            )

        with st.sidebar.expander("Kasa"):
            marka_kasa = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Kasa"),
                key="case_marka"
            )

            rgb_kasa = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="case_rgb"
            )

        with st.sidebar.expander("Soğutucu"):
            marka_cooler = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Soğutucu"),
                key="cooler_marka"
            )

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
            marka_monitor = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Monitör"),
                key="monitor_marka"
            )

            monitor_rgb = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="monitor_rgb"
            )

        with st.sidebar.expander("Klavye"):
            marka_keyboard = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Klavye"),
                key="keyboard_marka"
            )

            rgb_keyboard = st.selectbox(
                "RGB",
                ["Farketmez", "Var", "Yok"],
                key="keyboard_rgb"
            )

        with st.sidebar.expander("Mouse"):
            marka_mouse = st.selectbox(
                "Marka",
                marka_listesi_getir(pc_df, "Alt_Kategori", "Mouse"),
                key="mouse_marka"
            )

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
                    marka_cpu,
                    marka_mb,
                    marka_ram,
                    marka_gpu,
                    marka_ssd,
                    marka_hdd,
                    marka_psu,
                    marka_kasa,
                    marka_cooler,
                    marka_monitor,
                    marka_keyboard,
                    marka_mouse,
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

    ev_marka = st.sidebar.selectbox(
        "Marka",
        marka_listesi_getir(ev_df, "Ana_Kategori", ev_ana_kategori, "Alt_Kategori", ev_alt_kategori)
    )

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
    normal_marka = st.sidebar.selectbox(
        "Marka",
        normal_urun_marka_listesi(kategori)
    )

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
                stok=ev_stok,
                marka=ev_marka
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

            sonuc = normal_urun_marka_filtrele(sonuc, normal_marka)

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


pc_build_ekrani_acik = (
    st.session_state.aktif_mod == "pc_build"
    or (
        kategori == "Toplama Bilgisayar"
        and "pc_mod" in locals()
        and pc_mod == "Bütçeye göre uyumlu sistem topla"
    )
)

if pc_build_ekrani_acik:
    st.subheader("🖥️ Bütçeye Göre 5 Farklı Uyumlu Toplama Bilgisayar Sistemi")

    builds = st.session_state.get("pc_builds", [])

    if not builds:
        if st.session_state.aktif_mod == "pc_build":
            st.warning("Bu bütçe aralığında uygun sistem bulunamadı. Bütçe aralığını biraz genişletip tekrar deneyebilirsin.")
        else:
            st.info("Soldaki 🖥️ Sistem Topla butonuna basınca 5 sistem burada görünecek.")

    else:
        st.markdown(
            """
<div class="summary-box">
<b>Nasıl okunmalı?</b><br>
Sistem 1 daha ekonomik tarafa, Sistem 5 ise seçtiğin bütçe aralığının üst performans tarafına yakındır. 
Ekran kalabalığı olmaması için önce sadece özet kartlar gösterilir; seçtiğin sistemin detayları altta açılır.
</div>
""",
            unsafe_allow_html=True
        )

        etiketler = ["Ekonomik", "Fiyat/Performans", "Dengeli", "Performans", "Maksimum"]
        kart_kolonlari = st.columns(len(builds))

        for i, build_item in enumerate(builds):
            with kart_kolonlari[i]:
                secili_mi = st.session_state.get("selected_pc_build_index", 0) == i
                secili_yazi = "✓ Seçili" if secili_mi else "İncele"
                sistem_ismi = build_item.get("isim", f"Sistem {i + 1}")
                sistem_fiyati = fiyat_formatla(build_item.get("toplam_fiyat", 0))
                sistem_etiketi = etiketler[i] if i < len(etiketler) else "Alternatif"
                st.markdown(
                    f"""
<div class="system-card">
    <div class="system-title">{sistem_ismi}</div>
    <div class="system-price">{sistem_fiyati}</div>
    <span class="system-chip chip-{min(i + 1, 5)}">{sistem_etiketi}</span>
</div>
""",
                    unsafe_allow_html=True
                )
                if st.button(secili_yazi, key=f"select_pc_build_{i}"):
                    st.session_state.selected_pc_build_index = i
                    st.rerun()

        secili_index = st.session_state.get("selected_pc_build_index", 0)

        if secili_index >= len(builds):
            secili_index = 0
            st.session_state.selected_pc_build_index = 0

        build = builds[secili_index]
        toplam_fiyat = build.get("toplam_fiyat", 0)
        kalan = build.get("max_butce", max_butce) - toplam_fiyat
        secili_sistem_adi = build.get("isim", f"Sistem {secili_index + 1}")

        st.markdown(f"## Seçili Sistem: {secili_sistem_adi}")

        st.markdown(
            f"""
<div class="summary-box">
<b>Toplam Fiyat:</b> {fiyat_formatla(toplam_fiyat)}<br>
<b>Bütçe Aralığı:</b> {fiyat_formatla(build.get('min_butce', min_butce))} - {fiyat_formatla(build.get('max_butce', max_butce))}<br>
<b>Bütçede Kalan:</b> {fiyat_formatla(max(kalan, 0))}<br>
<b>Parça Sayısı:</b> {len(build.get('parcalar', {}))}
</div>
""",
            unsafe_allow_html=True
        )

        parca_satirlari = []
        for parca_adi, row in build.get("parcalar", {}).items():
            parca_satirlari.append({
                "Parça": parca_adi,
                "Marka": veri_getir(row, "Marka"),
                "Model": veri_getir(row, "Model"),
                "Fiyat": fiyat_formatla(veri_getir(row, "Fiyat_TL")),
            })

        if parca_satirlari:
            st.dataframe(pd.DataFrame(parca_satirlari), use_container_width=True, hide_index=True)

        col_a, col_b = st.columns([1, 1])

        with col_a:
            sistem_adi = st.text_input(
                "Bu sistemi kaydetmek için isim ver",
                value=f"Benim Toplama Bilgisayarım - {secili_sistem_adi}",
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
            if st.button("🔄 Alternatifleri Yenile", key="change_build_button"):
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

        st.markdown("### Parça Detayları")
        for parca_adi, row in build.get("parcalar", {}).items():
            detay_baslik = f"{parca_adi} - {veri_getir(row, 'Marka')} {veri_getir(row, 'Model')} / {fiyat_formatla(veri_getir(row, 'Fiyat_TL'))}"
            with st.expander(detay_baslik):
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
<span class="badge-blue">🏷️ Marka: {modelden_marka_tahmin(veri_getir(row, 'Model'))}</span><br><br>
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
🛒 <b>Fiyat Karşılaştırması:</b> Bu hazır ürün datasetinde site/link kolonu olmadığı için sadece tahmini marka filtresi uygulanır.<br>
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