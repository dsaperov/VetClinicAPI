import time
from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str

    # Хотел сделать pk: int | None = None, но тогда в components -> schemas -> Dog -> properties -> pk:
    # anyOf {int | null}, а в исходной документации такого нет
    pk: int = None
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}


post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]


@app.get('/', summary='Root')
def root():
    return 'Welcome!'


@app.post('/post', response_model=Timestamp, summary='Get Post')
def get_post():
    last_timestamp_id = post_db[-1].id
    new_timestamp = Timestamp(id=last_timestamp_id+1, timestamp=int(time.time()))
    post_db.append(new_timestamp)
    return new_timestamp


@app.get('/dog', response_model=List[Dog], summary='Get Dogs')
def get_dogs(kind: DogType = None):
    if not kind:
        return dogs_db.values()
    dogs = [dog for dog in dogs_db.values() if dog.kind == kind]
    return dogs


@app.post('/dog', response_model=Dog, summary='Create Dog')
def create_dog(dog: Dog):
    if dog.pk is None:
        dog.pk = max(dogs_db.keys()) + 1
    elif dog.pk in dogs_db:
        raise HTTPException(status_code=409, detail='The specified PK already exists.')
    dogs_db[dog.pk] = dog
    return dog


@app.get('/dog/{pk}', response_model=Dog, summary='Get Dog By Pk')
def get_dog_by_pk(pk: int):
    if pk not in dogs_db:
        raise HTTPException(status_code=404, detail='The specified PK is not found.')
    return dogs_db[pk]


@app.patch('/dog/{pk}', response_model=Dog, summary='Update Dog')
def update_dog(pk: int, dog: Dog):
    if pk not in dogs_db:
        raise HTTPException(status_code=404, detail='The specified PK is not found.')
    if pk != dog.pk:
        raise HTTPException(status_code=403, detail='PK modification is not allowed.')
    dogs_db[pk] = dog
    return dog
