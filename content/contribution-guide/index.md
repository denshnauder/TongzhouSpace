为了防止网站出现 404 错误并保持结构清晰，请在提交时严格遵守以下规范。

---

## 1. 文件命名与路径 (File Naming)
**这是导致网站 404 的头号杀手，请务必遵守！**

* **✅ 规则**：全小写英文 + 短横线命名 (kebab-case)。
* **❌ 禁止**：禁止中文、空格、下划线 `_` 或大写字母。
* **📂 结构**：必须使用**文件夹模式** (Folder Note)，即 `英文文件夹名/index.md`。

| ❌ 错误示范             | ✅ 正确示范                           |
| :----------------- | :------------------------------- |
| `理论力学.md`          | `theoretical-mechanics/index.md` |
| `Fluid Mechanics/` | `fluid-mechanics/`               |
| `Signal_System/`   | `signal-and-system/`             |

---

## 2. 内容格式 (Frontmatter)
每个 `index.md` 文件的顶部必须包含以下模板：
---
title: 页面显示的中文标题 (例如：理论力学笔记)
date: 2026-01-22
tags: 
  - 科目名
  - 课程性质
  - 相关专业
---

## 3.本地环境配置（setup）
提交代码前，请先在本地预览，确保没有报错
* 安装依赖（仅首次）
```
npm install
```
* 启动预览
```
npx quartz build --serve
```
* 检查
  打开浏览器访问
```
http://localhost:8080
```
确认你的页面能正常打开且无乱码

---

## 4.大文件上传（LFS）
PDF、ZIP 等超过 100MB 的文件请勿直接传到 GitHub。
* （1）直接将文件发送给仓库管理员DenShnauder
       由管理员上传到ModelScpoe并生成下载直链。
* （2）①注册 ModelScope 并申请 Token。
       ②本地新建 .env 文件并填入 MODELSCOPE_TOKEN=你的Token。
       ③使用仓库自带的 upload_to_oss.py 脚本上传。
