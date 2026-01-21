import os

def create_course(course_name):
    # 转换为全小写加连字符格式，避开大小写坑
    slug = course_name.lower().replace(" ", "-")
    base_path = f"content/{slug}"
    subfolders = ["notes", "exams", "homework", "attachments"]
    
    for folder in subfolders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    
    # 自动生成带有基本元数据的主页
    with open(os.path.join(base_path, "index.md"), "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {course_name}\nstatus: public\n---\n# {course_name}\n\n## 📂 资源列表\n- [[notes/|笔记]]\n- [[exams/|历年卷]]")

# 使用时只需改这一行
create_course("信号与系统")