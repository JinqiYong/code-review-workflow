from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class WorkflowState:
    task: str = ""
    current_code: str = ""
    review_history: List[Dict] = field(default_factory=list)
    max_iterations: int = 3
    current_iteration: int = 0
    is_passed: bool = False
    logs: List[str] = field(default_factory=list)

    def add_log(self, message: str):
        self.logs.append(f"[Iteration {self.current_iteration}] {message}")