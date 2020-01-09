import inspect
import warnings

from sqlalchemy import bindparam
from sqlalchemy.ext import baked
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.sql.expression import desc
from sqlalchemy import Boolean, Table, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import cast
from sqlalchemy import Unicode

from flask_admin.contrib.sqla import form, filters as sqla_filters, tools


class ModelViewWithBakedQueryMixin:

    bakery = baked.bakery()

    def _apply_path_joins(self, query, joins, path, inner_join=True):
        """
            Apply join path to the query.

            :param query:
                Query to add joins to
            :param joins:
                List of current joins. Used to avoid joining on same relationship more than once
            :param path:
                Path to be joined
            :param fn:
                Join function
        """
        last = None

        if path:
            for item in path:
                key = (inner_join, item)
                alias = joins.get(key)

                if key not in joins:
                    if not isinstance(item, Table):
                        alias = aliased(item.property.mapper.class_)

                    fn = query.join if inner_join else query.outerjoin

                    if last is None:
                        query = fn(item) if alias is None else fn(alias, item)
                    else:
                        prop = getattr(last, item.key)
                        query = fn(prop) if alias is None else fn(alias, prop)

                    joins[key] = alias

                last = alias

        return query, joins, last

    def _order_by(self, query, joins, sort_joins, sort_field, sort_desc):
        """
            Apply order_by to the query

            :param query:
                Query
            :pram joins:
                Current joins
            :param sort_joins:
                Sort joins (properties or tables)
            :param sort_field:
                Sort field
            :param sort_desc:
                Ascending or descending
        """
        if sort_field is not None:
            # Handle joins
            query, joins, alias = self._apply_path_joins(
                query, joins, sort_joins, inner_join=False)

            column = sort_field if alias is None else getattr(
                alias, sort_field.key)

            # if sort_desc:
            #     query += lambda q: q.order_by(desc(column))
            # else:
            #     query += lambda q: q.order_by(column)

            if sort_desc:
                query += lambda q: q.order_by(desc(bindparam('order_by')))
            else:
                query += lambda q: q.order_by(bindparam('order_by'))
            self.bakery_query_params['order_by'] = column.name

        return query, joins

    def _apply_filters(self, query, count_query, joins, count_joins, filters):
        for idx, flt_name, value in filters:
            flt = self._filters[idx]

            alias = None
            count_alias = None

            # Figure out joins
            if isinstance(flt, sqla_filters.BaseSQLAFilter):
                # If no key_name is specified, use filter column as filter key
                filter_key = flt.key_name or flt.column
                path = self._filter_joins.get(filter_key, [])

                query, joins, alias = self._apply_path_joins(
                    query, joins, path, inner_join=False)

                if count_query is not None:
                    count_query, count_joins, count_alias = self._apply_path_joins(
                        count_query, count_joins, path, inner_join=False)

            # Clean value .clean() and apply the filter
            clean_value = flt.clean(value)

            try:
                query = flt.apply(query, clean_value, alias)
            except TypeError:
                spec = inspect.getargspec(flt.apply)

                if len(spec.args) == 3:
                    warnings.warn('Please update your custom filter %s to '
                                  'include additional `alias` parameter.' % repr(flt))
                else:
                    raise

                query = flt.apply(query, clean_value)

            if count_query is not None:
                try:
                    count_query = flt.apply(
                        count_query, clean_value, count_alias)
                except TypeError:
                    count_query = flt.apply(count_query, clean_value)

        return query, count_query, joins, count_joins

    def _apply_search(self, query, count_query, joins, count_joins, search):
        """
            Apply search to a query.
        """
        terms = search.split(' ')

        for term in terms:
            if not term:
                continue

            stmt = tools.parse_like_term(term)

            filter_stmt = []
            count_filter_stmt = []

            for field, path in self._search_fields:
                query, joins, alias = self._apply_path_joins(
                    query, joins, path, inner_join=False)

                count_alias = None

                if count_query is not None:
                    count_query, count_joins, count_alias = self._apply_path_joins(
                        count_query, count_joins, path, inner_join=False)

                column = field if alias is None else getattr(alias, field.key)
                filter_stmt.append(
                    cast(column, Unicode).ilike(stmt))  # 使用ilike进行检索

                if count_filter_stmt is not None:
                    column = field if count_alias is None else getattr(
                        count_alias, field.key)
                    count_filter_stmt.append(cast(column, Unicode).ilike(stmt))

            query += lambda q: q.filter(or_(*filter_stmt))  # “或”查询

            if count_query is not None:
                count_query += lambda q: q.filter(or_(*count_filter_stmt))

        return query, count_query, joins, count_joins

    def _apply_pagination(self, query, page, page_size):
        if page_size is None:
            page_size = self.page_size

        if page_size:
            query += lambda q: q.limit(bindparam('page_size'))
            self.bakery_query_params['page_size'] = page_size

        if page and page_size:
            # query += lambda q: q.offset(page * page_size)
            query += lambda q: q.offset(bindparam('offset'))
            self.bakery_query_params['offset'] = page * page_size

        return query

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None):
        """
            Return records from the database.

            :param page:
                Page number
            :param sort_column:
                Sort column name
            :param sort_desc:
                Descending or ascending sort
            :param search:
                Search query
            :param execute:
                Execute query immediately? Default is `True`
            :param filters:
                List of filter tuples
            :param page_size:
                Number of results. Defaults to ModelView's page_size. Can be
                overriden to change the page_size limit. Removing the page_size
                limit requires setting page_size to 0 or False.
        """

        # Will contain join paths with optional aliased object
        joins = {}
        count_joins = {}

        query = self.get_query()
        count_query = self.get_count_query() if not self.simple_list_pager else None

        # Ignore eager-loaded relations (prevent unnecessary joins)
        # TODO: Separate join detection for query and count query?
        # eager-loading: https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#eager-loading
        if hasattr(query, '_join_entities'):
            for entity in query._join_entities:
                for table in entity.tables:
                    joins[table] = None

        # Apply search criteria
        if self._search_supported and search:
            query, count_query, joins, count_joins = self._apply_search(
                query, count_query, joins, count_joins, search)

        # Apply filters
        if filters and self._filters:
            query, count_query, joins, count_joins = self._apply_filters(
                query, count_query, joins, count_joins, filters)

        # Calculate number of rows if necessary
        count = count_query(self.session()).scalar() if count_query else None

        # Auto join
        for j in self._auto_joins:
            # joinedload: https://docs.sqlalchemy.org/en/13/orm/loading_relationships.html#sqlalchemy.orm.joinedload
            query += lambda q: q.options(joinedload(j))

        # Sorting
        query, joins = self._apply_sorting(
            query, joins, sort_column, sort_desc)

        # Pagination
        query = self._apply_pagination(query, page, page_size)

        # Execute if needed
        if execute:
            query = query(self.session()).params(
                **self.bakery_query_params
            ).all()

        return count, query

    def get_one(self, id):
        """override"""
        return super().get_one(id)
        # TODO:
        # q = self.bakery(lambda s: s.query(self.model))
        # q += lambda q: q.filter(self.model.id == bindparam("id"))
        # return q(self.session()).params(id=id).one()

    def get_query(self):
        """override"""
        # return super().get_query()
        q = self.bakery(lambda s: s.query(self.model))
        self.bakery_query_params = {}
        return q

    def get_count_query(self):
        """override"""
        # return super().get_count_query()
        q = self.bakery(lambda s: s.query(
            func.count('*')).select_from(self.model))
        return q


def with_baked_query(Class):
    for attr_name in ModelViewWithBakedQueryMixin.__dict__:
        if attr_name.startswith('__'):
            continue
        setattr(Class, attr_name,
                getattr(ModelViewWithBakedQueryMixin, attr_name))
    return Class
