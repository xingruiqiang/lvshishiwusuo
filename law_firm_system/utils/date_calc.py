"""
诉讼期限计算工具
计算上诉期、举证期、诉讼时效等
"""
from datetime import datetime, timedelta

def calc_deadline(start_date, deadline_type):
    """
    计算诉讼期限
    :param start_date: 起始日期 (datetime.date 或 str 'YYYY-MM-DD')
    :param deadline_type: 期限类型 ('appeal'上诉期15日, 'evidence'举证期15日, 'lawsuit'诉讼时效3年)
    :return: 期限截止日期 (datetime.date)
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if deadline_type == 'appeal':
        # 上诉期15日
        deadline = start_date + timedelta(days=15)
    elif deadline_type == 'evidence':
        # 举证期15日
        deadline = start_date + timedelta(days=15)
    elif deadline_type == 'lawsuit':
        # 诉讼时效3年
        deadline = start_date + timedelta(days=365*3)
    else:
        raise ValueError(f'不支持的期限类型: {deadline_type}')
    
    return deadline

def days_remaining(deadline_date):
    """
    计算剩余天数
    :param deadline_date: 截止日期
    :return: 剩余天数 (int, 负数表示已超期)
    """
    if isinstance(deadline_date, str):
        deadline_date = datetime.strptime(deadline_date, '%Y-%m-%d').date()
    
    today = datetime.now().date()
    return (deadline_date - today).days

def format_deadline_info(start_date, deadline_type):
    """
    格式化期限信息
    :return: dict {'start_date', 'deadline_date', 'days_remaining', 'status'}
    """
    deadline_date = calc_deadline(start_date, deadline_type)
    remaining = days_remaining(deadline_date)
    
    if remaining < 0:
        status = '已超期'
    elif remaining <= 3:
        status = '即将到期'
    else:
        status = '正常'
    
    return {
        'start_date': start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime.date) else start_date,
        'deadline_date': deadline_date.strftime('%Y-%m-%d'),
        'days_remaining': remaining,
        'status': status
    }
