import cv2
import numpy as np
import os
from datetime import datetime

def save_test_image(image_data):
    # 确保/test文件夹存在
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    # # 生成带时间戳的文件名
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_path = os.path.join(test_dir, f"contours_{timestamp}.jpg")

    # 覆盖，保存图像
    output_path = os.path.join(test_dir, f"contours.jpg")

    # 保存图像
    cv2.imwrite(output_path, image_data)

def process_image(image_data, 
                  sampling_rate,
                  offest_x, offset_y, 
                  scale, 
                  time_s, time_e,
                  method="thinging",
                  mode="vertical",
                  save_test=False):
    """图像处理函数，生成arc黑线指令
    
    Args:
        image_data: 图片二进制数据
        sampling_rate: 采样率 (0.01~0.1)
        offest_x: X轴偏移
        offset_y: Y轴偏移
        scale: 缩放倍数
        time_s: 起始时间(对于timeline模式)
        time_e: 结束时间(对于timeline模式)
        method: 处理方法（默认为thinging）
        mode: 处理模式（默认为vertical）
        
    Returns:
        list: 直线指令列表
    """
    # 参数校验
    if not (0.001 <= sampling_rate <= 0.1):
        raise ValueError("采样率需在0.001到0.1之间")
    if scale <= 0:
        raise ValueError("缩放倍数必须大于0")

    # 解码图像
    img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("无法读取图像数据")

    cv2.imshow("img", img)
    # 二值化处理(THRESH_BINARY_INV黑白反色处理，OTSU自动阈值处理)
    ret, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    if method == "contour":
        # 提取轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    elif method == "thinning":
        # 先进行骨架化：利用 cv2.ximgproc.thinning 方法
        skeleton = cv2.ximgproc.thinning(binary, thinningType=cv2.ximgproc.THINNING_GUOHALL)
        # 再提取骨架的轮廓
        contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    else:
        raise ValueError(f"不支持的处理方法: {method}，可选值为 'contour' 或 'thinning'")

    if save_test:
        # 创建一个新图像用于显示轮廓
        contour_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)

        # 保存测试图像
        save_test_image(contour_image)
    
    instructions = []
    image_height = img.shape[0]
    image_width = img.shape[1]
    
    # 计算最大尺寸用于归一化（保持比例）
    max_dimension = max(image_width, image_height)
    
    for contour in contours:
        # 计算轮廓周长用于采样率
        epsilon = sampling_rate * cv2.arcLength(contour, True)
        
        # 多边形近似
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # 生成线段指令
        for i in range(len(approx)):
            # 获取当前点和下一个点
            x1, y1 = approx[i][0]
            
            # 如果是最后一个点则连接回第一个点（闭合轮廓）
            if i == len(approx) - 1:
                x2, y2 = approx[0][0]
            else:
                x2, y2 = approx[i+1][0]

            # 坐标变换（归一化 + 翻转Y轴 + 缩放 + 平移）
            x1_norm = x1 / max_dimension
            y1_norm = (image_height - y1) / max_dimension
            x2_norm = x2 / max_dimension
            y2_norm = (image_height - y2) / max_dimension

            if mode == "vertical":
                # 在同一时间的垂直平面上生成traces(XY平面)，忽略终止时间 
                
                # 应用缩放和平移
                x1_trans = x1_norm * scale + offest_x
                y1_trans = y1_norm * scale + offset_y
                x2_trans = x2_norm * scale + offest_x
                y2_trans = y2_norm * scale + offset_y

                # 保留三位小数
                instructions.append(
                    f"arc({time_s},{time_s},{x1_trans:.3f},{x2_trans:.3f},s,{y1_trans:.3f},{y2_trans:.3f},0,none,true);"
                )
            elif mode == "timeline":
                # 在X轴与时间轴轨道组成平面上生成traces(XY平面)，起止时间决定垂直方向的拉伸系数
                # Y值由offset_y决定

                x1_trans = x1_norm * scale + offest_x
                x2_trans = x2_norm * scale + offest_x

                t1_trans = y1_norm * scale * (time_e - time_s) + time_s
                t2_trans = y2_norm * scale * (time_e - time_s) + time_s
                t1_trans = int(t1_trans)
                t2_trans = int(t2_trans)
                # 如果t1_trans大于t2_trans，交换它们的值，保证trace的起始时间小于结束时间
                if t1_trans > t2_trans:
                    t1_trans, t2_trans = t2_trans, t1_trans
                
                instructions.append(
                    f"arc({t1_trans},{t2_trans},{x1_trans:.3f},{x2_trans:.3f},s,{offset_y:.3f},{offset_y:.3f},0,none,true);"
                )  
            else:
                pass
        
    return instructions

# 测试代码
if __name__ == "__main__":
    with open("test.jpeg", "rb") as f:
        image_data = f.read()
    
    instructions = process_image(image_data, 0.01, 0, 0, 1, 100, 100, method="thinning", mode="vertical", save_test=True)
    for instr in instructions:
        print(instr)