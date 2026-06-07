# ⚖️ LawFirm System — 小型律所管理系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3.3-green?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-轻量数据库-lightgrey?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/Bootstrap-5.x-purple?logo=bootstrap" alt="Bootstrap">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
</p>

> 为中小型律所量身打造的轻量管理系统，部署简单，开箱即用，适合跑在 2G 内存的云服务器上。

---

## ✨ 功能亮点

| 模块 | 功能 |
|------|------|
| 👥 客户管理 | 客户档案增删改查、标签分类（个人/企业/顾问单位）、导出 Excel |
| 📁 案件管理 | 案件 CRUD、阶段跟踪、开庭日期预警（红色高亮提醒）|
| 🔔 案件提醒 | 开庭/举证/上诉提醒、首页待办汇总 |
| 📄 文书模板 | 系统预置模板 + 自定义模板、富文本编辑、在线预览/下载 |
| 📚 案例资料库 | 经典案例收录、关键词检索、裁判要点整理 |
| 💰 财务管理 | 收费记录、支出管理、月度/年度统计概览 |
| ⚙️ 系统设置 | 律所信息配置、用户管理（管理员/律师/助理三级角色）|

---

## 🖥️ 技术栈

- **后端**：Python 3.9+ / Flask 2.3.3 / Flask-SQLAlchemy 3.1.1
- **数据库**：SQLite（无需额外数据库服务，单文件存储）
- **前端**：Jinja2 模板引擎 / Bootstrap 5 / 原生 JavaScript
- **文件处理**：python-docx 1.1.0（Word 导出）/ openpyxl 3.1.2（Excel 导出）
- **生产部署**：Gunicorn 21.2.0 + Systemd

---

## 🚀 快速开始

### 本地运行

**环境要求**：Python 3.9+

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/law_firm_system.git
cd law_firm_system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库（含演示数据）
python init_data.py

# 4. 启动服务
python app.py
```

浏览器访问：[http://localhost:5066](http://localhost:5066)

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 律师 | lawyer1 | lawyer123 |
| 助理 | assistant1 | assistant123 |

> ⚠️ 首次登录后请立即修改默认密码！

---

## ☁️ 阿里云服务器部署

详见 [阿里云部署手册](./阿里云部署手册.md)，核心步骤：

```bash
# 服务器安装依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 初始化数据库
python3 init_data.py

# Gunicorn 生产启动（1 worker 适配 2G 内存）
gunicorn -w 1 -b 0.0.0.0:5066 --timeout 120 app:app
```

配置 Systemd 开机自启 + 每天 20:00 自动备份数据库，详细步骤见 [部署手册](./阿里云部署手册.md)。

---

## 📁 项目结构

```
law_firm_system/
├── app.py                  # Flask 主入口 / 全部路由
├── config.py               # 配置文件（端口、密钥、分页等）
├── models.py               # 数据库模型定义
├── init_data.py            # 初始化脚本（预置账号、模板、案例）
├── requirements.txt        # Python 依赖
├── static/                 # 静态资源（CSS / JS / 图片）
├── templates/              # Jinja2 HTML 模板
│   ├── base.html           # 公共布局
│   ├── index.html          # 首页仪表盘
│   ├── client/             # 客户管理模板
│   ├── case/               # 案件管理模板
│   ├── document/           # 文书模板库
│   ├── case_library/       # 案例资料库
│   ├── finance/            # 财务管理
│   └── system/             # 系统设置
├── db/
│   └── law_db.sqlite       # SQLite 数据库（⚠️ 定期备份）
├── backup/                 # 数据库备份目录
├── upload/                 # 案件附件存储
├── logs/                   # 运行日志
├── backup.sh               # 自动备份脚本
├── 阿里云部署手册.md        # 生产部署手册
└── README-for-github.md    # 本文档
```

---

## ⚙️ 配置说明

主要配置项在 `config.py`：

```python
PORT = 5066                  # 运行端口
SECRET_KEY = "your-secret"   # Session 密钥，生产环境请修改
ITEMS_PER_PAGE = 20          # 列表分页数量
DEBUG = False                # 生产环境请保持 False
```

---

## 📦 依赖清单

```
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
python-docx==1.1.0
openpyxl==3.1.2
gunicorn==21.2.0
Werkzeug==2.3.7
```

> ⚠️ **注意**：不兼容 Python 3.13/3.14 的 pandas 已从依赖中移除。若有数据分析需求，建议单独处理。

---

## 🔒 安全建议

1. 修改 `config.py` 中的 `SECRET_KEY`
2. 首次部署后立即修改所有默认密码
3. 阿里云安全组将 5066 端口仅开放给办公室 IP
4. 生产环境确保 `DEBUG = False`
5. 定期执行数据库备份（已配置每日 20:00 自动备份）

---

## 🛠️ 常见问题

**Q: 启动报 `attempt to write a readonly database`？**  
A: 数据库文件权限不对，执行 `chown -R 你的用户:你的用户 db/` 修复。

**Q: 模板中报 `date is undefined`？**  
A: `render_template` 需传入 `date=date`（`from datetime import date` 后直接传 `date`，不能传 `datetime.date`）。

**Q: 500 报错 `模型对象没有某某属性`？**  
A: 数据库结构与模型不一致，删除旧 `db/law_db.sqlite` 后重新执行 `python3 init_data.py`。

**Q: 2G 内存服务器内存不足？**  
A: Gunicorn 使用 `-w 1` 单 worker，并配置 2G Swap，详见部署手册。

---

## 📄 License

[MIT License](./LICENSE)

---

> 为律所而生，轻量、实用、易部署。
