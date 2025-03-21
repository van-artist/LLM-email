import smtplib
from email.message import EmailMessage
from typing import List, Optional


class EmailSender:
    def __init__(self, server: str, port: int, username: str, password: str):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        """
        Connects to the SMTP server and logs in.
        """
        try:
            print(f"Connecting to SMTP server: {self.server}:{self.port}")
            self.connection = smtplib.SMTP_SSL(self.server, self.port)
            self.connection.login(self.username, self.password)
            print("SMTP login successful.")
        except Exception as e:
            raise Exception(f"Error connecting to SMTP server: {e}")

    def disconnect(self):
        """
        Closes the SMTP connection.
        """
        if self.connection:
            try:
                self.connection.quit()
                print("SMTP connection closed.")
            except Exception as e:
                print(f"Error during SMTP disconnect: {e}")

    def send_email(
        self,
        to_email: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
    ):
        """
        Sends an email with optional CC, BCC, and attachments.
        """
        try:
            # Create the email
            msg = EmailMessage()
            msg["From"] = self.username
            msg["To"] = ", ".join(to_email)
            msg["Subject"] = subject
            if cc:
                msg["Cc"] = ", ".join(cc)
            if bcc:
                # BCC recipients are not added to the header
                to_email.extend(bcc)

            msg.set_content(body)

            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as file:
                            file_data = file.read()
                            file_name = file_path.split("/")[-1]
                            msg.add_attachment(
                                file_data,
                                maintype="application",
                                subtype="octet-stream",
                                filename=file_name,
                            )
                            print(f"Attachment added: {file_name}")
                    except Exception as e:
                        print(f"Error adding attachment {file_path}: {e}")

            if self.connection:
                self.connection.send_message(msg)
            else:
                raise Exception("No SMTP connection established. Call connect() before sending emails.")
            print(f"Email sent successfully to: {', '.join(to_email)}")

        except Exception as e:
            raise Exception(f"Error sending email: {e}")
