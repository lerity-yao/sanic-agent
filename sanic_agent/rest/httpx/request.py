from functools import partial
from typing import ClassVar, Dict, Callable, Union, cast, Any, Optional, Tuple, List
from pydantic import field_validator, Field, ValidationError
from pydantic_core import PydanticUndefinedType, ErrorDetails

from sanic_agent.core.model.base_model import BaseModelPydantic


class ParseModel(BaseModelPydantic):
    """支持自定义校验器的模型基类，支持必填和可选字段，以及额外参数"""

    # 全局校验器注册表（存储校验函数和默认参数）
    _validators_registry: ClassVar[Dict[str, Tuple[Callable, dict]]] = {}

    @classmethod
    def register_validator(cls, name: str, validator: Callable, **kwargs):
        """
        注册全局校验器，支持额外参数

        :param name: 校验器名称
        :param validator: 校验函数
        :param kwargs: 额外参数，将传递给校验函数（可选）
        """
        cls._validators_registry[name] = (validator, kwargs)

    def __init__(self, **kwargs):
        """初始化模型实例"""
        # 确保所有字段都被处理
        model_fields = cast(Dict[str, Any], self.__class__.model_fields)
        for field_name in model_fields:
            if field_name not in kwargs:
                # 如果字段有默认值，使用默认值
                field_info = model_fields[field_name]
                if field_info.default is not None:
                    kwargs[field_name] = field_info.default

        super().__init__(**kwargs)

    @classmethod
    def model_validate(cls, obj: Any, *, strict: bool | None = None, from_attributes: bool | None = None,
                       context: dict[str, Any] | None = None) -> BaseModelPydantic:
        """
        覆盖 model_validate 方法，自定义错误处理

        :param obj: 输入数据
        :param strict: 是否启用严格模式
        :param from_attributes: 是否从属性创建
        :param context: 上下文信息
        :return: 模型实例
        """
        try:
            # 调用父类的 model_validate 方法
            return super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)
        except ValidationError as e:
            # 自定义错误处理
            custom_errors = cls.customize_errors(e.errors())
            raise ValidationError.from_exception_data(
                title=e.title,
                line_errors=custom_errors
            ) from e

    @classmethod
    def customize_errors(cls, errors: List[ErrorDetails]) -> List[ErrorDetails]:
        """
        自定义错误消息

        :param errors: 原始错误列表
        :return: 自定义后的错误列表
        """
        custom_errors = []
        for error in errors:
            # 获取字段名称
            loc = error["loc"]
            if loc:
                field_name = loc[0]
            else:
                field_name = "unknown"

            # 获取字段信息
            field_info = cls.model_fields.get(field_name) if field_name in cls.model_fields else None

            # 检查是否有自定义错误消息
            custom_message = None
            if field_info and field_info.json_schema_extra:
                error_messages = field_info.json_schema_extra.get("error_messages", {})
                if error["type"] in error_messages:
                    custom_message = error_messages[error["type"]]

            # 创建自定义错误
            if custom_message:
                custom_error = {
                    "loc": error["loc"],
                    "msg": custom_message,
                    "type": error["type"],
                    "ctx": error.get("ctx", {})
                }
                custom_errors.append(custom_error)
            else:
                # 使用默认错误
                custom_errors.append(error)

        return custom_errors

    @field_validator("*", mode="before")
    def apply_custom_validators(cls, value, field):
        """
        应用自定义校验器
        """
        # 获取字段名称
        field_name = field.field_name

        # 通过类字段获取字段信息
        field_info = cls.model_fields[field_name]

        # 检查是否有自定义校验器
        if field_info.json_schema_extra and "validator" in field_info.json_schema_extra:
            validator_name = field_info.json_schema_extra["validator"]

            # 检查是否有额外参数
            extra_args = {}
            if "validator_args" in field_info.json_schema_extra:
                extra_args = field_info.json_schema_extra["validator_args"]

            if validator_name in cls._validators_registry:
                # 安全获取校验器数据
                validator_data = cls._validators_registry[validator_name]

                # 确保我们有一个元组
                if isinstance(validator_data, tuple):
                    validator, default_args = validator_data
                else:
                    # 处理旧格式（仅校验器函数）
                    validator = validator_data
                    default_args = {}

                # 合并默认参数和字段特定参数
                combined_args = {**default_args, **extra_args}

                # 如果值是未定义类型或None，跳过校验
                if isinstance(value, PydanticUndefinedType) or value is None:
                    return value

                # 如果校验器有额外参数，使用偏函数
                if combined_args:
                    validator = partial(validator, **combined_args)

                return validator(value)

        return value


