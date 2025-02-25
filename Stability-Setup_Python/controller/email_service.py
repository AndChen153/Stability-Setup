import os
import smtplib
from dotenv import load_dotenv
from helper.global_helpers import custom_print

# Load environment variables from .env file
load_dotenv()

class EmailSender:
    def __init__(self):
        # Retrieve credentials and settings from environment variables
        self.username = os.environ.get("EMAIL_USER")
        self.password = os.environ.get("EMAIL_PASS")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465

        # Validate essential variables are available
        if not self.username or not self.password:
            # TODO: add link here to instructions
            raise ValueError("Missing email credentials. Please set EMAIL_USER and EMAIL_PASS in your .env file.")

    def send_email(self, subject, body, to_email):
        """
        Sends an email with the given subject and body to the specified recipient.
        """
        # Construct the email message
        message = f"Subject: {subject}\n\n{body}"

        try:
            # Establish a secure session with the SMTP server using SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.sendmail(self.username, to_email, message)
            custom_print("Email sent successfully.")
        except Exception as e:
            custom_print(f"Error sending email: {e}")

# Example usage
if __name__ == "__main__":
    sender = EmailSender()
    sender.send_email(
        subject="Test Email",
        body="Hello,\n\nThis is a test email sent using a Python class with environment variables.",
        to_email="recipient@example.com"
    )
