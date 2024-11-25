from dataclasses import dataclass, asdict, field
from typing import List, Optional

@dataclass
class ApplicationIntent:
    program: str                          # 申请的项目名称，例如 "计算机科学硕士"
    interests: List[str]                  # 学生的研究兴趣，例如 ["人工智能", "机器学习"]
    additional_details: Optional[str] = ""  # 额外的申请意图说明

@dataclass
class Project:
    title: str                            # 项目名称
    description: Optional[str] = ""       # 项目描述
    results: Optional[str] = ""           # 项目成果，例如论文、比赛奖项等

@dataclass
class Background:
    projects: List[Project]               # 学生参与的项目
    courses: List[str]                    # 学生修读的课程
    skills: List[str] = field(default_factory=list)  # 学生的技能（可选）

@dataclass
class Request:
    type: str                             # 请求的类型，例如 "咨询" 或 "申请"
    appreciation: Optional[str] = ""      # 表示感谢的内容
    detailed_request: Optional[str] = ""  # 更详细的请求描述

@dataclass
class Student:
    id: str                               # 学生的唯一标识符
    name: str                             # 学生姓名
    university: str                       # 所在大学
    degree: str                           # 学位类型，例如 "本科" 或 "硕士"
    background: Background                # 学术背景
    application_intent: ApplicationIntent # 申请意图
    request: Request                      # 请求详情
    reason_for_applying: str              # 申请理由
    contact_email: Optional[str] = ""     # 学生的联系方式（可选）
    additional_notes: Optional[str] = ""  # 额外备注（可选）
