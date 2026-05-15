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
st.success("YENI CSS CALISIYOR")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f4d8f7 0%, #f1ccf6 48%, #ead1ff 100%);
    color: #080b2f;
}

section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.88);
    border-right: 1px solid rgba(76, 43, 230, 0.35);
    box-shadow: 8px 0 30px rgba(76, 43, 230, 0.12);
}

h1, h2, h3, h4 {
    color: #4b2ee8 !important;
    letter-spacing: -0.02em;
}

p, label {
    color: #080b2f;
}

.stButton button {
    background: linear-gradient(135deg, #4b2ee8 0%, #6d3cff 100%);
    color: white !important;
    border: none;
    border-radius: 14px;
    font-weight: 800;
    padding: 0.52rem 0.9rem;
    font-size: 15px;
    min-height: 44px;
    transition: all 0.22s ease;
    box-shadow: 0 10px 22px rgba(76, 43, 230, 0.22);
}

.stButton button:hover {
    background: linear-gradient(135deg, #ff9226 0%, #ff7a00 100%);
    color: white;
    transform: translateY(-2px);
    border: 1px solid rgba(75, 46, 232, 0.55);
}

[data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input {
    background-color: rgba(255, 255, 255, 0.96) !important;
    color: #080b2f !important;
    border-radius: 12px !important;
    border: 1px solid rgba(75, 46, 232, 0.55) !important;
}

.stChatInput textarea {
    background-color: rgba(255, 255, 255, 0.96) !important;
    color: #080b2f !important;
    border-radius: 14px !important;
    border: 1px solid rgba(75, 46, 232, 0.55) !important;
}

div[data-testid="stAlert"] {
    background-color: rgba(255, 255, 255, 0.92);
    border-left: 6px solid #ff9226;
    border-radius: 14px;
}

.product-card {
    background: #ffffff;
    border: 1px solid rgba(75, 46, 232, 0.35);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 16px 34px rgba(76, 43, 230, 0.16);
    transition: all 0.24s ease;
}

.product-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 22px 45px rgba(76, 43, 230, 0.20), 0 0 0 1px rgba(255, 146, 38, 0.35);
}

.product-card, .product-card div, .product-card p, .product-card b {
    color: #080b2f !important;
}

.product-title {
    font-size: 21px;
    font-weight: 900;
    color: #4b2ee8 !important;
}

.badge-blue {
    background-color: #4b2ee8;
    color: white !important;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
}

.badge-purple {
    background-color: #7b2cff;
    color: white !important;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
}

.badge-orange {
    background-color: #ff9226;
    color: white !important;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
}

.system-card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(75, 46, 232, 0.38);
    border-radius: 22px;
    padding: 18px;
    min-height: 138px;
    box-shadow: 0 18px 38px rgba(76, 43, 230, 0.18);
    transition: all 0.22s ease;
}

.system-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 22px 46px rgba(76, 43, 230, 0.22), 0 0 0 1px rgba(255, 146, 38, 0.32);
}

.system-card, .system-card div, .system-card span, .system-card b {
    color: #080b2f !important;
}

.system-title {
    font-size: 19px;
    font-weight: 900;
    color: #4b2ee8 !important;
}

