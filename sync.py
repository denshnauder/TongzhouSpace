import os
import shutil
import stat
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
TEMP_DIR = os.path.join(PROJECT_ROOT, ".temp_cache")
CONTACT_EMAIL = "denshnauder@gmail.com"

# 强力删除只读文件的回调函数
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

RESOURCES = [
    {
        "name": "signals-student",
        "url": "https://github.com/liyuxuan3003/SignalsAndSystems.git",
        "sub_path": "signals-and-systems/notes/student-notes",
        "title": "学长实战笔记"
    },
    {
        "name": "signals-zju",
        "url": "https://github.com/VipaiLab/Signals-and-Systems-course.git",
        "sub_path": "signals-and-systems/zju-materials",
        "title": "浙大官方名校课件"
    }
]

def generate_index_content(title, files):
    now = datetime.now().strftime("%Y-%m-%d")
    content = f"---\ntitle: {title}\nlast_updated: {now}\n---\n\n# {title}\n\n"
    content += f"> [!ABSTRACT] 资源说明\n> 本目录由脚本于 {now} 自动同步。如有侵权，请联系 **{CONTACT_EMAIL}**。\n\n"
    content += "## 📂 文件列表\n"
    for f in sorted(files):
        icon = "📄" if f.lower().endswith('.pdf') else "📝"
        content += f"- [[{f}|{icon} {f}]]\n"
    return content

def sync_and_index():
    # 彻底清理旧缓存
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly) # 使用修复函数
    os.makedirs(TEMP_DIR)
    
    for res in RESOURCES:
        repo_path = os.path.join(TEMP_DIR, res['name'])
        target_path = os.path.join(CONTENT_DIR, res['sub_path'])
        
        print(f"正在克隆: {res['name']}...")
        os.system(f"git clone --depth 1 {res['url']} {repo_path}")

        if os.path.exists(target_path):
            shutil.rmtree(target_path, onerror=remove_readonly)
        os.makedirs(target_path)
        
        synced_files = []
        for root, _, filenames in os.walk(repo_path):
            if '.git' in root: continue
            for f in filenames:
                # 增强匹配：包含所有常见文档格式
                if f.lower().endswith(('.md', '.pdf', '.jpg', '.png', '.jpeg')):
                    shutil.copy(os.path.join(root, f), target_path)
                    if f.lower() != 'readme.md':
                        synced_files.append(f)
        
        index_file = os.path.join(target_path, "index.md")
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(generate_index_content(res['title'], synced_files))
        print(f"成功同步 {len(synced_files)} 个文件。")

    shutil.rmtree(TEMP_DIR, onerror=remove_readonly)
    print("\n[OK] 同步完成，权限问题已解决。")

if __name__ == "__main__":
    sync_and_index()