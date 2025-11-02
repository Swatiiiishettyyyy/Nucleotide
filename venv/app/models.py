from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)

    mrp_price = Column(Float, nullable=False)
    sale_price = Column(Float, nullable=False)
    price_unit = Column(String(50), nullable=False)

    shipping_info = Column(String(200), nullable=False)
    sample_requirement = Column(String(200), nullable=False)

    long_description = Column(String(1000), nullable=False)
    features = Column(JSON, nullable=False)

    # ✅ This is your stock
    available_quantity = Column(Integer, nullable=False, default=0)


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    product = relationship("Product")
