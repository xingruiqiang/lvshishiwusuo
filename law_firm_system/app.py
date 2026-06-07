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

@app.route('/client/export')
def client_export():
    import openpyxl
    from openpyxl.styles import Font, Alignment
    from io import BytesIO
    
    clients = Client.query.all()
    
    # 创建Excel工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "客户列表"
    
    # 设置表头
    headers = ['ID', '姓名/企业名称', '身份证号', '电话', '地址', '标签', '备注']
    ws.append(headers)
    
    # 设置表头样式
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # 填充数据
    for client in clients:
        ws.append([
            client.id,
            client.name,
            client.id_card or '',
            client.phone or '',
            client.address or '',
            client.tag or '',
            client.remark or ''
        ])
    
    # 调整列宽
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 30
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 30
    
    # 保存到内存
    excel_io = BytesIO()
    wb.save(excel_io)
    excel_io.seek(0)
    
    from flask import make_response
    response = make_response(excel_io.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=客户列表.xlsx'
    return response

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
                         lawyers=lawyers, case_type=case_type, stage=stage, lawyer_id=lawyer_id,
                         date=date)

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

@app.route('/case/remind/<int:id>', methods=['GET', 'POST'])
def case_remind(id):
    case = CaseInfo.query.get_or_404(id)
    if request.method == 'POST':
        remind_type = request.form.get('remind_type', '开庭')
        remind_date_str = request.form.get('remind_date')
        remind_date = datetime.strptime(remind_date_str, '%Y-%m-%d').date() if remind_date_str else None
        remind = CaseRemind(case_id=case.id, remind_type=remind_type, remind_date=remind_date)
        db.session.add(remind)
        db.session.commit()
        flash('提醒添加成功')
        return redirect(url_for('case_list'))
    return render_template('case/remind.html', case=case)

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

@app.route('/document/preview/<int:id>')
def document_preview(id):
    doc = DocumentTemplate.query.get_or_404(id)
    return render_template('document/preview.html', doc=doc)

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
    return render_template('document/edit.html', doc=doc)

@app.route('/document/delete/<int:id>')
def document_delete(id):
    doc = DocumentTemplate.query.get_or_404(id)
    db.session.delete(doc)
    db.session.commit()
    flash('模板删除成功')
    return redirect(url_for('document_list'))

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
            key_point=request.form.get('key_point'),
            laws=request.form.get('laws'),
            case_content=request.form.get('case_content'),
            analysis=request.form.get('analysis'),
            is_system=0,
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
        case.key_point = request.form.get('key_point')
        case.laws = request.form.get('laws')
        case.case_content = request.form.get('case_content')
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
    # is_system 字段同时作为是否收藏标记：0=自建，1=系统预置/收藏
    # 这里简单处理：如果原来是0，则改为1（收藏），原来是1则改为0（取消收藏）
    case.is_system = 1 if case.is_system == 0 else 0
    db.session.commit()
    flash('收藏状态已更新')
    return redirect(url_for('case_library_list'))

# ==================== 财务管理模块 ====================
@app.route('/finance/income')
def finance_income():
    page = request.args.get('page', 1, type=int)
    query = FinanceIncome.query
    pagination = query.paginate(page=page, per_page=config.ITEMS_PER_PAGE, error_out=False)
    
    # 统计 data
    all_incomes = FinanceIncome.query.all()
    today = date.today()
    month_incomes = [inc for inc in all_incomes if inc.pay_date and inc.pay_date.month == today.month and inc.pay_date.year == today.year]
    month_income = sum([inc.amount or 0 for inc in month_incomes])
    
    # 待收费（没有收款日期或收款日期为空）
    pending_incomes = [inc for inc in all_incomes if not inc.pay_date]
    pending_income = sum([inc.amount or 0 for inc in pending_incomes])
    
    # 已开票未收款
    invoiced_not_received = [inc for inc in all_incomes if inc.invoice_status == 1 and not inc.pay_date]
    invoiced_not_received_amount = sum([inc.amount or 0 for inc in invoiced_not_received])
    
    # 本年收费
    year_incomes = [inc for inc in all_incomes if inc.pay_date and inc.pay_date.year == today.year]
    year_income = sum([inc.amount or 0 for inc in year_incomes])
    
    return render_template('finance/income.html',
                         incomes=pagination.items,
                         pagination=pagination,
                         month_income=month_income,
                         pending_income=pending_income,
                         invoiced_not_received=invoiced_not_received_amount,
                         year_income=year_income)

@app.route('/finance/income_add', methods=['GET', 'POST'])
def finance_income_add():
    if request.method == 'POST':
        pay_date_str = request.form.get('pay_date')
        pay_date = datetime.strptime(pay_date_str, '%Y-%m-%d').date() if pay_date_str else None
        inc = FinanceIncome(
            case_id=request.form.get('case_id', type=int) if request.form.get('case_id') else None,
            pay_type=request.form.get('pay_type'),
            amount=float(request.form.get('amount') or 0),
            pay_date=pay_date,
            invoice_status=1 if request.form.get('invoice_status') == '1' else 0,
            remark=request.form.get('remark')
        )
        db.session.add(inc)
        db.session.commit()
        flash('收费记录添加成功')
        return redirect(url_for('finance_income'))
    cases = CaseInfo.query.filter_by(status='在办').all()
    return render_template('finance/income_add.html', cases=cases)

