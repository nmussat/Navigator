#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import sqlalchemy

from .models import db, PGStats

from collections import OrderedDict
from flask import Blueprint, render_template, request

navigator = Blueprint('navigator', __name__)

inspector = None

@navigator.before_app_first_request
def _setup():
    global inspector
    inspector = db.inspect(db.engine)


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

