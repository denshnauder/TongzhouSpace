import os
import stat
import shutil
import subprocess
import sys
from dotenv import load_dotenv

# 1. 加载 Token
load_dotenv()
ACCESS_TOKEN = os.getenv("MODELSCOPE_TOKEN")

# 2. 配置信息
USERNAME = "DenShnauder" 
REPO_NAME = "Tongji-Res-Archive" 
LOCAL_FILE_PATH = r"G:\工程热力学.zip"  # 本地文件或文件夹路径
WORK_DIR = "./temp_git_workdir"

# 👇 【新增】专门处理Windows只读文件删除的回调函数
def remove_readonly(func, path, excinfo):
    # 修改文件权限为“可写”，然后再试一次删除
    os.chmod(path, stat.S_IWRITE)
    func(path)

def force_delete_dir(dir_path):
    if os.path.exists(dir_path):
        print(f"🧹 正在暴力清理目录: {dir_path}")
        # onerror 参数就是关键，遇到删不掉的文件，交给 remove_readonly 处理
        shutil.rmtree(dir_path, onerror=remove_readonly)

def run_git_cmd(cmd, cwd=None, stream_output=False):
    if stream_output:
        print(f"🔧 [实时执行]: {cmd}")
        process = subprocess.Popen(
            cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, encoding='utf-8', errors='replace'
        )
        for line in process.stdout:
            print(line, end='', flush=True)
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    else:
        print(f"🔧 [后台执行]: {cmd}")
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8'
        )

def upload_via_raw_git():
    if not ACCESS_TOKEN:
        print("❌ Token没读到！去检查 .env 文件")
        return

    GIT_URL = f"https://oauth2:{ACCESS_TOKEN}@www.modelscope.cn/datasets/{USERNAME}/{REPO_NAME}.git"

    try:
        # 0. LFS 检查
        try:
            run_git_cmd("git lfs install", cwd=".")
        except:
            pass

        # 1. 【关键修改】清理旧目录（使用强力删除）
        force_delete_dir(WORK_DIR)

        # 2. Clone
        print("📥 正在克隆仓库...")
        run_git_cmd(f"git clone --depth 1 {GIT_URL} {WORK_DIR}", stream_output=True)

        # 3. 搬运文件
        filename = os.path.basename(LOCAL_FILE_PATH)
        dest_path = os.path.join(WORK_DIR, filename)
        print(f"📦 正在搬运文件：{filename} ...")
        
        if os.path.isdir(LOCAL_FILE_PATH):
            force_delete_dir(dest_path) # 如果目标里已有同名文件夹，先删掉
            shutil.copytree(LOCAL_FILE_PATH, dest_path)
        else:
            shutil.copy(LOCAL_FILE_PATH, dest_path)

        # 4. Push
        print("☁️  正在准备推送...")
        run_git_cmd(f"git lfs track \"{filename}\"", cwd=WORK_DIR)
        run_git_cmd("git add .gitattributes", cwd=WORK_DIR)
        run_git_cmd("git add .", cwd=WORK_DIR)
        
        commit_msg = f"Auto-upload resource: {filename}"
        run_git_cmd(f'git commit -m "{commit_msg}"', cwd=WORK_DIR)
        
        print("🚀🚀🚀 开始上传！")
        run_git_cmd("git push --progress", cwd=WORK_DIR, stream_output=True)
        print(f"\n✅ 成功！")

    except Exception as e:
        print(f"\n❌ 流程终止: {e}")
        
    finally:
        # 脚本跑完，再次清理现场
        force_delete_dir(WORK_DIR)

if __name__ == "__main__":
    upload_via_raw_git()