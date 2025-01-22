# 测试代码
# Example usage
from utils import parse_email
from config import config
import os

DATA_DIR = config.DATA_DIR
test_input_file_path = os.path.join(DATA_DIR, "raw_emails", "1.txt")
test_output_file_path = os.path.join(DATA_DIR, "parsed_emails", "1.json")
parsed_email = parse_email(test_input_file_path)
# Save result
import json
with open(test_output_file_path, "w", encoding="utf-8") as f:
    json.dump(parsed_email, f, ensure_ascii=False, indent=4)

import json
print(json.dumps(parsed_email, ensure_ascii=False, indent=4))