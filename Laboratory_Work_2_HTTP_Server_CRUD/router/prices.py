from typing import Type, Union

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.PriceModel import PriceModel, PriceModelDTO

from models.PriceTable import PriceTableModel

import logging

logging.basicConfig(level=logging.INFO)

prices_router = APIRouter(
    prefix="/api/prices",
    tags=["Prices"],
)


# Implement CRUD Operations for Price Database Model


# C - Create Operations
# Create a single price
@prices_router.post('/create',
                    response_model=dict[str, Union[str, PriceModelDTO, int]],
                    status_code=status.HTTP_201_CREATED)
def post_prices(priceModel: PriceModel, response: Response, db: Session = Depends(get_db)):
    if priceModel.price < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': 'Price cannot be negative', 'Status Code': status.HTTP_400_BAD_REQUEST}
    if len(priceModel.currency) != 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be 3 characters long", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not priceModel.currency.isalpha():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be formed of characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not priceModel.currency.isupper():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be uppercase characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    price = PriceTableModel(
        price=priceModel.price,
        currency=priceModel.currency
    )
    db.add(price)
    db.commit()
    db.refresh(price)
    return {'message': 'Added single Price', 'price': price, 'Status Code': status.HTTP_201_CREATED}


# Create multiple prices
@prices_router.post('/create_many',
                    response_model=dict[str, Union[str, list[PriceModelDTO], int]],
                    status_code=status.HTTP_201_CREATED)
def post_prices(prices: list[PriceModel], response: Response, db: Session = Depends(get_db)):
    valid_prices = []
    invalid_prices = []
    for priceModel in prices:
        price = PriceTableModel(
            price=priceModel.price,
            currency=priceModel.currency
        )
        if priceModel.price < 0 or len(priceModel.currency) != 3 or not priceModel.currency.isalpha() or not priceModel.currency.isupper():
            invalid_prices.append(price)
        else:
            valid_prices.append(price)

    if invalid_prices:
        response.status_code = status.HTTP_400_BAD_REQUEST

    if valid_prices:
        response.status_code = status.HTTP_201_CREATED
        db.add_all(valid_prices)
        db.commit()

    response_message = {
        'message': 'Added multiple Prices' if valid_prices else 'No valid prices added',
        'valid_prices': valid_prices,
        'invalid_prices': invalid_prices,
        'Status Code': status.HTTP_201_CREATED if valid_prices else status.HTTP_400_BAD_REQUEST
    }
    return response_message

# # Read from form-data
# @prices_router.post('/create_form_data',
#                     response_model=dict[str, Union[str, PriceModel, int]],
#                     status_code=status.HTTP_201_CREATED)
# def post_prices_JSON()


# R - Read Operations
# Read all prices
@prices_router.get('/read/all',
                   response_model=dict[str, Union[str, list[PriceModelDTO], int]],
                   status_code=status.HTTP_200_OK)
def get_all_prices(response: Response,
                   offset: int | None = None,
                   limit: int | None = None,
                   db: Session = Depends(get_db)):
    prices = (db.query(PriceTableModel)
              .limit(limit)
              .offset(offset)
              .all())
    for price in prices:
        print(price)
    logging.info(prices)
    if not prices:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No prices found", "Status Code": status.HTTP_404_NOT_FOUND}

    return {"message": "Successfully returned prices", "prices": prices, "Status Code": status.HTTP_200_OK}


# Read price by id
@prices_router.get('/read/id:{price_id}',
                   response_model=dict[str, Union[str, PriceModelDTO, int]],
                   status_code=status.HTTP_200_OK)
def get_all_prices_by_id(price_id: int,
                         response: Response,
                         db: Session = Depends(get_db)):
    price = (db.query(PriceTableModel)
             .filter(PriceTableModel.id == price_id)
             .first())
    print(price)
    logging.info(price)
    if not price:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No prices found", "Status Code": status.HTTP_404_NOT_FOUND}

    return {"message": "Successfully returned price", "price": price, "Status Code": status.HTTP_200_OK}


# Read price by price_amount
@prices_router.get('/read/amount:{price_amount}',
                   response_model=dict[str, Union[str, list[PriceModelDTO], int]],
                   status_code=status.HTTP_200_OK)
def get_all_prices_by_amount(price_amount: float,
                             response: Response,
                             offset: int | None = None,
                             limit: int | None = None,
                             db: Session = Depends(get_db)):
    if price_amount < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Price cannot be negative", "Status Code": status.HTTP_400_BAD_REQUEST}

    prices = (db.query(PriceTableModel)
              .filter(PriceTableModel.price == price_amount)
              .limit(limit)
              .offset(offset)
              .all())
    logging.info(prices)
    if not prices:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No prices found", "Status Code": status.HTTP_404_NOT_FOUND}

    return {"message": "Successfully returned prices", "prices": prices, "Status Code": status.HTTP_200_OK}


# Read price by currency
@prices_router.get('/read/currency:{price_currency}',
                   response_model=dict[str, Union[str, list[PriceModelDTO], int]],
                   status_code=status.HTTP_200_OK)
