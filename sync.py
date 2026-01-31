"""
【工具名称】：sync.py (外部资源自动同步工具)
【使用方法】：
    1. 在 REPO_CONFIGS 中添加外部仓库 URL 和目标存放路径。
    2. 运行：python sync.py
【功能说明】：
    - 自动克隆外部仓库到临时目录。
    - 强制清洗文件名（全小写、去空格、去特殊字符）以符合 Quartz 规范。
    - 自动生成符合 Quartz 样式的目录索引 index.md。
【注意事项】：
    - 运行前请确保本地已安装 Git。
    - 会自动覆盖 target_path 下的同名文件，请勿在该目录下手动修改重要笔记。
"""

import os
import shutil
import subprocess
import logging
import stat
import re  # 导入正则表达式库
from pathlib import Path

# 每次使用只需要修改配置区域
# ================= 配置区域 =================

TEMP_DIR = Path(".temp_cache_runtime")
CONTENT_ROOT = Path("content")

REPO_CONFIGS = [
    {
        "url": "https://github.com/VipaiLab/Signals-and-Systems-course.git",
        "repo_name": "zju_signals_temp",
        "target_path": "signal-and-system/archives/zju-vipailab"  # 这里建议也改成英文/短横线格式
    }
]

ALLOWED_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.doc', '.ppt', 
    '.md', '.markdown', '.txt',
    '.m', '.mat', '.py', '.ipynb', '.c', '.cpp', '.h',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'
}

EXCLUDE_DIRS = {'.git', '.github', '.obsidian', '__pycache__', '.idea', '.vscode', 'node_modules'}

# ===========================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def sanitize_name(name):
    """
    【核心改动】将中文名转换或处理字符串以符合 Quartz 规范
    1. 转小写
    2. 空格、下划线替换为短横线
    3. 移除特殊字符
    """
    # 如果是路径对象，只处理它的名字部分
    name = str(name).lower()
    # 将空格、下划线、以及各种特殊符号替换为短横线
    name = re.sub(r'[\s_]+', '-', name)
    # 过滤掉不适合做URL的字符（保留中文、字母、数字、短横线）
    name = re.sub(r'[^\u4e00-\u9fa5a-z0-9\-.]', '', name)
    # 去掉重复的短横线
    name = re.sub(r'-+', '-', name)
    return name

def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, check=True, cwd=cwd, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"命令执行失败: {cmd}")
        raise e

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repos():
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly)
    TEMP_DIR.mkdir(parents=True)
    for config in REPO_CONFIGS:
        url = config['url']
        name = config['repo_name']
        logging.info(f"⬇️  正在下载: {name} ...")
        run_command(f"git clone --depth 1 {url} {name}", cwd=TEMP_DIR)

def generate_index_md(directory, title):
    """生成索引页，确保链接也能匹配到被 sanitize 后的文件名"""
    files = [f for f in directory.iterdir() if f.is_file() and f.name != 'index.md' and f.suffix in ALLOWED_EXTENSIONS]
    if not files: return

    files.sort(key=lambda x: x.name)
    content_lines = [
        "---",
        f"title: {title}",
        "---",
        "",
        "## 📂 自动归档文件列表",
        "> 以下文件已自动处理命名规范，点击即可预览或下载。",
        ""
    ]
    
    for f in files:
        icon = "📄"
        if f.suffix in ['.md', '.txt']: icon = "📝"
        if f.suffix in ['.pdf']: icon = "📕"
        if f.suffix in ['.ppt', '.pptx']: icon = "📊"
        
        # 注意：这里的链接文件名必须和硬盘上的真实文件名（sanitize后的）一致
        content_lines.append(f"- {icon} [{f.name}]({f.name})")
    
    index_path = directory / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content_lines))

def sync_files():
    logging.info("🔄 开始处理并归档文件...")
    sync_count = 0
    
    for config in REPO_CONFIGS:
        repo_name = config['repo_name']
        # 这里的 target_dir 现在是 signal-and-system/archives/zju-vipailab
        target_dir = CONTENT_ROOT / config['target_path']
        source_dir = TEMP_DIR / repo_name
        
        if not source_dir.exists(): continue

        for root, dirs, files in os.walk(source_dir):
            # 排除掉不需要的文件夹
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    # 关键：彻底清洗每一级路径
                    rel_path = file_path.relative_to(source_dir)
                    # 对每一层文件夹名、文件名都调用 sanitize_name
                    sanitized_parts = [sanitize_name(part) for part in rel_path.parts]
                    final_rel_path = Path(*sanitized_parts)
                    
                    final_dest = target_dir / final_rel_path
                    final_dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(file_path, final_dest)
                    sync_count += 1
        
        # 处理索引
        for root, dirs, files in os.walk(target_dir):
            current_path = Path(root)
            # 这里的标题我们稍微温柔点，把短横线换成空格，首字母大写，好看一点
            folder_title = current_path.name.replace("-", " ").title()
            generate_index_md(current_path, folder_title)

def clean_up():
    if TEMP_DIR.exists():
        logging.info("🧹 正在清理临时文件...")
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly)

if __name__ == "__main__":
    try:
        clone_repos()
        sync_files()
    except Exception as e:
        logging.error(f"❌ 发生错误: {e}")
    finally:
        clean_up()