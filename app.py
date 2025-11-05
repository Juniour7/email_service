import os
import smtplib
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import threading

load_dotenv()

app = Flask(__name__)

SMTP_SERVER = os.getenv("EMAIL_HOST", "smtp-relay.brevo.com")
SMTP_PORT = int(os.getenv("EMAIL_PORT", 587))
SMTP_USER = os.getenv("EMAIL_HOST_USER")
SMTP_PASS = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", SMTP_USER)
SERVICE_API_KEY = os.getenv("EMAIL_SERVICE_KEY")  # optional security key

def send_email_async(to_email, subject, body, from_email=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = from_email or DEFAULT_FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Email sent to {to_email} from {msg['From']}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

@app.route("/send-email", methods=["POST"])
def send_email():
    # optional security header
    if SERVICE_API_KEY and request.headers.get("X-API-KEY") != SERVICE_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    to_email = data.get("to")
    subject = data.get("subject")
    body = data.get("body")
    from_email = data.get("from_email")

    if not all([to_email, subject, body]):
        return jsonify({"error": "Missing required fields"}), 400

    threading.Thread(target=send_email_async, args=(to_email, subject, body, from_email)).start()
    return jsonify({"status": "queued", "message": "Email send initiated"}), 200


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Brevo email service running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
