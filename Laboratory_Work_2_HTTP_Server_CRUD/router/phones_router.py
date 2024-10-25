import json
import re
from typing import Type, Union

from fastapi import APIRouter, Depends, status, Response, UploadFile, File
from sqlalchemy.orm import Session

from database.connection import get_db

from schemas.PhoneModel import PhoneModel, PhoneModelDTO
from schemas.PriceModel import PriceModel
from models.PhoneTable import PhoneTableModel
from models.PriceTable import PriceTableModel

import logging

logging.basicConfig(level=logging.INFO)

phones_router = APIRouter(
    prefix="/api/phones",
    tags=["Phones"],
)

# Implement CRUD Operations for Phone Database Model

# C- Create Operations
# Create a single Phone
@phones_router.post("/create",
                    response_model=dict[str, Union[str, PhoneModelDTO, int]],
                    status_code=status.HTTP_201_CREATED)
def post_phone(phoneModel: PhoneModel,
               response: Response,
               db: Session = Depends(get_db)):
    if any(value is None for value in phoneModel.model_dump().values()):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Incomplete data provided", "status_code": response.status_code}


    phone_title: str = phoneModel.title
    if db.query(PhoneTableModel).filter(PhoneTableModel.title == phone_title).all():
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "Phone already exists", "status_code": response.status_code}

    price_currency: PriceModel = phoneModel.price_currency
    if price_currency.price < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': 'Price cannot be negative', 'Status Code': status.HTTP_400_BAD_REQUEST}
    if len(price_currency.currency) != 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be 3 characters long", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not price_currency.currency.isalpha():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be formed of characters", "Status Code": status.HTTP_400_BAD_REQUEST}
    if not price_currency.currency.isupper():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Currency must be uppercase characters", "Status Code": status.HTTP_400_BAD_REQUEST}

    # Unpack the dictionary into the key arguments
    price_currency_db = PriceTableModel(**price_currency.model_dump())
    db.add(price_currency_db)
    db.commit()
    phone_db = PhoneTableModel(**phoneModel.model_dump(exclude={'price_currency'}))
    phone_db.price_currency_id = price_currency_db.id
    db.add(phone_db)
    db.commit()
    db.refresh(phone_db)
    phoneDTO = PhoneModelDTO(id=phone_db.id, **phoneModel.model_dump())
    response.status_code = status.HTTP_201_CREATED
    return {"message": "Phone created successfully", "phone": phoneDTO, "status_code": response.status_code}


# Create multiple Phones
@phones_router.post("/create_many",
                    response_model=dict[str, Union[str, list[PhoneModelDTO], int]],
                    status_code=status.HTTP_201_CREATED)
def post_phones(phones: list[PhoneModel],
                response: Response,
                db: Session = Depends(get_db)):
    valid_phones = []
    invalid_phones = []
    for phoneModel in phones:
        price_currency: PriceModel = phoneModel.price_currency
        price_currency_db = PriceTableModel(
            price=price_currency.price,
            currency=price_currency.currency
        )

        if price_currency.price < 0 or len(price_currency.currency) != 3 or not price_currency.currency.isalpha() or not price_currency.currency.isupper():
            invalid_phone: PhoneModelDTO = PhoneModelDTO(**phoneModel.model_dump())
            invalid_phones.append(invalid_phone)
        else:
            phone_title: str = phoneModel.title
            if db.query(PhoneTableModel).filter(PhoneTableModel.title == phone_title).all():
                invalid_phone: PhoneModelDTO = PhoneModelDTO(**phoneModel.model_dump())
                invalid_phones.append(invalid_phone)
            else:
                db.add(price_currency_db)
                db.commit()
                phone_db = PhoneTableModel(**phoneModel.model_dump(exclude={'price_currency'}))
                phone_db.price_currency_id = price_currency_db.id
                valid_phones.append(phone_db)

    if invalid_phones:
        response.status_code = status.HTTP_400_BAD_REQUEST

    if valid_phones:
        response.status_code = status.HTTP_201_CREATED
        db.add_all(valid_phones)
        db.commit()

    response_message = {
        'message': 'Added multiple phones' if valid_phones else 'No valid prices added',
        'valid_phones': valid_phones,
        'invalid_phones': invalid_phones,
        'Status Code': status.HTTP_201_CREATED if valid_phones else status.HTTP_400_BAD_REQUEST
    }
    return response_message


# Create from JSON
@phones_router.post("/create_from_json",
                    response_model=dict[str, Union[str, list[PhoneModelDTO], int]],
                    status_code=status.HTTP_201_CREATED)
