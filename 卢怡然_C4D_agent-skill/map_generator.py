# -*- coding: utf-8 -*-
"""
SIAS University 交互式地图生成模块
====================================
使用 Folium 库将本地 Gemma 4 模型生成的地点数据渲染为交互式 HTML 地图。

功能：
- 根据模型输出的 JSON 数据创建 Folium 地图
- 每个地点添加可点击的标记点（Marker）
- 标记点弹窗展示：英文名称、中文名称、坐标、描述
- 地图支持缩放、拖拽、全屏
- 保存为可直接浏览器打开的 HTML 文件

作者：卢怡然
日期：2026-10
"""

import folium
from folium.plugins import Fullscreen, MeasureControl, MousePosition

import config


def generate_map(locations):
    """
    根据地点数据生成交互式 Folium 地图。

    参数：
        locations (list): 地点列表，每个地点为字典，包含：
            - name: 英文名称
            - name_zh: 中文名称
            - latitude: 纬度
            - longitude: 经度
            - description: 描述

    返回：
        str: 生成的 HTML 地图文件路径
    """
    # 创建 Folium 地图，以 SIAS University 为中心
    m = folium.Map(
        location=[config.SIAS_CENTER_LAT, config.SIAS_CENTER_LON],
        zoom_start=config.MAP_ZOOM_START,
        tiles="OpenStreetMap",  # 使用 OpenStreetMap 瓦片
        control_scale=True  # 显示比例尺
    )

    # 添加全屏控制插件
    Fullscreen(position="topleft").add_to(m)

    # 添加测距工具
    MeasureControl(position="topright").add_to(m)

    # 添加鼠标坐标显示
    MousePosition(position="bottomleft", separator=" , ").add_to(m)

    # 添加图层控制器（支持切换不同底图）
    folium.TileLayer("OpenStreetMap", name="标准地图").add_to(m)
    folium.TileLayer("Stamen Terrain", name="地形图").add_to(m)
    folium.TileLayer("Stamen Toner", name="黑白图").add_to(m)
    folium.LayerControl(position="bottomright").add_to(m)

    # 添加 SIAS University 中心标记（特殊样式）
    folium.Marker(
        location=[config.SIAS_CENTER_LAT, config.SIAS_CENTER_LON],
        popup=folium.Popup(
            f"""
            <div style="min-width: 200px;">
                <h3 style="color: #d4380d; margin: 0;">SIAS University</h3>
                <h4 style="color: #d4380d; margin: 5px 0;">郑州西亚斯学院</h4>
                <p style="margin: 5px 0;">坐标: {config.SIAS_CENTER_LAT}, {config.SIAS_CENTER_LON}</p>
                <p style="margin: 5px 0;">河南省新郑市，是一所以国际化教育为特色的本科院校。</p>
                <p style="margin: 5px 0; color: #999; font-size: 12px;">★ 中心定位点</p>
            </div>
            """,
            max_width=350
        ),
        tooltip="郑州西亚斯学院（中心点）",
        icon=folium.Icon(color="red", icon="star", prefix="fa")
    ).add_to(m)

    # 遍历模型生成的地点列表，添加标记点
    for i, loc in enumerate(locations):
        # 提取地点信息（容错：如果字段缺失则使用默认值）
        name = loc.get("name", f"Location_{i+1}")
        name_zh = loc.get("name_zh", "未知地点")
        latitude = float(loc.get("latitude", 0))
        longitude = float(loc.get("longitude", 0))
        description = loc.get("description", "暂无描述")

        # 跳过坐标无效的地点
        if latitude == 0 and longitude == 0:
            print(f"  [跳过] 第 {i+1} 个地点坐标无效: {name_zh}")
            continue

        # 构建弹窗 HTML 内容
        popup_html = f"""
        <div style="min-width: 220px; font-family: 'Microsoft YaHei', sans-serif;">
            <h3 style="color: #1890ff; margin: 0 0 5px 0;">{name}</h3>
            <h4 style="color: #333; margin: 0 0 8px 0;">{name_zh}</h4>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 8px 0;">
            <p style="margin: 4px 0;"><b>纬度:</b> {latitude}</p>
            <p style="margin: 4px 0;"><b>经度:</b> {longitude}</p>
            <p style="margin: 4px 0;"><b>描述:</b> {description}</p>
        </div>
        """

        # 根据地点序号分配不同颜色
        colors = ["blue", "green", "purple", "orange", "darkblue", "cadetblue", "darkgreen", "gray"]
        marker_color = colors[i % len(colors)]

        # 添加标记点到地图
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{name_zh} - 点击查看详情",
            icon=folium.Icon(color=marker_color, icon="info-sign", prefix="fa")
        ).add_to(m)

        print(f"  [添加] {i+1}. {name_zh} ({name}) - ({latitude}, {longitude})")

    # 在地图上添加 SIAS 周边圆形区域指示
    folium.Circle(
        radius=2000,  # 半径 2000 米
        location=[config.SIAS_CENTER_LAT, config.SIAS_CENTER_LON],
        popup="SIAS 周边区域 (2km)",
        color="#1890ff",
        fill=True,
        fill_color="#1890ff",
        fill_opacity=0.05
    ).add_to(m)

    # 在地图底部添加版权与信息说明
    info_html = f"""
    <div style="
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255,255,255,0.9);
        padding: 5px 15px;
        border-radius: 5px;
        font-size: 12px;
        color: #666;
        z-index: 9999;
        font-family: 'Microsoft YaHei', sans-serif;
    ">
        SIAS University 交互式地图 | 数据由本地 Gemma 4 E4B 生成 | 卢怡然 C4D 作业
    </div>
    """
    m.get_root().html.add_child(folium.Element(info_html))

    # 保存地图为 HTML 文件
    output_path = config.MAP_OUTPUT_FILE
    m.save(output_path)

    print(f"\n地图已生成: {output_path}")
    print(f"共标记 {len(locations)} 个地点 + 1 个中心点（SIAS University）")
    print(f"请在浏览器中打开 {output_path} 查看交互式地图。")

    return output_path


