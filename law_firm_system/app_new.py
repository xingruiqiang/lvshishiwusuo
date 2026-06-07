from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
import config
from models import db, SysUser, SysFirm, Client, CaseInfo, CaseRemind, DocumentTemplate, CaseLibrary, FinanceIncome, FinanceExpense, FinanceInvoice, CaseFile
from datetime import datetime, date
import os

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = config.SECRET_KEY
db.init_app(app)

# 登录拦截器
@app.before_request
def login_required():
    allowed_paths = ['/login', '/static/']
    if request.path in allowed_paths or request.path.startswith('/static'):
        return None
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return None

# ==================== 登录模块 ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = SysUser.query.filter_by(username=username, password=password).first()
        if user and user.status == 1:
            session['user_id'] = user.id
            session['username'] = user.username
            session['real_name'] = user.real_name
            session['role'] = user.role
            return redirect(url_for('index'))
        else:
            flash('账号或密码错误，或账号已禁用')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==================== 首页工作台 ====================
@app.route('/')
@app.route('/index')
def index():
    # 统计卡片数据
    case_count = CaseInfo.query.filter_by(status='在办').count()
    
    # 本月营收
    today = date.today()
    first_day = date(today.year, today.month, 1)
    month_incomes = FinanceIncome.query.filter(FinanceIncome.pay_date >= first_day).all()
    month_income = sum([inc.amount or 0 for inc in month_incomes])
    
    # 本月开庭案件
    next_month = date(today.year + (1 if today.month == 12 else 0), (today.month % 12) + 1, 1)
    court_comings = CaseInfo.query.filter(
        CaseInfo.court_date >= today,
        CaseInfo.court_date < next_month
    ).all()
    court_coming = len(court_comings)
    
    # 未开票收款笔数
    uninvoiced = FinanceIncome.query.filter_by(invoice_status=0).count()
    
    # 待办提醒
    reminds = CaseRemind.query.filter_by(is_finish=0).all()
    
    return render_template('index.html', 
                         case_count=case_count,
                         month_income=month_income,
                         court_coming=court_coming,
                         uninvoiced=uninvoiced,
                         reminds=reminds)

# ==================== 客户管理模块 ====================
@app.route('/client/list')
def client_list():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    query = Client.query
    if keyword:
        query = query.filter(Client.name.contains(keyword) | Client.phone.contains(keyword))
    pagination = query.paginate(page=page, per_page=config.ITEMS_PER_PAGE, error_out=False)
    return render_template('client/list.html', clients=pagination.items, pagination=pagination, keyword=keyword)

