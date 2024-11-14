from dataclasses import dataclass,asdict
from typing import List

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
class Student:
    id: str
    name: str
    university: str
    degree: str
    background: Background
    application_intent: ApplicationIntent
    request: Request
    reason_for_applying: str

