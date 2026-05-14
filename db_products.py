import os
import pandas as pd
import psycopg2
import streamlit as st


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
    )


@st.cache_data(ttl=3600, show_spinner=False)
def db_products_getir(
    source=None,
    kategori=None,
    alt_kategori=None,
    marka=None,
    min_fiyat=0,
    max_fiyat=999999999,
    min_puan=0,
    limit=100,
):
    """
    Products tablosundan filtreli ürün çeker.
    Sonuç 1 saat cache'de tutulur.
    """

    where = []
    params = []

    if source and source != "Tümü":
        where.append("source = %s")
        params.append(source)

    if kategori and kategori != "Tümü":
        where.append("kategori = %s")
        params.append(kategori)

    if alt_kategori and alt_kategori != "Tümü":
        where.append("(alt_kategori = %s OR alt_kategori ILIKE %s)")
        params.append(alt_kategori)
        params.append(f"%{alt_kategori}%")

    if marka and marka != "Farketmez":
        where.append("marka = %s")
        params.append(marka)

    where.append("fiyat_tl BETWEEN %s AND %s")
    params.extend([int(min_fiyat), int(max_fiyat)])

    where.append("puan >= %s")
    params.append(int(min_puan))

    where_sql = " AND ".join(where)

    sql = f"""
    SELECT
        id,
        source,
        kategori,
        alt_kategori,
        marka,
        model,
        fiyat_tl,
        puan,
        populerlik,
        data
    FROM products
    WHERE {where_sql}
    ORDER BY puan DESC, fiyat_tl ASC
    LIMIT %s
    """

    params.append(int(limit))

    with get_db_connection() as conn:
        df = pd.read_sql(sql, conn, params=params)

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def db_unique_values(source, column_name, kategori=None, alt_kategori=None):
    allowed = {
        "kategori": "kategori",
        "alt_kategori": "alt_kategori",
        "marka": "marka",
    }

    if column_name not in allowed:
        return []

    where = ["source = %s", f"{allowed[column_name]} IS NOT NULL"]
    params = [source]

    if kategori:
        where.append("kategori = %s")
        params.append(kategori)

    if alt_kategori:
        where.append("alt_kategori = %s")
        params.append(alt_kategori)

    sql = f"""
    SELECT DISTINCT {allowed[column_name]} AS value
    FROM products
    WHERE {' AND '.join(where)}
    ORDER BY value
    """

    with get_db_connection() as conn:
        df = pd.read_sql(sql, conn, params=params)

    return df["value"].dropna().astype(str).tolist()
