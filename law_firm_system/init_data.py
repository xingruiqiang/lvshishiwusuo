"""
初始化数据脚本
创建管理员账号、律所信息、内置文书模板、内置案例
"""
from app import app, db
from models import SysUser, SysFirm, DocumentTemplate, CaseLibrary
from datetime import datetime

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 1. 创建管理员账号
        admin = SysUser.query.filter_by(username='admin').first()
        if not admin:
            admin = SysUser(
                username='admin',
                password='admin123',  # 默认密码，首次登录后应修改
                real_name='系统管理员',
                role='admin',
                phone='13800138000',
                status=1
            )
            db.session.add(admin)
            db.session.commit()
            print('创建管理员账号: admin / admin123')
        
        # 2. 创建律所信息（空，待用户填写）
        firm = SysFirm.query.first()
        if not firm:
            firm = SysFirm(
                name='',
                address='',
                phone='',
                remark=''
            )
            db.session.add(firm)
            db.session.commit()
            print('创建律所信息表')
        
        # 3. 创建内置文书模板（示例10个，实际应123个）
        templates = [
            {'title': '民事起诉状', 'type': '诉讼文书', 'content': '民事起诉状\n\n原告：[原告信息]\n被告：[被告信息]\n诉讼请求：\n1. [诉讼请求1]\n2. [诉讼请求2]\n事实与理由：\n[事实与理由]\n\n此致\n[法院名称]\n\n起诉人：[原告姓名]\n[日期]'},
            {'title': '民事答辩状', 'type': '诉讼文书', 'content': '民事答辩状\n\n答辩人：[答辩人信息]\n被答辩人：[被答辩人信息]\n答辩事项：\n[答辩事项]\n事实与理由：\n[事实与理由]\n\n此致\n[法院名称]\n\n答辩人：[答辩人姓名]\n[日期]'},
            {'title': '上诉状', 'type': '诉讼文书', 'content': '上诉状\n\n上诉人：[上诉人信息]\n被上诉人：[被上诉人信息]\n上诉请求：\n[上诉请求]\n事实与理由：\n[事实与理由]\n\n此致\n[上级法院名称]\n\n上诉人：[上诉人姓名]\n[日期]'},
            {'title': '财产保全申请书', 'type': '诉讼文书', 'content': '财产保全申请书\n\n申请人：[申请人信息]\n被申请人：[被申请人信息]\n申请事项：\n[申请保全的财产]\n事实与理由：\n[事实与理由]\n\n此致\n[法院名称]\n\n申请人：[申请人姓名]\n[日期]'},
            {'title': '强制执行申请书', 'type': '诉讼文书', 'content': '强制执行申请书\n\n申请人：[申请人信息]\n被执行人：[被执行人信息]\n申请事项：\n[执行标的]\n事实与理由：\n[事实与理由]\n\n此致\n[法院名称]\n\n申请人：[申请人姓名]\n[日期]'},
            {'title': '授权委托书', 'type': '委托手续', 'content': '授权委托书\n\n委托人：[委托人姓名]\n受托人：[律师姓名] [律所名称]律师\n委托事项：\n[委托事项]\n\n委托人：[委托人姓名]\n[日期]'},
            {'title': '律师事务所函', 'type': '委托手续', 'content': '律师事务所函\n\n[法院名称]：\n贵院受理的[案号]一案，本所[律师姓名]律师已接受[委托人]的委托，担任其[审理阶段]的诉讼代理人。\n\n特此函告。\n\n[律所名称]\n[日期]'},
            {'title': '借款合同', 'type': '合同协议', 'content': '借款合同\n\n甲方（出借人）：[出借人信息]\n乙方（借款人）：[借款人信息]\n借款金额：[金额]\n借款期限：[期限]\n利息：[利息]\n\n甲方：[签字]\n乙方：[签字]\n[日期]'},
            {'title': '法律服务合同', 'type': '合同协议', 'content': '法律服务合同\n\n甲方（委托方）：[委托方信息]\n乙方（受托方）：[律所名称]\n服务内容：[服务内容]\n律师费：[律师费]\n\n甲方：[签字/盖章]\n乙方：[盖章]\n[日期]'},
            {'title': '律师函', 'type': '律师函', 'content': '律师函\n\n致：[收函人]\n\n[律所名称]接受[委托人]的委托，就[事项]向贵方致函：\n[函件内容]\n\n特此函告。\n\n[律所名称]\n[律师姓名]\n[日期]'}
        ]
        
        for t in templates:
            existing = DocumentTemplate.query.filter_by(title=t['title']).first()
            if not existing:
                template = DocumentTemplate(
                    title=t['title'],
                    type=t['type'],
                    content=t['content'],
                    is_system=1,
                    create_uid=1
                )
                db.session.add(template)
        db.session.commit()
        print(f'创建{len(templates)}个内置文书模板')
        
        # 4. 创建内置案例（示例5个，实际应500+）
        cases = [
            {'title': '张三诉李四民间借贷纠纷案', 'case_type': '民间借贷', 'key_point': '借条效力认定', 'case_content': '基本案情：张三向李四借款10万元...', 'law_basis': '民法典第六百六十七条', 'result': '支持原告诉讼请求'},
            {'title': '王某诉某保险公司交通事故纠纷案', 'case_type': '交通事故', 'key_point': '交通事故责任认定', 'case_content': '基本案情：王某被某保险公司车辆撞伤...', 'law_basis': '道路交通安全法第七十六条', 'result': '被告赔偿原告损失'},
            {'title': '李某诉某公司劳动争议案', 'case_type': '劳动争议', 'key_point': '违法解除劳动合同赔偿', 'case_content': '基本案情：李某被公司违法解除劳动关系...', 'law_basis': '劳动合同法第四十八条', 'result': '公司支付赔偿金'},
            {'title': '赵某诉钱某婚姻家庭纠纷案', 'case_type': '婚姻家事', 'key_point': '夫妻共同财产分割', 'case_content': '基本案情：赵某与钱某离婚纠纷...', 'law_basis': '民法典第一千零八十七条', 'result': '夫妻共同财产依法分割'},
            {'title': '孙某涉嫌帮信罪案', 'case_type': '帮信罪', 'key_point': '帮助信息网络犯罪活动罪认定', 'case_content': '基本案情：孙某明知他人利用信息网络实施犯罪...', 'law_basis': '刑法第二百八十七条之二', 'result': '判处有期徒刑八个月，缓刑一年'}
        ]
        
        for c in cases:
            existing = CaseLibrary.query.filter_by(title=c['title']).first()
            if not existing:
                case = CaseLibrary(
                    title=c['title'],
                    case_type=c['case_type'],
                    key_point=c['key_point'],
                    case_content=c['case_content'],
                    law_basis=c['law_basis'],
                    result=c['result'],
                    is_system=1,
                    create_uid=1
                )
                db.session.add(case)
        db.session.commit()
        print(f'创建{len(cases)}个内置案例')
        
        print('\n初始化完成！')
        print('管理员账号：admin / admin123')
        print('请首次登录后修改密码并完善律所信息')

if __name__ == '__main__':
    init_database()
