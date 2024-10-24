from typing import Type, Union

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from Laboratory_Work_2_HTTP_Server_CRUD.database.connection import get_db
from Laboratory_Work_2_HTTP_Server_CRUD.schemas.PriceModel import PriceModel

router = APIRouter(
    prefix="/api/prices",
    tags=["Prices"],
)


# Implement CRUD Operations for Price Database Model


# C - Create
@router.post('/create', status_code=status.HTTP_201_CREATED, )
def post_prices(priceModel: PriceModel, db: Session = Depends(get_db)):
    new_price = PriceModel()
    return {'message': 'Post prices'}


# R - Read
@router.get('/read_all', response_model=tuple[Union[list[Type[PriceModel]], str], int])
def get_all_prices(db: Session = Depends(get_db)):
    prices = db.query(PriceModel).all()
    if not prices:
        return "No prices found", 404
    return prices, 200