@app.route('/client/add', methods=['GET', 'POST'])
def client_add():
    if request.method == 'POST':
        client = Client(
            name=request.form.get('name'),
            id_card=request.form.get('id_card'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            tag=request.form.get('tag'),
            remark=request.form.get('remark')
        )
        db.session.add(client)
        db.session.commit()
        flash('客户添加成功')
        return redirect(url_for('client_list'))
    return render_template('client/add.html')

@app.route('/client/edit/<int:id>', methods=['GET', 'POST'])
def client_edit(id):
    client = Client.query.get_or_404(id)
    if request.method == 'POST':
        client.name = request.form.get('name')
        client.id_card = request.form.get('id_card')
        client.phone = request.form.get('phone')
        client.address = request.form.get('address')
        client.tag = request.form.get('tag')
        client.remark = request.form.get('remark')
        db.session.commit()
        flash('客户信息更新成功')
        return redirect(url_for('client_list'))
    return render_template('client/add.html', client=client)

@app.route('/client/detail/<int:id>')
def client_detail(id):
    client = Client.query.get_or_404(id)
    cases = CaseInfo.query.filter_by(client_id=id).all()
    return render_template('client/detail.html', client=client, cases=cases)

@app.route('/client/delete/<int:id>')
def client_delete(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash('客户删除成功')
    return redirect(url_for('client_list'))

# ==================== 案件管理模块 ====================
@app.route('/case/list')
def case_list():
    page = request.args.get('page', 1, type=int)
    lawyer_id = request.args.get('lawyer_id', type=int)
    case_type = request.args.get('case_type', '')
    stage = request.args.get('stage', '')
    
    query = CaseInfo.query
    if lawyer_id:
        query = query.filter_by(lawyer_id=lawyer_id)
    if case_type:
        query = query.filter_by(case_type=case_type)
    if stage:
        query = query.filter_by(stage=stage)
    
    pagination = query.paginate(page=page, per_page=config.ITEMS_PER_PAGE, error_out=False)
    lawyers = SysUser.query.filter_by(role='lawyer').all()
    return render_template('case/list.html', cases=pagination.items, pagination=pagination, 
                         lawyers=lawyers, case_type=case_type, stage=stage, lawyer_id=lawyer_id)

@app.route('/case/add', methods=['GET', 'POST'])
def case_add():
    if request.method == 'POST':
        court_date_str = request.form.get('court_date')
        court_date = datetime.strptime(court_date_str, '%Y-%m-%d').date() if court_date_str else None
        
        accept_date_str = request.form.get('accept_date')
        accept_date = datetime.strptime(accept_date_str, '%Y-%m-%d').date() if accept_date_str else None
        
        case = CaseInfo(
            client_id=request.form.get('client_id', type=int),
            case_no=request.form.get('case_no'),
            case_type=request.form.get('case_type'),
            court=request.form.get('court'),
            lawyer_id=request.form.get('lawyer_id', type=int),
            opposite_party=request.form.get('opposite_party'),
            accept_date=accept_date,
            stage=request.form.get('stage', '立案'),
            status=request.form.get('status', '在办'),
            court_date=court_date
        )
        db.session.add(case)
        db.session.commit()
        
        # 自动创建开庭提醒
        if court_date:
            remind = CaseRemind(case_id=case.id, remind_type='开庭', remind_date=court_date)
            db.session.add(remind)
            db.session.commit()
        
        flash('案件添加成功')
        return redirect(url_for('case_list'))
    
    clients = Client.query.all()
    lawyers = SysUser.query.filter_by(role='lawyer').all()
    return render_template('case/add.html', clients=clients, lawyers=lawyers)

@app.route('/case/edit/<int:id>', methods=['GET', 'POST'])
def case_edit(id):
    case = CaseInfo.query.get_or_404(id)
    if request.method == 'POST':
        court_date_str = request.form.get('court_date')
        court_date = datetime.strptime(court_date_str, '%Y-%m-%d').date() if court_date_str else None
        
        accept_date_str = request.form.get('accept_date')
        accept_date = datetime.strptime(accept_date_str, '%Y-%m-%d').date() if accept_date_str else None
        
        case.client_id = request.form.get('client_id', type=int)
        case.case_no = request.form.get('case_no')
        case.case_type = request.form.get('case_type')
        case.court = request.form.get('court')
        case.lawyer_id = request.form.get('lawyer_id', type=int)
        case.opposite_party = request.form.get('opposite_party')
        case.accept_date = accept_date
        case.stage = request.form.get('stage')
        case.status = request.form.get('status')
        case.court_date = court_date
        db.session.commit()
        flash('案件信息更新成功')
        return redirect(url_for('case_list'))
    
    clients = Client.query.all()
    lawyers = SysUser.query.filter_by(role='lawyer').all()
    return render_template('case/add.html', case=case, clients=clients, lawyers=lawyers)

@app.route('/case/delete/<int:id>')
def case_delete(id):
    case = CaseInfo.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    flash('案件删除成功')
    return redirect(url_for('case_list'))

# ==================== 文书模板库模块 ====================
@app.route('/document/list')
def document_list():
    doc_type = request.args.get('type', '')
    query = DocumentTemplate.query
    if doc_type:
        query = query.filter_by(type=doc_type)
    docs = query.all()
    return render_template('document/list.html', docs=docs, doc_type=doc_type)

@app.route('/document/add', methods=['GET', 'POST'])
def document_add():
    if request.method == 'POST':
        doc = DocumentTemplate(
            title=request.form.get('title'),
            type=request.form.get('type'),
            content=request.form.get('content'),
            is_system=0,
            create_uid=session.get('user_id')
        )
        db.session.add(doc)
        db.session.commit()
        flash('模板添加成功')
        return redirect(url_for('document_list'))
    return render_template('document/add.html')

@app.route('/document/edit/<int:id>', methods=['GET', 'POST'])
def document_edit(id):
    doc = DocumentTemplate.query.get_or_404(id)
    if request.method == 'POST':
        doc.title = request.form.get('title')
        doc.type = request.form.get('type')
        doc.content = request.form.get('content')
        db.session.commit()
        flash('模板更新成功')
        return redirect(url_for('document_list'))
    return render_template('document/add.html', doc=doc)

@app.route('/document/delete/<int:id>')
def document_delete(id):
    doc = DocumentTemplate.query.get_or_404(id)
    db.session.delete(doc)
    db.session.commit()
    flash('模板删除成功')
    return redirect(url_for('document_list'))

@app.route('/document/preview/<int:id>')
def document_preview(id):
    doc = DocumentTemplate.query.get_or_404(id)
    return render_template('document/preview.html', doc=doc)

@app.route('/document/export/<int:id>')
def document_export(id):
    doc = DocumentTemplate.query.get_or_404(id)
    from utils.doc_export import export_docx
    from io import BytesIO
    doc_io = export_docx(doc)
    from flask import make_response
    response = make_response(doc_io.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    response.headers['Content-Disposition'] = f'attachment; filename="{doc.title}.docx"'
    return response

# ==================== 案例资料库模块 ====================
@app.route('/case_library/list')
def case_library_list():
    case_type = request.args.get('case_type', '')
    keyword = request.args.get('keyword', '')
    query = CaseLibrary.query
    if case_type:
        query = query.filter_by(case_type=case_type)
    if keyword:
        query = query.filter(CaseLibrary.title.contains(keyword) | CaseLibrary.key_point.contains(keyword))
    cases = query.all()
    return render_template('case_library/list.html', cases=cases, case_type=case_type, keyword=keyword)

@app.route('/case_library/add', methods=['GET', 'POST'])
def case_library_add():
    if request.method == 'POST':
        judgment_date_str = request.form.get('judgment_date')
        judgment_date = datetime.strptime(judgment_date_str, '%Y-%m-%d').date() if judgment_date_str else None
        
        case = CaseLibrary(
            title=request.form.get('title'),
            case_type=request.form.get('case_type'),
            court=request.form.get('court'),
            judgment_date=judgment_date,
            keywords=request.form.get('keywords'),
            laws=request.form.get('laws'),
            content=request.form.get('content'),
            analysis=request.form.get('analysis'),
            is_favorite=0,
            create_uid=session.get('user_id')
        )
        db.session.add(case)
        db.session.commit()
        flash('案例添加成功')
        return redirect(url_for('case_library_list'))
    return render_template('case_library/add.html')

@app.route('/case_library/edit/<int:id>', methods=['GET', 'POST'])
def case_library_edit(id):
    case = CaseLibrary.query.get_or_404(id)
    if request.method == 'POST':
        judgment_date_str = request.form.get('judgment_date')
        judgment_date = datetime.strptime(judgment_date_str, '%Y-%m-%d').date() if judgment_date_str else None
        
        case.title = request.form.get('title')
        case.case_type = request.form.get('case_type')
        case.court = request.form.get('court')
        case.judgment_date = judgment_date
        case.keywords = request.form.get('keywords')
        case.laws = request.form.get('laws')
        case.content = request.form.get('content')
        case.analysis = request.form.get('analysis')
        db.session.commit()
        flash('案例更新成功')
        return redirect(url_for('case_library_list'))
    return render_template('case_library/add.html', case=case)

@app.route('/case_library/detail/<int:id>')
def case_library_detail(id):
    case = CaseLibrary.query.get_or_404(id)
    return render_template('case_library/detail.html', case=case)

@app.route('/case_library/delete/<int:id>')
def case_library_delete(id):
    case = CaseLibrary.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    flash('案例删除成功')
    return redirect(url_for('case_library_list'))

@app.route('/case_library/favorite/<int:id>')
def case_library_favorite(id):
    case = CaseLibrary.query.get_or_404(id)
    case.is_favorite = 1
    db.session.commit()
    flash('收藏成功')
    return redirect(url_for('case_library_list'))

# ==================== 财务管理模块 ====================
@app.route('/finance/income')
def finance_income():
    incomes = FinanceIncome.query.all()
    
    # 统计 data
    today = date.today()
    month_incomes = [inc for inc in incomes if inc.pay_date and inc.pay_date.month == today.month and inc.pay_date.year == today.year]
    month_income = sum([inc.amount or 0 for inc in month_incomes])
    
    pending_incomes = [inc for inc in incomes if inc.receive_status == 0]
    pending_income = sum([inc.amount or 0 for inc in pending_incomes])
    
    invoiced_not_received = [inc for inc in incomes if inc.invoice_status == 1 and inc.receive_status == 0]
    invoiced_not_received_amount = sum([inc.amount or 0 for inc in invoiced_not_received])
    
    year_incomes = [inc for inc in incomes if inc.pay_date and inc.pay_date.year == today.year]
    year_income = sum([inc.amount or 0 for inc in year_incomes])
    
    return render_template('finance/income.html', 
                         incomes=incomes,
                         month_income=month_income,
                         pending_income=pending_income,
                         invoiced_not_received=invoiced_not_received_amount,
                         year_income=year_income)

@app.route('/finance/expense')
def finance_expense():
    expenses = FinanceExpense.query.all()
    
    today = date.today()
    month_expenses = [exp for exp in expenses if exp.pay_date and exp.pay_date.month == today.month and exp.pay_date.year == today.year]
    month_expense = sum([exp.amount or 0 for exp in month_expenses])
    
    year_expenses = [exp for exp in expenses if exp.pay_date and exp.pay_date.year == today.year]
    year_expense = sum([exp.amount or 0 for exp in year_expenses])
    
    year_incomes = FinanceIncome.query.filter(FinanceIncome.pay_date.isnot(None)).all()
    year_income = sum([inc.amount or 0 for inc in year_incomes if inc.pay_date and inc.pay_date.year == today.year])
    
    return render_template('finance/expense.html',
                         expenses=expenses,
                         month_expense=month_expense,
                         year_expense=year_expense,
                         year_income=year_income)

@app.route('/finance/report')
def finance_report():
    selected_month = request.args.get('month', date.today().strftime('%Y-%m'))
    year, month = selected_month.split('-')
    year = int(year)
    month = int(month)
    
    incomes = FinanceIncome.query.filter(
        FinanceIncome.pay_date.isnot(None),
        FinanceIncome.pay_date >= date(year, month, 1)
    ).all()
    
    expenses = FinanceExpense.query.filter(
        FinanceExpense.pay_date.isnot(None),
        FinanceExpense.pay_date >= date(year, month, 1)
    ).all()
    
    income_total = sum([inc.amount or 0 for inc in incomes])
    expense_total = sum([exp.amount or 0 for exp in expenses])
    
    expense_office = sum([exp.amount or 0 for exp in expenses if exp.expense_type == '办公'])
    expense_case = sum([exp.amount or 0 for exp in expenses if exp.expense_type == '案件'])
    expense_other = sum([exp.amount or 0 for exp in expenses if exp.expense_type not in ['办公', '案件']])
    
    net_income = income_total - expense_total
    
    return render_template('finance/report.html',
                         selected_month=selected_month,
                         income_total=income_total,
                         expense_total=expense_total,
                         expense_office=expense_office,
                         expense_case=expense_case,
                         expense_other=expense_other,
                         net_income=net_income)

# ==================== 系统管理模块 ====================
@app.route('/system/user')
def system_user():
    if session.get('role') != 'admin':
        flash('无权限访问')
        return redirect(url_for('index'))
    users = SysUser.query.all()
    return render_template('system/user.html', users=users)

@app.route('/system/firm', methods=['GET', 'POST'])
def system_firm():
    if session.get('role') != 'admin':
        flash('无权限访问')
        return redirect(url_for('index'))
    firm = SysFirm.query.first()
    if request.method == 'POST':
        if not firm:
            firm = SysFirm()
            db.session.add(firm)
        firm.name = request.form.get('firm_name')
        firm.credit_code = request.form.get('credit_code')
        firm.legal_rep = request.form.get('legal_rep')
        establish_date_str = request.form.get('establish_date')
        firm.establish_date = datetime.strptime(establish_date_str, '%Y-%m-%d').date() if establish_date_str else None
        firm.address = request.form.get('address')
        firm.phone = request.form.get('phone')
        firm.email = request.form.get('email')
        firm.bank_name = request.form.get('bank_name')
        firm.bank_account = request.form.get('bank_account')
        db.session.commit()
        flash('律所信息更新成功')
        return redirect(url_for('system_firm'))
    return render_template('system/firm.html', firm=firm)

@app.route('/system/backup')
def system_backup():
    if session.get('role') != 'admin':
        flash('无权限访问')
        return redirect(url_for('index'))
    import shutil
    backup_dir = os.path.join(config.BASE_DIR, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f'law_db_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite')
    shutil.copy(config.DB_PATH, backup_path)
    flash(f'备份成功：{backup_path}')
    return redirect(url_for('index'))

# ==================== 启动应用 ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 检查是否需要初始化数据
        if not SysUser.query.filter_by(username='admin').first():
            print('首次运行，请执行: python init_data.py')
    app.run(host='0.0.0.0', port=5000, debug=True)
