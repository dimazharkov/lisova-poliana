from typing import Any, List, Union, Literal, Annotated
from pydantic import BaseModel, Field, model_validator, ConfigDict
'''
{
    "loc": "h1",
    "columns": [
        {
            "name": "treatment",
            "spec": {
                "type": "select",
                "default": None,
                "rules": [
                    {"when": [{"col": "h1", "op": "<",  "value": 10}], "then": 1},
                    {"when": [{"col": "h1", "op": ">=", "value": 10}, {"col": "h1", "op": "<", "value": 50}], "then": 2},
                    {"when": [{"col": "h1", "op": ">=", "value": 50}], "then": 3}
                ]
            }
        },
        {"name": "repeat", "value": 0}
    ]
}
'''
class Condition(BaseModel):
    col: str
    op: Literal["<", "<=", ">", ">=", "==", "!=", "="]
    value: Any

class Rule(BaseModel):
    when: List[Condition]
    then: Any

class ConstSpec(BaseModel):
    type: Literal["const"]
    value: Any

class SelectSpec(BaseModel):
    type: Literal["select"]
    default: Any = None
    rules: List[Rule]

Spec = Annotated[Union[ConstSpec, SelectSpec], Field(discriminator="type")]

class Column(BaseModel):
    name: str
    spec: Spec | None = None
    value: Any | None = None

    @model_validator(mode="before")
    @classmethod
    def _value_shortcut(cls, data: Any):
        # если пришёл шорткат с value — превратим в spec=ConstSpec
        if isinstance(data, dict) and "spec" not in data and "value" in data:
            return {**data, "spec": {"type": "const", "value": data["value"]}}
        return data

    @model_validator(mode="after")
    def _check_spec(self):
        # после парсинга spec уже должен быть собран (включая шорткат)
        if self.spec is None:
            raise ValueError(f"Column '{self.name}' needs 'spec' or 'value'")
        return self

class AddColumnsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    loc: Union[int, str]
    columns: List[Column]