if __name__ == "__main__":
    # 定义校验函数，支持额外参数（可选）
    def validate_phone(value: str, min_length: int = 11, prefix: str = "1") -> str:
        """校验电话号码格式，支持额外参数"""
        if not value:
            return value
        if not value.startswith(prefix) or len(value) != min_length or not value.isdigit():
            raise ValueError(f"Invalid phone number format: must start with '{prefix}' and be {min_length} digits")
        return value


    # 注册校验器，不提供额外参数
    ParseModel.register_validator("validate_phone", validate_phone)


    # 定义模型 - 必填字段（使用默认参数）
    class RequiredPhoneModel(ParseModel):
        Phone: str = Field(..., json_schema_extra={"validator": "validate_phone"})
        Name: str


    # 定义模型 - 可选字段（使用默认参数）
    class OptionalPhoneModel(ParseModel):
        Phone: Optional[str] = Field(default=None, json_schema_extra={"validator": "validate_phone"})


    # 定义模型 - 必填字段（覆盖默认参数）
    class CustomPhoneModel(ParseModel):
        Phone: str = Field(
            ...,
            json_schema_extra={
                "validator": "validate_phone",
                "validator_args": {
                    "prefix": "+",
                    "min_length": 13
                }
            }
        )


    # 测试必填字段 - 有效值（使用默认参数）

    required_valid = RequiredPhoneModel.from_data({
        "Phone": "13800138000"
    })
    print("必填字段有效实例:", required_valid.to_dict())


    # 测试必填字段 - 无效值（使用默认参数）
    try:
        required_invalid = RequiredPhoneModel.from_data({
            "Phone": "31111111111"  # 无效电话号码
        })
    except Exception as e:
        print(f"必填字段无效实例错误: {e}")

    # 测试可选字段 - 有效值（使用默认参数）
    try:
        optional_valid = OptionalPhoneModel.from_data({
            "Phone": "13900139000"
        })
        print("可选字段有效实例:", optional_valid.to_dict())
    except Exception as e:
        print(f"可选字段有效实例错误: {e}")

    # 测试可选字段 - 无效值（使用默认参数）
    try:
        optional_invalid = OptionalPhoneModel.from_data({
            "Phone": "31111111111"  # 无效电话号码
        })
    except Exception as e:
        print(f"可选字段无效实例错误: {e}")

    # 测试可选字段 - 空值（使用默认参数）
    try:
        optional_empty = OptionalPhoneModel.from_data()
        print("可选字段空值实例:", optional_empty.to_dict())  # 输出: {'Phone': None}
    except Exception as e:
        print(f"可选字段空值错误: {e}")

    # 测试自定义模型 - 有效值（覆盖默认参数）
    try:
        custom_valid = CustomPhoneModel.from_data({
            "Phone": "+8613800138000"  # 有效国际电话号码
        })
        print("自定义模型有效实例:", custom_valid.to_dict())
    except Exception as e:
        print(f"自定义模型有效实例错误: {e}")

    # 测试自定义模型 - 无效值（覆盖默认参数）
    try:
        custom_invalid = CustomPhoneModel.from_data({
            "Phone": "8613800138000"  # 无效国际电话号码（缺少+）
        })
    except Exception as e:
        print(f"自定义模型无效实例错误: {e}")