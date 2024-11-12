import os
import re
import time 
from core.model import reader_model,writer_model
from config import DATA_DIR,OPENAI_API_KEY
from utils import validate_json
import json



def main():
    
    email_path = os.path.join(DATA_DIR, "mails/1.txt")
    with open(email_path, "r", encoding="utf-8") as file:
        example_email = file.read()
    reader_reply = reader_model.generate_reply(example_email)
    output_path=os.path.join(DATA_DIR,f"jsons/output-{time.time()}.json")
    with open(output_path,"w",encoding="utf-8") as file:
        reader_reply = re.sub(r"```json|```", "", reader_reply).strip()
        validate_result=validate_json(json.loads(reader_reply))
        print("validate_result:",validate_result)
        file.write(reader_reply)
    writer_reply=writer_model.generate_reply(reader_reply)
    print("回复内容：")
    print(writer_reply)

if __name__ == "__main__":
    main()
