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

def process_image(image_data, sampling_rate, origin_x, origin_y, scale, time_s, time_e):
    """核心图像处理函数
    
    Args:
        image_data: 图片二进制数据
        sampling_rate: 采样率 (0.01~0.1)
        origin_x: 原点X坐标
        origin_y: 原点Y坐标
        scale: 缩放倍数
        
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
    
    # 提取轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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
            
            # 应用缩放和平移
            x1_trans = x1_norm * scale + origin_x
            y1_trans = y1_norm * scale + origin_y
            x2_trans = x2_norm * scale + origin_x
            y2_trans = y2_norm * scale + origin_y

            # 保留三位小数
            instructions.append(
                f"arc({time_s},{time_e},{x1_trans:.3f},{x2_trans:.3f},s,{y1_trans:.3f},{y2_trans:.3f},0,none,true);"
            )
    
    return instructions

def process_image_thinning(image_data, sampling_rate, origin_x, origin_y, scale, time_s, time_e):
    """利用骨架化（细化）输出图片形状的核心图像处理函数
    
    Args:
        image_data: 图片二进制数据
        sampling_rate: 采样率 (0.001~0.1)
        origin_x: 原点X坐标
        origin_y: 原点Y坐标
        scale: 缩放倍数
        
    Returns:
        list: 直线指令列表
    """
    # 参数校验
    if not (0.001 <= sampling_rate <= 0.1):
        raise ValueError("采样率需在0.001到0.1之间")
    if scale <= 0:
        raise ValueError("缩放倍数必须大于0")

    # 解码图像，转换为灰度图
    img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("无法读取图像数据")

    # 二值化处理 (THRESH_BINARY_INV黑白反色处理，OTSU自动阈值处理)
    ret, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 骨架化（细化）：利用 cv2.ximgproc.thinning 方法
    skeleton = cv2.ximgproc.thinning(binary, thinningType=cv2.ximgproc.THINNING_GUOHALL)
    
    # # 显示骨架图像（调试用）
    # cv2.imshow("skeleton", skeleton)
    # cv2.waitKey(0)  # 按任意键继续
    # cv2.destroyAllWindows()
    
    # 保存测试骨架图像
    save_test_image(skeleton)
    
    # 提取骨架的轮廓
    contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    instructions = []
    image_height = img.shape[0]
    image_width = img.shape[1]
    
    # 计算最大尺寸用于归一化（保持比例）
    max_dimension = max(image_width, image_height)
    
    for contour in contours:
        # 根据采样率计算轮廓近似参数
        epsilon = sampling_rate * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # 遍历近似轮廓的点，生成线段指令
        for i in range(len(approx)):
            x1, y1 = approx[i][0]
            # 如果是最后一点，则与第一点相连（闭合轮廓）
            if i == len(approx) - 1:
                x2, y2 = approx[0][0]
            else:
                x2, y2 = approx[i+1][0]
                
            # 坐标变换（归一化 + 翻转Y轴 + 缩放 + 平移）
            x1_norm = x1 / max_dimension
            y1_norm = (image_height - y1) / max_dimension
            x2_norm = x2 / max_dimension
            y2_norm = (image_height - y2) / max_dimension
            
            # 应用缩放和平移
            x1_trans = x1_norm * scale + origin_x
            y1_trans = y1_norm * scale + origin_y
            x2_trans = x2_norm * scale + origin_x
            y2_trans = y2_norm * scale + origin_y

            # 格式化指令，保留三位小数
            # instructions.append(
            #     f"LINE ({x1_trans:.3f}, {y1_trans:.3f}) -> ({x2_trans:.3f}, {y2_trans:.3f})"
            # )

            instructions.append(
                f"arc({time_s},{time_e},{x1_trans:.3f},{x2_trans:.3f},s,{y1_trans:.3f},{y2_trans:.3f},0,none,true);"
            )

    
    return instructions

# 测试代码
if __name__ == "__main__":
    with open("test.jpeg", "rb") as f:
        image_data = f.read()
    
    instructions = process_image_thinning(image_data, 0.01, 0, 0, 1)
    for instr in instructions:
        print(instr)