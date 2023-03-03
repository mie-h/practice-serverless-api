from pydantic import BaseModel

class Item(BaseModel):
    productId: int
    color: str
    price: int

class PatchItem(BaseModel):
    productId: int
    key: str
    value: str