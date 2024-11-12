import os
import re
import time 
from core.model import reader_model,writer_model
from config import DATA_DIR
from utils import validate_student_email
from database.database import student_email_data_client
import json

def main():
    email_path = os.path.join(DATA_DIR, "mails/example.txt")
    reply_path= os.path.join(DATA_DIR,"replys/output.txt")
    info_path=os.path.join(DATA_DIR,f"jsons/output-{time.time()}.json")

    with open(email_path, "r", encoding="utf-8") as file:
        example_email = file.read()
    reader_reply = reader_model.generate_reply(example_email)
    reader_reply = re.sub(r"```json|```", "", reader_reply).strip()

    with open(info_path,"w",encoding="utf-8") as file:
        validate_result=validate_student_email(json.loads(reader_reply))
        print("validate_result:",validate_result)
        file.write(reader_reply)

    current_student_id=student_email_data_client.insert_student_email(reader_reply)
    current_student_email_json:dict=student_email_data_client.get_student_email_by_id(current_student_id)
    current_student_email_str = json.dumps(current_student_email_json, ensure_ascii=False, indent=4)
    writer_reply=writer_model.generate_reply(current_student_email_str)
    
    with open(reply_path,'w',encoding="utf-8") as file:
        file.write(writer_reply)
    print("回复内容：")
    print(writer_reply)
    

if __name__ == "__main__":
    main()
