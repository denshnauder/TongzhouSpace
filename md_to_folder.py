"""
【工具名称】：md_to_folder.py (Markdown 文件转文件夹模式工具)
【使用方法】：直接运行 python md_to_folder.py
【功能说明】：
    - 扫描 content 目录下所有落单的 .md 文件。
    - 为每个文件创建同名文件夹，并将文件重命名为 index.md 移入其中。
    - 它是解决 Quartz 404 错误（因为路径不匹配）的最快方案。
【注意事项】：
    - 会直接移动文件。运行前请确保 content 目录下没有与文件名同名的文件夹。
"""

import os
import shutil

CONTENT_DIR = "content"

def convert_md_to_folder_notes():
    for item in os.listdir(CONTENT_DIR):
        item_path = os.path.join(CONTENT_DIR, item)
        
        # 只要是 .md 文件，且不是 index.md 和 README.md
        if os.path.isfile(item_path) and item.endswith(".md") and item not in ["index.md", "README.md"]:
            file_name = item[:-3] # 去掉 .md
            new_folder_path = os.path.join(CONTENT_DIR, file_name)
            
            # 1. 创建文件夹
            os.makedirs(new_folder_path, exist_ok=True)
            
            # 2. 移动并重命名为 index.md
            target_path = os.path.join(new_folder_path, "index.md")
            shutil.move(item_path, target_path)
            
            print(f"✅ 已转换: {item} -> {file_name}/index.md")

if __name__ == "__main__":
    convert_md_to_folder_notes()