def post_phones_from_json(response: Response,
                          phones_json: UploadFile = File(...),
                          db: Session = Depends(get_db)):
    if phones_json.content_type != "application/json":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "File must be a JSON file", "status_code": str(response.status_code)}

    try:
        file_content = phones_json.file.read()
        phones_data = json.loads(file_content)
    except json.JSONDecodeError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Invalid JSON format", "status_code": response.status_code}
    valid_phones = []
    invalid_phones = []
    for phone_data in phones_data:
        description: str = re.sub(r'[\s\n\r]+', ' ', phone_data.get('description'))

        title: str = phone_data.get('title').strip()
        url: str = phone_data.get('url').strip()
        price_currency = phone_data.get('price_currency')
        price = price_currency.get('price')
        currency = price_currency.get('currency')

        if price < 0 or len(currency) != 3 or not currency.isalpha() or not currency.isupper():
            invalid_phone: PhoneModelDTO = PhoneModelDTO(**phone_data)
            invalid_phones.append(invalid_phone)
        else:
            if db.query(PhoneTableModel).filter(PhoneTableModel.title == title).all():
                invalid_phone: PhoneModelDTO = PhoneModelDTO(**phone_data)
                invalid_phones.append(invalid_phone)
            else:
                price_currency_db = PriceTableModel(**price_currency)
                db.add(price_currency_db)
                db.commit()
                phone_model_db = PhoneModel(title=title, url=url, description=description, price_currency=price_currency)
                phone_db = PhoneTableModel(**phone_model_db.model_dump(exclude={'price_currency'}), price_currency_id=price_currency_db.id)
                valid_phones.append(phone_db)

    if invalid_phones:
        response.status_code = status.HTTP_400_BAD_REQUEST

    if valid_phones:
        response.status_code = status.HTTP_201_CREATED
        db.add_all(valid_phones)
        db.commit()

    response_message = {
        'message': 'Added multiple phones' if valid_phones else 'No valid prices added',
        'valid_phones': valid_phones,
        'invalid_phones': invalid_phones,
        'Status Code': status.HTTP_201_CREATED if valid_phones else status.HTTP_400_BAD_REQUEST
    }
    return response_message


# R - Read Operations
# Read all Phones
@phones_router.get("/read/all",
                   response_model=dict[str, Union[str, list[PhoneModelDTO], int]],
                   status_code=status.HTTP_200_OK)
def get_phones(response: Response,
               offset: int | None = None,
                limit: int | None = None,
               db: Session = Depends(get_db)):
    phones = db.query(PhoneTableModel).offset(offset).limit(limit).all()
    if not phones:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No phones found", "status_code": response.status_code}

    phonesDTO: list[PhoneModelDTO] = []
    for phone in phones:
        price_currency_id: int = phone.price_currency_id
        price_currency = db.query(PriceTableModel).filter(PriceTableModel.id == price_currency_id).first()
        phoneDTO = PhoneModelDTO(**phone.__dict__, price_currency=price_currency.__dict__)
        phonesDTO.append(phoneDTO)

    if not phonesDTO:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No phones found", "status_code": response.status_code}
    response.status_code = status.HTTP_200_OK
    return {"message": "Phones found", "phones": phonesDTO, "status_code": response.status_code}

# Read a single Phone
@phones_router.get("/read/id:{phone_id}",
                   response_model=dict[str, Union[str, PhoneModelDTO, int]],
                   status_code=status.HTTP_200_OK)
def get_phone(phone_id: int,
              response: Response,
              db: Session = Depends(get_db)):
    phone = db.query(PhoneTableModel).filter(PhoneTableModel.id == phone_id).first()
    if not phone:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Phone not found", "status_code": response.status_code}

    price_currency_id: int = phone.price_currency_id
    price_currency = db.query(PriceTableModel).filter(PriceTableModel.id == price_currency_id).first()
    phoneDTO = PhoneModelDTO(**phone.__dict__, price_currency=price_currency.__dict__)
    response.status_code = status.HTTP_200_OK
    return {"message": "Phone found", "phone": phoneDTO, "status_code": response.status_code}

# Read Phones by Title
@phones_router.get("/read/title:{phone_title}",
                   response_model=dict[str, Union[str, list[PhoneModelDTO], int]],
                   status_code=status.HTTP_200_OK)
