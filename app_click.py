# -*- coding:utf-8 -*-
"""
@Author:ddz
@Date:2024/10/14 16:42
@Project:app_click
"""
from fastapi import FastAPI, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

class Location(BaseModel):
    latitude: float
    longitude: float

@app.post("/location/")
async def receive_location(location: Location = Body(...)):
    res = {"latitude": location.latitude, "longitude": location.longitude}
    print(res)
    return res

@app.get("/")
async def iclick_html():
    return FileResponse('iclick.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
