from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions-with-str-discriminators


class Cat(BaseModel):
    pet_type: Literal["cat"]
    meows: int


class Dog(BaseModel):
    pet_type: Literal["dog"]
    barks: float


class Lizard(BaseModel):
    pet_type: Literal["reptile", "lizard"]
    scales: bool


class Model(BaseModel):
    pet: Cat | Dog | Lizard = Field(discriminator="pet_type")
    n: int


class Post(BaseModel):
    topic: str | None = Field(alias="PkTopic", default=None)
    content: str = Field(alias="Content")
    post_time: datetime = Field(alias="Sk")