def generate_demo_map():
    """
    生成演示用地图（不依赖模型输出）。

    此函数仅用于在没有运行 Ollama 时生成示例地图。
    实际作业中，地点数据必须由本地 Gemma 4 模型生成（通过 sias_agent.py 调用）。

    【注意】此函数中的地点数据仅为演示目的，
    实际运行 sias_agent.py 时，数据完全由本地模型生成。
    """
    # 以下数据为 SIAS University 周边的代表性地点坐标
    # 实际作业中，这些数据由本地 Gemma 4 模型通过 API 返回
    demo_locations = [
        {
            "name": "SIAS University Main Gate",
            "name_zh": "西亚斯学院正门",
            "latitude": 34.4065,
            "longitude": 113.7382,
            "description": "郑州西亚斯学院正门入口，是校园的主要出入口，气势恢宏。"
        },
        {
            "name": "SIAS University Library",
            "name_zh": "西亚斯图书馆",
            "latitude": 34.4055,
            "longitude": 113.7395,
            "description": "学校中心图书馆，藏书丰富，是学生自习和查阅资料的主要场所。"
        },
        {
            "name": "SIAS Sports Center",
            "name_zh": "西亚斯体育中心",
            "latitude": 34.4072,
            "longitude": 113.7408,
            "description": "校内体育场馆，包含篮球场、田径场等设施，举办各类体育赛事。"
        },
        {
            "name": "SIAS Student Dormitory",
            "name_zh": "学生公寓区",
            "latitude": 34.4045,
            "longitude": 113.7372,
            "description": "学生宿舍集中区域，生活设施齐全，距离教学区步行约10分钟。"
        },
        {
            "name": "SIAS Cafeteria",
            "name_zh": "西亚斯食堂",
            "latitude": 34.4058,
            "longitude": 113.7388,
            "description": "校内主食堂，提供多种餐饮选择，覆盖南北风味，价格实惠。"
        },
        {
            "name": "Xinzheng East Bus Station",
            "name_zh": "新郑东站",
            "latitude": 34.4120,
            "longitude": 113.7450,
            "description": "新郑市东部汽车站，距离西亚斯学院约2公里，可乘坐公交直达。"
        },
        {
            "name": "Xinzheng People's Park",
            "name_zh": "新郑人民公园",
            "latitude": 34.3985,
            "longitude": 113.7330,
            "description": "新郑市中心城市公园，周末休闲好去处，有湖景和绿化带。"
        },
        {
            "name": "Xinzheng Museum",
            "name_zh": "新郑博物馆",
            "latitude": 34.4000,
            "longitude": 113.7300,
            "description": "展示新郑历史文化，馆藏丰富，了解当地历史的好地方。"
        }
    ]

    print("[演示模式] 使用演示数据生成地图...")
    print("【注意】实际运行时，数据由本地 Gemma 4 模型生成，不会使用此演示数据。")
    generate_map(demo_locations)


if __name__ == "__main__":
    generate_demo_map()
