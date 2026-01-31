"""
【工具名称】：auto_index.py (缺失索引自动补全工具)
【使用方法】：直接运行 python auto_index.py
【功能说明】：
    - 递归扫描 content 目录下的所有子文件夹。
    - 发现没有 index.md 的文件夹时，自动创建一个基础的 index.md 文件。
    - 确保侧边栏和文件夹页面可以正常点击访问。
【注意事项】：
    - 生成的内容仅为占位标题，后续建议手动修改 index.md 增加详细描述。
"""

import os

CONTENT_DIR = "content"

def fix_missing_indices():
    for root, dirs, files in os.walk(CONTENT_DIR):
        # 如果文件夹里没有 index.md
        if "index.md" not in files:
            folder_name = os.path.basename(root)
            # 跳过根目录 content 本身（如果有 index 的话）
            if root == CONTENT_DIR: continue
            
            index_path = os.path.join(root, "index.md")
            # 自动生成一个基础的 index.md
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(f"---\ntitle: {folder_name}\n---\n\n# {folder_name}\n\n欢迎来到 {folder_name} 分类。")
            print(f"✨ 已自动补齐: {index_path}")

if __name__ == "__main__":
    fix_missing_indices()