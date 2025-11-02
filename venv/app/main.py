from fastapi import FastAPI
from .database import Base, engine
from .routers import product_router, cart_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(product_router.router)
app.include_router(cart_router.router)
