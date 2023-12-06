from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

users_db = []
transactions_db = []
credit_db = []

app = FastAPI()

class User(BaseModel):
    username: str
    password: str
    balance: float=0.0
    email: str
    credit: float=0.0
    
@app.get('/users/', response_model=List[User])
async def read_users():
    return users_db
    
@app.get('/users/{user_id}', response_model=User)   
async def read_user(user_id: int):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.post('/users/', response_model=User)
async def create_user(user: User):
    user_dict = user.dict()
    user_dict['balance'] = 0.0
    users_db.append(user_dict)
    return user_dict

@app.put('/users/{user_id}', response_model=User)
async def update_user(user_id: int, user: User):
    user_dict = user.dict()
    users_db[user_id] = user_dict
    return user_dict
    
@app.delete('/users/{user_id}', response_model=User)
async def delete_user(user_id: int):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        users_db.pop(user_id)
        
    return f"User deleted"


@app.post('/deposit/{user_id}', response_model=User)
async def deposit(user_id: int, amount: float):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        users_db[user_id]['balance'] += amount
    return users_db[user_id]

@app.get('/balance/{user_id}', response_model=float)
async def get_balance(user_id: int):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]['balance']

@app.put('/withdraw/{user_id}', response_model=float)
async def withdraw(user_id: int, amount: float):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    
    else:
        user = users_db[user_id]
    
        if user['balance'] < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        user['balance'] -= amount
        return user

    
@app.post("/credit/{user_id}", response_model=User)
async def issue_credit(user_id: int, credit_limit: float):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    
    if credit_limit < 0:
        raise HTTPException(status_code=400, detail="Invalid credit limit")
    if credit_limit < 1000 and credit_limit > 10000:
        raise HTTPException(status_code=400, detail="Credit limit must be between 1000 and 10000")
    
    user = users_db[user_id]
    try: 
        if user['credit'] > 0 and user['credit'] < 100000:
            user['credit'] += credit_limit
            user['balance'] += credit_limit
        elif user['credit'] == 0:
            user['credit'] = credit_limit
            user['balance'] += credit_limit
            return user
        else: 
            raise HTTPException(status_code=400, detail="Credit limit exceeded")
    except KeyError:
        user['credit'] = credit_limit
        user['balance'] += credit_limit
        return user
            
    
@app.get("/credit/{user_id}", response_model=float)
async def get_credit(user_id: int):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        return users_db[user_id]['credit']
    except KeyError:
        return 0.0
    
@app.put("/credit/payment/{user_id}", response_model=User)
async def pay_credit(user_id: int, amount: float):
    if user_id < 0 and user_id > len(users_db)-1:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    try:
        if user['credit'] <= 0:
            raise HTTPException(status_code=400, detail="No credit balance")
        if user['balance'] < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
    
        user['credit'] -= amount
        user['balance'] -= amount
        return user 
    
    except KeyError:
        raise HTTPException(status_code=400, detail="No credit balance")
    

