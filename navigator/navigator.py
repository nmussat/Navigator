#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import sqlalchemy

from app import db
from collections import OrderedDict
from flask import Blueprint, render_template, request

from sqlalchemy.dialects import postgresql
from sqlalchemy.types import TypeDecorator

navigator = Blueprint('navigator', __name__)

inspector = None

@navigator.before_app_first_request
def _setup():
    global inspector
    inspector = db.inspect(db.engine)


class AnyArray(TypeDecorator):

    impl = db.TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not value:
            return '{}'
        return '{{"{}"}}'.format('","'.join(value))

    # TODO: Value should be Unicode already
    # TODO: Enhance field decoding (eg. core_user.created)
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, list):
            return value
        if not value:
            return []
        value = value.decode('utf-8')
        return value.strip('{}"').split(',')


# TODO: make the model read-only
class PGStats(db.Model):
    __tablename__ = 'pg_stats'

    schema = db.Column('schemaname', db.TEXT(), primary_key=True)
    table = db.Column('tablename', db.TEXT(), primary_key=True)
    column = db.Column('attname', db.TEXT(), primary_key=True)
    inherited = db.Column('inherited', db.BOOLEAN())
    null_frac = db.Column('null_frac', db.REAL())
    avg_width = db.Column('avg_width', db.INTEGER())
    n_distinct = db.Column('n_distinct', db.REAL())
    most_common_vals = db.Column('most_common_vals', AnyArray())
    most_common_freqs = db.Column('most_common_freqs', AnyArray())
    histogram_bounds = db.Column('histogram_bounds', AnyArray())
    correlation = db.Column('correlation', db.REAL())
    most_common_elems = db.Column('most_common_elems', AnyArray())
    most_common_elem_freqs = db.Column('most_common_elem_freqs', postgresql.ARRAY(db.REAL))
    elem_count_histogram = db.Column('elem_count_histogram', postgresql.ARRAY(db.REAL))

    def to_dict(self):
        result = OrderedDict()
        for key in self.__mapper__.columns.keys():
            result[key] = getattr(self, key)
        return result


class SQLTypeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, sqlalchemy.sql.sqltypes.NullType):
            return 'NULL'
        if isinstance(obj, sqlalchemy.types.TypeEngine):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def make_response(context, template=None):
    if request.is_json:
        return json.dumps(context, cls=SQLTypeEncoder)
    if template:
        return render_template(template, **context)


@navigator.route('/')
def schemas():
    context = {
        'schemas': inspector.get_schema_names()
    }
    return make_response(context, template='schemas/index.html')


@navigator.route('/<schema>/tables')
def tables(schema):
    context = OrderedDict([
        ('schema', schema),
        ('tables', inspector.get_table_names())
    ])
    return make_response(context, template='schemas/tables.html')


@navigator.route('/<schema>/tables/<table>')
def table(schema, table):
    context = OrderedDict([
        ('schema', schema),
        ('name', table),
        ('oid', inspector.get_table_oid(table, schema=schema)),
        ('columns', inspector.get_columns(table, schema=schema)),
        ('primary_keys', inspector.get_primary_keys(table, schema=schema)),
        ('foreign_keys', inspector.get_foreign_keys(table, schema=schema)),
        ('indexes', inspector.get_indexes(table, schema=schema)),
    ])
    return make_response(context, template='schemas/table.html')


# TODO: Add indexes stats
@navigator.route('/<schema>/tables/<table>/stats')
def table_stats(schema, table):
    query = PGStats.query.filter(PGStats.schema == schema, PGStats.table == table)
    rows = query.all()
    context = OrderedDict([
        ('schema', schema),
        ('tables', table),
        ('columns', [stats.to_dict() for stats in rows])
    ])
    return make_response(context, template='schemas/table_stats.html')


@navigator.route('/<schema>/tables/<table>/stats', methods=['POST'])
def update_table_stats(schema, table):
    db.session.execute('ANALYZE {}.{}'.format(schema, table))
    db.session.commit()
    return ''


@navigator.route('/<schema>/tables/<table>/columns/<column>/stats')
def column_stats(schema, table, column):
    query = PGStats.query.filter(PGStats.schema == schema,
                                 PGStats.table == table, PGStats.column == column)
    stats = query.first_or_404()
    return make_response(stats.to_dict(), template='schemas/column_stats.html')


@navigator.route('/<schema>/tables/<table>/columns/<column>/stats', methods=['POST'])
def update_column_stats(schema, table, column):
    db.session.execute('ANALYZE {}.{} ({})'.format(schema, table, column))
    db.session.commit()
    return ''

