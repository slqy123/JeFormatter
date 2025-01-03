from dataclasses import dataclass


@dataclass
class Config:
    csharp_cate_threshold: int = 2  # 可以容忍的不能用C#记谱的音符种类数
    csharp_percentage_threshold: float = 0.20  # 可以容忍的不能用C#记谱的音符出现次数占比


config = Config()
