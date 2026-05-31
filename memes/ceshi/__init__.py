from pathlib import Path
from typing import List
from pil_utils import BuildImage  # 核心图像包装库
from meme_generator import add_meme, MemeArgsModel

# 1. 定义该表情包的静态素材目录
img_dir = Path(__file__).parent / "images"

# 2. 编写表情包生成的核心函数
def make_my_meme(images: List[BuildImage], texts: List[str], args: MemeArgsModel):
    """
    表情包合成函数
    """
    # 获取用户传入的第一张图片（转化为 RGBA 格式并转换为正方形）
    user_img = images[0].convert("RGBA").square()
    
    # 加载保存在 images 目录下的背景图片
    bg_img = BuildImage.open(img_dir / "background.png")
    
    # 调整用户图片的尺寸，例如缩放到 200x200 像素
    user_img = user_img.resize((200, 200))
    
    # 将用户图片贴到背景图指定位置 (x, y) = (50, 50)
    bg_img.paste(user_img, (50, 50), alpha=True)
    
    # 如果用户输入了文字，则进行绘制
    if texts:
        text = texts[0]
        # 在背景图的特定矩形框区域 (x, y, width, height) 内绘制文本
        bg_img.draw_text(
            (30, 270, 270, 320), 
            text, 
            font_size=24, 
            fill="black", 
            halign="center",    # 水平居中
            valign="center"     # 垂直居中
        )
    # 直接调用对象自带的方法返回（无需任何额外 import）
    return bg_img.save_png()

# 3. 注册该表情包到系统
add_meme(
    "ceshi",                 # 表情包的唯一 Key
    make_my_meme,            # 绑定上方编写的制作逻辑函数
    min_images=1,            # 至少需要 1 张图
    max_images=1,            # 至多需要 1 张图
    min_texts=1,             # 至少需要 1 行字
    max_texts=1,             # 至多需要 1 行字
    keywords=["测试"],       # 触发词
)