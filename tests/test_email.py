import smtplib
from email.mime.text import MIMEText

sender_email = "22ug2-0023K@sltc.edu.lk"
sender_password = "foyb mahx txlj zhcc"  # 16-digit App Password
msg = MIMEText("Test message from Flask app.")
msg['Subject'] = "Test Alert"
msg['From'] = sender_email
msg['To'] = sender_email

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        print("✅ Gmail login successful")
        server.send_message(msg)
        print("✅ Email sent successfully")
except Exception as e:
    print("❌ Email sending failed:", str(e))
