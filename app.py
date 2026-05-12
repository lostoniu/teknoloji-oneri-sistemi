# =========================
# app.py
# =========================

import streamlit as st
import pandas as pd
import json
import psycopg2
import os

from dotenv import load_dotenv

from auth import (
    login_user,
    register_user,
    verify_user,
    sifre_sifirlama_kodu_gonder,
    sifreyi_guncelle
)

load_dotenv()

st.set_page_config(
    page_title="Akıllı Teknoloji Ürünleri Öneri Sistemi",
    layout="wide"
)

# =========================
# CSS
# =========================

st.markdown("""
<style>

.stApp{
    background-color:#081229;
    color:white;
}

.block-container{
    padding-top:2rem;
}

div[data-testid="stSidebar"]{
    background-color:#07101f;
}

h1,h2,h3,h4,h5,h6,p,label{
    color:white !important;
}

.stButton>button{
    background:#ff9800;
    color:white;
    border:none;
    border-radius:10px;
    font-weight:bold;
}

.stButton>button:hover{
    background:#ffb74d;
}

.product-card{
    background:#0f1d3a;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
    border:1px solid #22355e;
}

.badge{
    display:inline-block;
    padding:5px 10px;
    border-radius:20px;
    margin-right:5px;
    margin-top:5px;
    font-size:12px;
    font-weight:bold;
}

.price-badge{
    background:#ff9800;
    color:white;
}

.score-badge{
    background:#8e44ad;
    color:white;
}

.category-badge{
    background:#3498db;
    color:white;
}

.chat-fab{
    position:fixed;
    bottom:30px;
    right:30px;
    width:70px;
    height:70px;
    border-radius:50%;
    background:#ff9800;
    display:flex;
    justify-content:center;
    align-items:center;
    font-size:32px;
    color:white;
    z-index:9999;
    box-shadow:0 0 20px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

# =========================
# DATABASE
# =========================

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

# =========================
# SESSION
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("teknoloji_urunleri_dataset.csv")

# =========================
# FAVORITES
# =========================

def add_to_favorites(product):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO favorites
        (user_id, product_type, product_name, product_data)
        VALUES (%s,%s,%s,%s)
        """,
        (
            st.session_state.user["id"],
            str(product.get("kategori", "")),
            str(product.get("model", "")),
            json.dumps(product)
        )
    )

    conn.commit()
    cur.close()
    conn.close()

def get_favorites():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT product_name, product_data
        FROM favorites
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (st.session_state.user["id"],)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

# =========================
# SAVE BUILD
# =========================

def save_build(name, data, total_price):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO saved_builds
        (user_id, build_name, build_data, total_price)
        VALUES (%s,%s,%s,%s)
        """,
        (
            st.session_state.user["id"],
            name,
            json.dumps(data),
            total_price
        )
    )

    conn.commit()
    cur.close()
    conn.close()

def get_saved_builds():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT build_name,total_price
        FROM saved_builds
        WHERE user_id=%s
        ORDER BY id DESC
        """,
        (st.session_state.user["id"],)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

# =========================
# AUTH SCREEN
# =========================

def auth_screen():

    st.title("🤖 Akıllı Teknoloji Ürünleri Öneri Sistemi")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Giriş Yap",
        "Kayıt Ol",
        "Mail Doğrula",
        "Şifremi Unuttum"
    ])

    with tab1:

        st.subheader("Giriş Yap")

        login_input = st.text_input(
            "Kullanıcı adı / E-posta"
        )

        password = st.text_input(
            "Şifre",
            type="password"
        )

        if st.button("Giriş Yap"):

            success, message, user = login_user(
                login_input,
                password
            )

            if success:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()

            else:
                st.error(message)

    with tab2:

        st.subheader("Kayıt Ol")

        username = st.text_input("Kullanıcı Adı")
        email = st.text_input("E-posta")
        password = st.text_input("Şifre", type="password")

        if st.button("Kayıt Ol"):

            success, message = register_user(
                username,
                email,
                password
            )

            if success:
                st.success(message)
            else:
                st.error(message)

    with tab3:

        st.subheader("Mail Doğrula")

        email = st.text_input("Doğrulama Maili")
        code = st.text_input("5 Haneli Kod")

        if st.button("Doğrula"):

            success, message = verify_user(
                email,
                code
            )

            if success:
                st.success(message)
            else:
                st.error(message)

    with tab4:

        st.subheader("Şifre Sıfırla")

        email = st.text_input("Kayıtlı Mail")
        code = st.text_input("Kod")
        new_password = st.text_input(
            "Yeni Şifre",
            type="password"
        )

        if st.button("Kod Gönder"):

            success, message = sifre_sifirlama_kodu_gonder(email)

            if success:
                st.success(message)
            else:
                st.error(message)

        if st.button("Şifreyi Güncelle"):

            success, message = sifreyi_guncelle(
                email,
                code,
                new_password
            )

            if success:
                st.success(message)
            else:
                st.error(message)