def get_phone_by_title(phone_title: str,
                       response: Response,
                       offset: int | None = None,
                       limit: int | None = None,
                       db: Session = Depends(get_db)):
    phones = db.query(PhoneTableModel).filter(PhoneTableModel.title.contains(phone_title)).offset(offset).limit(limit).all()
    if not phones:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No phones found", "status_code": response.status_code}

    phonesDTO: list[PhoneModelDTO] = []
    for phone in phones:
        price_currency_id: int = phone.price_currency_id
        price_currency = db.query(PriceTableModel).filter(PriceTableModel.id == price_currency_id).first()
        phoneDTO = PhoneModelDTO(**phone.__dict__, price_currency=price_currency.__dict__)
        phonesDTO.append(phoneDTO)

    response.status_code = status.HTTP_200_OK
    return {"message": "Phones found", "phones": phonesDTO, "status_code": response.status_code}


# U - Update Operations
# Update a single Phone
@phones_router.put("/update/id:{phone_id}",
                   response_model=dict[str, Union[str, PhoneModelDTO, int]],
                   status_code=status.HTTP_200_OK)
def update_phone_by_id(phone_id: int,
                       new_phone: PhoneModel,
                       response: Response,
                       db: Session = Depends(get_db)):
    if all(value is None for value in new_phone.model_dump().values()):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No data provided", "status_code": response.status_code}

    old_phone = db.query(PhoneTableModel).filter(PhoneTableModel.id == phone_id).first()
    if not old_phone:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Phone not found", "status_code": response.status_code}

    new_price_currency: PriceModel = new_phone.price_currency

    if new_price_currency is not None:
        if new_price_currency.price < 0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'message': 'Price cannot be negative', 'Status Code': status.HTTP_400_BAD_REQUEST}
        if len(new_price_currency.currency) != 3:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Currency must be 3 characters long", "Status Code": status.HTTP_400_BAD_REQUEST}
        if not new_price_currency.currency.isalpha():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Currency must be formed of characters", "Status Code": status.HTTP_400_BAD_REQUEST}
        if not new_price_currency.currency.isupper():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Currency must be uppercase characters", "Status Code": status.HTTP_400_BAD_REQUEST}

        new_price_currency_id: int = old_phone.price_currency_id
        db.query(PriceTableModel).filter(PriceTableModel.id == new_price_currency_id).update(new_price_currency.model_dump(exclude_unset=True))
        db.commit()

    # Update other phone fields selectively based on what's provided in `new_phone`
    phone_update_data = new_phone.model_dump(exclude_unset=True, exclude={'price_currency'})
    if phone_update_data:
        db.query(PhoneTableModel).filter(PhoneTableModel.id == phone_id).update(phone_update_data)
        db.commit()

    # Refresh and return updated phone
    db.refresh(old_phone)
    new_price_currency_id = old_phone.price_currency_id
    new_phoneDTO = PhoneModelDTO(
        **old_phone.__dict__,
        price_currency=db.query(PriceTableModel).filter(
            PriceTableModel.id == new_price_currency_id).first().__dict__
    )
    logging.info(new_phoneDTO)
    response.status_code = status.HTTP_200_OK
    return {"message": "Phone updated successfully", "phone": new_phoneDTO, "status_code": response.status_code}

# D - Delete Operations
# Delete all phones
@phones_router.delete("/delete/all",
                      response_model=dict[str, Union[str, int]],
                      status_code=status.HTTP_200_OK)
def delete_all_phones(response: Response,
                      db: Session = Depends(get_db)):
    db.query(PhoneTableModel).delete()
    db.query(PriceTableModel).delete()
    db.commit()
    response.status_code = status.HTTP_200_OK
    return {"message": "All phones deleted successfully", "status_code": response.status_code}


# Delete a single Phone
@phones_router.delete("/delete/id:{phone_id}",
                      response_model=dict[str, Union[str, PhoneModelDTO, int]],
                      status_code=status.HTTP_200_OK)
def delete_phone_by_id(phone_id: int,
                       response: Response,
                       db: Session = Depends(get_db)):
    phone = db.query(PhoneTableModel).filter(PhoneTableModel.id == phone_id).first()
    if not phone:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Phone not found", "status_code": response.status_code}

    price_currency_id: int = phone.price_currency_id
    if not db.query(PhoneTableModel).filter(PhoneTableModel.price_currency_id == price_currency_id).first():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Price for this phone not found", "status_code": response.status_code}

    db.query(PhoneTableModel).filter(PhoneTableModel.id == phone_id).delete()
    db.query(PriceTableModel).filter(PriceTableModel.id == price_currency_id).delete()
    db.commit()
    response.status_code = status.HTTP_200_OK
    return {"message": "Phone deleted successfully", "status_code": response.status_code}