@app.route('/finance/income_edit/<int:id>', methods=['GET', 'POST'])
def finance_income_edit(id):
    inc = FinanceIncome.query.get_or_404(id)
    if request.method == 'POST':
        pay_date_str = request.form.get('pay_date')
        pay_date = datetime.strptime(pay_date_str, '%Y-%m-%d').date() if pay_date_str else None
        inc.case_id = request.form.get('case_id', type=int) if request.form.get('case_id') else None
        inc.pay_type = request.form.get('pay_type')
        inc.amount = float(request.form.get('amount') or 0)
        inc.pay_date = pay_date
        inc.invoice_status = 1 if request.form.get('invoice_status') == '1' else 0
        inc.remark = request.form.get('remark')
        db.session.commit()
        flash('收费记录更新成功')
        return redirect(url_for('finance_income'))
    cases = CaseInfo.query.filter_by(status='在办').all()
    return render_template('finance/income_add.html', inc=inc, cases=cases)

@app.route('/finance/expense')
def finance_expense():
    page = request.args.get('page', 1, type=int)
    query = FinanceExpense.query
    pagination = query.paginate(page=page, per_page=config.ITEMS_PER_PAGE, error_out=False)
    
    # 统计 data
    all_expenses = FinanceExpense.query.all()
    today = date.today()
    month_expenses = [exp for exp in all_expenses if exp.pay_date and exp.pay_date.month == today.month and exp.pay_date.year == today.year]
    month_expense = sum([exp.amount or 0 for exp in month_expenses])
    
    year_expenses = [exp for exp in all_expenses if exp.pay_date and exp.pay_date.year == today.year]
    year_expense = sum([exp.amount or 0 for exp in year_expenses])
    
    year_incomes = FinanceIncome.query.filter(FinanceIncome.pay_date.isnot(None)).all()
    year_income = sum([inc.amount or 0 for inc in year_incomes if inc.pay_date and inc.pay_date.year == today.year])
    
    return render_template('finance/expense.html',
                         expenses=pagination.items,
                         pagination=pagination,
                         month_expense=month_expense,
                         year_expense=year_expense,
                         year_income=year_income)

@app.route('/finance/expense_add', methods=['GET', 'POST'])
def finance_expense_add():
    if request.method == 'POST':
        pay_date_str = request.form.get('pay_date')
        pay_date = datetime.strptime(pay_date_str, '%Y-%m-%d').date() if pay_date_str else None
        exp = FinanceExpense(
            case_id=request.form.get('case_id', type=int) if request.form.get('case_id') else None,
            expense_type=request.form.get('expense_type'),
            amount=float(request.form.get('amount') or 0),
            pay_date=pay_date,
            remark=request.form.get('remark')
        )
        db.session.add(exp)
        db.session.commit()
        flash('支出记录添加成功')
        return redirect(url_for('finance_expense'))
    cases = CaseInfo.query.filter_by(status='在办').all()
    return render_template('finance/expense_add.html', cases=cases)

@app.route('/finance/expense_edit/<int:id>', methods=['GET', 'POST'])
def finance_expense_edit(id):
    exp = FinanceExpense.query.get_or_404(id)
    if request.method == 'POST':
        pay_date_str = request.form.get('pay_date')
        pay_date = datetime.strptime(pay_date_str, '%Y-%m-%d').date() if pay_date_str else None
        exp.case_id = request.form.get('case_id', type=int) if request.form.get('case_id') else None
        exp.expense_type = request.form.get('expense_type')
        exp.amount = float(request.form.get('amount') or 0)
        exp.pay_date = pay_date
        exp.remark = request.form.get('remark')
        db.session.commit()
        flash('支出记录更新成功')
        return redirect(url_for('finance_expense'))
    cases = CaseInfo.query.filter_by(status='在办').all()
    return render_template('finance/expense_add.html', exp=exp, cases=cases)

# ==================== 系统管理模块 ====================
@app.route('/system/user')
def system_user():
    if session.get('role') != 'admin':
        flash('无权限访问')
        return redirect(url_for('index'))
    users = SysUser.query.all()
    return render_template('system/user.html', users=users)

@app.route('/system/user/add', methods=['GET', 'POST'])
def system_user_add():
    if session.get('role') != 'admin':
        flash('无权限访问')
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = SysUser(
            username=request.form.get('username'),
            password=request.form.get('password'),
            real_name=request.form.get('real_name'),
            role=request.form.get('role', 'lawyer'),
            status=1
        )
        db.session.add(user)
        db.session.commit()
        flash('用户添加成功')
        return redirect(url_for('system_user'))
    return render_template('system/user_add.html')

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
        firm.name = request.form.get('name')
        firm.address = request.form.get('address')
        firm.phone = request.form.get('phone')
        firm.remark = request.form.get('remark')
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
    app.run(host='0.0.0.0', port=5066, debug=True)
