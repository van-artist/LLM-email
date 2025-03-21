from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

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
        dirs= self._get_dirs()
        self.BASE_DIR = dirs[0]
        self.SRC_DIR = dirs[1]
        self.PROJECT_ROOT = dirs[2]
        self.DATA_DIR = dirs[3]

    def _get_required_env(self, var_name:str)->Optional[str]:
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"{var_name} is required")
        return value
    
    def _get_dirs(self) -> tuple[Path, Path,Path, Path]:
        BASE_DIR = Path(__file__).resolve().parent
        SRC_DIR = BASE_DIR.parent
        PROJECT_ROOT = SRC_DIR.parent
        DATA_DIR = PROJECT_ROOT / 'data'
        return BASE_DIR, SRC_DIR, PROJECT_ROOT,DATA_DIR
        

        
    
config = Config()

