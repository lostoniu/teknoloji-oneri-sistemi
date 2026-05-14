import os
from pathlib import Path
import pandas as pd
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

"""
import_products_to_supabase.py

Bu script 3 CSV dosyasını Supabase PostgreSQL içindeki products tablosuna basar.

Çalıştırmadan önce:
1) .env dosyanda DB bilgileri olmalı:
   DB_HOST=
   DB_NAME=
   DB_USER=
   DB_PASSWORD=
   DB_PORT=

2) Terminal:
   python import_products_to_supabase.py

Bu script app.py'nin logic'ini değiştirmez.
Sadece ürünleri database tablosuna aktarır.
"""

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATASETS = [
    {
        "file": "teknoloji_urunleri_dataset.csv",
        "source": "teknoloji",
        "kategori_col": "Kategori",
        "alt_col": None,
        "marka_col": "Marka",
        "model_col": "Model",
        "fiyat_cols": ["Fiyat_TL", "Fiyat (TL)", "FIYAT_SAYI"],
        "puan_cols": ["Topluluk_Puani", "Puan", "ONERI_PUANI"],
    },
    {
        "file": "pc_parts_dataset.csv",
        "source": "pc",
        "kategori_col": "Kategori",
        "alt_col": "Alt_Kategori",
        "marka_col": "Marka",
        "model_col": "Model",
        "fiyat_cols": ["Fiyat_TL"],
        "puan_cols": ["Topluluk_Puani", "Puan", "ONERI_PUANI"],
    },
    {
        "file": "elektronik_ev_esyalari_dataset.csv",
        "source": "ev",
        "kategori_col": "Ana_Kategori",
        "alt_col": "Alt_Kategori",
        "marka_col": "Marka",
        "model_col": "Model",
        "fiyat_cols": ["Fiyat_TL"],
        "puan_cols": ["Topluluk_Puani", "Puan"],
    },
]


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
    )


def temiz_str(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() in ["nan", "none", "null", ""]:
        return None
    return text


def sayiya_cevir(value):
    if pd.isna(value):
        return 0

    text = str(value)
    text = text.replace("TL", "")
    text = text.replace("₺", "")
    text = text.replace(".", "")
    text = text.replace(",", ".")
    text = text.strip()

    try:
        return int(float(text))
    except Exception:
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0


def fiyat_bul(row, cols):
    for col in cols:
        if col in row.index:
            val = sayiya_cevir(row[col])
            if val > 0:
                return val
    return 0


def puan_bul(row, cols):
    for col in cols:
        if col in row.index:
            try:
                val = float(row[col])
                if val > 0:
                    if val <= 10:
                        val *= 10
                    return int(round(val))
            except Exception:
                pass
    return 0


def kolon(row, col):
    if col and col in row.index:
        return temiz_str(row[col])
    return None


def create_table():
    sql = """
    CREATE TABLE IF NOT EXISTS products (
        id BIGSERIAL PRIMARY KEY,
        source TEXT NOT NULL,
        kategori TEXT,
        alt_kategori TEXT,
        marka TEXT,
        model TEXT,
        fiyat_tl INTEGER DEFAULT 0,
        puan INTEGER DEFAULT 0,
        populerlik TEXT,
        data JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_products_source ON products(source);
    CREATE INDEX IF NOT EXISTS idx_products_kategori ON products(kategori);
    CREATE INDEX IF NOT EXISTS idx_products_alt_kategori ON products(alt_kategori);
    CREATE INDEX IF NOT EXISTS idx_products_marka ON products(marka);
    CREATE INDEX IF NOT EXISTS idx_products_fiyat ON products(fiyat_tl);
    CREATE INDEX IF NOT EXISTS idx_products_puan ON products(puan);
    CREATE INDEX IF NOT EXISTS idx_products_model ON products(model);
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def clear_table():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE products RESTART IDENTITY;")
        conn.commit()


def import_dataset(info):
    path = BASE_DIR / info["file"]

    if not path.exists():
        print(f"Atlandı, dosya yok: {info['file']}")
        return 0

    print(f"Okunuyor: {info['file']}")
    df = pd.read_csv(path, low_memory=False)
    rows = []

    for _, row in df.iterrows():
        kategori = kolon(row, info["kategori_col"])
        alt_kategori = kolon(row, info["alt_col"])
        marka = kolon(row, info["marka_col"])
        model = kolon(row, info["model_col"])
        fiyat = fiyat_bul(row, info["fiyat_cols"])
        puan = puan_bul(row, info["puan_cols"])
        populerlik = kolon(row, "Populerlik")

        data = {
            k: (None if pd.isna(v) else v)
            for k, v in row.to_dict().items()
        }

        rows.append((
            info["source"],
            kategori,
            alt_kategori,
            marka,
            model,
            fiyat,
            puan,
            populerlik,
            json.dumps(data, ensure_ascii=False),
        ))

    sql = """
    INSERT INTO products
    (source, kategori, alt_kategori, marka, model, fiyat_tl, puan, populerlik, data)
    VALUES %s
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows, page_size=1000)
        conn.commit()

    print(f"Aktarıldı: {info['file']} -> {len(rows)} satır")
    return len(rows)


def main():
    create_table()

    cevap = input("products tablosu temizlenip yeniden doldurulsun mu? (e/h): ").strip().lower()
    if cevap == "e":
        clear_table()
        print("products tablosu temizlendi.")
    else:
        print("Temizleme yapılmadı. Var olan kayıtların üstüne ekleme yapılacak.")

    total = 0
    for info in DATASETS:
        total += import_dataset(info)

    print()
    print(f"Bitti. Toplam aktarılan satır: {total}")


if __name__ == "__main__":
    main()
