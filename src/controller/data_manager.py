import json
import os
from typing import List, Dict, Any
import uuid
from config import DATA_DIR
from controller.schemas.student import Request, ApplicationIntent, Background
from controller.schemas.student import Student
from controller.schemas.student_email import StudentEmail
import copy
import logging

class DataClient:
    def __init__(self, data_type: str, readonly: bool = False):
        self.data_type = data_type
        self.data_file = os.path.join(DATA_DIR, f"json/{data_type}.json")
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

    def insert_from_json(self, json_string: str) -> str:
        """接受 JSON 字符串并插入数据"""
        try:
            data = json.loads(json_string)
            if isinstance(data, dict):  # 如果是单条数据，插入一条记录
                return self.insert(data)
            elif isinstance(data, list):  # 如果是多条数据，逐条插入
                for record in data:
                    self.insert(record)
                return str(len(data))  # 返回插入的记录数
            else:
                raise ValueError("JSON 格式不符合预期")
        except json.JSONDecodeError as e:
            logging.error(f"JSON 解码错误: {e}")
            return "-1"
        except ValueError as e:
            logging.error(f"数据格式错误: {e}")
            return "-1"

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

student_email_data_client = DataClient("student_email", readonly=False)
student_data_client = DataClient("student", readonly=False) 
reference_data_client = DataClient("reference", readonly=True)
