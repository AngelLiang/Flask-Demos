import datetime

from sqlalchemy import func, extract

from app.extensions import db


def get_past_Monday(past=1):
    """获取过去 past 的星期一的日期"""
    today = datetime.date.today()
    days = today.weekday() + past * 7
    return today - datetime.timedelta(days=days)


def get_stats_by_week(datetime_column, past=1, autofill=True):
    """获取上一周的统计数据

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


def get_stats_past_days(datetime_column, past=7, autofill=True):
    """获取过去 past 天数的统计数据

    :param datetime_column: ORM Column
    :param past: int, 过去的天数
    """
    today = datetime.date.today()
    stats = db.session.query(
        datetime_column, func.count('*')
    ).filter(
        # 筛选过去7天的数据
        today-datetime.timedelta(days=past) < datetime_column,
        datetime_column <= today
    ).group_by(
        extract('day', datetime_column)
    ).all()

    # 如果达不到当天日期，应该填充剩下的数据
    if autofill:
        while stats[-1][0].date() < today:
            stats.append((stats[-1][0]+datetime.timedelta(days=1), 0))

    return stats