# =========================
# LOGIN CONTROL
# =========================

if not st.session_state.logged_in:
    auth_screen()
    st.stop()

# =========================
# SIDEBAR
# =========================

st.sidebar.title("👤 Kullanıcı")

st.sidebar.success(
    st.session_state.user["username"]
)

if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.rerun()

# =========================
# FAVORITES SIDEBAR
# =========================

st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Favorilerim")

favorites = get_favorites()

for fav in favorites[:10]:
    st.sidebar.write("⭐ " + fav[0])

# =========================
# SAVED BUILDS
# =========================

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Kaydedilen Sistemler")

builds = get_saved_builds()

for build in builds[:10]:
    st.sidebar.write(
        f"🖥️ {build[0]} - {build[1]} TL"
    )

# =========================
# MAIN
# =========================

st.title("🤖 Akıllı Teknoloji Ürünleri Öneri Sistemi")

st.write("""
Bu sistem kullanıcı ihtiyacına göre:
- teknoloji ürünü
- elektronik ev eşyası
- toplama bilgisayar

önerileri sunar.
""")

# =========================
# FILTERS
# =========================

kategori = st.sidebar.selectbox(
    "Kategori",
    sorted(df["kategori"].dropna().unique())
)

min_price = int(df["fiyat"].min())
max_price = int(df["fiyat"].max())

price_range = st.sidebar.slider(
    "Bütçe",
    min_price,
    max_price,
    (min_price, max_price)
)

sort_option = st.sidebar.selectbox(
    "Listeyi Sırala",
    [
        "Popülerlik",
        "Teknik Puan",
        "Akıllı Sıralama",
        "Yeniden Eskiye",
        "En Düşük Fiyat",
        "En Yüksek Fiyat",
        "Yorum Sayısı",
        "Bellek (RAM)",
        "GPU Bellek",
        "Pil Gücü"
    ]
)

filtered_df = df[
    (df["kategori"] == kategori)
]

filtered_df = filtered_df[
    (filtered_df["fiyat"] >= price_range[0]) &
    (filtered_df["fiyat"] <= price_range[1])
]

# =========================
# SORT
# =========================

if sort_option == "En Düşük Fiyat":
    filtered_df = filtered_df.sort_values(
        by="fiyat"
    )

elif sort_option == "En Yüksek Fiyat":
    filtered_df = filtered_df.sort_values(
        by="fiyat",
        ascending=False
    )

elif sort_option == "Teknik Puan":

    if "puan" in filtered_df.columns:
        filtered_df = filtered_df.sort_values(
            by="puan",
            ascending=False
        )

# =========================
# PRODUCTS
# =========================

st.subheader("🛒 Ürünler")

for index, row in filtered_df.head(20).iterrows():

    st.markdown(
        f"""
        <div class="product-card">

        <h3>{row.get('marka','')} {row.get('model','')}</h3>

        <div class="badge category-badge">
        {row.get('kategori','')}
        </div>

        <div class="badge price-badge">
        {row.get('fiyat',0)} TL
        </div>

        <div class="badge score-badge">
        ⭐ {row.get('puan',0)}
        </div>

        <br><br>

        <b>İşlemci:</b> {row.get('islemci','Bilinmiyor')}<br>
        <b>RAM:</b> {row.get('ram','Bilinmiyor')}<br>
        <b>GPU:</b> {row.get('gpu','Bilinmiyor')}<br>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        f"⭐ Favorilere Ekle {index}"
    ):
        add_to_favorites(row.to_dict())
        st.success("Favorilere eklendi.")

# =========================
# BUILD SAVE
# =========================

st.markdown("---")
st.subheader("💾 Toplama Bilgisayar Kaydet")

build_name = st.text_input(
    "Sistem Adı"
)

build_price = st.number_input(
    "Toplam Fiyat"
)

if st.button("💾 Sistemi Kaydet"):

    save_build(
        build_name,
        {"example":"build"},
        build_price
    )

    st.success("Sistem kaydedildi.")

# =========================
# CHAT FLOAT BUTTON
# =========================

st.markdown(
    """
    <div class="chat-fab">
    💬
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# CHAT
# =========================

with st.expander("💬 Chatbot", expanded=False):

    user_message = st.text_input(
        "Mesaj Yaz"
    )

    if st.button("Gönder"):

        st.success(
            f"Mesaj alındı: {user_message}"
        )