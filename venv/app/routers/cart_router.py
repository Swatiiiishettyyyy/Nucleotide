from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.CartItemModel import CartItem
from app.models.ProductModel import Product
from app.schemas.CartItem import CartAdd, CartUpdate

router = APIRouter(prefix="/cartItem", tags=["Cart"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add")
def add_to_cart(item: CartAdd, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.ProductId == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(CartItem).filter(CartItem.product_id == item.product_id).first()
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
        "status": "success",
        "message": "Product added to cart successfully.",
        "data": {
            "product_id": product.ProductId,
            "quantity": cart_item.quantity,
            "price": product.Price,
            "special_price": product.SpecialPrice,
            "total_amount": cart_item.quantity * product.SpecialPrice
        }
    }


@router.put("/update/{cart_item_id}")
def update_cart_item(cart_item_id: int, update: CartUpdate, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.quantity = update.quantity
    db.commit()
    db.refresh(cart_item)

    product = cart_item.product
    return {
        "status": "success",
        "message": "Cart item updated successfully.",
        "data": {
            "product_id": product.ProductId,
            "quantity": cart_item.quantity,
            "price": product.Price,
            "special_price": product.SpecialPrice,
            "total_amount": cart_item.quantity * product.SpecialPrice
        }
    }


@router.delete("/delete/{cart_item_id}")
def delete_cart_item(cart_item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return {
        "status": "success",
        "message": f"Cart item {cart_item_id} deleted successfully."
    }


@router.delete("/clear")
def clear_cart(db: Session = Depends(get_db)):
    deleted_count = db.query(CartItem).delete()
    db.commit()
    return {
        "status": "success",
        "message": f"Cleared {deleted_count} item(s) from the cart."
    }


@router.get("/view")
def view_cart(db: Session = Depends(get_db)):
    cart_items = db.query(CartItem).all()
    if not cart_items:
        return {
            "status": "success",
            "message": "Cart is empty.",
            "data": {
                "cart_summary": None,
                "cart_items": []
            }
        }

    subtotal_amount = 0
    delivery_charge = 50
    cart_item_details = []

    for item in cart_items:
        product = item.product
        total = item.quantity * product.SpecialPrice
        subtotal_amount += total

        cart_item_details.append({
            "cart_item_id": item.id,
            "product_id": product.ProductId,
            "product_name": product.Name,
            "product_images": product.Images,
            "price": product.Price,
            "special_price": product.SpecialPrice,
            "quantity": item.quantity,
            "total_amount": total
        })

    grand_total = subtotal_amount + delivery_charge

    summary = {
        "total_items": len(cart_items),
        "subtotal_amount": subtotal_amount,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total
    }

    return {
        "status": "success",
        "message": "Cart data fetched successfully.",
        "data": {
            "cart_summary": summary,
            "cart_items": cart_item_details
        }
    }