.system-price {
    font-size: 22px;
    font-weight: 900;
    color: #ff7a00 !important;
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

.chip-1 { background: #4b2ee8; }
.chip-2 { background: #6d3cff; color: white !important; }
.chip-3 { background: #7b2cff; }
.chip-4 { background: #ff9226; }
.chip-5 { background: #080b2f; }

.summary-box {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(75, 46, 232, 0.35);
    border-radius: 22px;
    padding: 20px;
    margin: 16px 0 20px 0;
    box-shadow: 0 18px 38px rgba(76,43,230,0.15);
}

.summary-box, .summary-box div, .summary-box b {
    color: #080b2f !important;
}

hr {
    border: 1px solid rgba(75, 46, 232, 0.35);
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

.price-compare-box {
    background: rgba(244, 216, 247, 0.55);
    border: 1px solid rgba(75, 46, 232, 0.22);
    border-radius: 14px;
    padding: 12px;
    margin-top: 14px;
}

.price-compare-title {
    color: #4b2ee8 !important;
    font-weight: 900;
    margin-bottom: 8px;
}

.price-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px dashed rgba(75, 46, 232, 0.22);
}

.price-row:last-child {
    border-bottom: none;
}

.price-site {
    color: #080b2f !important;
    font-weight: 800;
}

.price-value {
    color: #ff7a00 !important;
    font-weight: 900;
}

.price-link {
    display: inline-block;
    margin-top: 10px;
    background: #ff9226;
    color: white !important;
    text-decoration: none;
    padding: 8px 12px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 13px;
}

.price-link-secondary {
    display: inline-block;
    margin: 6px 6px 0 0;
    background: #4b2ee8;
    color: white !important;
    text-decoration: none;
    padding: 7px 10px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 12px;
}

/* CHATBOT GÖRÜNÜRLÜK DÜZELTMESİ */
[data-testid="stPopoverBody"] {
    width: 520px !important;
    max-width: 520px !important;
    height: 620px !important;
    background: #ffffff !important;
    border-radius: 24px !important;
    border: 2px solid #eadcff !important;
    padding: 16px !important;
    overflow-y: auto !important;
    box-shadow: 0 18px 45px rgba(109,60,255,0.18) !important;
}

[data-testid="stPopoverBody"],
[data-testid="stPopoverBody"] * {
    color: #111827 !important;
}

[data-testid="stPopoverBody"] .stChatMessage {
    background: #f8f5ff !important;
    border: 1px solid #e7ddff !important;
    border-radius: 16px !important;
    padding: 10px 12px !important;
    margin-bottom: 10px !important;
}

[data-testid="stChatInput"] {
    background: #f4efff !important;
    border: 1px solid #e0d2ff !important;
    border-radius: 18px !important;
    padding: 8px !important;
}

[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    border: 2px solid #7b4dff !important;
    border-radius: 14px !important;
    min-height: 52px !important;
    font-weight: 600 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #6b7280 !important;
    -webkit-text-fill-color: #6b7280 !important;
}

[data-testid="stChatInput"] button {
    background: #6d3cff !important;
    color: white !important;
    width: 44px !important;
    height: 44px !important;
    min-height: 44px !important;
    border-radius: 14px !important;
    padding: 0 !important;
}

[data-testid="stPopoverBody"] .stButton button {
    width: 42px !important;
    min-width: 42px !important;
    max-width: 42px !important;
    height: 42px !important;
    min-height: 42px !important;
    padding: 0 !important;
    border-radius: 12px !important;
    background: #6d3cff !important;
    color: transparent !important;
    font-size: 0 !important;
    overflow: hidden !important;
}

[data-testid="stPopoverBody"] .stButton button::before {
    content: "🗑️";
    color: white !important;
    font-size: 16px !important;
}

[data-testid="stPopoverBody"] .stButton button:hover {
    width: 160px !important;
    min-width: 160px !important;
    max-width: 160px !important;
    background: #ff9226 !important;
}

[data-testid="stPopoverBody"] .stButton button:hover::before {
    content: "🗑️ Sohbeti Temizle";
    color: white !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
}

</style>
""", unsafe_allow_html=True)


def get_secret_value(key, default=None):
    env_value = os.getenv(key)
    if env_value not in [None, ""]:
        return env_value

    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def get_db_connection():
    return psycopg2.connect(
        host=get_secret_value("DB_HOST"),
        database=get_secret_value("DB_NAME"),
        user=get_secret_value("DB_USER"),
        password=get_secret_value("DB_PASSWORD"),
        port=get_secret_value("DB_PORT", "5432")
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


def _json_data_to_df(rows):
    temiz_rows = []

    for row in rows:
        data = row.get("data", {})

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                data = {}

        if not isinstance(data, dict):
            data = {}

        merged = dict(data)
        merged.setdefault("Kategori", row.get("kategori"))
        merged.setdefault("Ana_Kategori", row.get("kategori"))
        merged.setdefault("Alt_Kategori", row.get("alt_kategori"))
        merged.setdefault("Marka", row.get("marka"))
        merged.setdefault("Model", row.get("model"))
        merged.setdefault("Fiyat_TL", row.get("fiyat_tl", 0))
        merged.setdefault("Puan", row.get("puan", 0))
        merged.setdefault("Topluluk_Puani", row.get("puan", 0))
        merged.setdefault("Populerlik", row.get("populerlik"))
        temiz_rows.append(merged)

    return pd.DataFrame(temiz_rows)


@st.cache_data(ttl=86400, show_spinner=False)
def products_db_yukle(source):
    try:
        with get_db_connection() as conn:
            df = pd.read_sql(
                """
                SELECT source, kategori, alt_kategori, marka, model, fiyat_tl, puan, populerlik, data
                FROM products
                WHERE source = %s
                """,
                conn,
                params=[source]
            )

        if df.empty:
            return pd.DataFrame()

        return _json_data_to_df(df.to_dict("records"))

    except Exception as e:
        st.warning(f"Ürün tablosu okunamadı, CSV yedeği kullanılacak: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def ev_esyalari_yukle():
    df = products_db_yukle("ev")

    if df.empty:
        dosya = "elektronik_ev_esyalari_dataset.csv"
        if not os.path.exists(dosya):
            return pd.DataFrame()
        df = pd.read_csv(dosya, low_memory=False)

    if "Fiyat_TL" in df.columns:
        df["Fiyat_TL"] = pd.to_numeric(df["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
    if "Puan" in df.columns:
        df["Puan"] = pd.to_numeric(df["Puan"], errors="coerce").fillna(0)
    if "Topluluk_Puani" in df.columns:
        df["Topluluk_Puani"] = pd.to_numeric(df["Topluluk_Puani"], errors="coerce").fillna(0)
    if "Yorum_Sayisi" in df.columns:
        df["Yorum_Sayisi"] = pd.to_numeric(df["Yorum_Sayisi"], errors="coerce").fillna(0).astype(int)
    if "Garanti_Ay" in df.columns:
        df["Garanti_Ay"] = pd.to_numeric(df["Garanti_Ay"], errors="coerce").fillna(0).astype(int)

    return df


@st.cache_data(ttl=86400, show_spinner=False)
def pc_dataset_yukle():
    df = products_db_yukle("pc")

    if df.empty:
        dosya = "pc_parts_dataset.csv"
        if not os.path.exists(dosya):
            return pd.DataFrame()
        df = pd.read_csv(dosya, low_memory=False)

    if "Fiyat_TL" in df.columns:
        df["Fiyat_TL"] = pd.to_numeric(df["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
    if "Puan" in df.columns:
        df["Puan"] = pd.to_numeric(df["Puan"], errors="coerce").fillna(0)
    if "Topluluk_Puani" in df.columns:
        df["Topluluk_Puani"] = pd.to_numeric(df["Topluluk_Puani"], errors="coerce").fillna(0)
    if "Yorum_Sayisi" in df.columns:
        df["Yorum_Sayisi"] = pd.to_numeric(df["Yorum_Sayisi"], errors="coerce").fillna(0).astype(int)

    return df


@st.cache_data(ttl=86400, show_spinner=False)
def teknoloji_dataset_yukle():
    df = products_db_yukle("teknoloji")

    if df.empty:
        dosya = "teknoloji_urunleri_dataset.csv"
        if not os.path.exists(dosya):
            return pd.DataFrame()
        df = pd.read_csv(dosya, low_memory=False)

    if "Fiyat_TL" in df.columns:
        df["Fiyat_TL"] = pd.to_numeric(df["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
        df["FIYAT_SAYI"] = df["Fiyat_TL"]
    elif "Fiyat (TL)" in df.columns:
        df["Fiyat (TL)"] = pd.to_numeric(df["Fiyat (TL)"], errors="coerce").fillna(0).astype(int)
        df["FIYAT_SAYI"] = df["Fiyat (TL)"]
    elif "FIYAT_SAYI" in df.columns:
        df["FIYAT_SAYI"] = pd.to_numeric(df["FIYAT_SAYI"], errors="coerce").fillna(0).astype(int)
    else:
        df["FIYAT_SAYI"] = 0

    if "RAM" in df.columns:
        df["RAM_SAYI"] = df["RAM"].astype(str).str.extract(r"(\d+)")[0]
        df["RAM_SAYI"] = pd.to_numeric(df["RAM_SAYI"], errors="coerce").fillna(0).astype(int)
    else:
        df["RAM_SAYI"] = 0

    if "Topluluk_Puani" in df.columns:
        df["ONERI_PUANI"] = pd.to_numeric(df["Topluluk_Puani"], errors="coerce").fillna(0).astype(int)
    elif "Puan" in df.columns:
        df["ONERI_PUANI"] = pd.to_numeric(df["Puan"], errors="coerce").fillna(0).astype(int)
    elif "ONERI_PUANI" in df.columns:
        df["ONERI_PUANI"] = pd.to_numeric(df["ONERI_PUANI"], errors="coerce").fillna(0).astype(int)
    else:
        df["ONERI_PUANI"] = 0

    return df


ev_df = ev_esyalari_yukle()
pc_df = pc_dataset_yukle()
tech_df = teknoloji_dataset_yukle()



def kart_puani_getir(row):
    for kolon in ["Topluluk_Puani", "TOPLULUK_PUANI", "ONERI_PUANI", "Puan"]:
        try:
            if kolon in row.index and str(row[kolon]) != "nan":
                puan = float(row[kolon])

                # Eski 5/10 ölçekli puan gelirse 100'lük sisteme çevir
                if puan <= 10:
                    puan = puan * 10

                puan = int(round(puan))

                if puan > 0:
                    return f"{puan}/100"
        except Exception:
            pass

    return "Belirtilmedi"


def kart_populerlik_getir(row):
    if "Populerlik" in row.index and str(row["Populerlik"]) != "nan":
        return row["Populerlik"]

    try:
        puan = kart_puani_getir(row)
        if "/" in str(puan):
            sayi = int(str(puan).split("/")[0])
            if sayi >= 85:
                return "Çok Yüksek"
            if sayi >= 70:
                return "Yüksek"
            if sayi >= 55:
                return "Orta"
            return "Düşük"
    except Exception:
        pass

    return "Belirtilmedi"


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


def marka_listesi_getir(df, kategori_kolon=None, kategori_deger=None, ana_kolon=None, ana_deger=None):
    """Verilen dataframe içinden güvenli şekilde marka listesi üretir."""
    if df is None or df.empty or "Marka" not in df.columns:
        return ["Farketmez"]

    sonuc = df.copy()

    if ana_kolon and ana_deger and ana_deger not in ["Tümü", "Farketmez", None]:
        if ana_kolon in sonuc.columns:
            sonuc = sonuc[sonuc[ana_kolon].astype(str) == str(ana_deger)]

    if kategori_kolon and kategori_deger and kategori_deger not in ["Tümü", "Farketmez", None]:
        if kategori_kolon in sonuc.columns:
            sonuc = sonuc[sonuc[kategori_kolon].astype(str) == str(kategori_deger)]

    markalar = sorted([
        str(x).strip()
        for x in sonuc["Marka"].dropna().unique()
        if str(x).strip() not in ["", "nan", "None"]
    ])

    return ["Farketmez"] + markalar




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


def hazir_urun_oner_db(kategori, min_butce, max_butce, min_ram, siralama, kullanim=""):
    if tech_df.empty:
        return pd.DataFrame()

    sonuc = tech_df.copy()

    if "Kategori" in sonuc.columns:
        sonuc = sonuc[sonuc["Kategori"].astype(str).apply(temizle_yazi) == temizle_yazi(kategori)]

    if "FIYAT_SAYI" not in sonuc.columns:
        if "Fiyat_TL" in sonuc.columns:
            sonuc["FIYAT_SAYI"] = pd.to_numeric(sonuc["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
        elif "Fiyat (TL)" in sonuc.columns:
            sonuc["FIYAT_SAYI"] = pd.to_numeric(sonuc["Fiyat (TL)"], errors="coerce").fillna(0).astype(int)
        else:
            sonuc["FIYAT_SAYI"] = 0

    sonuc = sonuc[(sonuc["FIYAT_SAYI"] >= int(min_butce)) & (sonuc["FIYAT_SAYI"] <= int(max_butce))]

    if temizle_yazi(kategori) in ["bilgisayar", "telefon", "tablet"] and "RAM_SAYI" in sonuc.columns:
        sonuc = sonuc[sonuc["RAM_SAYI"] >= int(min_ram)]

    if kullanim and "Kullanım Amacı" in sonuc.columns:
        k = temizle_yazi(kullanim)
        filtre = sonuc[sonuc["Kullanım Amacı"].astype(str).apply(temizle_yazi).str.contains(k, na=False)]
        if not filtre.empty:
            sonuc = filtre

    if "ONERI_PUANI" not in sonuc.columns:
        if "Topluluk_Puani" in sonuc.columns:
            sonuc["ONERI_PUANI"] = pd.to_numeric(sonuc["Topluluk_Puani"], errors="coerce").fillna(0).astype(int)
        elif "Puan" in sonuc.columns:
            sonuc["ONERI_PUANI"] = pd.to_numeric(sonuc["Puan"], errors="coerce").fillna(0).astype(int)
        else:
            sonuc["ONERI_PUANI"] = 0

    if "Model" in sonuc.columns:
        sonuc = sonuc.drop_duplicates(subset=["Model"], keep="first")

    sonuc = siralama_uygula(
        sonuc,
        siralama,
        fiyat_kolon="FIYAT_SAYI",
        puan_kolon="ONERI_PUANI",
        ram_kolon="RAM"
    )

    return sonuc.head(50)


def ev_alt_kategori_tipi(alt_kategori):
    """Elektronik ev eşyasında sadece ilgili filtreler çıksın diye alt kategori tipini belirler."""
    a = temizle_yazi(str(alt_kategori))

    # ÖNEMLİ: "Buharlı Dikey Ütü" içinde dikey geçtiği için önce ütüyü yakalıyoruz.
    if any(k in a for k in ["utu", "buharli utu", "buhar kazanli", "utuler"]):
        return "utu"

    # Sadece "dikey" kelimesine göre süpürge sayma. Dikey ütü de var.
    if any(k in a for k in ["supurge", "robot supurge", "dikey supurge", "sarjli supurge", "elektrikli supurge", "vacuum"]):
        return "supurge"

    if any(k in a for k in ["airfryer", "fritoz", "fritöz", "pisirme", "firin", "fırın", "mikrodalga"]):
        return "pisirme"

    if any(k in a for k in ["kahve", "espresso", "cay", "çay", "kettle", "su isitici", "su ısıtıcı"]):
        return "icecek"

    if any(k in a for k in ["klima", "hava", "vantilator", "vantilatör", "isitici", "ısıtıcı", "kombi", "nem", "temizleyici"]):
        return "hava_iklim"

    if any(k in a for k in ["kedi", "tuvalet", "mama", "evcil", "pet"]):
        return "evcil"

    if any(k in a for k in ["kamera", "guvenlik", "güvenlik", "kilit", "sensor", "sensör", "alarm"]):
        return "guvenlik"

    if any(k in a for k in ["bulasik", "bulaşık", "camasir", "çamaşır", "buzdolabi", "buzdolabı", "derin dondurucu"]):
        return "beyaz_esya"

    return "genel"



GUVENILIR_SITE_LINKLERI = {
    "Amazon Türkiye": "https://www.amazon.com.tr/s?k={q}",
    "Amazon": "https://www.amazon.com.tr/s?k={q}",
    "Hepsiburada": "https://www.hepsiburada.com/ara?q={q}",
    "Trendyol": "https://www.trendyol.com/sr?q={q}",
    "Teknosa": "https://www.teknosa.com/arama/?s={q}",
    "MediaMarkt": "https://www.mediamarkt.com.tr/tr/search.html?query={q}",
    "Vatan Bilgisayar": "https://www.vatanbilgisayar.com/arama/{q}/",
    "Vatan": "https://www.vatanbilgisayar.com/arama/{q}/",
    "n11": "https://www.n11.com/arama?q={q}",
    "İtopya": "https://www.itopya.com/arama/?search={q}",
    "Itopya": "https://www.itopya.com/arama/?search={q}",
    "İncehesap": "https://www.incehesap.com/arama/?q={q}",
    "Incehesap": "https://www.incehesap.com/arama/?q={q}",
    "Sinerji": "https://www.sinerji.gen.tr/arama?q={q}",
    "GamingGenTR": "https://www.gaming.gen.tr/?s={q}&post_type=product",
    "Akakçe": "https://www.akakce.com/arama/?q={q}",
    "Akakce": "https://www.akakce.com/arama/?q={q}",
    "Epey": "https://www.epey.com/arama/?q={q}",
}

GUVENILIR_SITE_ADLARI = list(GUVENILIR_SITE_LINKLERI.keys())


def html_escape(deger):
    return (
        str(deger)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def site_guvenilir_mi(site_adi):
    site = str(site_adi).strip().lower()
    if site in ["", "nan", "none", "yok"]:
        return False
    for guvenilir in GUVENILIR_SITE_ADLARI:
        guvenilir_lower = guvenilir.lower()
        if site == guvenilir_lower or guvenilir_lower in site or site in guvenilir_lower:
            return True
    return False


def site_adi_duzelt(site_adi):
    site = str(site_adi).strip()
    for guvenilir in GUVENILIR_SITE_ADLARI:
        guvenilir_lower = guvenilir.lower()
        site_lower = site.lower()
        if site_lower == guvenilir_lower or guvenilir_lower in site_lower or site_lower in guvenilir_lower:
            return guvenilir
    return site


def guvenilir_site_arama_linki(site_adi, urun_adi):
    from urllib.parse import quote_plus
    site = site_adi_duzelt(site_adi)
    q = quote_plus(str(urun_adi))
    kalip = GUVENILIR_SITE_LINKLERI.get(site)
    if kalip:
        return kalip.format(q=q)
    return "https://www.google.com/search?q=" + q


def urun_adi_olustur(row):
    marka = veri_getir(row, "Marka")
    model = veri_getir(row, "Model")
    if marka != "Yok" and model != "Yok":
        return f"{marka} {model}"
    if model != "Yok":
        return str(model)
    return str(row.get("Model", "Ürün"))


def ayni_urun_kaynaklari(kaynak_turu, row):
    if kaynak_turu == "ev":
        df = ev_df.copy()
        site_kolon = "Kaynak_Site"
        fiyat_kolon = "Fiyat_TL"
        marka = str(veri_getir(row, "Marka"))
        model = str(veri_getir(row, "Model"))
        if df.empty or site_kolon not in df.columns:
            return pd.DataFrame()
        adaylar = df[(df["Marka"].astype(str) == marka) & (df["Model"].astype(str) == model)].copy()
    elif kaynak_turu == "pc":
        df = pc_df.copy()
        site_kolon = "Kaynak"
        fiyat_kolon = "Fiyat_TL"
        marka = str(veri_getir(row, "Marka"))
        model = str(veri_getir(row, "Model"))
        if df.empty or site_kolon not in df.columns:
            return pd.DataFrame()
        adaylar = df[(df["Marka"].astype(str) == marka) & (df["Model"].astype(str) == model)].copy()
    else:
        return pd.DataFrame()
    if adaylar.empty:
        return adaylar
    adaylar = adaylar[adaylar[site_kolon].apply(site_guvenilir_mi)].copy()
    if adaylar.empty:
        return adaylar
    adaylar[fiyat_kolon] = pd.to_numeric(adaylar[fiyat_kolon], errors="coerce").fillna(0).astype(int)
    adaylar = adaylar[adaylar[fiyat_kolon] > 0]
    adaylar = adaylar.sort_values(by=fiyat_kolon, ascending=True)
    adaylar = adaylar.drop_duplicates(subset=[site_kolon], keep="first")
    adaylar = adaylar.rename(columns={site_kolon: "Site", fiyat_kolon: "Fiyat"})
    return adaylar[["Site", "Fiyat"]].head(5)


def fiyat_karsilastirma_html(kaynak_turu, row):
    urun_adi = urun_adi_olustur(row)
    return f"""
<div class=\"price-compare-box\">
    <div class=\"price-compare-title\">Güncel Fiyatı Güvenilir Sitelerde Kontrol Et</div>
    <div>Gösterilen tutar ortalama piyasa fiyatıdır. Satıcıya, kampanyaya ve stok durumuna göre fiyat değişebilir; en güncel fiyatı aşağıdaki güvenilir sitelerde kontrol edebilirsin.</div>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Akakçe', urun_adi)}\" target=\"_blank\">Akakçe'de ara</a>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Hepsiburada', urun_adi)}\" target=\"_blank\">Hepsiburada'da ara</a>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Amazon Türkiye', urun_adi)}\" target=\"_blank\">Amazon'da ara</a>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Teknosa', urun_adi)}\" target=\"_blank\">Teknosa'da ara</a>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Vatan Bilgisayar', urun_adi)}\" target=\"_blank\">Vatan'da ara</a>
</div>
"""


def hazir_urun_guvenilir_link_html(row):
    model = str(veri_getir(row, "Model"))
    return f"""
<div class=\"price-compare-box\">
    <div class=\"price-compare-title\">Güncel Fiyatı Güvenilir Sitelerde Kontrol Et</div>
    <div>Gösterilen tutar ortalama piyasa fiyatıdır. Satıcıya, kampanyaya ve stok durumuna göre fiyat değişebilir; en güncel fiyatı güvenilir sitelerde kontrol edebilirsin.</div>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Akakçe', model)}\" target=\"_blank\">Akakçe'de ara</a>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Hepsiburada', model)}\" target=\"_blank\">Hepsiburada'da ara</a>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Amazon Türkiye', model)}\" target=\"_blank\">Amazon'da ara</a>
    <a class=\"price-link-secondary\" href=\"{guvenilir_site_arama_linki('Teknosa', model)}\" target=\"_blank\">Teknosa'da ara</a>
</div>
"""


MARKA_KELIMELERI = [
    "Apple", "Samsung", "Xiaomi", "Huawei", "Honor", "OnePlus", "Oppo", "Vivo", "Realme",
    "Lenovo", "HP", "Dell", "Asus", "Acer", "MSI", "Monster", "Casper", "Huawei",
    "Sony", "JBL", "Anker", "Sennheiser", "Beats", "Logitech", "Philips", "TCL",
    "Garmin", "Amazfit", "Fitbit"
]


def modelden_marka_bul(model):
    metin = str(model).lower()

    for marka in MARKA_KELIMELERI:
        if marka.lower() in metin:
            return marka

    ilk_kelime = str(model).strip().split(" ")[0] if str(model).strip() else "Bilinmiyor"
    return ilk_kelime


def hazir_urun_markalari_getir(kategori):
    if tech_df.empty or "Kategori" not in tech_df.columns or "Model" not in tech_df.columns:
        return ["Farketmez"]

    df = tech_df[tech_df["Kategori"].astype(str) == str(kategori)].copy()

    if df.empty:
        return ["Farketmez"]

    markalar = sorted(df["Model"].apply(modelden_marka_bul).dropna().astype(str).unique())

    return ["Farketmez"] + markalar


def secenekleri_getir(df, kategori, kolon):
    if df.empty or "Kategori" not in df.columns or kolon not in df.columns:
        return ["Farketmez"]

    sonuc = df[df["Kategori"].astype(str) == str(kategori)][kolon]
    secenekler = sorted([str(x) for x in sonuc.dropna().unique() if str(x).strip() != ""])

    return ["Farketmez"] + secenekler


def kapasite_gb_cek(deger):
    metin = str(deger).lower().replace(",", ".")

    bulunan = pd.Series([metin]).str.extract(r"(\d+(?:\.\d+)?)")[0].iloc[0]

    if pd.isna(bulunan):
        return 0

    sayi = float(bulunan)

    if "tb" in metin:
        sayi *= 1000

    return int(sayi)


def evet_hayir_filtrele(df, kolon, secim):
    if secim == "Farketmez" or kolon not in df.columns:
        return df

    if secim == "Evet":
        return df[df[kolon].astype(str).str.lower().str.contains("evet|var|ip|atm|5atm|su", na=False)]

    return df[~df[kolon].astype(str).str.lower().str.contains("evet|var|ip|atm|5atm|su", na=False)]




def ekran_hz_cek(deger):
    import re
    metin = str(deger).lower()
    hzler = re.findall(r"(\d+)\s*hz", metin)
    if hzler:
        return max([int(x) for x in hzler])
    sayilar = re.findall(r"\d+", metin)
    if sayilar:
        adaylar = [int(x) for x in sayilar if int(x) in [60, 75, 90, 120, 144, 165, 240, 300, 360]]
        if adaylar:
            return max(adaylar)
    return 0


def cpu_seviye_uygun_mu(islemci, seviye):
    if seviye == "Farketmez":
        return True
    i = str(islemci).lower()
    if seviye == "Giriş":
        return any(k in i for k in ["i3", "ryzen 3", "celeron", "pentium"])
    if seviye == "Orta":
        return any(k in i for k in ["i5", "ryzen 5", "m1", "m2"])
    if seviye == "Üst":
        return any(k in i for k in ["i7", "ryzen 7", "m3"])
    if seviye == "Premium":
        return any(k in i for k in ["i9", "ryzen 9", "m4", "ultra 9"])
    return True


def gpu_seviye_uygun_mu(gpu, seviye):
    if seviye == "Farketmez":
        return True
    g = str(gpu).lower()
    if seviye == "Paylaşımlı":
        return any(k in g for k in ["uhd", "iris", "integrated", "paylaşımlı", "dahili"])
    if seviye == "Giriş":
        return any(k in g for k in ["rtx 3050", "rtx 4050", "gtx", "mx"])
    if seviye == "Orta":
        return any(k in g for k in ["rtx 3060", "rtx 4060", "rtx 3070", "rtx 4070", "rx 7600", "rx 7700"])
    if seviye == "Üst":
        return any(k in g for k in ["rtx 4080", "rtx 4090", "rtx 5080", "rtx 5090", "rx 7900"])
    return True

def hazir_urun_detay_filtrele(df, kategori, filtreler):
    if df is None or df.empty:
        return df

    sonuc = df.copy()

    marka = filtreler.get("marka", "Farketmez")
    if marka != "Farketmez" and "Model" in sonuc.columns:
        sonuc = sonuc[sonuc["Model"].apply(modelden_marka_bul).astype(str) == str(marka)]

    if kategori == "Telefon":
        min_depolama = filtreler.get("min_depolama", "Farketmez")
        if min_depolama != "Farketmez" and "Depolama" in sonuc.columns:
            sonuc = sonuc[sonuc["Depolama"].apply(kapasite_gb_cek) >= int(min_depolama)]

        min_kamera = filtreler.get("min_kamera", "Farketmez")
        if min_kamera != "Farketmez" and "Kamera (MP)" in sonuc.columns:
            sonuc = sonuc[sonuc["Kamera (MP)"].apply(sayi_cek) >= int(min_kamera)]

        min_batarya = filtreler.get("min_batarya", "Farketmez")
        if min_batarya != "Farketmez" and "Batarya (mAh)" in sonuc.columns:
            sonuc = sonuc[pd.to_numeric(sonuc["Batarya (mAh)"], errors="coerce").fillna(0) >= int(min_batarya)]

        sonuc = evet_hayir_filtrele(sonuc, "5G", filtreler.get("bes_g", "Farketmez"))
        sonuc = evet_hayir_filtrele(sonuc, "NFC", filtreler.get("nfc", "Farketmez"))
        sonuc = evet_hayir_filtrele(sonuc, "Su Geçirmezlik", filtreler.get("su", "Farketmez"))

    elif kategori == "Bilgisayar":
        min_depolama = filtreler.get("min_depolama", "Farketmez")
        if min_depolama != "Farketmez" and "Depolama" in sonuc.columns:
            sonuc = sonuc[sonuc["Depolama"].apply(kapasite_gb_cek) >= int(min_depolama)]

        cpu_marka = filtreler.get("cpu_marka", "Farketmez")
        if cpu_marka != "Farketmez" and "İşlemci" in sonuc.columns:
            sonuc = sonuc[sonuc["İşlemci"].astype(str).str.lower().str.contains(cpu_marka.lower(), na=False)]

        cpu_seviye = filtreler.get("cpu_seviye", "Farketmez")
        if cpu_seviye != "Farketmez" and "İşlemci" in sonuc.columns:
            sonuc = sonuc[sonuc["İşlemci"].apply(lambda x: cpu_seviye_uygun_mu(x, cpu_seviye))]

        gpu_tercihi = filtreler.get("gpu_tercihi", "Farketmez")
        if gpu_tercihi != "Farketmez" and "GPU" in sonuc.columns:
            sonuc = sonuc[sonuc["GPU"].astype(str).str.lower().str.contains(gpu_tercihi.lower(), na=False)]

        gpu_seviye = filtreler.get("gpu_seviye", "Farketmez")
        if gpu_seviye != "Farketmez" and "GPU" in sonuc.columns:
            sonuc = sonuc[sonuc["GPU"].apply(lambda x: gpu_seviye_uygun_mu(x, gpu_seviye))]

        panel = filtreler.get("panel", "Farketmez")
        if panel != "Farketmez" and "Ekran" in sonuc.columns:
            sonuc = sonuc[sonuc["Ekran"].astype(str).str.lower().str.contains(panel.lower(), na=False)]

        min_hz = filtreler.get("min_hz", "Farketmez")
        if min_hz != "Farketmez" and "Ekran" in sonuc.columns:
            sonuc = sonuc[sonuc["Ekran"].apply(ekran_hz_cek) >= int(min_hz)]

        isletim = filtreler.get("isletim", "Farketmez")
        if isletim != "Farketmez" and "İşletim Sistemi" in sonuc.columns:
            sonuc = sonuc[sonuc["İşletim Sistemi"].astype(str) == isletim]

    elif kategori == "Tablet":
        min_depolama = filtreler.get("min_depolama", "Farketmez")
        if min_depolama != "Farketmez" and "Depolama" in sonuc.columns:
            sonuc = sonuc[sonuc["Depolama"].apply(kapasite_gb_cek) >= int(min_depolama)]

        min_batarya = filtreler.get("min_batarya", "Farketmez")
        if min_batarya != "Farketmez" and "Batarya (mAh)" in sonuc.columns:
            sonuc = sonuc[pd.to_numeric(sonuc["Batarya (mAh)"], errors="coerce").fillna(0) >= int(min_batarya)]

        panel = filtreler.get("panel", "Farketmez")
        if panel != "Farketmez" and "Ekran" in sonuc.columns:
            sonuc = sonuc[sonuc["Ekran"].astype(str).str.lower().str.contains(panel.lower(), na=False)]

        min_hz = filtreler.get("min_hz", "Farketmez")
        if min_hz != "Farketmez" and "Ekran" in sonuc.columns:
            sonuc = sonuc[sonuc["Ekran"].apply(ekran_hz_cek) >= int(min_hz)]

        isletim = filtreler.get("isletim", "Farketmez")
        if isletim != "Farketmez" and "İşletim Sistemi" in sonuc.columns:
            sonuc = sonuc[sonuc["İşletim Sistemi"].astype(str) == isletim]

        sonuc = evet_hayir_filtrele(sonuc, "Su Geçirmezlik", filtreler.get("su", "Farketmez"))

    elif kategori == "Kulaklık":
        kulaklik_tipi = filtreler.get("kulaklik_tipi", "Farketmez")
        if kulaklik_tipi != "Farketmez" and "Kulaklık Tipi" in sonuc.columns:
            sonuc = sonuc[sonuc["Kulaklık Tipi"].astype(str) == kulaklik_tipi]

        baglanti = filtreler.get("baglanti", "Farketmez")
        if baglanti != "Farketmez" and "Bağlantı Türü" in sonuc.columns:
            sonuc = sonuc[sonuc["Bağlantı Türü"].astype(str) == baglanti]

        sonuc = evet_hayir_filtrele(sonuc, "Gürültü Engelleme", filtreler.get("gurultu", "Farketmez"))
        sonuc = evet_hayir_filtrele(sonuc, "Mikrofon", filtreler.get("mikrofon", "Farketmez"))

        min_pil = filtreler.get("min_pil", "Farketmez")
        if min_pil != "Farketmez" and "Pil Ömrü" in sonuc.columns:
            sonuc = sonuc[sonuc["Pil Ömrü"].apply(sayi_cek) >= int(min_pil)]

    elif kategori == "Akıllı Saat / Bileklik":
        sonuc = evet_hayir_filtrele(sonuc, "GPS", filtreler.get("gps", "Farketmez"))
        sonuc = evet_hayir_filtrele(sonuc, "Su Geçirmezlik", filtreler.get("su", "Farketmez"))

        min_pil_gun = filtreler.get("min_pil_gun", "Farketmez")
        if min_pil_gun != "Farketmez" and "Pil Ömrü (gün)" in sonuc.columns:
            sonuc = sonuc[pd.to_numeric(sonuc["Pil Ömrü (gün)"], errors="coerce").fillna(0) >= int(min_pil_gun)]

        isletim = filtreler.get("isletim", "Farketmez")
        if isletim != "Farketmez" and "İşletim Sistemi" in sonuc.columns:
            sonuc = sonuc[sonuc["İşletim Sistemi"].astype(str) == isletim]

    return sonuc



def karsilastirma_urun_adi(row):
    marka = veri_getir(row, "Marka")
    model = veri_getir(row, "Model")

    if marka != "Yok" and model != "Yok":
        return f"{marka} {model}"

    if model != "Yok":
        return str(model)

    return "Ürün"


def karsilastirma_fiyat(row):
    for kolon in ["Fiyat_TL", "FIYAT_SAYI", "Fiyat (TL)"]:
        if kolon in row.index and str(row[kolon]) != "nan":
            return fiyat_formatla(row[kolon])
    return "Yok"


def karsilastirma_puan(row):
    if "kart_puani_getir" in globals():
        return kart_puani_getir(row)

    for kolon in ["Topluluk_Puani", "Puan", "ONERI_PUANI"]:
        if kolon in row.index and str(row[kolon]) != "nan":
            try:
                puan = float(row[kolon])
                if puan <= 10:
                    puan *= 10
                return f"{int(round(puan))}/100"
            except Exception:
                pass

    return "Yok"


def karsilastirma_satiri_uret(ozellik, row1, row2, kolonlar):
    deger1 = "Yok"
    deger2 = "Yok"

    for kolon in kolonlar:
        if kolon in row1.index and str(row1[kolon]) != "nan":
            deger1 = row1[kolon]
            break

    for kolon in kolonlar:
        if kolon in row2.index and str(row2[kolon]) != "nan":
            deger2 = row2[kolon]
            break

    return {
        "Özellik": ozellik,
        "1. Ürün": deger1,
        "2. Ürün": deger2
    }


def karsilastirma_tablo_olustur(row1, row2, kaynak_turu):
    satirlar = [
        {"Özellik": "Ürün", "1. Ürün": karsilastirma_urun_adi(row1), "2. Ürün": karsilastirma_urun_adi(row2)},
        {"Özellik": "Ortalama Piyasa Fiyatı", "1. Ürün": karsilastirma_fiyat(row1), "2. Ürün": karsilastirma_fiyat(row2)},
        {"Özellik": "Puan", "1. Ürün": karsilastirma_puan(row1), "2. Ürün": karsilastirma_puan(row2)},
        karsilastirma_satiri_uret("Marka", row1, row2, ["Marka"]),
        karsilastirma_satiri_uret("Kategori", row1, row2, ["Kategori", "Ana_Kategori"]),
        karsilastirma_satiri_uret("Alt Kategori", row1, row2, ["Alt_Kategori"]),
        karsilastirma_satiri_uret("Segment", row1, row2, ["Segment"]),
    ]

    if kaynak_turu == "Hazır Teknoloji Ürünleri":
        ekstra = [
            ("Kullanım Amacı", ["Kullanım Amacı"]),
            ("İşlemci", ["İşlemci"]),
            ("RAM", ["RAM"]),
            ("Depolama", ["Depolama"]),
            ("GPU", ["GPU"]),
            ("Ekran", ["Ekran"]),
            ("Batarya", ["Batarya (mAh)", "Pil Ömrü", "Pil Ömrü (gün)"]),
            ("Kamera", ["Kamera (MP)"]),
            ("5G", ["5G"]),
            ("NFC", ["NFC"]),
            ("Su Geçirmezlik", ["Su Geçirmezlik"]),
            ("İşletim Sistemi", ["İşletim Sistemi"]),
            ("Bağlantı", ["Bağlantı Türü"]),
            ("Gürültü Engelleme", ["Gürültü Engelleme"]),
            ("Mikrofon", ["Mikrofon"]),
            ("GPS", ["GPS"]),
        ]

    elif kaynak_turu == "Elektronik Ev Eşyaları":
        ekstra = [
            ("Kullanım Amacı", ["Kullanim_Amaci"]),
            ("Özellikler", ["Ozellikler"]),
            ("Enerji Sınıfı", ["Enerji_Sinifi"]),
            ("Renk", ["Renk"]),
            ("Garanti", ["Garanti_Ay"]),
            ("Kaynak Site", ["Kaynak_Site"]),
            ("Popülerlik", ["Populerlik"]),
        ]

    else:
        ekstra = [
            ("Soket", ["Soket"]),
            ("RAM Tipi", ["RAM_Tipi"]),
            ("Watt", ["Watt"]),
            ("Kapasite", ["Kapasite"]),
            ("Uyumluluk", ["Uyumluluk"]),
            ("RGB", ["RGB"]),
            ("Boyut", ["Boyut"]),
            ("Çözünürlük", ["Cozunurluk"]),
            ("VRAM", ["VRAM"]),
            ("Kaynak", ["Kaynak"]),
            ("Popülerlik", ["Populerlik"]),
        ]

    for ozellik, kolonlar in ekstra:
        satir = karsilastirma_satiri_uret(ozellik, row1, row2, kolonlar)
        if satir["1. Ürün"] != "Yok" or satir["2. Ürün"] != "Yok":
            satirlar.append(satir)

    return pd.DataFrame(satirlar)


def karsilastirma_dataframe_getir(kaynak_turu, kategori_secimi):
    if kaynak_turu == "Hazır Teknoloji Ürünleri":
        if tech_df.empty:
            return pd.DataFrame()

        df = tech_df.copy()

        if "Kategori" in df.columns and kategori_secimi != "Tümü":
            df = df[df["Kategori"].astype(str) == str(kategori_secimi)]

        if "FIYAT_SAYI" not in df.columns:
            if "Fiyat_TL" in df.columns:
                df["FIYAT_SAYI"] = pd.to_numeric(df["Fiyat_TL"], errors="coerce").fillna(0).astype(int)
            elif "Fiyat (TL)" in df.columns:
                df["FIYAT_SAYI"] = pd.to_numeric(df["Fiyat (TL)"], errors="coerce").fillna(0).astype(int)

        return df.drop_duplicates(subset=["Model"], keep="first").copy()

    if kaynak_turu == "Elektronik Ev Eşyaları":
        if ev_df.empty:
            return pd.DataFrame()

        df = ev_df.copy()

        if "Alt_Kategori" in df.columns and kategori_secimi != "Tümü":
            df = df[df["Alt_Kategori"].astype(str) == str(kategori_secimi)]

        return df.drop_duplicates(subset=["Marka", "Model"], keep="first").copy()

    if pc_df.empty:
        return pd.DataFrame()

    df = pc_df.copy()

    if "Alt_Kategori" in df.columns and kategori_secimi != "Tümü":
        df = df[df["Alt_Kategori"].astype(str) == str(kategori_secimi)]

    return df.drop_duplicates(subset=["Alt_Kategori", "Marka", "Model"], keep="first").copy()


def karsilastirma_urun_listesi(df):
    if df.empty:
        return []

    liste = []

    for index, row in df.iterrows():
        ad = karsilastirma_urun_adi(row)

        kategori_bilgi = ""
        if "Alt_Kategori" in row.index and str(row["Alt_Kategori"]) != "nan":
            kategori_bilgi = f" / {row['Alt_Kategori']}"
        elif "Kategori" in row.index and str(row["Kategori"]) != "nan":
            kategori_bilgi = f" / {row['Kategori']}"

        fiyat = karsilastirma_fiyat(row)
        liste.append((f"{ad}{kategori_bilgi} - {fiyat}", index))

    return liste

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
    siralama,
    marka="Farketmez"
):
    sonuc = pc_parcalari_getir(alt_kategori, min_butce, max_butce)

    if sonuc.empty:
        return sonuc

    if marka != "Farketmez" and "Marka" in sonuc.columns:
        sonuc = sonuc[sonuc["Marka"].astype(str).str.upper() == str(marka).upper()]

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


def pc_kurulum_kategorileri(kurulum_tipi="Temel Sistem"):
    temel = [
        "İşlemci",
        "Ekran Kartı",
        "Anakart",
        "RAM",
        "SSD",
        "Güç Kaynağı",
        "Kasa",
        "Soğutucu"
    ]

    if kurulum_tipi == "Tam Kurulum":
        return temel + ["HDD", "Monitör", "Klavye", "Mouse"]

    return temel


def pc_butce_oranlari(kurulum_tipi="Temel Sistem"):
    if kurulum_tipi == "Tam Kurulum":
        return {
            "İşlemci": 0.15,
            "Ekran Kartı": 0.30,
            "Anakart": 0.09,
            "RAM": 0.08,
            "SSD": 0.07,
            "HDD": 0.04,
            "Güç Kaynağı": 0.06,
            "Kasa": 0.05,
            "Soğutucu": 0.04,
            "Monitör": 0.09,
            "Klavye": 0.015,
            "Mouse": 0.015,
        }

    return {
        "İşlemci": 0.18,
        "Ekran Kartı": 0.35,
        "Anakart": 0.12,
        "RAM": 0.10,
        "SSD": 0.08,
        "Güç Kaynağı": 0.07,
        "Kasa": 0.05,
        "Soğutucu": 0.05
    }


def tek_sistem_fast_olustur(min_butce, max_butce, hedef_fiyat, kullanim, seed, ana_havuzlar, varyasyon, kurulum_tipi="Temel Sistem"):
    oranlar = pc_butce_oranlari(kurulum_tipi)
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

    zorunlu_kategoriler = ["Anakart", "RAM", "SSD", "Güç Kaynağı", "Kasa", "Soğutucu"]
    ek_kategoriler = ["HDD", "Monitör", "Klavye", "Mouse"] if kurulum_tipi == "Tam Kurulum" else []

    for kategori in zorunlu_kategoriler + ek_kategoriler:
        uyumlu_havuzlar[kategori] = uyumlu_havuz_filtrele(
            ana_havuzlar.get(kategori, pd.DataFrame()),
            kategori,
            soket=soket,
            ram_tipi=ram_tipi,
            min_psu=min_psu
        )

        secilen = fiyat_hedefine_yakin_satir(
            uyumlu_havuzlar[kategori],
            hedef_fiyat * oranlar.get(kategori, 0.03),
            varyasyon
        )

        # Temel parçalar olmadan sistem oluşturulmaz. Tam kurulum ek parçalarında veri yoksa sistem tamamen iptal edilmez.
        if secilen is None:
            if kategori in zorunlu_kategoriler:
                return None
            continue

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
        "kurulum_tipi": kurulum_tipi,
        "imza": sistem_imza(parcalar)
    }


def besli_pc_sistem_olustur(min_butce, max_butce, kullanim, seed, kurulum_tipi="Temel Sistem"):
    if pc_df.empty:
        return []

    kategoriler = pc_kurulum_kategorileri(kurulum_tipi)

    # En büyük hız kazancı burada: Veri seti her sistem için tekrar tekrar filtrelenmez.
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
                varyasyon=(i * 2) + varyasyon,
                kurulum_tipi=kurulum_tipi
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
    sistemler = besli_pc_sistem_olustur(0, max_butce, kullanim, seed, kurulum_tipi="Temel Sistem")
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
        # Alt kategori birebir eşleşmezse esnek eşleşme yap.
        # Örn: "Kahve Makinesi" seçilince "Espresso Kahve Makinesi" de gelsin.
        alt_norm = temizle_yazi(alt_kategori)
        birebir = sonuc[sonuc["Alt_Kategori"].astype(str).apply(temizle_yazi) == alt_norm]

        if not birebir.empty:
            sonuc = birebir
        else:
            sonuc = sonuc[
                sonuc["Alt_Kategori"]
                .astype(str)
                .apply(temizle_yazi)
                .str.contains(alt_norm, na=False)
                |
                pd.Series([alt_norm in temizle_yazi(x) for x in sonuc["Alt_Kategori"].astype(str)], index=sonuc.index)
            ]

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
<span class="badge-orange">💰 Ortalama Piyasa Fiyatı: {fiyat_formatla(veri_getir(row, 'Fiyat_TL'))}</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Alt_Kategori')}</span>
<span class="badge-purple">⭐ Puan: {kart_puani_getir(row)}</span>
<br><br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanim_Amaci')}<br>
🔌 <b>Soket:</b> {veri_getir(row, 'Soket')}<br>
🧠 <b>RAM Tipi:</b> {veri_getir(row, 'RAM_Tipi')}<br>
⚡ <b>Watt:</b> {veri_getir(row, 'Watt')}<br>
💾 <b>Kapasite:</b> {veri_getir(row, 'Kapasite')}<br>
🔗 <b>Uyumluluk:</b> {veri_getir(row, 'Uyumluluk')}<br>
🔥 <b>Popülerlik:</b> {kart_populerlik_getir(row)}<br>
💬 <b>Yorum Sayısı:</b> {veri_getir(row, 'Yorum_Sayisi')}<br>
🌈 <b>RGB:</b> {veri_getir(row, 'RGB')}<br>
📏 <b>Boyut:</b> {veri_getir(row, 'Boyut')}<br>
🖥️ <b>Çözünürlük:</b> {veri_getir(row, 'Cozunurluk')}<br>
🎮 <b>VRAM:</b> {veri_getir(row, 'VRAM')}<br>
📚 <b>Kaynak:</b> {veri_getir(row, 'Kaynak')}
{fiyat_karsilastirma_html('pc', row)}
</div>
""", unsafe_allow_html=True)


def ev_karti(row):
    st.markdown(f"""
<div class="product-card">
<div class="product-title">🏠 {veri_getir(row, 'Marka')} {veri_getir(row, 'Model')}</div><br>
<span class="badge-orange">💰 Ortalama Piyasa Fiyatı: {fiyat_formatla(veri_getir(row, 'Fiyat_TL'))}</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Alt_Kategori')}</span>
<span class="badge-purple">⭐ Puan: {kart_puani_getir(row)}</span>
<br><br>
📂 <b>Ana Kategori:</b> {veri_getir(row, 'Ana_Kategori')}<br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanim_Amaci')}<br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
⚙️ <b>Özellikler:</b> {veri_getir(row, 'Ozellikler')}<br>
🔋 <b>Enerji Sınıfı:</b> {veri_getir(row, 'Enerji_Sinifi')}<br>
🎨 <b>Renk:</b> {veri_getir(row, 'Renk')}<br>
🛡️ <b>Garanti:</b> {veri_getir(row, 'Garanti_Ay')} ay<br>
🔥 <b>Popülerlik:</b> {kart_populerlik_getir(row)}<br>
💬 <b>Yorum Sayısı:</b> {veri_getir(row, 'Yorum_Sayisi')}<br>
🛒 <b>Kaynak Site:</b> {veri_getir(row, 'Kaynak_Site')}
{fiyat_karsilastirma_html('ev', row)}
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




def chatbot_kategori_bul(mesaj_lower):
    kategori_kelimeleri = {
        "Toplama Bilgisayar": ["toplama", "sistem topla", "pc topla", "oyun sistemi", "parça", "parca"],
        "Elektronik Ev Eşyaları": ["süpürge", "supurge", "airfryer", "kahve", "klima", "ütü", "utu", "kettle", "blender", "ev eşyası", "ev esyasi", "çay makinesi", "cay makinesi", "robot", "dikey süpürge", "hava temizleyici", "vantilatör", "kombi", "kedi tuvaleti"],
        "Bilgisayar": ["laptop", "notebook", "bilgisayar", "oyun bilgisayarı", "oyun bilgisayari"],
        "Telefon": ["telefon", "iphone", "android", "samsung", "xiaomi", "redmi", "oppo", "vivo", "realme"],
        "Tablet": ["tablet", "ipad"],
        "Kulaklık": ["kulaklık", "kulaklik", "earbuds", "airpods", "kulak üstü", "kulak ustu"],
        "Akıllı Saat / Bileklik": ["akıllı saat", "akilli saat", "bileklik", "watch", "akıllı bileklik", "akilli bileklik"],
    }
    for kategori_adi, kelimeler in kategori_kelimeleri.items():
        if any(kelime in mesaj_lower for kelime in kelimeler):
            return kategori_adi
    return None



def chatbot_ev_alt_kategori_bul(mesaj_lower):
    """Chatbotun elektronik ev eşyasında alt kategoriyi paneldeki filtreler kadar doğru yakalaması için kullanılır."""
    alt_map = {
        "Dikey Süpürge": ["dikey süpürge", "dikey supurge", "şarjlı süpürge", "sarjli supurge"],
        "Robot Süpürge": ["robot süpürge", "robot supurge", "robot vacuum"],
        "Elektrikli Süpürge": ["elektrikli süpürge", "elektrikli supurge", "süpürge", "supurge"],
        "Buharlı Ütü": ["buharlı ütü", "buharli utu", "ütü", "utu"],
        "Buhar Kazanlı Ütü": ["buhar kazanlı", "buhar kazanli"],
        "Airfryer": ["airfryer", "fritöz", "fritoz"],
        "Espresso Kahve Makinesi": ["espresso"],
        "Filtre Kahve Makinesi": ["filtre kahve"],
        "Türk Kahvesi Makinesi": ["türk kahvesi", "turk kahvesi"],
        "Kahve Makinesi": ["kahve makinesi", "kahve"],
        "Çay Makinesi": ["çay makinesi", "cay makinesi"],
        "Kettle": ["kettle", "su ısıtıcı", "su isitici"],
        "Hava Temizleyici": ["hava temizleyici", "hava temizleme"],
        "Klima": ["klima"],
        "Akıllı Kedi Tuvaleti": ["kedi tuvaleti", "akıllı kedi", "akilli kedi"],
    }

    mevcut_altlar = []
    if not ev_df.empty and "Alt_Kategori" in ev_df.columns:
        mevcut_altlar = [str(x) for x in ev_df["Alt_Kategori"].dropna().unique()]

    for hedef_alt, kelimeler in alt_map.items():
        if any(k in mesaj_lower for k in kelimeler):
            if hedef_alt in mevcut_altlar:
                return hedef_alt
            # Datasette "Dikey Süpürge" yerine "Şarjlı Dikey Süpürge" gibi daha uzun ad varsa onu yakala.
            hedef_norm = temizle_yazi(hedef_alt)
            for alt in mevcut_altlar:
                alt_norm = temizle_yazi(alt)
                if hedef_norm in alt_norm or alt_norm in hedef_norm:
                    return alt
            # Sadece süpürge gibi genel ifadelerde, varsa en yakın süpürge alt kategorisini döndür.
            if "supurge" in hedef_norm:
                for alt in mevcut_altlar:
                    if "supurge" in temizle_yazi(alt):
                        return alt
            return hedef_alt

    return "Tümü"


def chatbot_pc_kurulum_tipi_bul(mesaj_lower):
    if any(k in mesaj_lower for k in ["tam kurulum", "monitör", "monitor", "klavye", "mouse", "fare", "hdd"]):
        return "Tam Kurulum"
    return "Temel Sistem"

def chatbot_urun_istegi_var_mi(mesaj_lower):
    urun_kelimeleri = [
        "öner", "oner", "al", "alayım", "alayim", "ne al", "bütçe", "butce", "tl", "₺",
        "telefon", "bilgisayar", "laptop", "tablet", "kulaklık", "kulaklik", "saat",
        "toplama", "süpürge", "supurge", "kahve", "airfryer", "ütü", "utu"
    ]
    return any(kelime in mesaj_lower for kelime in urun_kelimeleri)


def chatbot_resmi_kontrol(mesaj_lower):
    ton_kelimeleri = [
        "saygılı ol", "saygili ol", "resmi konuş", "resmi konus", "kanka deme",
        "samimi konuşma", "samimi konusma", "düzgün konuş", "duzgun konus"
    ]
    return any(kelime in mesaj_lower for kelime in ton_kelimeleri)


def chatbot_kriter_mesaji(kategori, min_butce, max_butce, ram=0, kullanim=""):
    satirlar = [
        "Algılanan kriterler:",
        f"- Kategori: {kategori if kategori else 'Belirtilmedi'}",
        f"- Bütçe aralığı: {fiyat_formatla(min_butce)} - {fiyat_formatla(max_butce)}",
    ]
    if ram and int(ram) > 0:
        satirlar.append(f"- Minimum RAM: {ram} GB")
    if kullanim:
        satirlar.append(f"- Kullanım amacı: {kullanim}")
    return "\n".join(satirlar)


def chatbot_sonuc_mesaji(sonuc, kategori, min_butce, max_butce, ram=0, kullanim=""):
    kriter = chatbot_kriter_mesaji(kategori, min_butce, max_butce, ram, kullanim)
    if sonuc is None:
        adet = 0
    elif isinstance(sonuc, list):
        adet = len(sonuc)
    elif hasattr(sonuc, "empty"):
        adet = 0 if sonuc.empty else len(sonuc)
    else:
        adet = 0
    if adet == 0:
        return (
            "Belirttiğiniz kriterlere uygun ürün bulunamadı.\n\n"
            f"{kriter}\n\n"
            "Öneri: Bütçe aralığını artırabilir, kategori tercihini netleştirebilir veya filtreleri azaltabilirsiniz."
        )
    return (
        f"Belirttiğiniz kriterlere göre {adet} uygun sonuç bulundu. En uygun seçenekler aşağıda listelenmiştir.\n\n"
        f"{kriter}"
    )


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

            mesaj_lower = kullanici_mesaji.lower()

            if chatbot_resmi_kontrol(mesaj_lower):
                bot_mesaji = "Elbette. Bundan sonra daha resmi, saygılı ve açıklayıcı bir dil kullanacağım."
                st.session_state.mesajlar.append({
                    "rol": "assistant",
                    "icerik": bot_mesaji
                })
                st.rerun()

            if not chatbot_urun_istegi_var_mi(mesaj_lower):
                bot_mesaji = (
                    "Size yardımcı olabilmem için lütfen ürün kategorisini, bütçe aralığını ve kullanım amacını belirtiniz.\n\n"
                    "Örnek: 40000-50000 TL arası oyun için bilgisayar öner."
                )
                st.session_state.mesajlar.append({
                    "rol": "assistant",
                    "icerik": bot_mesaji
                })
                st.rerun()

            chat_kategori, chat_min_butce, chat_max_butce, chat_ram, chat_kullanim = chatbot_metnini_anla(
                kullanici_mesaji
            )

            kategori_mesajdan = chatbot_kategori_bul(mesaj_lower)

            llm_sonuc = None
            try:
                gelen_llm_sonuc = llm_analiz_et(kullanici_mesaji)
                if gelen_llm_sonuc is not None:
                    llm_sonuc = gelen_llm_sonuc
            except Exception:
                llm_sonuc = None

            if llm_sonuc is not None:
                llm_kategori = llm_sonuc.get("kategori", None)
                if kategori_mesajdan:
                    chat_kategori = kategori_mesajdan
                elif llm_kategori and str(llm_kategori).strip() not in ["", "None", "null"]:
                    chat_kategori = llm_kategori

                chat_min_butce = int(llm_sonuc.get("min_butce", chat_min_butce))
                chat_max_butce = int(llm_sonuc.get("max_butce", chat_max_butce))
                chat_ram = int(llm_sonuc.get("ram", chat_ram))
                chat_kullanim = llm_sonuc.get("kullanim", chat_kullanim)
            else:
                if kategori_mesajdan:
                    chat_kategori = kategori_mesajdan

            if kategori_mesajdan is None:
                bot_mesaji = (
                    "Ürün kategorisi net olarak belirtilmediği için öneri listesi oluşturamadım.\n\n"
                    f"{chatbot_kriter_mesaji(None, chat_min_butce, chat_max_butce, chat_ram, chat_kullanim)}\n\n"
                    "Lütfen kategori de belirterek tekrar deneyiniz. Örneğin: 30000 TL bütçeyle telefon öner."
                )
                st.session_state.mesajlar.append({
                    "rol": "assistant",
                    "icerik": bot_mesaji
                })
                st.rerun()

            if int(chat_max_butce) < 100:
                bot_mesaji = (
                    "Belirttiğiniz bütçe aralığında uygun teknoloji ürünü bulunması mümkün görünmüyor.\n\n"
                    f"{chatbot_kriter_mesaji(chat_kategori, chat_min_butce, chat_max_butce, chat_ram, chat_kullanim)}\n\n"
                    "Öneri: Bütçeyi artırarak veya daha düşük fiyatlı bir kategori seçerek tekrar deneyebilirsiniz."
                )
                st.session_state.mesajlar.append({
                    "rol": "assistant",
                    "icerik": bot_mesaji
                })
                st.rerun()

            if chat_kategori == "Toplama Bilgisayar":
                st.session_state.aktif_mod = "pc_build"
                st.session_state.sonuc = None
                st.session_state.pc_build = None
                chat_kurulum_tipi = chatbot_pc_kurulum_tipi_bul(mesaj_lower)
                st.session_state.pc_builds = besli_pc_sistem_olustur(
                    min_butce=chat_min_butce,
                    max_butce=chat_max_butce,
                    kullanim=chat_kullanim,
                    seed=st.session_state.pc_random_seed,
                    kurulum_tipi=chat_kurulum_tipi
                )
                st.session_state.selected_pc_build_index = 0
                bot_mesaji = chatbot_sonuc_mesaji(
                    st.session_state.pc_builds,
                    chat_kategori,
                    chat_min_butce,
                    chat_max_butce,
                    chat_ram,
                    chat_kullanim
                )

            elif chat_kategori == "Elektronik Ev Eşyaları":
                st.session_state.aktif_mod = "ev_esyalari"
                st.session_state.pc_build = None
                st.session_state.pc_builds = []
                chat_ev_alt_kategori = chatbot_ev_alt_kategori_bul(mesaj_lower)
                st.session_state.sonuc = ev_esyasi_oner(
                    ana_kategori="Tümü",
                    alt_kategori=chat_ev_alt_kategori,
                    min_butce=chat_min_butce,
                    max_butce=chat_max_butce,
                    siralama=chatbot_siralama,
                    kullanim="",
                    min_puan=0,
                    enerji_sinifi="Farketmez",
                    kaynak_site="Farketmez"
                )
                bot_mesaji = chatbot_sonuc_mesaji(
                    st.session_state.sonuc,
                    chat_kategori,
                    chat_min_butce,
                    chat_max_butce,
                    chat_ram,
                    chat_kullanim
                )

            else:
                st.session_state.aktif_mod = "chatbot"
                st.session_state.pc_build = None
                st.session_state.pc_builds = []
                st.session_state.sonuc = hazir_urun_oner_db(
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

                bot_mesaji = chatbot_sonuc_mesaji(
                    st.session_state.sonuc,
                    chat_kategori,
                    chat_min_butce,
                    chat_max_butce,
                    chat_ram,
                    chat_kullanim
                )

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
        "Elektronik Ev Eşyaları",
        "Ürün Karşılaştırma"
    ]
)

st.sidebar.markdown("### Bütçe Aralığı (TL)")

butce_col1, butce_col2 = st.sidebar.columns(2)

with butce_col1:
    min_butce = st.number_input(
        "Minimum",
        min_value=0,
        max_value=250000,
        value=int(st.session_state.get("min_butce", 10000)),
        step=100,
        key="min_butce_input"
    )

with butce_col2:
    max_butce = st.number_input(
        "Maximum",
        min_value=0,
        max_value=250000,
        value=int(st.session_state.get("max_butce", 30000)),
        step=100,
        key="max_butce_input"
    )

if min_butce > max_butce:
    st.sidebar.warning("Minimum bütçe maximum bütçeden büyük olamaz. Değerler otomatik düzeltildi.")
    min_butce, max_butce = max_butce, min_butce

st.session_state.min_butce = int(min_butce)
st.session_state.max_butce = int(max_butce)

siralama_secenekleri = [
    "Akıllı Sıralama",
    "Popülerlik",
    "Teknik Puan",
    "En Düşük Fiyat",
    "En Yüksek Fiyat",
    "Yorum Sayısı"
]

if kategori in ["Bilgisayar", "Toplama Bilgisayar"]:
    siralama_secenekleri.append("Bellek / RAM")

siralama = st.sidebar.selectbox(
    "Listeyi Sırala",
    siralama_secenekleri
)

kullanim_secimleri = {
    "Telefon": ["", "Günlük Kullanım", "Oyun", "Kamera / Fotoğraf", "Video İçerik Üretimi", "Sosyal Medya", "Uzun Pil", "İş"],
    "Bilgisayar": ["", "Oyun", "Yazılım", "Ofis", "Okul", "Tasarım", "Video Edit", "Günlük Kullanım"],
    "Tablet": ["", "Okul", "Not Alma", "Çizim", "Film / Dizi", "Günlük Kullanım", "İş"],
    "Kulaklık": ["", "Müzik", "Oyun", "Spor", "Gürültü Engelleme", "Toplantı", "Günlük Kullanım"],
    "Akıllı Saat / Bileklik": ["", "Spor", "Sağlık Takibi", "Günlük Kullanım", "Bildirim", "Uzun Pil"],
    "Toplama Bilgisayar": ["", "Oyun", "Yazılım", "Tasarım", "Video Edit", "Ofis"],
    "Elektronik Ev Eşyaları": ["", "Ev Temizliği", "Pratik Yemek", "Akıllı Ev", "Alerji", "Hava Kalitesi", "Güvenlik", "Günlük Kullanım"],
    "Ürün Karşılaştırma": [""]
}

kullanim = st.sidebar.selectbox(
    "Kullanım Amacı",
    kullanim_secimleri.get(kategori, [""])
)

min_ram = 0

hazir_marka = "Farketmez"
hazir_min_depolama = "Farketmez"
hazir_min_kamera = "Farketmez"
hazir_min_batarya = "Farketmez"
hazir_5g = "Farketmez"
hazir_nfc = "Farketmez"
hazir_su = "Farketmez"
hazir_gpu = "Farketmez"
hazir_isletim = "Farketmez"
hazir_kulaklik_tipi = "Farketmez"
hazir_baglanti = "Farketmez"
hazir_gurultu = "Farketmez"
hazir_mikrofon = "Farketmez"
hazir_min_pil = "Farketmez"
hazir_gps = "Farketmez"
hazir_min_pil_gun = "Farketmez"
hazir_cpu_marka = "Farketmez"
hazir_cpu_seviye = "Farketmez"
hazir_gpu_seviye = "Farketmez"
hazir_panel = "Farketmez"
hazir_min_hz = "Farketmez"

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
ev_marka = "Farketmez"


if kategori == "Ürün Karşılaştırma":
    st.sidebar.markdown("### ⚖️ Ürün Karşılaştırma")

    karsilastirma_kaynak = st.sidebar.selectbox(
        "Karşılaştırma Grubu",
        [
            "Hazır Teknoloji Ürünleri",
            "Elektronik Ev Eşyaları",
            "Toplama PC Parçaları"
        ],
        key="karsilastirma_kaynak"
    )

    if karsilastirma_kaynak == "Hazır Teknoloji Ürünleri":
        if tech_df.empty or "Kategori" not in tech_df.columns:
            karsilastirma_kategoriler = ["Tümü"]
        else:
            karsilastirma_kategoriler = ["Tümü"] + sorted(tech_df["Kategori"].dropna().astype(str).unique())

    elif karsilastirma_kaynak == "Elektronik Ev Eşyaları":
        if ev_df.empty or "Alt_Kategori" not in ev_df.columns:
            karsilastirma_kategoriler = ["Tümü"]
        else:
            karsilastirma_kategoriler = ["Tümü"] + sorted(ev_df["Alt_Kategori"].dropna().astype(str).unique())

    else:
        if pc_df.empty or "Alt_Kategori" not in pc_df.columns:
            karsilastirma_kategoriler = ["Tümü"]
        else:
            karsilastirma_kategoriler = ["Tümü"] + sorted(pc_df["Alt_Kategori"].dropna().astype(str).unique())

    karsilastirma_kategori = st.sidebar.selectbox(
        "Karşılaştırılacak Kategori",
        karsilastirma_kategoriler,
        key="karsilastirma_kategori"
    )

    karsilastirma_df = karsilastirma_dataframe_getir(
        karsilastirma_kaynak,
        karsilastirma_kategori
    )

    urun_listesi = karsilastirma_urun_listesi(karsilastirma_df)

    if len(urun_listesi) < 2:
        st.sidebar.warning("Bu grupta karşılaştırma için yeterli ürün yok.")
    else:
        urun_etiketleri = [x[0] for x in urun_listesi]

        urun1_label = st.sidebar.selectbox(
            "1. Ürün",
            urun_etiketleri,
            key="karsilastirma_urun1"
        )

        urun2_label = st.sidebar.selectbox(
            "2. Ürün",
            urun_etiketleri,
            index=1,
            key="karsilastirma_urun2"
        )

        if st.sidebar.button("⚖️ Ürünleri Karşılaştır", key="karsilastirma_button"):
            urun1_index = dict(urun_listesi)[urun1_label]
            urun2_index = dict(urun_listesi)[urun2_label]

            st.session_state.karsilastirma = {
                "kaynak": karsilastirma_kaynak,
                "urun1": karsilastirma_df.loc[urun1_index].to_dict(),
                "urun2": karsilastirma_df.loc[urun2_index].to_dict()
            }

            st.session_state.aktif_mod = "karsilastirma"
            st.session_state.sonuc = None
            st.session_state.pc_build = None
            st.session_state.pc_builds = []
            st.rerun()



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
            marka_cpu = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "İşlemci"), key="cpu_marka")
            soket_cpu = st.selectbox("Soket", ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"], key="cpu_soket")

        with st.sidebar.expander("Anakart"):
            marka_mb = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Anakart"), key="mb_marka")
            soket_mb = st.selectbox("Soket", ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"], key="mb_soket")
            ramtip_mb = st.selectbox("RAM Tipi", ["Farketmez", "DDR4", "DDR5"], key="mb_ramtip")

        with st.sidebar.expander("RAM"):
            marka_ram = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "RAM"), key="ram_marka")
            ramtip_ram = st.selectbox("RAM Tipi", ["Farketmez", "DDR4", "DDR5"], key="ram_ramtip")
            rgb_ram = st.selectbox("RGB", ["Farketmez", "Var", "Yok"], key="ram_rgb")

        with st.sidebar.expander("Ekran Kartı"):
            marka_gpu = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Ekran Kartı"), key="gpu_marka")
            min_vram_gpu = st.selectbox("Minimum VRAM", ["Farketmez", "4", "6", "8", "12", "16", "24"], key="gpu_vram")

        with st.sidebar.expander("SSD"):
            marka_ssd = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "SSD"), key="ssd_marka")
            min_kapasite_ssd = st.selectbox("Minimum Kapasite", ["Farketmez", "500", "1000", "2000", "4000"], key="ssd_capacity")

        with st.sidebar.expander("HDD"):
            marka_hdd = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "HDD"), key="hdd_marka")
            min_kapasite_hdd = st.selectbox("Minimum Kapasite", ["Farketmez", "500", "1000", "2000", "4000"], key="hdd_capacity")

        with st.sidebar.expander("Güç Kaynağı"):
            marka_psu = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Güç Kaynağı"), key="psu_marka")
            min_watt_psu = st.selectbox("Minimum Watt", ["Farketmez", "500", "600", "650", "750", "850", "1000"], key="psu_watt")

        with st.sidebar.expander("Kasa"):
            marka_kasa = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Kasa"), key="case_marka")
            rgb_kasa = st.selectbox("RGB", ["Farketmez", "Var", "Yok"], key="case_rgb")

        with st.sidebar.expander("Soğutucu"):
            marka_cooler = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Soğutucu"), key="cooler_marka")
            soket_cooler = st.selectbox("Soket", ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"], key="cooler_soket")
            rgb_cooler = st.selectbox("RGB", ["Farketmez", "Var", "Yok"], key="cooler_rgb")

        with st.sidebar.expander("Monitör"):
            marka_monitor = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Monitör"), key="monitor_marka")
            monitor_rgb = st.selectbox("RGB", ["Farketmez", "Var", "Yok"], key="monitor_rgb")

        with st.sidebar.expander("Klavye"):
            marka_keyboard = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Klavye"), key="keyboard_marka")
            rgb_keyboard = st.selectbox("RGB", ["Farketmez", "Var", "Yok"], key="keyboard_rgb")

        with st.sidebar.expander("Mouse"):
            marka_mouse = st.selectbox("Marka", marka_listesi_getir(pc_df, "Alt_Kategori", "Mouse"), key="mouse_marka")
            rgb_mouse = st.selectbox("RGB", ["Farketmez", "Var", "Yok"], key="mouse_rgb")
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
                    siralama,
                    marka=marka_cpu
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
                    siralama,
                    marka=marka_mb
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
                    siralama,
                    marka=marka_ram
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
                    siralama,
                    marka=marka_gpu
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
                    siralama,
                    marka=marka_ssd
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
                    siralama,
                    marka=marka_hdd
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
                    siralama,
                    marka=marka_psu
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
                    siralama,
                    marka=marka_kasa
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
                    siralama,
                    marka=marka_cooler
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
                    siralama,
                    marka=marka_monitor
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
                    siralama,
                    marka=marka_keyboard
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
                    siralama,
                    marka=marka_mouse
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
        pc_kurulum_tipi = st.sidebar.selectbox(
            "Kurulum Tipi",
            ["Temel Sistem", "Tam Kurulum"],
            help="Temel Sistem sadece kasa içi parçaları toplar. Tam Kurulum monitör, klavye, mouse ve varsa HDD de ekler.",
            key="pc_kurulum_tipi_select"
        )
        st.session_state.pc_kurulum_tipi = pc_kurulum_tipi

        if st.sidebar.button("🖥️ Sistem Topla", key="build_pc_button"):
            st.session_state.aktif_mod = "pc_build"
            st.session_state.pc_build = None
            st.session_state.pc_builds = besli_pc_sistem_olustur(
                min_butce=min_butce,
                max_butce=max_butce,
                kullanim=kullanim,
                seed=st.session_state.pc_random_seed,
                kurulum_tipi=pc_kurulum_tipi
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
    ev_tipi = ev_alt_kategori_tipi(ev_alt_kategori)

    ev_marka = st.sidebar.selectbox(
        "Marka",
        marka_listesi_getir(ev_df, "Alt_Kategori", ev_alt_kategori, "Ana_Kategori", ev_ana_kategori),
        key="ev_marka"
    )

    ev_min_puan = st.sidebar.slider(
        "Minimum Puan",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0
    )

    ev_site = st.sidebar.selectbox(
        "Kaynak Site",
        ["Farketmez", "Hepsiburada", "Trendyol", "Teknosa", "MediaMarkt", "Vatan Bilgisayar", "Amazon Türkiye", "n11"]
    )

    if ev_tipi in ["pisirme", "icecek", "hava_iklim", "utu", "beyaz_esya"]:
        ev_enerji = st.sidebar.selectbox(
            "Enerji Sınıfı",
            ["Farketmez", "A+++", "A++", "A+", "A", "B", "C", "Belirtilmemiş"]
        )

    if ev_tipi in ["pisirme", "icecek", "hava_iklim", "utu"]:
        ev_min_watt = st.sidebar.selectbox(
            "Minimum Watt",
            ["Farketmez", "500", "800", "1000", "1200", "1500", "1800", "2000", "2200", "2500", "3000"]
        )

    if ev_tipi == "supurge":
        ev_min_emis = st.sidebar.selectbox(
            "Minimum Emiş Gücü / Pa",
            ["Farketmez", "1000", "2000", "3000", "4000", "5000", "6000", "7000"]
        )

    if ev_tipi in ["supurge", "pisirme", "icecek", "evcil"]:
        hazne_etiketi = "Minimum Hazne / Litre"
        if ev_tipi == "evcil":
            hazne_etiketi = "Minimum Atık/Hazne Kapasitesi"
        ev_min_hazne = st.sidebar.selectbox(
            hazne_etiketi,
            ["Farketmez", "1", "2", "3", "4", "5", "6", "7", "8"]
        )

    if ev_tipi in ["supurge", "icecek", "hava_iklim", "evcil", "guvenlik"]:
        ev_wifi = st.sidebar.selectbox(
            "Wi-Fi / Akıllı Bağlantı",
            ["Farketmez", "Var", "Yok"]
        )

    if ev_tipi in ["guvenlik"]:
        ev_rgb = st.sidebar.selectbox(
            "RGB / Işık",
            ["Farketmez", "Var", "Yok"]
        )

    ev_garanti = st.sidebar.selectbox(
        "Minimum Garanti",
        ["Farketmez", "12", "24", "36"]
    )


elif kategori in ["Telefon", "Bilgisayar", "Tablet", "Kulaklık", "Akıllı Saat / Bileklik"]:
    st.sidebar.markdown("### 🔎 Kategoriye Özel Filtreler")

    hazir_marka = st.sidebar.selectbox(
        "Marka",
        hazir_urun_markalari_getir(kategori),
        key=f"hazir_marka_{kategori}"
    )

    if kategori == "Telefon":
        hazir_min_depolama = st.sidebar.selectbox("Minimum Depolama", ["Farketmez", "64", "128", "256", "512", "1000"], key="telefon_depolama")
        hazir_min_kamera = st.sidebar.selectbox("Minimum Kamera / MP", ["Farketmez", "12", "24", "48", "64", "108", "200"], key="telefon_kamera")
        hazir_min_batarya = st.sidebar.selectbox("Minimum Batarya / mAh", ["Farketmez", "3000", "4000", "4500", "5000", "5500", "6000"], key="telefon_batarya")
        hazir_5g = st.sidebar.selectbox("5G", ["Farketmez", "Evet", "Hayır"], key="telefon_5g")
        hazir_nfc = st.sidebar.selectbox("NFC", ["Farketmez", "Evet", "Hayır"], key="telefon_nfc")
        hazir_su = st.sidebar.selectbox("Su Geçirmezlik", ["Farketmez", "Evet", "Hayır"], key="telefon_su")

    elif kategori == "Bilgisayar":
        hazir_cpu_marka = st.sidebar.selectbox("İşlemci Markası", ["Farketmez", "Intel", "AMD", "Apple"], key="bilgisayar_cpu_marka")
        hazir_cpu_seviye = st.sidebar.selectbox("İşlemci Seviyesi", ["Farketmez", "Giriş", "Orta", "Üst", "Premium"], key="bilgisayar_cpu_seviye")
        min_ram = st.sidebar.selectbox("Minimum RAM", [0, 4, 8, 12, 16, 24, 32, 64], index=2, key="bilgisayar_ram")
        hazir_min_depolama = st.sidebar.selectbox("Minimum Depolama", ["Farketmez", "256", "512", "1000", "2000", "4000"], key="bilgisayar_depolama")
        hazir_gpu = st.sidebar.selectbox("GPU Tercihi", ["Farketmez", "RTX", "GTX", "Radeon", "Intel", "Apple", "Paylaşımlı"], key="bilgisayar_gpu")
        hazir_gpu_seviye = st.sidebar.selectbox("GPU Seviyesi", ["Farketmez", "Paylaşımlı", "Giriş", "Orta", "Üst"], key="bilgisayar_gpu_seviye")
        hazir_panel = st.sidebar.selectbox("Ekran Paneli", ["Farketmez", "IPS", "OLED", "AMOLED", "Retina"], key="bilgisayar_panel")
        hazir_min_hz = st.sidebar.selectbox("Minimum Yenileme Hızı", ["Farketmez", "60", "90", "120", "144", "165", "240"], key="bilgisayar_hz")
        hazir_isletim = st.sidebar.selectbox("İşletim Sistemi", secenekleri_getir(tech_df, kategori, "İşletim Sistemi"), key="bilgisayar_isletim")

    elif kategori == "Tablet":
        hazir_min_depolama = st.sidebar.selectbox("Minimum Depolama", ["Farketmez", "64", "128", "256", "512", "1000"], key="tablet_depolama")
        hazir_min_batarya = st.sidebar.selectbox("Minimum Batarya / mAh", ["Farketmez", "4000", "6000", "8000", "10000"], key="tablet_batarya")
        hazir_panel = st.sidebar.selectbox("Ekran Paneli", ["Farketmez", "IPS", "OLED", "AMOLED", "Retina"], key="tablet_panel")
        hazir_min_hz = st.sidebar.selectbox("Minimum Yenileme Hızı", ["Farketmez", "60", "90", "120", "144"], key="tablet_hz")
        hazir_isletim = st.sidebar.selectbox("İşletim Sistemi", secenekleri_getir(tech_df, kategori, "İşletim Sistemi"), key="tablet_isletim")
        hazir_su = st.sidebar.selectbox("Su Geçirmezlik", ["Farketmez", "Evet", "Hayır"], key="tablet_su")

    elif kategori == "Kulaklık":
        hazir_kulaklik_tipi = st.sidebar.selectbox("Kulaklık Tipi", secenekleri_getir(tech_df, kategori, "Kulaklık Tipi"), key="kulaklik_tipi")
        hazir_baglanti = st.sidebar.selectbox("Bağlantı Türü", secenekleri_getir(tech_df, kategori, "Bağlantı Türü"), key="kulaklik_baglanti")
        hazir_gurultu = st.sidebar.selectbox("Gürültü Engelleme", ["Farketmez", "Evet", "Hayır"], key="kulaklik_gurultu")
        hazir_mikrofon = st.sidebar.selectbox("Mikrofon", ["Farketmez", "Evet", "Hayır"], key="kulaklik_mikrofon")
        hazir_min_pil = st.sidebar.selectbox("Minimum Pil Ömrü / saat", ["Farketmez", "5", "10", "20", "30", "40", "50"], key="kulaklik_pil")

    elif kategori == "Akıllı Saat / Bileklik":
        hazir_gps = st.sidebar.selectbox("GPS", ["Farketmez", "Evet", "Hayır"], key="saat_gps")
        hazir_su = st.sidebar.selectbox("Su Geçirmezlik", ["Farketmez", "Evet", "Hayır"], key="saat_su")
        hazir_min_pil_gun = st.sidebar.selectbox("Minimum Pil Ömrü / gün", ["Farketmez", "1", "3", "5", "7", "10", "14"], key="saat_pil")
        hazir_isletim = st.sidebar.selectbox("İşletim Sistemi", secenekleri_getir(tech_df, kategori, "İşletim Sistemi"), key="saat_isletim")


st.sidebar.markdown("---")

if kategori not in ["Toplama Bilgisayar", "Ürün Karşılaştırma"]:
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
                marka=ev_marka
            )

        else:
            st.session_state.aktif_mod = "panel"
            sonuc = hazir_urun_oner_db(
                kategori,
                min_butce,
                max_butce,
                min_ram,
                siralama,
                kullanim
            )

            hazir_filtreler = {
                "marka": hazir_marka,
                "min_depolama": hazir_min_depolama,
                "min_kamera": hazir_min_kamera,
                "min_batarya": hazir_min_batarya,
                "bes_g": hazir_5g,
                "nfc": hazir_nfc,
                "su": hazir_su,
                "gpu_tercihi": hazir_gpu,
                "isletim": hazir_isletim,
                "kulaklik_tipi": hazir_kulaklik_tipi,
                "baglanti": hazir_baglanti,
                "gurultu": hazir_gurultu,
                "mikrofon": hazir_mikrofon,
                "min_pil": hazir_min_pil,
                "gps": hazir_gps,
                "min_pil_gun": hazir_min_pil_gun,
                "cpu_marka": hazir_cpu_marka,
                "cpu_seviye": hazir_cpu_seviye,
                "gpu_seviye": hazir_gpu_seviye,
                "panel": hazir_panel,
                "min_hz": hazir_min_hz
            }

            sonuc = hazir_urun_detay_filtrele(sonuc, kategori, hazir_filtreler)

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


if st.session_state.aktif_mod == "karsilastirma":
    st.subheader("⚖️ Ürün Karşılaştırma")

    bilgi = st.session_state.get("karsilastirma", None)

    if not bilgi:
        st.info("Soldaki panelden iki ürün seçip karşılaştırabilirsin.")

    else:
        row1 = pd.Series(bilgi["urun1"])
        row2 = pd.Series(bilgi["urun2"])
        kaynak = bilgi.get("kaynak", "Hazır Teknoloji Ürünleri")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
<div class="product-card">
<div class="product-title">1️⃣ {karsilastirma_urun_adi(row1)}</div><br>
<span class="badge-orange">💰 Ortalama Piyasa Fiyatı: {karsilastirma_fiyat(row1)}</span>
<span class="badge-purple">⭐ Puan: {karsilastirma_puan(row1)}</span>
</div>
""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
<div class="product-card">
<div class="product-title">2️⃣ {karsilastirma_urun_adi(row2)}</div><br>
<span class="badge-orange">💰 Ortalama Piyasa Fiyatı: {karsilastirma_fiyat(row2)}</span>
<span class="badge-purple">⭐ Puan: {karsilastirma_puan(row2)}</span>
</div>
""", unsafe_allow_html=True)

        tablo = karsilastirma_tablo_olustur(row1, row2, kaynak)
        st.dataframe(tablo, use_container_width=True, hide_index=True)

        st.markdown("### 🔎 Güncel Fiyat Kontrolü")

        col_link1, col_link2 = st.columns(2)

        with col_link1:
            if kaynak == "Elektronik Ev Eşyaları":
                st.markdown(fiyat_karsilastirma_html("ev", row1), unsafe_allow_html=True)
            elif kaynak == "Toplama PC Parçaları":
                st.markdown(fiyat_karsilastirma_html("pc", row1), unsafe_allow_html=True)
            else:
                st.markdown(hazir_urun_guvenilir_link_html(row1), unsafe_allow_html=True)

        with col_link2:
            if kaynak == "Elektronik Ev Eşyaları":
                st.markdown(fiyat_karsilastirma_html("ev", row2), unsafe_allow_html=True)
            elif kaynak == "Toplama PC Parçaları":
                st.markdown(fiyat_karsilastirma_html("pc", row2), unsafe_allow_html=True)
            else:
                st.markdown(hazir_urun_guvenilir_link_html(row2), unsafe_allow_html=True)

elif pc_build_ekrani_acik:
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
                    seed=st.session_state.pc_random_seed,
                    kurulum_tipi=st.session_state.get("pc_kurulum_tipi", "Temel Sistem")
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
<span class="badge-orange">💰 Ortalama Piyasa Fiyatı: {fiyat_formatla(veri_getir(row, 'FIYAT_SAYI'))}</span>
<span class="badge-blue">🏷️ {veri_getir(row, 'Kategori')}</span>
<span class="badge-purple">⭐ Puan: {kart_puani_getir(row)}</span>
<br><br>
🎯 <b>Kullanım Amacı:</b> {veri_getir(row, 'Kullanım Amacı')}<br>
📌 <b>Segment:</b> {veri_getir(row, 'Segment')}<br>
⚙️ <b>İşlemci:</b> {veri_getir(row, 'İşlemci')}<br>
🧠 <b>RAM:</b> {veri_getir(row, 'RAM')}<br>
💾 <b>Depolama:</b> {veri_getir(row, 'Depolama')}<br>
🎮 <b>GPU:</b> {veri_getir(row, 'GPU')}<br>
🖥️ <b>Ekran:</b> {veri_getir(row, 'Ekran')}<br>
{hazir_urun_guvenilir_link_html(row)}
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