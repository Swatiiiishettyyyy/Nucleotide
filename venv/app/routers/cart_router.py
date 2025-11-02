from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/cartItem", tags=["Cart"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add")
def add_to_cart(item: schemas.CartAdd, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == item.product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check stock before adding
    if item.quantity > product.available_quantity:
        raise HTTPException(status_code=400, 
                            detail="Requested quantity exceeds stock")

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.product_id == item.product_id).first()

    if cart_item:
        # Ensure total quantity does not exceed stock
        if cart_item.quantity + item.quantity > product.available_quantity:
            raise HTTPException(status_code=400,
                                detail="Not enough stock to add more to cart")
        cart_item.quantity += item.quantity
    else:
        cart_item = models.CartItem(
            product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)

    db.commit()
    return {"message": "Item added to cart successfully"}


@router.get("/view", response_model=list[schemas.CartItemResponse])
def view_cart(db: Session = Depends(get_db)):
    return db.query(models.CartItem).all()


@router.put("/update/{cart_item_id}")
def update_cart_item(cart_item_id: int, update_data: schemas.CartUpdate, 
                     db: Session = Depends(get_db)):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Prevent assigning quantity > stock
    product = db.query(models.Product).filter(
        models.Product.id == item.product_id).first()
    if update_data.quantity > product.available_quantity:
        raise HTTPException(
            status_code=400, 
            detail="Requested quantity exceeds available stock")
    if update_data.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = update_data.quantity

    db.commit()
    return {"message": "Cart item updated successfully"}


# Increase Quantity (with stock check)
@router.patch("/{cart_item_id}/increase")
def increase_quantity(cart_item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = db.query(models.Product).filter(
        models.Product.id == item.product_id).first()

    if item.quantity >= product.available_quantity:
        raise HTTPException(status_code=400, 
                            detail="Cannot increase. Product out of stock.")

    item.quantity += 1
    db.commit()
    return {"message": "Quantity increased", "quantity": item.quantity}


# Decrease Quantity (Never below 1)
@router.patch("/{cart_item_id}/decrease")
def decrease_quantity(cart_item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item.quantity > 1:
        item.quantity -= 1
        db.commit()
        return {"message": "Quantity decreased", "quantity": item.quantity}
    else:
        raise HTTPException(
            status_code=400, detail="Quantity cannot be less than 1")


@router.delete("/delete/{cart_item_id}")
def remove_cart_item(cart_item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/clear")
def clear_cart(db: Session = Depends(get_db)):
    db.query(models.CartItem).delete()
    db.commit()
    return {"message": "Cart cleared successfully"}
