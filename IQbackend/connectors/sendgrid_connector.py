from IQbackend import settings
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


class SendgridConnector:
    def __init__(self):
        self._sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self._otp_email = "noreply@iqland.ai"

    def send_email(self, from_email: str, to_email: str, subject: str, content: str, html_content: str = None):
        message = Mail(
            from_email=Email(f"IQLand <{from_email}>"),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=Content("text/plain", content)
        )

        if html_content:
            message.add_content(Content("text/html", html_content))

        return self._sg.send(message)

    def send_signup_email_verification_otp(self, to_email: str, html_content: str):
        subject = "Your Verification Code from IQLand"
        content = " "
        return self.send_email(self._otp_email, to_email, subject, content, html_content)
    
    def send_login_otp(self, to_email: str, html_content: str):
        subject = "Your Sign-In Verification Code from IQLand"
        content = " "
        return self.send_email(self._otp_email, to_email, subject, content, html_content)
    
    def send_reset_password_link(self, to_email: str, reset_link: str):
        subject = "[IQLand] Reset Password Link"
        content = f"Your can reset password by using this link: {reset_link}"
        return self.send_email(self._otp_email, to_email, subject, content)

    def send_report(self, to_email: str, address: str, html_content: str):
        subject = f"[IQLand] Here is your IQLAND.ai Report for {address}"
        content = " "
        return self.send_email(self._otp_email, to_email, subject, content, html_content)
    
    def send_trial_end_email(self, to_email: str, html_content: str):
        subject = "Your Free Trial Is Ending Soon - Don't Miss Out!"
        content = " "
        return self.send_email(self._otp_email, to_email, subject, content, html_content)
    
    def send_purchase_email(self, to_email: str, html_content: str):
        subject = "Payment Received – Thank You for Your Purchase!"
        content = " "
        return self.send_email(self._otp_email, to_email, subject, content, html_content)