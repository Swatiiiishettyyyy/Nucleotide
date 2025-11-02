from pydantic import BaseModel
from typing import List


class ProductCreate(BaseModel):
    name: str
    mrp_price: float
    sale_price: float
    price_unit: str
    shipping_info: str
    sample_requirement: str
    long_description: str
    features: List[str]
    available_quantity: int


class ProductResponse(ProductCreate):
    id: int
    
    class Config:
        orm_mode = True
        

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
