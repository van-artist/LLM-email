from dotenv import load_dotenv
from typing import Optional
import os

class Config:
    def __init__(self):
        load_dotenv()
        self.OPENAI_API_KEY = self._get_required_env('OPENAI_API_KEY')
        self.EMAIL_USERNAME = self._get_required_env('EMAIL_USERNAME')
        self.EMAIL_PASSWORD = self._get_required_env('EMAIL_PASSWORD')
        self.POP_SERVER = self._get_required_env('POP_SERVER')
        self.POP_PORT = int(os.getenv('POP_PORT', 995))
        self.IMAP_SERVER = self._get_required_env('IMAP_SERVER')
        self.IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
        self.SMTP_SERVER = self._get_required_env('SMTP_SERVER')
        self.SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
        self.GMAIL_PASSWORD = self._get_required_env('GMAIL_PASSWORD')
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, '../data')

    def _get_required_env(self, var_name:str)->Optional[str]:
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"{var_name} is required")
        return value
    
config = Config()

