import os
import stat
import shutil
import subprocess
import re  # 导入正则，用来清洗文件名
from dotenv import load_dotenv

# 1. 加载 Token
load_dotenv()
ACCESS_TOKEN = os.getenv("MODELSCOPE_TOKEN")

# 2. 配置信息
USERNAME = "DenShnauder" 
REPO_NAME = "Tongji-Res-Archive" 
LOCAL_FILE_PATH = r"G:\工程热力学.zip"  # 你要上传的文件路径
WORK_DIR = "./temp_git_workdir"

def sanitize_name(name):
    """清洗文件名：转小写、去空格、去特殊字符，确保 URL 不会断掉"""
    name = name.lower()
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^\u4e00-\u9fa5a-z0-9\-.]', '', name)
    return name

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def force_delete_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path, onerror=remove_readonly)

def run_git_cmd(cmd, cwd=None):
    subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True)

def upload_via_raw_git():
    if not ACCESS_TOKEN:
        print("❌ 错误：未在 .env 中找到 MODELSCOPE_TOKEN")
        return

    # 预先清洗文件名
    original_filename = os.path.basename(LOCAL_FILE_PATH)
    clean_filename = sanitize_name(original_filename)
    
    GIT_URL = f"https://oauth2:{ACCESS_TOKEN}@www.modelscope.cn/datasets/{USERNAME}/{REPO_NAME}.git"

    try:
        force_delete_dir(WORK_DIR)
        print(f"📥 正在连接 ModelScope 仓库...")
        run_git_cmd(f"git clone --depth 1 {GIT_URL} {WORK_DIR}")

        dest_path = os.path.join(WORK_DIR, clean_filename)
        
        # 复制文件
        if os.path.isdir(LOCAL_FILE_PATH):
            shutil.copytree(LOCAL_FILE_PATH, dest_path)
        else:
            shutil.copy(LOCAL_FILE_PATH, dest_path)

        # Git LFS 和 推送
        print(f"🚀 正在上传文件: {clean_filename} ...")
        run_git_cmd(f"git lfs track \"{clean_filename}\"", cwd=WORK_DIR)
        run_git_cmd("git add .", cwd=WORK_DIR)
        run_git_cmd(f'git commit -m "Upload: {clean_filename}"', cwd=WORK_DIR)
        run_git_cmd("git push", cwd=WORK_DIR)

        # 【核心改进】自动生成直链
        # ModelScope 的文件直链格式如下：
        download_url = f"https://www.modelscope.cn/datasets/{USERNAME}/{REPO_NAME}/resolve/master/{clean_filename}"
        
        print("\n" + "="*50)
        print("✅ 上传成功！")
        print("📂 文件名:", clean_filename)
        print("🔗 下载直链:", download_url)
        print("\n📝 请复制下方 Markdown 代码到你的 Quartz 笔记中：")
        print(f"> [!DOWNLOAD] 资源下载\n> [{original_filename}]({download_url})")
        print("="*50)

    except Exception as e:
        print(f"❌ 流程出错: {e}")
    finally:
        force_delete_dir(WORK_DIR)

if __name__ == "__main__":
    upload_via_raw_git()