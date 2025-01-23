# 继续提取body内容，解析成语义文本
# 批量处理全部原始文件
from utils import parse_email,handle_email_body
from config import config
import os
import json

DATA_DIR = config.DATA_DIR
RAW_EMAIL_DIR = os.path.join(DATA_DIR, "raw_emails")
PARSED_EMAIL_DIR = os.path.join(DATA_DIR, "parsed_emails")

for filename in os.listdir(PARSED_EMAIL_DIR):
    input_file_path = os.path.join(PARSED_EMAIL_DIR, filename)
    output_file_path = os.path.join(PARSED_EMAIL_DIR, f"{filename}.json")
    with open(input_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    email_json=json.loads(content)
    handled_body=handle_email_body(email_json['body'])
    print("handled_body",handled_body)
    email_json['handled_body']=handled_body
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(email_json, indent=4, ensure_ascii=False))

