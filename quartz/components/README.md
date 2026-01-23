# Quartz 组件库 (Customized by Ency)

这是“同舟空间”网站的核心组件目录。

## 组件开发规范
1. **源码位置**: `*.tsx` 文件定义结构与逻辑。
2. **样式定义**: 通过 `Component.css = \`...\`` 注入组件私有样式。
3. **注册机制**: 必须在 `index.ts` 中导出，才能在 `layout.ts` 中通过 `Component.X` 调用。

## 重点组件清单
| 组件名 | 描述 | 修改建议 |
| :--- | :--- | :--- |
| `Wisdom.tsx` | 随机显示格言 | 增加句子请直接修改 `quotes` 数组 |
| `Explorer.tsx` | 左侧目录树 | 修改 `title` 参数可改变导航栏标题 |
| `Breadcrumbs.tsx` | 面包屑导航 | 已手动将 "Home" 修改为 "同舟空间" |

## 参数 (Props) 速查
- **fileData**: 访问当前页面的标题、日期、标签。
- **allFiles**: 如果需要统计全站文件数量，请遍历此数组。
- **displayClass**: 用于适配响应式布局。