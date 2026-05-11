import os
import pandas as pd
import streamlit as st

from recommender import (
    urun_oner,
    chatbot_metnini_anla,
    aciklama_uret,
    pc_alt_kategorileri_getir,
    pc_parca_oner,
    pc_sistem_topla,
    pc_sistem_aciklama_uret,
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


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "sonuc" not in st.session_state:
    st.session_state.sonuc = None

if "pc_build" not in st.session_state:
    st.session_state.pc_build = None

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

if "chat_siralama" not in st.session_state:
    st.session_state.chat_siralama = "Ucuzdan pahalıya"

if "llm_durum" not in st.session_state:
    st.session_state.llm_durum = ""

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []


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


ev_df = ev_esyalari_yukle()


def ev_ana_kategorileri_getir():
    if ev_df.empty:
        return ["Dataset bulunamadı"]
    return sorted(ev_df["Ana_Kategori"].dropna().unique())


def ev_alt_kategorileri_getir():
    if ev_df.empty:
        return ["Dataset bulunamadı"]
    return sorted(ev_df["Alt_Kategori"].dropna().unique())


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

    if siralama == "Ucuzdan pahalıya":
        sonuc = sonuc.sort_values(by=["Fiyat_TL", "Puan"], ascending=[True, False])
    else:
        sonuc = sonuc.sort_values(by=["Fiyat_TL", "Puan"], ascending=[False, False])

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

        username = st.text_input("Kullanıcı adı", key="login_username")
        email = st.text_input("E-posta", key="login_email")
        password = st.text_input("Şifre", type="password", key="login_password")

        if st.button("Giriş Yap"):
            if username.strip() == "" or email.strip() == "" or password.strip() == "":
                st.error("Kullanıcı adı, e-posta ve şifre boş bırakılamaz.")
            else:
                success, message, user = login_user(username, email, password)

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

        if st.button("Kayıt Ol"):
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

        if st.button("Doğrula"):
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

        if st.button("Şifre Sıfırlama Kodu Gönder"):
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

        if st.button("Şifreyi Güncelle"):
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


st.sidebar.markdown("### 🧪 Test Modu")

if st.sidebar.button("Test Kullanıcısı Olarak Gir"):
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


st.title("🤖 Akıllı Teknoloji Ürünleri Öneri Sistemi")

st.write(
    "Bu sistem; hazır teknoloji ürünleri, toplama bilgisayar parçaları ve elektronik ev eşyaları için "
    "bütçe ve kullanım amacına göre öneri sunar."
)

st.sidebar.write(f"👤 Kullanıcı: {st.session_state.user['username']}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


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
    "Sıralama",
    ["Ucuzdan pahalıya", "Pahalıdan ucuza"]
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

pc_mod = None
pc_alt_kategori = None
pc_ozellik_tipi = None
pc_ozellik_degeri = None

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
            "Alt kategoriye göre parça göster",
            "Bütçeye göre uyumlu sistem topla"
        ]
    )

    alt_kategoriler = pc_alt_kategorileri_getir()

    if pc_mod == "Alt kategoriye göre parça göster":
        pc_alt_kategori = st.sidebar.selectbox("Alt Kategori", alt_kategoriler)

        if pc_alt_kategori in ["RAM", "Anakart"]:
            pc_ozellik_tipi = "RAM_Tipi"
            pc_ozellik_degeri = st.sidebar.selectbox("RAM Tipi", ["Farketmez", "DDR4", "DDR5"])

        elif pc_alt_kategori in ["İşlemci", "Soğutucu"]:
            pc_ozellik_tipi = "Soket"
            pc_ozellik_degeri = st.sidebar.selectbox("Soket", ["Farketmez", "AM4", "AM5", "LGA1700", "LGA1851"])

        elif pc_alt_kategori == "Ekran Kartı":
            pc_ozellik_tipi = "VRAM"
            pc_ozellik_degeri = st.sidebar.selectbox("Minimum VRAM", ["Farketmez", "4", "6", "8", "12", "16"])

        elif pc_alt_kategori in ["SSD", "HDD"]:
            pc_ozellik_tipi = "Kapasite"
            pc_ozellik_degeri = st.sidebar.selectbox("Minimum Kapasite", ["Farketmez", "500", "1000", "2000", "4000"])

        elif pc_alt_kategori == "Güç Kaynağı":
            pc_ozellik_tipi = "Watt"
            pc_ozellik_degeri = st.sidebar.selectbox("Minimum Watt", ["Farketmez", "500", "600", "650", "750", "850", "1000"])

        elif pc_alt_kategori in ["Kasa", "Klavye", "Mouse", "Monitör"]:
            pc_ozellik_tipi = "RGB"
            pc_ozellik_degeri = st.sidebar.selectbox("RGB", ["Farketmez", "Var", "Yok"])


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


