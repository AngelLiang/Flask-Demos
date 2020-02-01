import datetime

from sqlalchemy import func, extract

from app.extensions import db


def get_past_Monday(past=1):
    """获取过去 past 的星期一的日期"""
    today = datetime.date.today()
    days = today.weekday() + past * 7
    return today - datetime.timedelta(days=days)


def get_stats_by_week(datetime_column, past=1, autofill=True):
    """
    :param datetime_column: ORM Column
    :param past: int, 过去的周数
    :param autofill: bool, 是否自动填充未来的数据
    """
    the_Monday = get_past_Monday(past)
    stats = db.session.query(
        datetime_column, func.count('*')
    ).filter(
        # 筛选大于等于某星期一，小于下星期一
        the_Monday <= datetime_column,
        datetime_column < the_Monday+datetime.timedelta(days=7)
    ).group_by(
        extract('day', datetime_column)
    ).all()

    # 如果达不到七天，应该填充剩下的数据
    if autofill:
        while len(stats) < 7:
            stats.append((stats[-1][0]+datetime.timedelta(days=1), 0))

    return stats
