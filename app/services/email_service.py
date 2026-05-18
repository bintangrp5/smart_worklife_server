import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


async def send_otp_email(email_to: str, otp_code: str):
    """
    Kirim email berisi kode OTP untuk verifikasi akun atau reset password.
    """
    message = MIMEMultipart()
    message["From"] = settings.SMTP_FROM
    message["To"] = email_to
    message["Subject"] = "Kode OTP Smart-WorkLife"

    body = f"""
    <html>
        <body>
            <h2>Verifikasi Akun Smart-WorkLife</h2>
            <p>Halo,</p>
            <p>Gunakan kode OTP berikut untuk memverifikasi akun atau mereset password Anda:</p>
            <h1 style="color: #4CAF50; letter-spacing: 5px;">{otp_code}</h1>
            <p>Kode ini berlaku selama 1 menit. Jangan bagikan kode ini kepada siapa pun.</p>
            <p>Terima kasih,<br>Tim Smart-WorkLife</p>
        </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True if settings.SMTP_PORT == 465 else False,
            start_tls=True if settings.SMTP_PORT == 587 else False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        # Dalam production, sebaiknya gunakan logger
        return False
