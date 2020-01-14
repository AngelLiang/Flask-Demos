# coding=utf-8

import random
import string
from io import BytesIO
try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    print('Install pillow at first')
    exit(1)

FONT_PATH = 'app/static/font/Asterix-Blink.ttf'


def random_color():
    """随机颜色"""
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))


def draw_lines(draw, num, width, height):
    for num in range(num):
        x1 = random.randint(0, width / 2)
        y1 = random.randint(0, height / 2)
        x2 = random.randint(0, width)
        y2 = random.randint(height / 2, height)
        draw.line((x1, y1), (x2, y2), fill='black', width=1)


def generate_verify_code(length=4):
    """生成验证码字符串
    :param length: int, 验证码长度

    :return str: 验证码字符串
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def generate_verify_code_image(code_length=4, width=120, height=50,
                               font_path=FONT_PATH, font_size=16):
    """生成验证码图片

    :param code_length: int, 验证码长度
    :param width: int, 图片宽度
    :param height: int, 图片高度
    :param font_path: str, 字体路径
    :param font_size: int, 字体大小

    :return (Image, str):


    Usage::

        @app.route('/auth/code')
        def get_code():
            from verify_code import generate_verify_code_image
            image, code = generate_verify_code_image()
            buf = BytesIO()
            image.save(buf, 'jpeg')
            buf_str = buf.getvalue()
            response = make_response(buf_str)
            response.headers['Content-Type'] = 'image/gif'
            # 将验证码字符串存储在 session 中
            session['code'] = code
            return response

    """
    code = generate_verify_code(code_length)
    # 图片
    im = Image.new('RGB', (width, height), 'white')
    # 字体
    font = ImageFont.truetype(font_path, font_size)
    # ImageFont
    draw = ImageDraw.Draw(im)
    # 绘制字符串
    for item in range(code_length):
        draw.text((5 + random.randint(-3, 3) + 23 * item, 5 + random.randint(-3, 3)),
                  text=code[item], fill=random_color(), font=font)
    return im, code


def generate_flask_response():
    """生成flask响应

    Usage::

        @app.route('/auth/code')
        def get_code():
            from verify_code import generate_flask_response
            return generate_flask_response()
    """

    from flask import session, make_response
    image, code = generate_verify_code_image()
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    response = make_response(buf_str)
    response.headers['Context-Type'] = 'image/gif'
    # 将验证码字符串存储在 session 中
    session['code'] = code
    return response
