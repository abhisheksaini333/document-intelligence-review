from dataclasses import dataclass, asdict
import math
@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int
    def __post_init__(self):
        if any(type(v) is not int for v in (self.x,self.y,self.width,self.height)) or min(self.x,self.y)<0 or min(self.width,self.height)<=0:
            raise ValueError('Invalid pixel bounding box')
    @property
    def area(self): return self.width*self.height
@dataclass(frozen=True)
class Token:
    text: str
    confidence: float
    box: Box
    page: int
    def __post_init__(self):
        if not self.text.strip() or not math.isfinite(self.confidence) or not 0<=self.confidence<=100 or type(self.page) is not int or self.page<1:
            raise ValueError('Invalid OCR token')
    def to_dict(self): return asdict(self)
