import io
import requests
import numpy as np
from PIL import Image

class RecraftVectorizeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {
                    "default": "t3UvHXxY30Hpu7eRrFfQgaha2JRvkfnglGf8iHyvfEHeCYy9bDxyQKYW38AWF8ES",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("SVG",)
    RETURN_NAMES = ("svg",)
    FUNCTION = "vectorize"
    CATEGORY = "Recraft"

    def vectorize(self, image, api_key):
        try:
            # 处理图像（取第一张，转换格式）
            image_tensor = image[0]  # 取batch中的第一张
            image_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
            
            # CHW -> HWC
            if image_np.shape[0] == 3:
                image_np = image_np.transpose(1, 2, 0)
            
            # 转换为PIL图像
            pil_image = Image.fromarray(image_np)
            
            # 转换为字节
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            
            # 准备API请求
            url = "https://external.api.recraft.ai/v1/images/vectorize"
            headers = {"Authorization": f"Bearer {api_key}"}
            files = {"file": ("image.png", img_buffer.getvalue(), "image/png")}
            
            # 发送请求
            print("🔄 正在调用Recraft API...")
            response = requests.post(url, headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                svg_url = result.get("image", {}).get("url")
                if svg_url:
                    print(f"✅ 获取SVG URL: {svg_url}")
                    
                    # 下载SVG内容
                    svg_response = requests.get(svg_url, timeout=30)
                    if svg_response.status_code == 200:
                        svg_data = svg_response.text
                        print(f"✅ 下载SVG成功，长度: {len(svg_data)} 字符")
                        
                        # 正确创建SVG对象 - 使用BytesIO
                        svg_bytes_io = io.BytesIO(svg_data.encode('utf-8'))
                        
                        # 导入SVG类并创建对象
                        from comfy_extras.nodes_images import SVG
                        svg_object = SVG([svg_bytes_io])
                        
                        return (svg_object,)
                    else:
                        raise Exception(f"下载SVG失败: {svg_response.status_code}")
                else:
                    raise Exception("响应中未找到SVG URL")
            else:
                raise Exception(f"API错误 {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ 矢量化失败: {str(e)}")
            raise

# 节点映射
NODE_CLASS_MAPPINGS = {
    "RecraftVectorizeImage": RecraftVectorizeNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RecraftVectorizeImage": "Recraft图像矢量化"
}