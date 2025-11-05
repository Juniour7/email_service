# app.py
from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
import os
import threading

app = Flask(__name__)

# Background email sender (non-blocking)
def send_email_async(to, subject, body):
    def _send():
        try:
            msg = MIMEText(body, "html")
            msg["Subject"] = subject
            msg["From"] = os.getenv("EMAIL_FROM")
            msg["To"] = to

            with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
                server.starttls()
                server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
                server.send_message(msg)

            print(f"✅ Email sent to {to}")
        except Exception as e:
            print(f"❌ Email send failed: {e}")

    threading.Thread(target=_send).start()


@app.route("/send-email", methods=["POST"])
def send_email():
    """
    Public endpoint that Django will call to send emails.
    Requires a valid x-api-key header.
    """
    api_key = request.headers.get("x-api-key")
    if api_key != os.getenv("EMAIL_SERVICE_API_KEY"):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    to = data.get("to")
    subject = data.get("subject")
    body = data.get("body")

    if not all([to, subject, body]):
        return jsonify({"error": "Missing fields"}), 400

    send_email_async(to, subject, body)
    return jsonify({"status": "queued"}), 200


@app.route("/")
def home():
    return jsonify({"status": "Email Service Running ✅"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
