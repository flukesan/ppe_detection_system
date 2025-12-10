"""
Notification utility for sending alerts via email and Line Notify.
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime, timedelta


class NotificationManager:
    """
    Manager for sending notifications via multiple channels.
    """

    def __init__(self, config: dict):
        """
        Initialize notification manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.last_alert_time = {}
        self.cooldown = config.get("cooldown", 60)  # seconds

    def send_email(
        self,
        subject: str,
        body: str,
        recipients: Optional[List[str]] = None,
    ) -> bool:
        """
        Send email notification.

        Args:
            subject: Email subject
            body: Email body
            recipients: List of recipient emails

        Returns:
            True if successful
        """
        if not self.config.get("enabled", False):
            return False

        email_config = self.config.get("email", {})

        if not email_config.get("username") or not email_config.get("password"):
            return False

        recipients = recipients or email_config.get("recipients", [])

        if not recipients:
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(
                email_config['smtp_server'],
                email_config['smtp_port']
            )

            if email_config.get('use_tls', True):
                server.starttls()

            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_line_notify(self, message: str) -> bool:
        """
        Send Line Notify message.

        Args:
            message: Message text

        Returns:
            True if successful
        """
        if not self.config.get("enabled", False):
            return False

        line_config = self.config.get("line_notify", {})
        token = line_config.get("token")

        if not token:
            return False

        try:
            url = "https://notify-api.line.me/api/notify"
            headers = {"Authorization": f"Bearer {token}"}
            data = {"message": message}

            response = requests.post(url, headers=headers, data=data)
            return response.status_code == 200

        except Exception as e:
            print(f"Failed to send Line Notify: {e}")
            return False

    def send_violation_alert(
        self,
        person_id: int,
        missing_ppe: List[str],
        screenshot_path: Optional[str] = None,
    ) -> bool:
        """
        Send violation alert through configured channels.

        Args:
            person_id: Person ID
            missing_ppe: List of missing PPE
            screenshot_path: Path to screenshot

        Returns:
            True if at least one notification was sent
        """
        # Check cooldown
        alert_key = f"person_{person_id}"
        current_time = datetime.now()

        if alert_key in self.last_alert_time:
            elapsed = (current_time - self.last_alert_time[alert_key]).total_seconds()
            if elapsed < self.cooldown:
                return False

        self.last_alert_time[alert_key] = current_time

        # Prepare message
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        missing_items = ", ".join(missing_ppe)

        subject = "⚠️ PPE Violation Alert"
        message = f"""
PPE Violation Detected!

Time: {timestamp}
Person ID: {person_id}
Missing PPE: {missing_items}

Please take immediate action.
        """.strip()

        success = False

        # Send email
        if self.config.get("email", False):
            success |= self.send_email(subject, message)

        # Send Line Notify
        if self.config.get("line_notify", False):
            line_message = f"🚨 {subject}\n{message}"
            success |= self.send_line_notify(line_message)

        return success
