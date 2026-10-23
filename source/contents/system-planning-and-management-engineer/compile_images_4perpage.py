#!/usr/bin/env python3
"""将目录下所有图片按时间排序，每页四张（2x2排列）排版到 A4 横向 PDF 中。"""

import os
import glob
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from reportlab.lib.units import mm

PAGE_W, PAGE_H = landscape(A4)

# 边距
MARGIN_TOP = 8 * mm
MARGIN_BOTTOM = 8 * mm
MARGIN_SIDE = 8 * mm
IMAGE_GAP = 5 * mm


def image_time_label(filename):
    return os.path.getmtime(filename)


def draw_image_fitted(c, img_path, x, y, box_w, box_h):
    """在指定矩形区域内绘制图片，保持宽高比，居中填充，带边框。"""
    img = utils.ImageReader(img_path)
    iw, ih = img.getSize()
    img_ratio = iw / ih
    box_ratio = box_w / box_h

    if img_ratio > box_ratio:
        draw_w = box_w
        draw_h = box_w / img_ratio
    else:
        draw_h = box_h
        draw_w = box_h * img_ratio

    offset_x = x + (box_w - draw_w) / 2
    offset_y = y + (box_h - draw_h) / 2

    # 白色背景
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, y, box_w, box_h, fill=1, stroke=0)

    # 图片（直接绘制，保持原始清晰度）
    c.drawImage(img_path, offset_x, offset_y, draw_w, draw_h)

    # 灰色细边框
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(0.5)
    c.rect(x, y, box_w, box_h, fill=0, stroke=1)


def main():
    input_dir = "./"
    output_path = os.path.join(input_dir, "screenshots_4perpage.pdf")

    image_files = []
    for ext in ["*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG", "*.gif", "*.GIF", "*.bmp", "*.BMP", "*.webp", "*.WEBP"]:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))

    image_files.sort(key=image_time_label)

    total = len(image_files)
    num_pages = (total + 3) // 4  # 每页4张

    print(f"找到 {total} 张图片，生成 {num_pages} 页 PDF（每页4张，横向A4）...")

    c = canvas.Canvas(output_path, pagesize=(PAGE_W, PAGE_H))

    # 2x2 网格：每张图的可用区域（横向页面）
    cell_w = (PAGE_W - MARGIN_SIDE * 2 - IMAGE_GAP) / 2
    cell_h = (PAGE_H - MARGIN_TOP - MARGIN_BOTTOM - IMAGE_GAP) / 2

    # 全局图片序号（已移除序号标签）

    for page_idx in range(num_pages):
        i = page_idx * 4
        page_images = image_files[i:i+4]

        # 从左到右、从上到下: 上左, 上右, 下左, 下右
        # col=0 左, col=1 右; row=1 上, row=0 下（Canvas y 从下往上）
        positions = [
            (0, 1),  # 上左
            (1, 1),  # 上右
            (0, 0),  # 下左
            (1, 0),  # 下右
        ]

        for j, img_path in enumerate(page_images):
            col, row = positions[j]

            box_x = MARGIN_SIDE + col * (cell_w + IMAGE_GAP)
            box_y = MARGIN_BOTTOM + row * (cell_h + IMAGE_GAP)

            draw_image_fitted(c, img_path, box_x, box_y, cell_w, cell_h)

        c.showPage()
        if (page_idx + 1) % 10 == 0:
            print(f"  已生成 {page_idx + 1}/{num_pages} 页...")

    c.save()
    print(f"PDF 已生成: {output_path}")
    print(f"共 {total} 张图片，分成 {num_pages} 页")


if __name__ == "__main__":
    main()
