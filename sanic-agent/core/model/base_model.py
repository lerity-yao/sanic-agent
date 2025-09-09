from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Type, Tuple


class BaseModelPydantic(BaseModel):
    """
    基础模型类，使用 Pydantic 提供数据验证和设置管理

    使用示例:
    class User(BaseModelPydantic):
        id: int
        name: str = "Anonymous"
        email: Optional[str] = None
        is_admin: bool = False

    user = User.from_data({
        'id': 123,
        'name': 'Alice',
        'email': 'alice@example.com'
    })
    """

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> 'BaseModelPydantic':
        """
        从字典创建模型实例

        :param data: 包含字段数据的字典
        :return: 模型实例
        """
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型转换为字典

        :return: 包含所有字段数据的字典
        """
        return self.dict()

    def update(self, data: Dict[str, Any]):
        """
        使用字典数据更新模型

        :param data: 包含更新数据的字典
        """
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        """
        返回模型的友好表示

        :return: 模型表示字符串
        """
        return self.__str__()

    def __eq__(self, other: Any) -> bool:
        """
        比较两个模型是否相等（字段值相同）

        :param other: 另一个对象
        :return: 是否相等
        """
        if not isinstance(other, BaseModelPydantic):
            return False
        return self.dict() == other.dict()

    def __ne__(self, other: Any) -> bool:
        """不等于运算符"""
        return not self.__eq__(other)

    def __contains__(self, name: str) -> bool:
        """
        检查字段是否存在于模型中

        :param name: 字段名称
        :return: 是否存在
        """
        return name in self.__fields__

    def __getitem__(self, name: str) -> Any:
        """
        通过字典方式获取字段值

        :param name: 字段名称
        :return: 字段值
        :raises KeyError: 如果字段不存在
        """
        if name not in self.__fields__:
            raise KeyError(f"Field '{name}' not found in {self.__class__.__name__}")
        return getattr(self, name)

    def __setitem__(self, name: str, value: Any):
        """
        通过字典方式设置字段值

        :param name: 字段名称
        :param value: 字段值
        :raises KeyError: 如果字段不存在
        """
        if name not in self.__fields__:
            raise KeyError(f"Field '{name}' not found in {self.__class__.__name__}")
        setattr(self, name, value)

    def keys(self) -> List[str]:
        """
        获取所有字段名称

        :return: 字段名称列表
        """
        return list(self.__fields__.keys())

    def values(self) -> List[Any]:
        """
        获取所有字段值

        :return: 字段值列表
        """
        return [getattr(self, name) for name in self.__fields__]

    def items(self) -> List[Tuple[str, Any]]:
        """
        获取所有字段键值对

        :return: 字段键值对列表
        """
        return [(name, getattr(self, name)) for name in self.__fields__]


# 使用示例
if __name__ == "__main__":
    class TestModel(BaseModelPydantic):
        Id: int = Field(default=1, description="唯一标识")
        Name: str = Field(default='test', description="名称")
        Code: List[str] = Field(default=['a', 'b'], description="代码列表")
        Sec: Dict[str, int] = Field(default={'a': 1, 'b': 2}, description="安全字典")

        @validator('Sec', pre=True)
        def validate_sec(cls, value):
            """验证 Sec 字段的值都是整数"""
            if isinstance(value, dict):
                for k, v in value.items():
                    if not isinstance(v, int):
                        raise ValueError(f"Sec 字段的值必须是整数，但得到 {type(v).__name__}")
            return value


    # 创建实例
    test = TestModel.from_data({
        'Id': 2,
        'Name': 'test2',
        'Sec': {'c': 3, 'd': 4}
    })

    print(test.to_dict())
    # 输出: {'Id': 2, 'Name': 'test2', 'Code': ['a', 'b'], 'Sec': {'c': 3, 'd': 4}}

    # 更新实例
    test.update({
        'Name': 'updated',
        'Code': ['x', 'y', 'z']
    })
    print(test.to_dict())
    # 输出: {'Id': 2, 'Name': 'updated', 'Code': ['x', 'y', 'z'], 'Sec': {'c': 3, 'd': 4}}

    # 测试验证
    try:
        invalid_test = TestModel(Sec={'e': 'invalid'})
    except ValueError as e:
        print(f"验证错误: {e}")
        # 输出: 验证错误: Sec 字段的值必须是整数，但得到 str

    # 测试相等性
    test2 = TestModel(Id=2, Name='updated', Code=['x', 'y', 'z'], Sec={'c': 3, 'd': 4})
    print(test == test2)  # True

    test3 = TestModel(Id=3)
    print(test == test3)  # False

    # 测试字典式访问
    print(test['Name'])  # 'updated'
    test['Name'] = 'new name'
    print(test.Name)  # 'new name'

    # 测试包含检查
    print('Id' in test)  # True
    print('Invalid' in test)  # False

# if __name__ == "__main__":
#     class TestModel(BaseModel):
#         Id: int = 1
#         Name: str = 'test'
#
#     test = TestModel.from_data({
#         'Id': 1,
#         'Name': 'test2',
#     })
#
#     class TestModel1(BaseModel):
#         Id: int = 1
#         Name: str = 'test2'
#         Code: List[str] = ['a', 'b']
#         Sec: Dict[str, int] = {'a': 'abc', 'b': 2}
#
#     test1 = TestModel1.from_data({
#         'Sec': {'a':'abc', 'b': 2},
#     })
#     print(test.to_dict(), test1.to_dict())
#     print(test == test1)