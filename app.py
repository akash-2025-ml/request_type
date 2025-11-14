# filename: main.py
from fastapi import FastAPI
from pydantic import BaseModel
from redis_1 import get_value
import datetime

strat1 = datetime.datetime.now()
print("request_type#fast api start" + str(strat1))
app = FastAPI()


# Define request model
class InputData(BaseModel):
    Massage_Id: str
    Tanent_id: str
    mailbox_id: str


# Define response model (optional, you can return dict directly)
class OutputData(BaseModel):
    # result: str
    signal: str
    value: str


@app.post("/process", response_model=OutputData)
async def process_text(data: InputData):
    # You can modify this logic based on your processing
    input_text = data.Massage_Id
    output_text = get_value(input_text)  # example: convert input to uppercase
    end = datetime.datetime.now()
    print("request_type#fast api end" + str(end))
    print("total time taken by fast api = ", (end - strat1))
    # return {"result": output_text}
    return {"signal": "request_type", "value": output_text}


# Root endpoint (optional)
@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}
