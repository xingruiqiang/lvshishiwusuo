from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SysUser(db.Model):
    """用户表"""
    __tablename__ = "sys_user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    real_name = db.Column(db.String(32), nullable=False)
    role = db.Column(db.String(16), nullable=False)  # admin/lawyer/assistant
    phone = db.Column(db.String(16))
    status = db.Column(db.Integer, default=1)  # 1启用 0禁用
    create_time = db.Column(db.DateTime, default=datetime.now)

class SysFirm(db.Model):
    """律所信息表"""
    __tablename__ = "sys_firm"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))  # 律所全称
    address = db.Column(db.String(256))  # 地址
    phone = db.Column(db.String(32))  # 联系电话
    remark = db.Column(db.Text)  # 备注

class Client(db.Model):
    """客户信息表"""
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)  # 客户姓名
    id_card = db.Column(db.String(32))  # 身份证号
    phone = db.Column(db.String(16), index=True)  # 手机号
    address = db.Column(db.String(256))  # 住址
    tag = db.Column(db.String(32))  # 客户标签：个人/企业/法律顾问单位
    remark = db.Column(db.Text)  # 备注
    create_time = db.Column(db.DateTime, default=datetime.now)

class CaseInfo(db.Model):
    """案件主表"""
    __tablename__ = "case_info"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))  # 客户ID
    case_no = db.Column(db.String(64))  # 案号
    case_type = db.Column(db.String(32))  # 案件类型：民事/刑事/劳动/行政/执行
    court = db.Column(db.String(128))  # 受理法院
    lawyer_id = db.Column(db.Integer, db.ForeignKey("sys_user.id"))  # 承办律师ID
    opposite_party = db.Column(db.String(128))  # 对方当事人
    accept_date = db.Column(db.Date)  # 收案日期
    stage = db.Column(db.String(32), default="立案")  # 审理阶段
    status = db.Column(db.String(16), default="在办")  # 案件状态：在办/结案
    court_date = db.Column(db.Date)  # 开庭日期
    create_time = db.Column(db.DateTime, default=datetime.now)

class CaseRemind(db.Model):
    """案件提醒表"""
    __tablename__ = "case_remind"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case_info.id"))  # 案件ID
    remind_type = db.Column(db.String(16))  # 提醒类型：开庭/举证/上诉
    remind_date = db.Column(db.Date)  # 提醒日期
    is_finish = db.Column(db.Integer, default=0)  # 0未处理 1已完成
    case_info = db.relationship('CaseInfo', backref='reminds')

class DocumentTemplate(db.Model):
    """文书模板表"""
    __tablename__ = "document_template"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128))  # 模板名称
    type = db.Column(db.String(32))  # 分类
    content = db.Column(db.Text)  # 富文本内容
    is_system = db.Column(db.Integer, default=1)  # 1系统预置 0自定义
    create_uid = db.Column(db.Integer, db.ForeignKey("sys_user.id"))  # 创建人ID
    create_time = db.Column(db.DateTime, default=datetime.now)

class CaseLibrary(db.Model):
    """案例库表"""
    __tablename__ = "case_library"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256))  # 案例标题
    case_type = db.Column(db.String(64))  # 案由
    key_point = db.Column(db.Text)  # 裁判要点
    case_content = db.Column(db.Text)  # 案情详情
    law_basis = db.Column(db.Text)  # 法律依据
    result = db.Column(db.Text)  # 裁判结果
    is_system = db.Column(db.Integer, default=0)  # 1系统预置 0自建
    create_uid = db.Column(db.Integer, db.ForeignKey("sys_user.id"))  # 录入人ID
    create_time = db.Column(db.DateTime, default=datetime.now)

class FinanceIncome(db.Model):
    """收费收入表"""
    __tablename__ = "finance_income"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case_info.id"))  # 案件ID
    amount = db.Column(db.Float)  # 金额
    pay_type = db.Column(db.String(32))  # 收款方式
    pay_date = db.Column(db.Date)  # 收款日期
    invoice_status = db.Column(db.Integer, default=0)  # 1已开票 0未开票
    remark = db.Column(db.Text)  # 备注
    create_time = db.Column(db.DateTime, default=datetime.now)

class FinanceExpense(db.Model):
    """支出表"""
    __tablename__ = "finance_expense"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exp_type = db.Column(db.String(32))  # 支出分类
    amount = db.Column(db.Float)  # 支出金额
    exp_date = db.Column(db.Date)  # 支出日期
    remark = db.Column(db.Text)  # 备注
    create_time = db.Column(db.DateTime, default=datetime.now)

class FinanceInvoice(db.Model):
    """发票明细表"""
    __tablename__ = "finance_invoice"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    income_id = db.Column(db.Integer, db.ForeignKey("finance_income.id"))  # 收入记录ID
    invoice_no = db.Column(db.String(64))  # 发票号码
    tax_rate = db.Column(db.String(16))  # 税率
    invoice_title = db.Column(db.String(128))  # 购方抬头
    create_time = db.Column(db.DateTime, default=datetime.now)

class CaseFile(db.Model):
    """案件附件表"""
    __tablename__ = "case_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case_info.id"))  # 案件ID
    file_name = db.Column(db.String(256))  # 原文件名
    save_path = db.Column(db.String(512))  # 本地存储路径
    upload_time = db.Column(db.DateTime, default=datetime.now)
