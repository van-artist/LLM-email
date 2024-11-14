# 实例化客户端后从文件加载数据到内存中
# 数据操作先修改内存,然后开一个新的线程把写入文件的任务任务添加到任务队列实现非阻塞I/O
import json
import os
import threading
from typing import List, Dict, Any
import uuid
from config import DATA_DIR
from database.schemas import student
from database.schemas.student import Student
from database.schemas.student_email import StudentEmail
import copy

class DataClient:
    def __init__(self, data_type: str):
        """初始化数据客户端并从文件加载数据"""
        self.data_type = data_type
        self.data_file = os.path.join(DATA_DIR, f"json/{data_type}.json")
        self.data = self._load_data()

    def _load_data(self) -> List[Dict[str, Any]]:
        """从文件加载数据，文件不存在则返回空列表"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_data(self):
        """将数据保存回文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def insert(self, data: Dict[str, Any]) -> str:
        """插入一条数据，并返回其唯一标识符"""
        new_data = data.copy()
        new_data["id"] = str(uuid.uuid4())  
        # print("插入对象")
        # print(new_data)
        self.data.append(new_data)
        self._save_data()
        # print("当前数据")
        # print(self.data)
        return new_data["id"]

    def insert_from_json(self, json_string: str) -> str:
        """接受 JSON 字符串并插入数据"""
        try:
            # print("解析json:")
            # print(json_string)
            data = json.loads(json_string)

            if isinstance(data, dict):  
                return self.insert(data)
            elif isinstance(data, list): 
                for record in data:
                    self.insert(record)
                return len(data)  
            else:
                raise ValueError("JSON 格式不符合预期")
        except json.JSONDecodeError as e:
            print(f"JSON 解码错误: {e}")
            return -1
        except ValueError as e:
            print(f"数据格式错误: {e}")
            return -1

    def delete(self, record_id: str) -> bool:
        """根据 ID 删除记录"""
        for i, record in enumerate(self.data):
            if record.get("id") == record_id:
                del self.data[i]
                self._save_data()  # 保存到文件
                return True
        return False

    def update(self, record_id: str, new_data: Dict[str, Any]) -> bool:
        """根据 ID 更新记录"""
        for i, record in enumerate(self.data):
            if record.get("id") == record_id:
                self.data[i].update(new_data)
                self._save_data()  # 保存到文件
                return True
        return False

    def find(self, record_id: str) -> Dict[str, Any]:
        """根据 ID 查找记录"""
        for record in self.data:
            if record.get("id") == record_id:
                return record
        return {}

    def find_all(self) -> List[Dict[str, Any]]:
        """返回所有记录"""
        return self.data


def email_to_student(email:StudentEmail) -> Student:
    student=Student(
        id=uuid.uuid4(),
        name=email.sender['name'],
        degree=email.sender['degree'],
        request=copy.deepcopy(email.request),
        application_intent=copy.deepcopy(email.application_intent),
        background=copy.deepcopy(email.background),
        reason_for_applying=email.reason_for_applying,
        university=email.sender['university']
    )
    return student



student_email_data_client=DataClient("student_email")
student_data_client=DataClient("student")
