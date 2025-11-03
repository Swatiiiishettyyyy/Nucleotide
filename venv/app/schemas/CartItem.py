from pydantic import BaseModel
from .Product import ProductResponse


class CartItemResponse(BaseModel):
    id: int
    quantity: int
    product: ProductResponse   # nested product object

    class Config:
        orm_mode = True


class CartAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdate(BaseModel):
    quantity: int
