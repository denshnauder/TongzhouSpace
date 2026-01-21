import os
import shutil
import subprocess
import logging
from pathlib import Path

# ================= 配置区域 =================

# 1. 临时缓存目录 (运行结束后会自动删除)
TEMP_DIR = Path(".temp_cache_runtime")

# 2. 最终目标根目录
CONTENT_ROOT = Path("content")

# 3. 仓库映射配置
# 格式: {
#   "git_url": "仓库地址",
#   "target_path": "你在 content 里的分类路径 (例如: 课程名/子分类)",
#   "repo_name": "临时文件夹名 (随便起，用于git clone)"
# }
REPO_CONFIGS = [
    {
        # 浙大信号与系统 -> 归档到同济课程文件夹下的"外校参考"中
        "url": "https://github.com/VipaiLab/Signals-and-Systems-course.git",
        "repo_name": "zju_signals_temp",
        "target_path": "信号与系统/外校存档/浙大VipaiLab_课程资料" 
    },
    # 你可以在这里添加更多仓库，例如:
    # {
    #     "url": "https://github.com/...",
    #     "repo_name": "mit_linear_algebra",
    #     "target_path": "线性代数/MIT_1806"
    # }
]

# 4. 允许同步的文件后缀 (保留 PDF, PPT, Matlab, 代码)
ALLOWED_EXTENSIONS = {
    # 核心文档
    '.pdf', '.docx', '.pptx', '.doc', '.ppt', 
    '.md', '.markdown', '.txt',
    # 编程与数据
    '.m', '.mat',      # Matlab/Simulink
    '.py', '.ipynb',   # Python
    '.c', '.cpp', '.h',# C/C++
    # 图片资源
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'
}

# 5. 排除的垃圾目录
EXCLUDE_DIRS = {'.git', '.github', '.obsidian', '__pycache__', '.idea', '.vscode', 'node_modules'}

# ===========================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_command(cmd, cwd=None):
    """执行 Shell 命令"""
    try:
        subprocess.run(cmd, check=True, cwd=cwd, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"命令执行失败: {cmd}")
        raise e

def clone_repos():
    """将所有仓库 Clone 到临时目录"""
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True)

    for config in REPO_CONFIGS:
        url = config['url']
        name = config['repo_name']
        logging.info(f"⬇️  正在下载: {name} ...")
        
        # 为了加快速度，可以使用 --depth 1 (浅克隆，不下载历史记录)
        run_command(f"git clone --depth 1 {url} {name}", cwd=TEMP_DIR)

def sync_files():
    """执行文件筛选与移动"""
    logging.info("🔄 开始处理并归档文件...")
    
    sync_count = 0
    
    for config in REPO_CONFIGS:
        repo_name = config['repo_name']
        # 组合完整的目标路径: content/课程名/子文件夹
        target_dir = CONTENT_ROOT / config['target_path']
        source_dir = TEMP_DIR / repo_name
        
        if not source_dir.exists():
            logging.warning(f"⚠️ 源目录不存在，跳过: {repo_name}")
            continue

        # 遍历临时目录下的仓库
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                suffix = file_path.suffix.lower()

                if suffix in ALLOWED_EXTENSIONS:
                    # 计算相对路径
                    rel_path = file_path.relative_to(source_dir)
                    final_dest = target_dir / rel_path
                    
                    # 确保目标父文件夹存在
                    final_dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 复制逻辑 (覆盖更新)
                    # 如果需要保留用户在 content 里修改过的文件，可以加时间戳判断
                    # 这里默认强制覆盖，保证和仓库一致
                    shutil.copy2(file_path, final_dest)
                    sync_count += 1
    
    logging.info(f"✅ 同步完成！共归档 {sync_count} 个文件。")

def clean_up():
    """清理临时文件夹"""
    if TEMP_DIR.exists():
        logging.info("🧹 正在清理临时文件...")
        # 强制删除临时目录及其内容
        # ignore_errors=True 防止因为文件占用导致的报错
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        logging.info("✨ 清理完毕。")

if __name__ == "__main__":
    try:
        clone_repos()
        sync_files()
    except Exception as e:
        logging.error(f"❌ 发生错误: {e}")
    finally:
        # 无论成功还是失败，只要 temp 文件夹还在，就删掉它
        clean_up()