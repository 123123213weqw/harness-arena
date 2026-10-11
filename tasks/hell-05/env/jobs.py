"""任务定义(不得修改)。"""
from dataclasses import dataclass, field


@dataclass
class Job:
    id: str
    priority: int
    deps: list = field(default_factory=list)
