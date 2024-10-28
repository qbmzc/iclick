# -*- coding:utf-8 -*-
"""
@Author:ddz
@Date:2024/10/14 16:42
@Project:app_click
"""
from fastapi import FastAPI, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

from ialgo import TravelingSalesman
from ialgo import AmapDriving
from ialgo import iCenterline

app = FastAPI()


class iloc(BaseModel):
    lat: float
    lng: float


class Location(BaseModel):
    pts: List[iloc]


@app.post("/location/")
async def receive_location(location: Location):
    # 处理前端传入的坐标点
    pnts = [{"lat": _.lat, "lng": _.lng} for _ in location.pts]
    otravel = TravelingSalesman(pnts)
    pnts = otravel.find_shortest_path()  # 点排序
    path = []  # 高德规划路径 多段
    for fp, tp in zip(pnts[:-1], pnts[1:]):
        oAmap = AmapDriving(fp)
        amap_path = oAmap.get_driving_route(fp, tp)
        path.append(amap_path)
    path = ';'.join(path)  # 高德路径拼接
    path = [eval(_) for _ in path.split(';')]
    oline = iCenterline(path)  # 计算中心线 防止回头路
    res = oline.iSampleLine()  # 格式同 Location
    return res


@app.get("/")
async def iclick_html():
    return FileResponse('templates/pathBaseMultiPoint.html')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