def get_all_prices_by_currency(price_currency: str,
                               response: Response,
                               offset: int | None = None,
                               limit: int | None = None,
                               db: Session = Depends(get_db)):
    if len(price_currency) != 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be 3 characters long", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not price_currency.isalpha():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be formed of characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not price_currency.isupper():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be uppercase characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    prices = (db.query(PriceTableModel)
              .filter(PriceTableModel.currency == price_currency)
              .limit(limit)
              .offset(offset)
              .all())
    logging.info(prices)
    if not prices:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No prices found", "Status Code": status.HTTP_404_NOT_FOUND}

    return {"message": "Successfully Returned Prices", "prices": prices, "Status Code": status.HTTP_200_OK}


# U - Update Operations
# Update price by id
@prices_router.put('/update/id:{price_id}',
                   response_model=dict[str, Union[str, PriceModelDTO, int]],
                   status_code=status.HTTP_200_OK)
def update_price_by_id(price_id: int, new_price: PriceModel, response: Response, db: Session = Depends(get_db)):
    if new_price.price < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': 'Price cannot be negative', 'Status Code': status.HTTP_400_BAD_REQUEST}
    if len(new_price.currency) != 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be 3 characters long", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not new_price.currency.isalpha():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be formed of characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not new_price.currency.isupper():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be uppercase characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    old_price = db.query(PriceTableModel).filter(PriceTableModel.id == price_id).first()
    if not old_price:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Old price not found", "Status Code": status.HTTP_404_NOT_FOUND}

    db.query(PriceTableModel).filter(PriceTableModel.id == price_id).update(new_price.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(old_price)
    return {"message": "Price updated", "updated_price": old_price, "Status Code": status.HTTP_200_OK}

# D - Delete Operations
# Delete all prices
@prices_router.delete("/delete",
                      response_model=dict[str, Union[str, int]],
                      status_code=status.HTTP_200_OK)
def delete_all_prices(response: Response,
                      db: Session = Depends(get_db)):
    if not db.query(PriceTableModel).all():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No prices found", "Status Code": status.HTTP_404_NOT_FOUND}
    db.query(PriceTableModel).delete()
    db.commit()
    return {"message": "All prices deleted", "Status Code": status.HTTP_200_OK}


# # Delete multiple prices
# @prices_router.delete("/delete/many",
#                       response_model=dict[str, Union[str, int]],
#                       status_code=status.HTTP_200_OK)
# def delete_all_prices(prices: list[PriceModel],
#                       response: Response,
#                       db: Session = Depends(get_db)):
#     valid_prices = []
#     invalid_prices = []
#     for priceModel in prices:
#         price = PriceTableModel(priceModel.model_dump(exclude_unset=True))
#         if priceModel.price < 0 or len(priceModel.currency) != 3 or not priceModel.currency.isalpha() or not priceModel.currency.isupper():
#             invalid_prices.append(price)
#         else:
#             valid_prices.append(price)



# Delete price by id
@prices_router.delete("/delete/id:{price_id}",
                      response_model=dict[str, Union[str, PriceModelDTO, int]],
                      status_code=status.HTTP_200_OK)
def delete_price_by_id(price_id: int,
                       response: Response,
                       db: Session = Depends(get_db)):
    if not db.query(PriceTableModel).filter(PriceTableModel.id == price_id).first():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Price not found", "Status Code": status.HTTP_404_NOT_FOUND}
    price = db.query(PriceTableModel).filter(PriceTableModel.id == price_id).first()
    db.query(PriceTableModel).filter(PriceTableModel.id == price_id).delete()
    db.commit()
    return {"message": "Price deleted", "price_delete": price, "Status Code": status.HTTP_200_OK}


# Delete price by price_currency
@prices_router.delete("/delete/currency:{price_currency}",
                      response_model=dict[str, Union[str, list[PriceModelDTO], int]],
                      status_code=status.HTTP_200_OK)
def delete_prices_by_currency(price_currency: str,
                              response: Response,
                              db: Session = Depends(get_db)):
    if len(price_currency) != 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be 3 characters long", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not price_currency.isalpha():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be formed of characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not price_currency.isupper():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be uppercase characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not db.query(PriceTableModel).filter(PriceTableModel.currency == price_currency).all():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Price not found", "Status Code": status.HTTP_404_NOT_FOUND}

    price = db.query(PriceTableModel).filter(PriceTableModel.currency == price_currency).all()
    db.query(PriceTableModel).filter(PriceTableModel.currency == price_currency).delete()
    db.commit()
    return {"message": "Prices deleted", "price_delete": price, "Status Code": status.HTTP_200_OK}


# Delete price by price_amount
@prices_router.delete("/delete/amount:{price_amount}",
                      response_model=dict[str, Union[str, list[PriceModelDTO], int]],
                      status_code=status.HTTP_200_OK)
def delete_prices_by_currency(price_amount: float,
                              response: Response,
                              db: Session = Depends(get_db)):
    if price_amount < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Price cannot be negative", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not db.query(PriceTableModel).filter(PriceTableModel.price == price_amount).all():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Price not found", "Status Code": status.HTTP_404_NOT_FOUND}

    prices = db.query(PriceTableModel).filter(PriceTableModel.price == price_amount).all()
    print(prices)
    db.query(PriceTableModel).filter(PriceTableModel.price == price_amount).delete()
    db.commit()
    return {"message": "Prices deleted", "price_delete": prices, "Status Code": status.HTTP_200_OK}
