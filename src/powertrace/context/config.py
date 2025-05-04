from dataclasses import dataclass


@dataclass
class Config:
    exit_after: bool = True
    repeat: bool = True
