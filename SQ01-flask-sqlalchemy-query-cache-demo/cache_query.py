# coding=utf-8

import logging
from sqlalchemy import event, func, inspect
from sqlalchemy.orm import Query, class_mapper
from sqlalchemy.orm.exc import UnmappedClassError

from app import cache, db

__all__ = ('CacheQueryMixin',)

CACHE_MODEL_PREFIX = 'db'

logger = logging.getLogger('cache_query')

GET_CACHE_TIMEOUT = 60 * 60 * 24
FF_CACHE_TIMEOUT = 60 * 2
COUNT_CACHE_TIMEOUT = 60 * 60 * 24
FC_CACHE_TIMEOUT = 60 * 5
ALL_CACHE_TIMEOUT = 60 * 5


def _get_primary_keys(target):
    return [key for key, column in inspect(target).columns.items() if column.primary_key]


def _unique_suffix(target, primary_key):
    pks = _get_primary_keys(target)
    return '-'.join(pks)


def _unique_key(target, primary_key):
    key = _unique_suffix(target, primary_key)
    return target.generate_cache_prefix('get') + key


def _itervalues(data, idents):
    for k in idents:
        item = data[str(k)]
        if item is not None:
            yield item

####################################################################
# 缓存数据的业务逻辑


def get_cache(key, *args, **kwargs):
    logger.debug('get cache for {}'.format(key))
    return cache.get(key, *args, **kwargs)


def get_cache_dict(*keys):
    return cache.get_dict(*keys)


def set_cache(key, value, timeout, *args, **kwargs):
    logger.debug('set cache for {}'.format(key))
    return cache.set(key, value, timeout)


def del_cache(key):
    logger.debug('delete cache for {}'.format(key))
    return cache.delete(key)


def inc_cache(key):
    logger.debug('increase cache for {}'.format(key))
    return cache.inc(key)


def delete_many(key, *args):
    logger.debug('delete many cache for {}'.format(key))
    return cache.delete_many(key, *args)


def set_cache_many(data, timeout):
    logger.debug('set many cache')
    return cache.set_many(data, timeout)

####################################################################


class CacheQuery(Query):

    def get(self, ident):
        """覆写 ``Query.get()`` 方法"""

        # 获取模型的mapper
        # 相当于 sqlalchemy.inspect(Model) 和 sqlalchemy.orm.class_mapper(Model)
        # 只不过 _only_full_mapper_zero('get') 是 Query 的私有方法
        mapper = self._only_full_mapper_zero('get')
        # mapper = class_mapper(self)

        # 生成后缀
        if isinstance(ident, (list, tuple)):
            # 多个主键，例如：get((5, 10))
            # https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.get
            suffix = '-'.join(map(str, ident))
        else:
            suffix = str(ident)

        key = mapper.class_.generate_cache_prefix('get') + suffix
        logger.debug('[get] key={}'.format(key))

        # rv = cache.get(key)
        rv = get_cache(key)
        if rv:
            logger.debug('[get] cache hit')
            return rv
        logger.debug('[get] cache missing')

        rv = super().get(ident)
        if rv is None:
            return None
        # 设置缓存
        # cache.set(key, rv, GET_CACHE_TIMEOUT)
        set_cache(key, rv, GET_CACHE_TIMEOUT)
        return rv

    def get_dict(self, idents):
        if not idents:
            return {}

        mapper = self._only_full_mapper_zero('get')
        if len(mapper.primary_key) != 1:
            raise NotImplementedError

        # 生成前缀
        prefix = mapper.class_.generate_cache_prefix('get')
        # 生成keys
        keys = {prefix + str(i) for i in idents}
        # 获取缓存数据
        # rv = cache.get_dict(*keys)
        rv = get_cache_dict(*keys)
        # 缓存数据是否命中
        missed = {i for i in idents if rv[prefix + str(i)] is None}

        rv = {k.lstrip(prefix): rv[k] for k in rv}
        # 全都命中则返回
        if not missed:
            return rv

        # 获取第一个主键
        pk = mapper.primary_key[0]
        # 主键 in_ 查询
        missing = self.filter(pk.in_(missed)).all()
        to_cache = {}
        for item in missing:
            ident = str(getattr(item, pk.name))
            to_cache[prefix + ident] = item
            rv[ident] = item

        # cache.set_many(to_cache, GET_CACHE_TIMEOUT)
        set_cache_many(to_cache, GET_CACHE_TIMEOUT)
        return rv

    def get_many(self, idents, clean=True):
        """根据id获取多个"""
        d = self.get_dict(idents)
        if clean:
            return list(_itervalues(d, idents))
        return [d[str(k)] for k in idents]

    def all(self, order_by=None):
        mapper = self._only_entity_zero()
        # 生成缓存 key 的前缀， 这里使用 mapper 之后就不再需要了
        key = mapper.class_.generate_cache_prefix('all')

        rv = get_cache(key)
        if rv is not None:
            return rv

        q = super()
        if order_by:
            q = q.order_by(order_by)
        rv = q.all()

        set_cache(key, rv, ALL_CACHE_TIMEOUT)
        return rv

    def filter_all(self, *args, order_by=None):
        mapper = self._only_entity_zero()

        # 生成缓存 key 的前缀， 这里使用 mapper 之后就不再需要了
        prefix = mapper.class_.generate_cache_prefix('all')
        key = prefix + '-'.join([str(arg) for arg in args])
        logger.debug('[ff] key={}'.format(key))

        rv = get_cache(key)
        if rv is not None:
            return rv

        q = super().filter(*args)
        if order_by:
            q = q.order_by(order_by)
        rv = q.all()

        set_cache(key, rv, ALL_CACHE_TIMEOUT)
        return rv

    def filter2_first(self, *args):
        mapper = self._only_entity_zero()
        # 生成缓存key的前缀， 这里使用 mapper 之后就不再需要了
        prefix = mapper.class_.generate_cache_prefix('ff')

        key = prefix + '-'.join([str(arg) for arg in args])
        logger.debug('[ff] key={}'.format(key))

        # 获取缓存
        rv = get_cache(key)
        # 缓存命中
        if rv:
            logger.debug('[ff] cache hit')
            return rv
        logger.debug('[ff] cache missing')
        # 缓存没命中
        rv = self.filter(*args).first()
        if rv is None:
            return None
        # 设置缓存
        # it is hard to invalidate this cache, expires in 2 minutes
        set_cache(key, rv, FF_CACHE_TIMEOUT)
        return rv

    def filter_first(self, *args, **kwargs):
        # mapper = self._only_mapper_zero()
        mapper = self._only_entity_zero()
        # 生成缓存key的前缀， 这里使用 mapper 之后就不再需要了
        prefix = mapper.class_.generate_cache_prefix('ff')

        # 缓存key
        key = prefix + '-'.join(['%s$%s' % (k, kwargs[k]) for k in kwargs])
        logger.debug('[ff] key={}'.format(key))
        # 获取缓存
        rv = get_cache(key)
        # 缓存命中
        if rv:
            logger.debug('[ff] cache hit')
            return rv
        logger.debug('[ff] cache missing')
        # 缓存没命中
        rv = self.filter_by(**kwargs).first()
        if rv is None:
            return None
        # 设置缓存
        # it is hard to invalidate this cache, expires in 2 minutes
        set_cache(key, rv, FF_CACHE_TIMEOUT)
        return rv

    def filter_count(self, **kwargs):
        # mapper = self._only_mapper_zero()
        mapper = self._only_entity_zero()
        model = mapper.class_  # 获取模型

        if not kwargs:
            key = model.generate_cache_prefix('count')
            # rv = cache.get(key)
            rv = get_cache(key)
            if rv is not None:
                return rv
            q = self.select_from(model).with_entities(func.count(1))
            rv = q.scalar()
            set_cache(key, rv, COUNT_CACHE_TIMEOUT)
            return rv

        # 生成前缀
        prefix = model.generate_cache_prefix('fc')
        # 生成缓存key
        key = prefix + '-'.join(['%s$%s' % (k, kwargs[k]) for k in kwargs])
        # 从缓存中获取数据
        rv = get_cache(key)
        # 缓存命中
        if rv:
            return rv
        # 缓存没命中，数据库查询
        q = self.select_from(model).with_entities(func.count(1))
        rv = q.filter_by(**kwargs).scalar()
        # 设置缓存
        set_cache(key, rv, FC_CACHE_TIMEOUT)
        return rv