def veri_getir(row, kolon):
    if kolon in row.index and str(row[kolon]) != "nan":
        return row[kolon]
    return "Yok"


def fiyat_formatla(deger):
    try:
        return f"{int(float(deger)):,}".replace(",", ".") + " TL"
    except Exception:
        return str(deger)


def sayisal_filtre_degeri(seri):
    return seri.astype(str).str.extract(r"(\d+)")[0].fillna(0).astype(int)


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


st.sidebar.markdown("---")

if st.sidebar.button("Öneri Getir"):
    st.session_state.pc_build = None
    st.session_state.sonuc = None

    if kategori == "Toplama Bilgisayar":
        if pc_mod == "Alt kategoriye göre parça göster":
            st.session_state.aktif_mod = "pc_parca"

            sonuc = pc_parca_oner(
                alt_kategori=pc_alt_kategori,
                min_butce=min_butce,
                max_butce=max_butce,
                siralama=siralama,
                kullanim=kullanim
            )

            if pc_ozellik_degeri and pc_ozellik_degeri != "Farketmez":
                if pc_ozellik_tipi in ["VRAM", "Kapasite", "Watt"]:
                    sonuc = sonuc[
                        sayisal_filtre_degeri(sonuc[pc_ozellik_tipi]) >= int(pc_ozellik_degeri)
                    ]
                elif pc_ozellik_tipi in ["RAM_Tipi", "Soket", "RGB"]:
                    sonuc = sonuc[
                        sonuc[pc_ozellik_tipi].astype(str).str.lower()
                        == pc_ozellik_degeri.lower()
                    ]

            st.session_state.sonuc = sonuc

        else:
            st.session_state.aktif_mod = "pc_build"
            st.session_state.pc_build = pc_sistem_topla(
                max_butce=max_butce,
                kullanim=kullanim,
                min_butce=min_butce
            )

    elif kategori == "Elektronik Ev Eşyaları":
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
        st.session_state.sonuc = urun_oner(
            kategori,
            min_butce,
            max_butce,
            min_ram,
            siralama,
            kullanim
        )

    st.session_state.kategori = kategori
    st.session_state.min_butce = min_butce
    st.session_state.max_butce = max_butce
    st.session_state.min_ram = min_ram


st.markdown("---")
st.subheader("💬 Sohbet Botu ile Ürün Önerisi")

chatbot_siralama = st.selectbox(
    "Chatbot sonuç sıralaması",
    ["Ucuzdan pahalıya", "Pahalıdan ucuza"],
    key="chatbot_siralama_select"
)

for mesaj in st.session_state.mesajlar:
    with st.chat_message(mesaj["rol"]):
        st.write(mesaj["icerik"])

kullanici_mesaji = st.chat_input(
    "Mesaj yaz... Örnek: 50000 TL bütçem var, oyun için toplama bilgisayar istiyorum"
)

if kullanici_mesaji:
    st.session_state.mesajlar.append({
        "rol": "user",
        "icerik": kullanici_mesaji
    })

    with st.chat_message("user"):
        st.write(kullanici_mesaji)

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
            st.session_state.llm_durum = "✅ LLM kullanıldı"
        else:
            st.session_state.llm_durum = "⚠️ LLM analiz çalışmadı, kural tabanlı sistem kullanıldı"

    except Exception:
        st.session_state.llm_durum = "⚠️ LLM bağlantısı yok, kural tabanlı sistem kullanıldı"

    if llm_sonuc is not None:
        chat_kategori = llm_sonuc.get("kategori", chat_kategori)
        chat_min_butce = int(llm_sonuc.get("min_butce", chat_min_butce))
        chat_max_butce = int(llm_sonuc.get("max_butce", chat_max_butce))
        chat_ram = int(llm_sonuc.get("ram", chat_ram))
        chat_kullanim = llm_sonuc.get("kullanim", chat_kullanim)

        if "toplama" in mesaj_lower or "parça" in mesaj_lower or "parca" in mesaj_lower:
            chat_kategori = "Toplama Bilgisayar"

    if urun_istegi_var:
        st.session_state.chat_siralama = chatbot_siralama
        st.session_state.kategori = chat_kategori
        st.session_state.min_butce = chat_min_butce
        st.session_state.max_butce = chat_max_butce
        st.session_state.min_ram = chat_ram

        if chat_kategori == "Toplama Bilgisayar":
            st.session_state.aktif_mod = "pc_build"
            st.session_state.sonuc = None
            st.session_state.pc_build = pc_sistem_topla(
                max_butce=chat_max_butce,
                kullanim=chat_kullanim,
                min_butce=chat_min_butce
            )
            bot_mesaji = f"{llm_cevap}\n\nAnladığım kriterler: Toplama Bilgisayar, bütçe: {chat_min_butce}-{chat_max_butce} TL."

        elif chat_kategori == "Elektronik Ev Eşyaları":
            st.session_state.aktif_mod = "ev_esyalari"
            st.session_state.pc_build = None
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
            st.session_state.sonuc = urun_oner(
                chat_kategori,
                chat_min_butce,
                chat_max_butce,
                chat_ram,
                chatbot_siralama,
                chat_kullanim
            )
            bot_mesaji = f"{llm_cevap}\n\nAnladığım kriterler: {chat_kategori}, {chat_min_butce}-{chat_max_butce} TL."

    else:
        bot_mesaji = llm_cevap

    st.session_state.mesajlar.append({
        "rol": "assistant",
        "icerik": bot_mesaji
    })

    with st.chat_message("assistant"):
        st.write(bot_mesaji)


