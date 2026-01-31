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