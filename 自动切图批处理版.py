# -*- coding: utf-8 -*-
import os
import sys
import os.path
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image

def select_files():
    root = tk.Tk()
    root.withdraw()  # 隐藏tkinter的主窗口
    file_paths = filedialog.askopenfilenames(filetypes=[("Atlas files", "*.atlas")])
    root.destroy()  # 关闭窗口
    return file_paths

def process_atlas_file(atlas_path):
    if atlas_path.endswith('.atlas'):
        fileName = atlas_path[:-6]
    else:
        fileName = atlas_path

    pngName = fileName + '.png'
    atlasName = fileName + '.atlas'

    print(f"处理文件: {pngName}, {atlasName}")
    
    if not os.path.exists(pngName) or not os.path.exists(atlasName):
        print(f"文件不存在: {pngName} 或 {atlasName}")
        return False

    try:
        big_image = Image.open(pngName)
        atlas = open(atlasName, encoding="utf8")
    except Exception as e:
        print(f"打开文件失败: {e}")
        return False

    # 创建主输出目录
    curPath = os.path.dirname(atlas_path)
    aim_path = os.path.join(curPath, os.path.basename(fileName))
    print(f"输出目录: {aim_path}")
    
    if os.path.isdir(aim_path):
        shutil.rmtree(aim_path, True)  # 如果有该目录,删除
    os.makedirs(aim_path)

    # 读取文件中与解包无关的前几行字符串
    for _ in range(6):
        _line = atlas.readline()

    while True:
        line1 = atlas.readline()  # name
        if len(line1) == 0:
            break
        else:
            line2 = atlas.readline()  # rotate
            line3 = atlas.readline()  # xy
            line4 = atlas.readline()  # size
            line5 = atlas.readline()  # orig
            line6 = atlas.readline()  # offset
            line7 = atlas.readline()  # index

            print("文件名:" + line1, end="")
            print("是否旋转:" + line2, end="")
            print("坐标:" + line3, end="")
            print("大小:" + line4, end="")
            print("原点:" + line5, end="")
            print("阻挡:" + line6, end="")
            print("索引:" + line7, end="")

            name = line1.replace("\n", "") + ".png"
            
            # 处理包含子目录的文件名
            if "/" in name:
                # 创建子目录
                sub_dir = os.path.join(aim_path, os.path.dirname(name))
                if not os.path.exists(sub_dir):
                    os.makedirs(sub_dir)
                # 只保留文件名部分
                file_name_only = os.path.basename(name)
                output_path = os.path.join(sub_dir, file_name_only)
            else:
                output_path = os.path.join(aim_path, name)

            args = line4.split(":")[1].split(",")
            width = int(args[0])
            height = int(args[1])

            args = line3.split(":")[1].split(",")
            ltx = int(args[0])
            lty = int(args[1])

            if (line2 == '  rotate: true\n'):
                rbx = ltx + height
                rby = lty + width
            else:
                rbx = ltx + width
                rby = lty + height

            print("文件名：" + name + " 宽度：" + str(width) + " 高度：" + str(height) + " 起始横坐标：" + str(ltx) + " 起始纵坐标：" + str(lty) + " 结束横坐标：" + str(rbx) + " 结束纵坐标：" + str(rby) + "\n")
            
            if (line2 == '  rotate: true\n'):
                result_image = Image.new("RGBA", (height, width), (0, 0, 0, 0))
                rect_on_big = big_image.crop((ltx, lty, rbx, rby))
                result_image.paste(rect_on_big, (0, 0, height, width))
            else:
                result_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                rect_on_big = big_image.crop((ltx, lty, rbx, rby))
                result_image.paste(rect_on_big, (0, 0, width, height))

            if (line2 == '  rotate: true\n'):
                result_image = result_image.transpose(Image.ROTATE_270)
            if (line2 == '  rotate: 180\n'):
                result_image = result_image.transpose(Image.ROTATE_180)
            
            result_image.save(output_path)
    
    atlas.close()
    del big_image
    return True

# 主程序
file_paths = select_files()
if not file_paths:
    print("没有选择文件")
    exit()

print(f"选择了 {len(file_paths)} 个文件")

for i, file_path in enumerate(file_paths):
    print(f"\n处理第 {i+1}/{len(file_paths)} 个文件: {file_path}")
    success = process_atlas_file(file_path)
    if success:
        print(f"完成处理: {file_path}")
    else:
        print(f"处理失败: {file_path}")

print("\n所有文件处理完成！")