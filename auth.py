import os
import random
import smtplib
import bcrypt
import psycopg2

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )


def send_verification_email(email, code):
    sender_email = os.getenv("MAIL_ADDRESS")
    sender_password = os.getenv("MAIL_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = "Doğrulama / Şifre Sıfırlama Kodunuz"

    body = f"""
Merhaba,

5 haneli kodunuz:

{code}

Bu kodu uygulamada ilgili alana giriniz.
"""

    msg.attach(MIMEText(body, "plain", "utf-8"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()


def register_user(username, email, password):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email)
        )

        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()
            return False, "Bu kullanıcı adı veya e-posta zaten kayıtlı."

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        verification_code = str(random.randint(10000, 99999))

        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, verification_code, is_verified)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (username, email, password_hash, verification_code, False)
        )

        conn.commit()

        send_verification_email(email, verification_code)

        cur.close()
        conn.close()

        return True, "Kayıt başarılı. Mail adresine doğrulama kodu gönderildi."

    except Exception as e:
        return False, f"Kayıt hatası: {e}"


def verify_user(email, code):
    try:
        conn = get_connection()
        cur = conn.cursor()

        email = str(email).strip()
        code = str(code).strip()

        cur.execute(
            """
            SELECT verification_code
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        result = cur.fetchone()

        if not result:
            cur.close()
            conn.close()
            return False, "Bu e-posta ile kayıtlı kullanıcı bulunamadı."

        db_code = str(result[0]).strip()

        if code != db_code:
            cur.close()
            conn.close()
            return False, "Doğrulama kodu yanlış."

        cur.execute(
            """
            UPDATE users
            SET is_verified = %s,
                verification_code = NULL
            WHERE email = %s
            """,
            (True, email)
        )

        conn.commit()

        cur.close()
        conn.close()

        return True, "Mail doğrulama başarılı. Artık giriş yapabilirsin."

    except Exception as e:
        return False, f"Doğrulama hatası: {e}"


def login_user(username, email, password):
    try:
        conn = get_connection()
        cur = conn.cursor()

        username = str(username).strip()
        email = str(email).strip()

        cur.execute(
            """
            SELECT id, username, email, password_hash, is_verified
            FROM users
            WHERE username = %s AND email = %s
            """,
            (username, email)
        )

        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()
            return False, "Kullanıcı adı veya e-posta yanlış.", None

        user_id = user[0]
        db_username = user[1]
        db_email = user[2]
        password_hash = user[3]
        is_verified = user[4]

        if not is_verified:
            cur.close()
            conn.close()
            return False, "Mail doğrulaması yapılmamış.", None

        password_ok = bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

        if not password_ok:
            cur.close()
            conn.close()
            return False, "Şifre yanlış.", None

        cur.close()
        conn.close()

        return True, "Giriş başarılı.", {
            "id": user_id,
            "username": db_username,
            "email": db_email
        }

    except Exception as e:
        return False, f"Giriş hatası: {e}", None


def sifre_sifirlama_kodu_gonder(email):
    try:
        conn = get_connection()
        cur = conn.cursor()

        email = str(email).strip()

        cur.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()
            return False, "Bu e-posta kayıtlı değil."

        code = str(random.randint(10000, 99999))

        cur.execute(
            """
            UPDATE users
            SET verification_code = %s
            WHERE email = %s
            """,
            (code, email)
        )

        conn.commit()

        send_verification_email(email, code)

        cur.close()
        conn.close()

        return True, "Şifre sıfırlama kodu mail adresine gönderildi."

    except Exception as e:
        return False, f"Şifre sıfırlama kodu gönderme hatası: {e}"


def sifreyi_guncelle(email, code, new_password):
    try:
        if str(new_password).strip() == "":
            return False, "Yeni şifre boş olamaz."

        conn = get_connection()
        cur = conn.cursor()

        email = str(email).strip()
        girilen_kod = str(code).strip()

        cur.execute(
            """
            SELECT verification_code
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        result = cur.fetchone()

        if not result:
            cur.close()
            conn.close()
            return False, "Bu e-posta kayıtlı değil."

        db_kod = str(result[0]).strip()

        if girilen_kod != db_kod:
            cur.close()
            conn.close()
            return False, f"Kod yanlış. DB kodu: {db_kod} / Girilen kod: {girilen_kod}"

        new_hash = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cur.execute(
            """
            UPDATE users
            SET password_hash = %s,
                verification_code = NULL,
                is_verified = %s
            WHERE email = %s
            """,
            (new_hash, True, email)
        )

        conn.commit()

        cur.close()
        conn.close()

        return True, "Şifre başarıyla güncellendi. Yeni şifrenle giriş yapabilirsin."

    except Exception as e:
        return False, f"Şifre güncelleme hatası: {e}"