from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import image_processor

app = Flask(__name__)
CORS(app)

# 默认参数配置
DEFAULT_PARAMS = {
    "sampling_rate": 0.05,
    "origin_x": 0.0,
    "origin_y": 0.0,
    "scale": 1.0,
    "method": "contour",
    "mode": "vertical",
    "time_s": 0,
    "time_e": 0
}

@app.route('/process', methods=['POST'])
def handle_image_processing():
    try:
        # 获取上传文件
        if 'image' not in request.files:
            raise BadRequest("未上传图片文件")
        
        file = request.files['image']
        if file.filename == '':
            raise BadRequest("无效的文件名")

        # 获取参数（带默认值）
        params = {
            'sampling_rate': float(request.form.get('sampling_rate', DEFAULT_PARAMS['sampling_rate'])),
            'origin_x': float(request.form.get('origin_x', DEFAULT_PARAMS['origin_x'])),
            'origin_y': float(request.form.get('origin_y', DEFAULT_PARAMS['origin_y'])),
            'scale': float(request.form.get('scale', DEFAULT_PARAMS['scale'])),
            'time_s': int(request.form.get('time_s', DEFAULT_PARAMS['time_s'])),
            'time_e': int(request.form.get('time_e', DEFAULT_PARAMS['time_e'])),
            "method": request.form.get('method', DEFAULT_PARAMS['method']),
            "mode": request.form.get('mode', DEFAULT_PARAMS['mode'])
        }

        instructions = image_processor.process_image(
            image_data=file.read(),
            sampling_rate=params['sampling_rate'],
            offest_x=params['origin_x'],
            offset_y=params['origin_y'],
            scale=params['scale'],
            time_s=params['time_s'],
            time_e=params['time_e'],
            method=params['method'],
            mode=params['mode']
        )
        
        #     raise ValueError(f"不支持的处理方法: {method}，可选值为 'contour' 或 'thinning'")

        return jsonify({
            "status": "success",
            "instruction_count": len(instructions),
            "instructions": instructions
        })
    
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": f"参数错误: {str(e)}"
        }), 400
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"处理失败: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)