if st.button("Sohbeti Temizle"):
    st.session_state.mesajlar = []
    st.session_state.sonuc = None
    st.session_state.pc_build = None
    st.rerun()


st.markdown("---")


if st.session_state.aktif_mod == "pc_build":
    st.subheader("🖥️ Bütçeye Göre Uyumlu Toplama Bilgisayar Sistemi")

    build = st.session_state.pc_build

    if build is None:
        st.info("Toplama bilgisayar önerisi için bütçe girip öneri alabilirsin.")

    elif not build.get("basarili", False):
        st.warning(build.get("mesaj", "Bu bütçeye uygun uyumlu sistem oluşturulamadı."))

        if "parcalar" in build:
            st.info("Bütçeyi aşan en yakın sistem parçaları aşağıda gösteriliyor.")
            for parca_adi, row in build["parcalar"].items():
                st.markdown(f"## {parca_adi}")
                pc_parca_karti(row)

    else:
        st.success(
            f"Toplam sistem fiyatı: {fiyat_formatla(build['toplam_fiyat'])} "
            f"/ Bütçe: {fiyat_formatla(build['butce'])}"
        )

        st.info(pc_sistem_aciklama_uret(build))

        for parca_adi, row in build["parcalar"].items():
            st.markdown(f"## {parca_adi}")
            pc_parca_karti(row)


elif st.session_state.aktif_mod == "pc_parca":
    st.subheader("🧩 Toplama Bilgisayar Parçaları")

    sonuc = st.session_state.sonuc

    if sonuc is None:
        st.info("Soldan alt kategori seçip parça listeleyebilirsin.")

    elif sonuc.empty:
        st.warning("Bu kriterlere uygun parça bulunamadı.")

    else:
        st.success(f"{len(sonuc)} parça bulundu.")
        for _, row in sonuc.iterrows():
            pc_parca_karti(row)


elif st.session_state.aktif_mod == "ev_esyalari":
    st.subheader("🏠 Elektronik Ev Eşyaları")

    sonuc = st.session_state.sonuc

    if ev_df.empty:
        st.error("elektronik_ev_esyalari_dataset.csv bulunamadı. Dosyayı app.py ile aynı klasöre koymalısın.")

    elif sonuc is None:
        st.info("Soldan elektronik ev eşyası filtrelerini seçip öneri alabilirsin.")

    elif sonuc.empty:
        st.warning("Bu kriterlere uygun elektronik ev eşyası bulunamadı.")

    else:
        st.success(f"{len(sonuc)} ürün bulundu.")
        for _, row in sonuc.iterrows():
            ev_karti(row)


else:
    st.subheader("🔎 Önerilen Ürünler")

    if st.session_state.sonuc is None:
        st.info("Soldaki panelden filtreleme yapabilir veya sohbet botuna isteğini yazabilirsin.")

    else:
        sonuc = st.session_state.sonuc

        if sonuc.empty:
            st.warning("Bu kriterlere uygun ürün bulunamadı.")

        else:
            st.success(f"{len(sonuc)} ürün bulundu.")

            for _, row in sonuc.iterrows():
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

                aciklama = aciklama_uret(
                    row,
                    st.session_state.kategori,
                    st.session_state.min_butce,
                    st.session_state.max_butce,
                    st.session_state.min_ram
                )

                st.info(aciklama)