from typing import Type, Union

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.PriceModel import PriceModel

from models.PriceTable import PriceTableModel

import logging

logging.basicConfig(level=logging.INFO)

prices_router = APIRouter(
    prefix="/api/prices",
    tags=["Prices"],
)


# Implement CRUD Operations for Price Database Model


# C - Create
@prices_router.post('/create', status_code=status.HTTP_201_CREATED)
def post_prices(priceModel: PriceModel, db: Session = Depends(get_db)):
    # new_price = PriceModel()
    return {'message': 'Post prices'}


# R - Read
@prices_router.get('/read_all', response_model=tuple[Union[list[PriceModel], str], int])
def get_all_prices(db: Session = Depends(get_db)):
    prices = db.query(PriceTableModel).all()
    print(prices)
    if not prices:
        return "No prices found", 404
    return prices, 200