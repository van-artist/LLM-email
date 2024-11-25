import json
import os
import datetime
import copy
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import asdict
from controller.schemas.student import Student
from controller.schemas.email import StudentEmail
from config import ROLES_WRITER,ROLES_STUDENT,DATA_DIR

class DataClient:
    def __init__(self, data_type: str, readonly: bool = False,output_dir:str="json"):
        self.data_type = data_type
        self.data_file = os.path.join(DATA_DIR,output_dir, f"{data_type}.json")
        self.readonly = readonly
        self.data = self._load_data()

    def _load_data(self) -> List[Dict[str, Any]]:
        """从文件加载数据，文件不存在则返回空列表"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 创建文件
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        return []

    def _save_data(self):
        """将数据保存回文件"""
        if self.readonly:
            raise PermissionError("Read-only mode. Write operations are not allowed.")
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def insert(self, data: Dict[str, Any]) -> str:
        """插入数据"""
        new_data = data.copy()
        new_data["id"] = str(uuid.uuid4())
        self.data.append(new_data)
        self._save_data()
        return new_data["id"]
    
    def insert_from_json_string(self, json_string: str) -> str:
        """从 JSON 字符串插入数据"""
        data = json.loads(json_string)
        return self.insert(data)

    def find(self, record_id: str) -> Dict[str, Any]:
        """根据 ID 查找记录"""
        return next((record for record in self.data if record.get("id") == record_id), {})
    
    def update(self, record_id: str, new_data: Dict[str, Any]) -> bool:
        """根据 ID 更新记录"""
        for record in self.data:
            if record.get("id") == record_id:
                record.update(new_data)
                self._save_data()
                return True
        return False

    def delete(self, record_id: str) -> bool:
        """根据 ID 删除记录"""
        for i, record in enumerate(self.data):
            if record.get("id") == record_id:
                del self.data[i]
                self._save_data()
                return True
        return False
    
    def find_all(self) -> List[Dict[str, Any]]:
        """返回所有记录"""
        return self.data
class StudentDataClient(DataClient):
    def __init__(self):
        super().__init__("student")

    def find_by_university(self, university: str) -> List[Dict[str, Any]]:
        """根据大学查找学生"""
        return [record for record in self.data if record.get("university") == university]

    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        """根据姓名查找学生"""
        return [record for record in self.data if record.get("name") == name]

class EmailDataClient(DataClient):
    def __init__(self,output_dir:str):
        super().__init__("email",output_dir=output_dir)

    def add_email(self, student_id: str, role: str, content: StudentEmail, timestamp: Optional[str] = None):
        """
        新增邮件记录到某个学生的邮件历史文件中。
        如果该学生没有历史记录，将创建新的文件。
        """
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()

        try:
            student_history = self.find(student_id)
            if not student_history:
                raise ValueError(f"Student with ID {student_id} not found.")
        except ValueError as e:
            student_history = {
                "id": student_id,
                "name": "Unknown",
                "email": "unknown@example.com",
                "history": []
            }
            raise e
        student_history["history"].append({
            "timestamp": timestamp,
            "role": role,
            "content": asdict(content) 
        })

        # 更新记录
        self.update(student_id, student_history)

    def append_email(self, student_id: str, email: StudentEmail):
        """
        将邮件添加到学生的邮件历史记录中。
        """
        self.add_email(student_id, ROLES_STUDENT, email)
    def append_reply(self, student_id: str, email: StudentEmail):
        """
        将回复添加到学生的邮件历史记录中。
        """
        self.add_email(student_id, ROLES_WRITER, email)

    def get_email_history(self, student_id: str) -> List[Dict[str, Any]]:
        """
        获取某个学生的所有邮件历史。
        """
        student_history = self.find(student_id)
        return student_history.get("history", [])

    def find_students_with_emails(self) -> List[Dict[str, Any]]:
        """
        返回所有有邮件历史的学生列表。
        """
        return [
            {
                "id": record["id"],
                "name": record.get("name", ""),
                "email": record.get("email", "")
            }
            for record in self.data if "history" in record and record["history"]
        ]

class ReferenceDataClient(DataClient):
    def __init__(self):
        super().__init__("reference", readonly=True)

    def get_all_references(self) -> List[Dict[str, Any]]:
        """获取所有参考文档"""
        return self.find_all()

def email_to_student(email: StudentEmail) -> Student:
    student = Student(
        id=str(uuid.uuid4()),
        name=email.sender['name'], # type: ignore
        degree=email.sender['name'], # type: ignore
        request=copy.deepcopy(email.request),  # type: ignore
        application_intent=copy.deepcopy(email.application_intent),  # type: ignore
        background=copy.deepcopy(email.background),  # type: ignore
        reason_for_applying=email.reason_for_applying,
        university=email.sender['university'] # type: ignore
    )
    return student
email_data_client = EmailDataClient("mails")
student_data_client = StudentDataClient() 
reference_data_client = ReferenceDataClient()
