import os
import shutil

# 配置你要抓取的资源仓库
RESOURCES = [
    {
        "name": "signals-notes-student",
        "url": "https://github.com/liyuxuan3003/SignalsAndSystems.git",
        "target_dir": "content/signals-and-systems/notes/student-notes"
    },
    {
        "name": "signals-zju-official",
        "url": "https://github.com/VipaiLab/Signals-and-Systems-course.git",
        "target_dir": "content/signals-and-systems/zju-materials"
    }
]

def sync():
    for res in RESOURCES:
        temp_dir = f"temp_{res['name']}"
        
        # 1. 抓取仓库 (或者更新)
        if os.path.exists(temp_dir):
            print(f"Updating {res['name']}...")
            os.system(f"cd {temp_dir} && git pull")
        else:
            print(f"Cloning {res['name']}...")
            os.system(f"git clone {res['url']} {temp_dir}")

        # 2. 自动创建目标文件夹
        os.makedirs(res['target_dir'], exist_ok=True)

        # 3. 筛选并搬运 (只拿 PDF 和 Markdown)
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(('.md', '.pdf', '.jpg', '.png')):
                    src_path = os.path.join(root, file)
                    # 保持原有的层级结构或直接扁平化处理
                    shutil.copy(src_path, res['target_dir'])
        
        print(f"Successfully synced {res['name']} to {res['target_dir']}")

if __name__ == "__main__":
    sync()