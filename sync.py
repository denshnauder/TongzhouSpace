import os
import shutil
import subprocess
import logging
import stat
from pathlib import Path

# ================= 配置区域 =================

TEMP_DIR = Path(".temp_cache_runtime")
CONTENT_ROOT = Path("content")

REPO_CONFIGS = [
    {
        "url": "https://github.com/VipaiLab/Signals-and-Systems-course.git",
        "repo_name": "zju_signals_temp",
        "target_path": "信号与系统/外校存档/浙大VipaiLab_课程资料" 
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

def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, check=True, cwd=cwd, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"命令执行失败: {cmd}")
        raise e

def remove_readonly(func, path, _):
    """
    辅助函数：强制删除只读文件 (解决 Windows [WinError 5] 问题)
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repos():
    # 1. 如果存在旧的临时文件夹，先强力删除
    if TEMP_DIR.exists():
        # onerror=remove_readonly 是关键，遇到权限问题自动修复
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly)
    
    TEMP_DIR.mkdir(parents=True)
    
    for config in REPO_CONFIGS:
        url = config['url']
        name = config['repo_name']
        logging.info(f"⬇️  正在下载: {name} ...")
        # 2. 浅克隆
        run_command(f"git clone --depth 1 {url} {name}", cwd=TEMP_DIR)

def generate_index_md(directory, title):
    files = [f for f in directory.iterdir() if f.is_file() and f.name != 'index.md' and f.suffix in ALLOWED_EXTENSIONS]
    
    if not files:
        return

    files.sort(key=lambda x: x.name)
    
    content_lines = [
        "---",
        f"title: {title}",
        "---",
        "",
        "## 📂 自动归档文件列表",
        "> 以下文件由同步脚本自动生成链接，点击即可预览或下载。",
        ""
    ]
    
    for f in files:
        icon = "📄"
        if f.suffix in ['.md', '.txt']: icon = "📝"
        if f.suffix in ['.pdf']: icon = "📕"
        if f.suffix in ['.ppt', '.pptx']: icon = "📊"
        if f.suffix in ['.m', '.py', '.c', '.cpp']: icon = "💻"
        
        content_lines.append(f"- {icon} [{f.name}]({f.name})")
    
    index_path = directory / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content_lines))
    
    logging.info(f"📝 已生成索引页: {index_path}")

def sync_files():
    logging.info("🔄 开始处理并归档文件...")
    sync_count = 0
    
    for config in REPO_CONFIGS:
        repo_name = config['repo_name']
        target_dir = CONTENT_ROOT / config['target_path']
        source_dir = TEMP_DIR / repo_name
        
        if not source_dir.exists():
            continue

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    rel_path = file_path.relative_to(source_dir)
                    final_dest = target_dir / rel_path
                    final_dest.parent.mkdir(parents=True, exist_ok=True)
                    # 强制覆盖
                    shutil.copy2(file_path, final_dest)
                    sync_count += 1
        
        for root, dirs, files in os.walk(target_dir):
            current_path = Path(root)
            folder_title = current_path.name if current_path != target_dir else config['target_path'].split('/')[-1]
            generate_index_md(current_path, folder_title)

    logging.info(f"✅ 同步完成！共归档 {sync_count} 个文件。")

def clean_up():
    if TEMP_DIR.exists():
        logging.info("🧹 正在清理临时文件...")
        # 同样加上 onerror=remove_readonly
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly)
        logging.info("✨ 清理完毕。")

if __name__ == "__main__":
    try:
        clone_repos()
        sync_files()
    except Exception as e:
        logging.error(f"❌ 发生错误: {e}")
    finally:
        clean_up()