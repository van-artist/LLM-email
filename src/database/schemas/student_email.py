from dataclasses import dataclass, field
from typing import List
from utils import validate_student_email
import json
from jsonschema import ValidationError

@dataclass
class Sender:
    name: str
    university: str
    degree: str
    email: str

@dataclass
class ApplicationIntent:
    program: str
    interests: List[str]

@dataclass
class Project:
    title: str
    results: str

@dataclass
class Background:
    projects: List[Project]
    courses: List[str]

@dataclass
class Request:
    type: str
    appreciation: str

@dataclass
class StudentEmail:
    subject: str
    sender: Sender
    application_intent: ApplicationIntent
    background: Background
    reason_for_applying: str
    request: Request
    closing: str


def create_student_email_from_json(json_data: str) -> StudentEmail:
    try:
        data = json.loads(json_data)

        validate_student_email(json_data)

        sender = Sender(**data["sender"])
        application_intent = ApplicationIntent(**data["application_intent"])
        projects = [Project(**proj) for proj in data["background"]["projects"]]
        background = Background(projects=projects, courses=data["background"]["courses"])
        request = Request(**data["request"])
        
        return StudentEmail(
            subject=data["subject"],
            sender=sender,
            application_intent=application_intent,
            background=background,
            reason_for_applying=data["reason_for_applying"],
            request=request,
            closing=data["closing"]
        )
    except ValidationError as e:
        print("JSON格式不符合要求:", e)
        return None
    except json.JSONDecodeError as e:
        print("JSON解析失败:", e)
        return None
    
def StudentEmail_to_dict(student_email):
    return {
        "subject": student_email.subject,
        "sender": {
            "name": student_email.sender.name,
            "university": student_email.sender.university,
            "degree": student_email.sender.degree,
            "email": student_email.sender.email
        },
        "application_intent": {
            "program": student_email.application_intent.program,
            "interests": student_email.application_intent.interests
        },
        "background": {
            "projects": [
                {"title": proj.title, "results": proj.results} for proj in student_email.background.projects
            ],
            "courses": student_email.background.courses
        },
        "reason_for_applying": student_email.reason_for_applying,
        "request": {
            "type": student_email.request.type,
            "appreciation": student_email.request.appreciation
        },
        "closing": student_email.closing
    }
