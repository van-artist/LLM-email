import json
import os
import threading
import uuid
from config import DATA_DIR
from .schemas.student_email import create_student_email_from_json, StudentEmail_to_dict

class StudentEmailDatabaseClient:
    def __init__(self):
        self.data_path = os.path.join(DATA_DIR, "db/db.json")
        self.lock = threading.Lock()

        # 初始化数据库文件
        if not os.path.exists(self.data_path):
            with open(self.data_path, "w", encoding="utf-8") as file:
                json.dump({"student_emails": []}, file)

    # 加载数据
    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {"student_emails": []}

    # 保存数据
    def save_data(self, data):
        with self.lock:
            with open(self.data_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

    # 插入新邮件，并生成唯一 ID
    def insert_student_email(self, json_data: str):
        student_email = create_student_email_from_json(json_data)
        if student_email is None:
            print("数据验证失败，无法插入。")
            return

        data = self.load_data()
        student_email_dict = StudentEmail_to_dict(student_email)
        student_email_dict["id"] = str(uuid.uuid4())  # 生成唯一 ID

        data["student_emails"].append(student_email_dict)
        self.save_data(data)
        print("插入成功！")
        return student_email_dict["id"]

    # 获取所有邮件
    def get_all_student_emails(self):
        data = self.load_data()
        return data.get("student_emails", [])

    # 根据索引获取特定邮件
    def get_student_email(self, index: int):
        data = self.load_data()
        try:
            return data["student_emails"][index]
        except IndexError:
            print(f"索引 {index} 超出范围")
            return None

    # 根据 ID 获取特定邮件
    def get_student_email_by_id(self, email_id: str):
        data = self.load_data()
        for email in data["student_emails"]:
            if email.get("id") == email_id:
                return email
        print(f"未找到 ID 为 {email_id} 的邮件")
        return None

    # 更新邮件
    def update_student_email(self, email_id: str, json_data: str):
        student_email = create_student_email_from_json(json_data)
        if student_email is None:
            print("数据验证失败，无法更新。")
            return

        data = self.load_data()
        updated = False
        for index, email in enumerate(data["student_emails"]):
            if email.get("id") == email_id:
                student_email_dict = StudentEmail_to_dict(student_email)
                student_email_dict["id"] = email_id  # 保留原来的 ID
                data["student_emails"][index] = student_email_dict
                updated = True
                break

        if updated:
            self.save_data(data)
            print("更新成功！")
        else:
            print(f"未找到 ID 为 {email_id} 的邮件，无法更新。")

    # 删除特定 ID 的邮件
    def delete_student_email(self, email_id: str):
        data = self.load_data()
        for index, email in enumerate(data["student_emails"]):
            if email.get("id") == email_id:
                deleted_email = data["student_emails"].pop(index)
                self.save_data(data)
                print(f"删除成功！已删除: {deleted_email}")
                return
        print(f"未找到 ID 为 {email_id} 的邮件，无法删除。")

# 实例化数据库客户端
student_email_data_client = StudentEmailDatabaseClient()
