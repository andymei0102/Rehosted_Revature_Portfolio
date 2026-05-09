import smtplib
from dotenv import load_dotenv
import os
from email.message import EmailMessage

def send_email(recipient_email, subject,message, image_path=None):
    load_dotenv()

    email_addr = os.getenv("email")
    password = os.getenv("app_pwd")

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_addr
    msg['To'] = recipient_email

    msg.set_content(message)

    # attach image if provided
    if image_path:
        with open(image_path, 'rb') as img:
            img_data = img.read()
            img_name = os.path.basename(image_path)

        # Change subtype if needed (png, jpeg, etc.)
        msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=img_name)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_addr, password)
        server.send_message(msg)

if __name__ == "__main__":
    load_dotenv()
    print("Sending email...")
    send_email(
        os.getenv("EMAIL2"),
        "Driver report + image",
        "image test",
        image_path="output.jpg"
    )

    print("Success!")