小型律所管理系统文档集（V1.0）
文档 1：小型律所管理系统 - 业务需求说明书 (BRD).docx
Plain Text
文档编号：LS-BRD-V1.0
编制日期：2026-06-05
项目名称：小型律师事务所管理系统
适用范围：3～10人中小型律师事务所
1 项目概述
1.1 项目背景
当前中小律所普遍采用 Excel、Word 零散管理客户、案件、文书、财务：律师文书重复撰写效率低下、办案案例无统一归档、案件开庭 / 时效依靠备忘录容易遗漏、律师费收支手工记账对账困难。本系统打造本地化轻量化律所管理平台，集成文书模板库、案例资料库、案件全生命周期管理、简易财务管理四大核心能力，本地文件数据库存储，不用云端年费，适配 Windows 单机 / 局域网多客户端使用。
1.2 建设目标
1）标准化客户档案与案件台账，实现案件从收案、办案到结案归档全流程管控；
2）内置 120 + 司法常用法律文书模板，支持信息自动填充，一键导出 Word/PDF；
3）内置 500 + 民商事、刑事高频判例，支持自建本所办案案例库；
4）轻量化财务记账：律师费收款、律所日常支出、发票台账、律师业绩自动统计；
5）案件关键节点（开庭、举证期、上诉期）自动弹窗提醒，规避执业失误；
6）数据本地加密存储，一键备份恢复，零基础内勤可上手运维。
1.3 目标用户
角色	人员说明
系统管理员	律所主任 / 行政主管，全系统配置、权限管控、数据维护
执业律师	办案律师，案件录入、文书调取、案例查阅、个人收费查看
内勤助理	档案录入人员，新增客户、案件基础信息录入，无财务查看权限
2 业务流程说明
2.1 整体主业务流程
系统初始化（录入律所基础信息 + 创建系统账号）→内勤 / 律师录入客户信息→新建委托案件→关联文书模板自动填充案件 / 客户信息→文书编辑导出→案件进度阶段性更新→系统自动提醒开庭 / 时效→案件收费 / 支出台账录入→结案归档。
2.2 文书使用业务流程
进入文案库→按案由筛选模板→绑定已有案件→系统自动带入客户名称、案号、受理法院、律所抬头→在线富文本修改内容→导出 Word/PDF 存档打印。
2.3 财务管理业务流程
案件委托签约→录入应收律师费→实际到账后登记收款记录、发票信息→日常房租 / 差旅费 / 鉴定费录入支出台账→月末自动生成律师个人业绩报表、全所收支汇总表。
3 功能模块业务划分
1.系统管理模块：账号权限管理、律所基础信息配置、系统日志、数据库备份恢复；
2.客户管理模块：客户信息建档、标签分类、历史委托案件关联、信息导入导出；
3.案件管理模块：案件建档、进度维护、时效提醒、卷宗归档；
4.法律文书库模块：系统内置模板 + 自定义新增模板；
5.裁判案例库模块：预置经典案例 + 律所自建案例归档、检索收藏；
6.财务管理模块：收入登记、支出登记、发票管理、多维度财务报表；
7.辅助工具箱：诉讼期限计算器、常用法条速查、案件附件存储。
4 非功能性业务要求
1.部署：支持 Windows7/10/11 单机部署、局域网多台电脑共享访问；
2.存储：数据本地 SQLite 文件保存，不上传第三方云端；
3.兼容性：导出文件兼容 Office2016 及以上版本；
4.易用性：页面仿照 Office 布局，律师 10 分钟完成基础操作学习。
保存为：【01 - 业务需求说明书 (BRD).docx】
文档 2：小型律所管理系统 - 详细需求说明书 (PRD).docx
Plain Text
文档编号：LS-PRD-V1.0
版本：V1.0
1 模块详细功能需求
1.1 系统管理模块
1.1.1 用户管理：新增账号、编辑信息、启用 / 禁用账号、重置登录密码；字段：登录账号、明文姓名、角色（管理员 / 律师 / 助理）、联系电话；
1.1.2 角色权限：管理员全开权限；律师仅可操作案件、文书、案例、本人收费；助理仅录入客户案件，屏蔽财务菜单；
1.1.3 律所配置：录入律所全称、地址、联系方式、统一文书落款信息，全系统文书自动带入；
1.1.4 数据管理：一键全库备份至本地文件夹、从备份文件恢复数据，记录所有关键操作日志。
1.2 客户管理模块
1.2.1 新增客户：必填项（姓名、联系电话），选填（身份证号、住址、备注、分类标签：个人 / 企业 / 法律顾问单位）；
1.2.2 客户列表：支持姓名 / 手机号模糊检索，分页展示；点击详情查看该客户全部历史案件；
1.2.3 数据导出：单客户 / 全量客户信息导出 Excel。
1.3 案件管理模块
1.3.1 案件录入：案号、案件类型（民事 / 刑事 / 劳动 / 行政 / 执行）、受理法院、对方当事人、承办律师、收案日期；
1.3.2 案件阶段：立案→举证→开庭→一审判决→二审→执行→归档，状态手动切换；
1.3.3 智能提醒：录入开庭日自动生成提醒，系统启动弹窗；举证期限、上诉期自动倒计时；
1.3.4 案件附件：上传判决书、证据扫描件、委托合同，附件与案件绑定存储。
1.4 法律文书库
1.4.1 内置分类：
诉讼文书：民事起诉状、答辩状、上诉状、保全申请、强制执行申请书、辩护词、代理词；
非诉文书：各类律师函、借款 / 租赁 / 买卖 / 劳务合同、法律顾问协议、法律意见书；
手续文书：授权委托书、出庭函、送达地址确认书；合计预置 123 套标准模板；
1.4.2 模板操作：选中案件自动回填文书变量（姓名、法院、案号、律所信息）；自定义新增个人 / 全所专属模板；
1.4.3 输出：在线编辑后导出 docx、PDF。
1.5 案例资料库
1.5.1 内置 500 + 判例，分类：婚姻家事、民间借贷、交通事故、劳动争议、帮信、故意伤害等高频案由；
1.5.2 案例字段：案例标题、案由、裁判要点、案情简介、法律依据、裁判结果、办案思路；
1.5.3 自建案例：律师办结案件可新增入库，支持关键词检索、收藏、导出打印。
1.6 财务管理模块
1.6.1 收入管理：绑定对应案件，录入收费金额、收费类型（一次性 / 分期 / 风险代理）、收款日期、收款方式、发票开具状态；分期收费支持多笔分次入账；
1.6.2 支出管理：支出分类（房租、人员工资、差旅费、公告费、鉴定费、办公耗材）、金额、支出日期、备注；
1.6.3 发票台账：关联收款记录，登记发票号码、开票抬头、税率；
1.6.4 统计报表：按律师统计业绩、按月 / 按年统计全所收支、待收欠款清单，报表导出 Excel。
1.7 辅助工具
1.7.1 期限计算器：输入起始日期，自动计算上诉期 15 日、举证期 15 日、诉讼时效 3 年；
1.7.2 法条库：民法典、民诉法、刑法常用法条全文检索查看。
2 UI 交互需求
1.整体布局：左侧菜单栏 + 顶部系统标题 + 右侧主内容区；
2.列表页：顶部搜索 + 新增 / 导出按钮，下方数据表格 + 分页控件；
3.新增编辑统一弹窗表单样式；
4.待办提醒在首页工作台集中展示。
3 性能需求
1.单表存储 10 万条数据无卡顿，检索响应≤1s；
2.Word/PDF 导出耗时≤5 秒；
3.局域网 3-10 人同时在线访问正常。
保存为：【02 - 详细产品需求说明书 (PRD).docx】
文档 3：数据库设计说明书.docx
Plain Text
数据库：SQLite3（文件型免安装数据库）
字符集：UTF8MB4
数据库文件名：law_db.sqlite
1 数据表清单（共 11 张数据表）
表 1 sys_user 用户表
字段名	数据类型	主键 / 非空	备注
id	INTEGER	主键自增	用户 ID
username	VARCHAR(32)	非空	登录账号
password	VARCHAR(64)	非空	加密密码
real_name	VARCHAR(32)	非空	真实姓名
role	VARCHAR(16)	非空	admin/ lawyer/assistant
phone	VARCHAR(16)		联系电话
status	INTEGER	默认 1	1 启用 0 禁用
create_time	DATETIME		创建时间
表 2 sys_firm 律所信息表
id	name	address	phone	remark
主键	律所全称	地址	联系电话	备注
表 3 client 客户信息表
id	name	id_card	phone	address	tag	create_time	remark
主键	客户姓名	身份证号	手机号	住址	客户标签	建档时间	备注
索引：phone（手机号索引，快速检索）							
表 4 case_info 案件主表
id	client_id	case_no	case_type	court	lawyer_id	opposite_party	accept_date	stage	status	create_time
主键	客户 ID 外键	案号	案件类型	管辖法院	承办律师 ID 外键	对方当事人	收案日期	审理阶段	案件状态	创建时间
索引：client_id、lawyer_id 联合索引										
表 5 case_remind 案件提醒表
id	case_id	remind_type	remind_date	is_finish
主键	案件 ID 外键	提醒类型 (开庭 / 举证 / 上诉)	提醒日期	0 未处理 1 已完成
表 6 document_template 文书模板表
id	title	type	content	is_system	create_uid
主键	模板名称	分类	富文本内容	1 系统预置 0 自定义	创建人 ID
索引：title 标题索引					
表 7 case_library 案例库表
id	title	case_type	key_point	case_content	law_basis	result	create_uid
主键	案例标题	案由	裁判要点	案情详情	法律依据	裁判结果	录入人 ID
表 8 finance_income 收费收入表
id	case_id	amount	pay_type	pay_date	invoice_status	remark
主键	案件 ID 外键	金额	收款方式	收款日期	1 已开票 0 未开票	备注
表 9 finance_expense 支出表
id	exp_type	amount	exp_date	remark
主键	支出分类	支出金额	支出日期	备注
表 10 finance_invoice 发票明细表
id	income_id	invoice_no	tax_rate	invoice_title
主键	收入记录 ID 外键	发票号码	税率	购方抬头
表 11 case_file 案件附件表
id	case_id	file_name	save_path	upload_time
主键	案件 ID 外键	原文件名	本地存储路径	上传时间
2 表关联关系
1.case_info.client_id → [client.id](client.id)（案件绑定客户）
2.case_info.lawyer_id → sys\[_user.id](_user.id)（案件绑定承办律师）
3.case_remind.case_id → case\[_info.id](_info.id)（提醒绑定案件）
4.finance_income.case_id → case\[_info.id](_info.id)（收款绑定案件）
5.finance_invoice.income_id → finance\[_income.id](_income.id)（发票绑定收款）
6.case_file.case_id → case\[_info.id](_info.id)（附件绑定案件）
###3 数据库初始化说明
项目首次启动自动创建全部数据表，自动导入系统预置 123 份文书、500 条案例初始化数据。
保存为：【03 - 数据库设计说明书.docx】
文档 4：产品原型设计说明书.docx
1 页面原型文字描述（可直接复制到 Word，配合 Visio/PPT 绘图）
页面 1：登录页
页面布局：居中登录卡片；顶部展示律所名称；表单：账号输入框、密码输入框；登录按钮；底部标注系统版本 V1.0、版权信息；无注册入口，账号由管理员后台创建。
页面 2：首页工作台
布局：左侧竖向菜单栏、右上统计卡片、右下待办提醒列表；
1.左侧菜单：系统设置、客户管理、案件管理、文书模板库、案例资料库、财务管理、辅助工具；
2.右上数据卡片：在办案件总数、本月营收、待开庭案件数量、未开票收款笔数；
3.右下待办：即将开庭提醒、超期未收律师费提醒，点击跳转对应详情页。
页面 3：客户管理列表页
顶部：搜索框（姓名 / 手机号）+ 新增客户 + 导出 Excel 按钮；中间数据表格：序号、姓名、电话、客户标签、建档时间、操作（详情 / 编辑 / 绑定案件）；底部分页控件。
弹窗：新增客户弹窗，表单录入客户基础信息。
页面 4：案件管理列表页
顶部筛选：承办律师下拉、案件类型下拉、审理阶段筛选；搜索框、新增案件；表格字段：案号、客户名称、承办律师、开庭日期、案件阶段、操作（编辑、新增文书、添加提醒、附件上传、归档）；开庭日期临近数据标红高亮。
页面 5：文书模板页面
左侧树形分类（民事文书 / 刑事文书 / 合同协议 / 律师函 / 委托手续）；右侧模板列表；选中模板→【选用】按钮弹窗绑定案件，自动填充变量；在线富文本编辑器，保存模板 / 导出 Word/PDF。
页面 6：案例库页面
顶部：案由筛选 + 关键词搜索；列表：案例标题、案由；查看详情弹窗展示完整裁判要点、法条、案情；支持收藏、导出、新增自建案例。
页面 7：财务管理页面
顶部 TAB 切换：收入登记、支出登记、发票管理、财务报表；
收入页：新增收款绑定案件、填写金额；报表页：图表 + 数据表格，导出 Excel。
页面 8：系统设置页
TAB：用户管理、律所信息配置、数据备份恢复；用户管理列表增删改账号；律所信息表单填写全所信息。
保存为：【04 - 产品原型设计说明书.docx】
文档 5：后端开发框架说明书.docx
Plain Text
开发技术栈：Python3.9 + Flask + Flask-SQLAlchemy + SQLite3
前端：LayUI+Bootstrap
文档生成：python-docx
打包工具：Pyinstaller（打包Windows桌面exe）
1 项目目录结构
Plain Text
law_firm_system/
├── app.py               # 项目启动入口
├── config.py            # 全局配置文件
├── models.py            # ORM数据库模型定义
├── init_data.py         # 初始化内置文书、案例脚本
├── static/               # css/js静态资源
│   ├── css/
│   ├── js/
├── templates/            # html页面模板
│   ├── login.html
│   ├── index.html
│   ├── client/
│   ├── case/
│   ├── document/
│   ├── finance/
├── utils/                # 工具类
│   ├── doc_export.py     # Word导出工具
│   ├── date_calc.py     # 期限计算工具
├── upload/               # 案件附件存储目录
├── db/law_db.sqlite      # 数据库文件
└── requirements.txt      # 依赖清单
2 核心依赖 requirements.txt
Plain Text
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
python-docx==1.0.2
pycryptodome==3.19.0
安装命令：pip install -r requirements.txt
###3 关键代码片段
[config.py](config.py)
python
import os
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR,"db","law_db.sqlite")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "lawfirm2026syskey"
[models.py](models.py)（节选用户 & 客户模型）
python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class SysUser(db.Model):
    __tablename__ = "sys_user"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(32),nullable=False)
    password = db.Column(db.String(64),nullable=False)
    real_name = db.Column(db.String(32),nullable=False)
    role = db.Column(db.String(16),nullable=False)
    status = db.Column(db.Integer,default=1)

class Client(db.Model):
    __tablename__ = "client"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(32),nullable=False)
    phone = db.Column(db.String(16),index=True)
    id_card = db.Column(db.String(32))
    tag = db.Column(db.String(32))
[app.py](app.py) 入口
python
from flask import Flask,render_template
from models import db
import config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/index")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # db.create_all() #首次运行打开创建数据表
    app.run(host="0.0.0.0",port=5000,debug=False)
###4 打包发布方案
执行打包命令生成 exe 桌面程序：
pyinstaller -F -w app.py
打包后 dist 目录生成 exe，直接在 Windows 双击运行，自带内置数据库与初始化文书案例。
保存为：【05 - 开发框架说明书.docx】
使用操作：
1.桌面新建 5 个 Word 空白文档，按上面命名；
2.分段复制对应区块内容粘贴进去，保存即可直接交付开发 / 律所验收。
|（注：文档部分内容可能由 AI 生成）
