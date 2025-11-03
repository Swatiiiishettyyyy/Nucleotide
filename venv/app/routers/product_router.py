from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.ProductModel import Product

from app.schemas.Product import ProductResponse, ProductCreate
# ProductModel.py
from app.database import SessionLocal
router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/addProduct", response_model=ProductResponse)
def create_product(payload: ProductCreate,
                   db: Session = Depends(get_db)):
    new_product = Product(**payload.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/viewProduct", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