class CacheProperty(object):
    """属性缓存

    Usage::

        class BaseModel(db.Model):
            __abstract__ = True
            cache = CacheProperty(db)  # cache query

    """

    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = class_mapper(type)
            if mapper:
                return CacheQuery(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None


class CacheQueryMixin(object):
    """缓存查询混入类

    Usage::

        class BaseModel(db.Model, CacheQueryMixin):
            __abstract__ = True

    """

    cache = CacheProperty(db)  # cache query

    @classmethod
    def generate_cache_prefix(cls, name):
        """生成缓存前缀

        :param name: str, 标识
        """

        # 拼接缓存前缀:  `db:<name>:<table_name>`
        prefix = '%s:%s:%s' % (CACHE_MODEL_PREFIX, name, cls.__tablename__)
        if hasattr(cls, '__cache_version__'):
            # example: `db:<name>:<table_name>|<__cache_version__>:`
            return '%s|%s:' % (prefix, cls.__cache_version__)
        # example: `db:<name>:<table_name>:`
        return '%s:' % prefix


@event.listens_for(CacheQueryMixin, 'after_insert')
def receive_after_insert_for_cache_query(mapper, conn, target):
    """注册Mapper事件，监听insert之后

    :param mapper:
    :param conn:
    :param target: 模型
    """
    logger.debug('after_insert {}'.format(target))
    inc_cache(target.generate_cache_prefix('count'))
    del_cache(target.generate_cache_prefix('all'))


@event.listens_for(CacheQueryMixin, 'after_update')
def receive_after_update_for_cache_query(mapper, conn, target):
    """注册Mapper事件，监听update之后

    :param mapper:
    :param conn:
    :param target: 模型
    """
    logger.debug('after_update {}'.format(target))

    key = _unique_key(target, mapper.primary_key)
    # 设置缓存
    # cache.set(key, target, GET_CACHE_TIMEOUT)
    # cls.cache.set_cache(key, target, GET_CACHE_TIMEOUT)
    # 删除缓存
    # CacheQueryMixin.cache.del_cache(key)
    del_cache(key)
    del_cache(target.generate_cache_prefix('all'))


@event.listens_for(CacheQueryMixin, 'after_delete')
def receive_after_delete_for_cache_query(mapper, conn, target):
    """注册Mapper事件，监听delete之后

    :param mapper:
    :param conn:
    :param target: 模型
    """
    logger.debug('after_delete {}'.format(target))

    key = _unique_key(target, mapper.primary_key)
    count = target.generate_cache_prefix('count')
    # 需要更新统计
    # cache.delete_many(key, target.generate_cache_prefix('count'))
    # CacheQueryMixin.cache.delete_many(key, target.generate_cache_prefix('count'))
    delete_many(key, count)
    del_cache(target.generate_cache_prefix('all'))
