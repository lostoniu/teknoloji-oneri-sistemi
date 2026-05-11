import requests
import json
import re

API_KEY = "NM6N1K0-Q3W4XRJ-NCX4GZQ-8NTHR1R"
WORKSPACE_SLUG = "teknoloji-oneri"

API_URL = f"http://localhost:3001/api/v1/workspace/{WORKSPACE_SLUG}/chat"


def json_temizle(text):
    try:
        return json.loads(text)
    except:
        pass

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass

    return None


def anythingllm_mesaj_gonder(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "message": prompt,
        "mode": "chat"
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=60)

        if response.status_code != 200:
            print("AnythingLLM Status:", response.status_code)
            print("AnythingLLM Cevap:", response.text)
            return None

        cevap = response.json()

        text = (
            cevap.get("textResponse")
            or cevap.get("text")
            or cevap.get("response")
            or cevap.get("message")
            or cevap.get("answer")
            or ""
        )

        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

        return text

    except Exception as hata:
        print("AnythingLLM bağlantı hatası:", hata)
        return None


def llm_analiz_et(metin):
    prompt = f"""
Sen bir teknoloji ürün öneri sistemi için kullanıcı isteğini analiz eden asistansın.

Sadece JSON döndür. Açıklama yazma.

JSON formatı:
{{
  "urun_istegi_var": true,
  "kategori": "Bilgisayar",
  "min_butce": 40000,
  "max_butce": 50000,
  "ram": 0,
  "kullanim": "Oyun"
}}

Kategoriler sadece şunlardan biri olabilir:
Telefon
Bilgisayar
Tablet
Kulaklık
Akıllı Saat / Bileklik

Kurallar:
- Eğer kullanıcı sadece sohbet ediyorsa "urun_istegi_var": false yap.
- Kullanıcı kulaklık derse kategori Kulaklık olsun.
- Kullanıcı laptop veya bilgisayar derse kategori Bilgisayar olsun.
- Kullanıcı telefon derse kategori Telefon olsun.
- Kullanıcı tablet derse kategori Tablet olsun.
- Kullanıcı saat veya bileklik derse kategori Akıllı Saat / Bileklik olsun.
- Kullanıcı 40000-50000 arası derse min_butce 40000, max_butce 50000 yap.
- Kullanıcı sadece 30000 TL derse min_butce 0, max_butce 30000 yap.
- Bütçe belirtilmemişse min_butce 0, max_butce 30000 yaz.
- RAM belirtilmemişse 0 yaz.
- Oyun, okul, ofis, tasarım, video, yazılım gibi kullanım amacı varsa kullanim alanına yaz.
- Kullanım amacı yoksa kullanim boş string olsun.
- Sadece JSON döndür.

Kullanıcı mesajı:
{metin}
"""

    text = anythingllm_mesaj_gonder(prompt)

    if text is None:
        return None

    return json_temizle(text)


def llm_sohbet_et(metin):
    prompt = f"""
Sen gençlerle konuşan doğal Türkçe kullanan samimi bir teknoloji danışmanısın.

ASLA:
- robot gibi konuşma
- resmi konuşma
- müşteri hizmetleri gibi davranma
- uzun uzun açıklama yapma

Örnek:
Kullanıcı: selam
Sen: Selam 😄

Kullanıcı: nasılsın
Sen: İyiyim kanka sen nasılsın 😄

Kullanıcı: 40000-50000 arası oyun bilgisayarı istiyorum
Sen: Tamam kanka, o fiyat aralığında oyun için uygun bilgisayarları listeliyorum 👇

Kısa, samimi ve Türkçe cevap ver.

Kullanıcı mesajı:
{metin}
"""

    cevap = anythingllm_mesaj_gonder(prompt)

    if cevap is None or cevap.strip() == "":
        return "Şu an cevap veremedim kanka 😄"

    return cevap