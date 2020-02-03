"""
"""
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract


ONE_DAY = 1
EMPTY_DATA = None
MIN_MONTH = 1
MAX_MONTH = 12


def get_today():
    return datetime.date.today()


def get_day(days=0):
    return datetime.date.today() + datetime.timedelta(days=days)


def get_month():
    return datetime.date.today().month


def get_year():
    return datetime.date.today().year


def get_first_day_by_week(weeks=0):
    """获取某周的星期一的日期

    :param weeks: int, 负数表示过去的周数，正数表示未来的
    """
    today = get_today()
    days = today.weekday() - weeks * 7
    return today - datetime.timedelta(days=days)


def get_first_day_and_last_day_by_month(months=0):
    """获取某月份的第一天的日期和最后一天的日期

    :param months: int, 负数表示过去的月数，正数表示未来的

    :return tuple: (某月第一天日期, 某月最后一天日期)
    """
    day = get_today() + relativedelta(months=months)
    year = day.year
    month = day.month

    # 获取某年某月的第一天的星期和该月总天数
    _, month_range = calendar.monthrange(year, month)

    first = datetime.date(year=year, month=month, day=1)
    last = datetime.date(year=year, month=month, day=month_range)

    return first, last


def get_stats_by_days(session, datetime_column, days, autofill=True):
    """获取天统计数据

    :param session: db.sessoin
    :param datetime_column: ORM Column
    :param days: int, 用负数表示过去的天数
    :param autofill: bool, 是否自动填充没有的数据
    """
    today = get_today()
    stats = session.query(
        datetime_column, func.count('*')
    ).filter(
        # 筛选过去 days 天的数据
        get_day(days) < datetime_column,
        datetime_column <= today
    ).group_by(
        extract('day', datetime_column)
    ).all()

    # 如果达不到当天日期，应该填充剩下的数据
    if autofill:
        if not stats:
            stats.append((today, EMPTY_DATA))
        while stats[-1][0].date() < today:
            stats.append(
                (stats[-1][0]+datetime.timedelta(days=ONE_DAY), EMPTY_DATA))

    return stats


def get_stats_by_week(session, datetime_column, weeks, autofill=True):
    """获取周统计数据

    :param session: db.sessoin
    :param datetime_column: ORM Column
    :param weeks: int, 用负数表示过去的周数
    :param autofill: bool, 是否自动填充没有的数据
    """
    Monday = get_first_day_by_week(weeks)
    stats = session.query(
        datetime_column, func.count('*')
    ).filter(
        # 筛选大于等于某星期一，小于下星期一
        Monday <= datetime_column,
        datetime_column < Monday+datetime.timedelta(days=7)
    ).group_by(
        extract('day', datetime_column)
    ).all()

    # 如果达不到七天，应该填充剩下的数据
    if autofill:
        if not stats:
            stats.append((Monday, EMPTY_DATA))
        while len(stats) < 7:
            stats.append(
                (stats[-1][0]+datetime.timedelta(days=ONE_DAY), EMPTY_DATA))

    return stats


def get_stats_by_month(session, datetime_column, months, autofill=True):
    """获取月统计数据

    :param session: db.sessoin
    :param datetime_column: ORM Column
    :param months: int, 用负数表示过去的月数
    :param autofill: bool, 是否自动填充没有的数据
    """
    first_day, last_day = get_first_day_and_last_day_by_month(months)
    stats = session.query(
        datetime_column, func.count('*')
    ).filter(
        # 筛选当月
        first_day <= datetime_column,
        datetime_column <= last_day
    ).group_by(
        extract('day', datetime_column)
    ).all()

    if autofill:
        delta = last_day.day - first_day.day
        if not stats:
            stats.append((first_day, EMPTY_DATA))
        while len(stats) < delta:
            stats.append(
                (stats[-1][0]+datetime.timedelta(days=ONE_DAY), EMPTY_DATA))

    return stats


def get_stats_by_year(session, datetime_column, years, sep='month', autofill=True):
    """获取年统计数据

    :param session: db.sessoin
    :param datetime_column: ORM Column
    :param months: int, 用负数表示过去的年份
    :param autofill: bool, 是否自动填充没有的数据
    """

    year = get_year()+years

    first_day = datetime.date(year=year, month=1, day=1)
    last_day = datetime.date(year=year, month=12, day=31)

    stats = session.query(
        datetime_column, func.count('*')
    ).filter(
        first_day <= datetime_column, datetime_column <= last_day
    ).group_by(
        extract(sep, datetime_column)
    ).all()

    if autofill:
        pass

    return stats
