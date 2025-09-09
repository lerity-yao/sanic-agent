from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Tuple, cast


class BaseModelPydantic(BaseModel):
    """
    基础模型类，使用 Pydantic 提供数据验证和默认值管理

    核心功能：
    1. 自动类型检查和转换
    2. 默认值支持
    3. 字典式访问
    """

    @classmethod
    def from_data(cls, data: Dict[str, Any] = None) -> 'BaseModelPydantic':
        """
        从字典创建模型实例，自动应用默认值和类型校验

        :param data: 包含字段数据的字典
        :return: 模型实例
        """
        return cls.model_validate(data or {})

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型转换为字典

        :return: 包含所有字段数据的字典
        """
        return self.model_dump()

    def update(self, data: Dict[str, Any]):
        """
        使用字典数据更新模型

        :param data: 包含更新数据的字典
        """
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        for key, value in data.items():
            if key in model_fields:
                setattr(self, key, value)

    def __contains__(self, name: str) -> bool:
        """
        检查字段是否存在于模型中

        :param name: 字段名称
        :return: 是否存在
        """
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        return name in model_fields

    def __getitem__(self, name: str) -> Any:
        """
        通过字典方式获取字段值

        :param name: 字段名称
        :return: 字段值
        :raises KeyError: 如果字段不存在
        """
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        if name not in model_fields:
            raise KeyError(f"Field '{name}' not found in {self.__class__.__name__}")
        return getattr(self, name)

    def __setitem__(self, name: str, value: Any):
        """
        通过字典方式设置字段值

        :param name: 字段名称
        :param value: 字段值
        :raises KeyError: 如果字段不存在
        """
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        if name not in model_fields:
            raise KeyError(f"Field '{name}' not found in {self.__class__.__name__}")
        setattr(self, name, value)

    def keys(self) -> List[str]:
        """
        获取所有字段名称

        :return: 字段名称列表
        """
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        return list(model_fields.keys())

    def values(self) -> List[Any]:
        """
        获取所有字段值

        :return: 字段值列表
        """
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        return [getattr(self, name) for name in model_fields]

    def items(self) -> List[Tuple[str, Any]]:
        """
        获取所有字段键值对

        :return: 字段键值对列表
        """
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        return [(name, getattr(self, name)) for name in model_fields]


# 使用示例
if __name__ == "__main__":
    class TestModel(BaseModelPydantic):
        Id: Optional[int] = 1
        Name: str  # 必填字段
        Code: List[str] = ['a', 'b']  # 带默认值的可选字段
        Sec: Dict[str, int]  # 必填字段
        OptionalField: Optional[str] = None  # 带默认值的可选字段


    # 1. 创建实例（提供所有必填字段）
    instance = TestModel(
        Sec={"key": 100}
    )
    print("实例:", instance.to_dict())
    # 输出: {'Id': 1, 'Name': 'Test', 'Code': ['a', 'b'], 'Sec': {'key': 100}, 'OptionalField': None}

    # 2. 从字典创建实例
    data_instance = TestModel.from_data({
        'Id': 2,
        'Name': 'Test2',
        'Sec': {'key': 200},
        'OptionalField': 'value'
    })
    print("数据实例:", data_instance.to_dict())
    # 输出: {'Id': 2, 'Name': 'Test2', 'Code': ['a', 'b'], 'Sec': {'key': 200}, 'OptionalField': 'value'}

    # 3. 缺少必填字段（会报错）
    try:
        error_instance = TestModel(
            Id=3,
            # 缺少 Name 字段
            Sec={'key': 300}
        )
    except ValueError as e:
        print(f"错误: {e}")
        # 输出: 错误: 1 validation error for TestModel
        # Name: Field required

    # 4. 使用默认值
    default_instance = TestModel(
        Id=4,
        Name="Default",
        Sec={}
    )
    print("默认值实例:", default_instance.to_dict())
    # 输出: {'Id': 4, 'Name': 'Default', 'Code': ['a', 'b'], 'Sec': {}, 'OptionalField': None}

    # 5. 更新实例
    data_instance.update({
        'Id': 100,
        'Name': 'Updated',
        'Code': ['x', 'y', 'z'],
        'Sec': {'new_key': 500}
    })
    print("更新后实例:", data_instance.to_dict())
    # 输出: {'Id': 100, 'Name': 'Updated', 'Code': ['x', 'y', 'z'], 'Sec': {'new_key': 500}, 'OptionalField': 'value'}

    # 6. 字典式访问
    print("Name字段:", data_instance['Name'])  # 'Updated'
    data_instance['Name'] = 'New Name'
    print("更新后Name:", data_instance.Name)  # 'New Name'

    # 7. 包含检查
    print("包含Id字段:", 'Id' in data_instance)  # True
    print("包含无效字段:", 'Invalid' in data_instance)  # False

    # 8. 键值对访问
    print("所有字段:", data_instance.keys())
    print("所有值:", data_instance.values())
    print("所有键值对:", data_instance.items())
