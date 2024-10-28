# -*- coding:utf-8 -*-
"""
@Author:ddz
@Date:2024/10/24 10:07
@Project:ialgo
"""
import itertools
from geopy.distance import geodesic
from shapely.geometry import LineString
from pygeoops import centerline
import geopandas as gpd
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

# from ilog import logger


class TravelingSalesman:
    # 旅行商问题
    # 输入：经纬度点列表
    # 输出：排序好的点列表
    def __init__(self, points):
        self.points = points  # 经纬度点列表
        self.min_distance = float('inf')  # 最小距离初始化为无穷大
        self.best_path = []  # 最优路径

    def calculate_distance2(self, point1, point2):
        """计算两点间的欧几里得距离"""
        print(point1[::-1], point2[::-1])
        return geodesic(point1[::-1], point2[::-1]).m

    def calculate_distance(self, point1, point2):
        """计算两点间的欧几里得距离"""
        # 检查输入参数是否为元组或列表
        if not (isinstance(point1, (tuple, list)) and isinstance(point2, (tuple, list))):
            raise ValueError("Points must be tuples or lists")

        # 检查每个点是否包含两个元素
        if len(point1) != 2 or len(point2) != 2:
            raise ValueError("Each point must contain exactly two elements (latitude, longitude)")

        # 计算距离
        distance = geodesic(point1, point2).m

        # 记录日志
        logging.debug(f"Calculating distance between {point1} and {point2}")
        logging.debug(f"Distance: {distance} meters")

        return distance

    def find_shortest_path(self):
        """找到旅行商问题的最短路径"""
        # 生成所有可能的路径
        for path in itertools.permutations(self.points):
            distance = self.calculate_total_distance(path)
            if distance < self.min_distance:
                self.min_distance = distance
                self.best_path = path

        return self.best_path

    def calculate_total_distance(self, path):
        """计算给定路径的总距离"""
        total_distance = 0
        for i in range(len(path) - 1):
            total_distance += self.calculate_distance(path[i], path[i + 1])

        return total_distance


class iCenterline:
    def __init__(self, points, crs='epsg:4525'):
        # points 经纬度点列表
        self.gps = gpd.GeoSeries(LineString(points), crs=4326).to_crs(crs)
        self.crs = crs

    def iSampleLine(self):
        sline = self.gps.geometry.values[0]
        sline = sline.buffer(30).buffer(-15)
        cline = centerline(sline)
        gps = gpd.GeoSeries(cline, crs=self.crs).to_crs(4326)
        gps.to_file('vector/cline.geojson', driver='GeoJSON')
        return [{'lng': lng, 'lat': lat} for lng, lat in gps.geometry.values[0].coords]


class AmapDriving:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://restapi.amap.com/v3/direction/driving"

    def get_driving_route(self, origin, destination):
        params = {
            'key': self.api_key,
            'origin': origin,  # 起点经纬度，格式为"经度,纬度"
            'destination': destination  # 终点经纬度，格式为"经度,纬度"
        }
        response = requests.get(self.url, params=params)
        route_info = response.json()
        if route_info.get('status') == '1':
            path_segments = route_info.get('route').get('paths')[0].get('steps')
            path = []
            for ipath in path_segments:
                path.append(ipath.get('polyline'))
            path = ';'.join(path)
        else:
            path = ''

        print("驾车路线信息:", path)
        return path


if __name__ == "__main__":
    # 输入一些经纬度点
    points = [(34.89042, 113.4074), (34.82304, 113.4737), (34.80522, 113.2437), (34.8566, 113.23522)]
    points = [_[::-1] for _ in points]
    tsp = TravelingSalesman(points)
    best_path = tsp.find_shortest_path()
    cline = iCenterline(best_path)
    sline = cline.iSampleLine()
    print("最短路径:", best_path)
