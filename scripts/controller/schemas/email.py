from dataclasses import dataclass, field
from typing import List

# 优化后的数据模型
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
class ExtraInfo:
    key: str
    value: str

@dataclass
class StudentEmail:
    id: str
    subject: str
    raw_mail_path: str
    sender: Sender
    application_intent: ApplicationIntent
    background: Background
    reason_for_applying: str
    request: Request
    closing: str
    extra_info: List[ExtraInfo] = field(default_factory=list) 