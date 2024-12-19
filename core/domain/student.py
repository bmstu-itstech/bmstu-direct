from dataclasses import dataclass

@dataclass
class Student:
    full_name: str
    study_group: str

    def __str__(self):
        return f"{self.full_name} {self.study_group}"
