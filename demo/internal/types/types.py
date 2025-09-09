from pydantic import BaseModel

# 定义严格类型的数据模型
class User(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool = True  # 默认值
    tags: list[str] = []    # 列表类型
