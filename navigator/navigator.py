#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import sqlalchemy

from collections import OrderedDict
from flask import Blueprint, render_template, request, url_for
from itertools import chain

from .models import db, PGStats
from .utils import make_response

navigator = Blueprint('navigator', __name__)

inspector = None

@navigator.before_app_first_request
def _setup():
    global inspector
    inspector = db.inspect(db.engine)


def _search(q):
    def _table_match(table, schema):
        url = url_for('.table', schema=schema, table=table, _external=True)
        return {'type': 'table', 'title': '.'.join([schema, table]), 'url': url}
    schemas = inspector.get_schema_names()
    matches = []
    for schema in schemas:
        tables = inspector.get_table_names(schema=schema)
        if q in schema.lower():
            url = url_for('.tables', schema=schema, _external=True)
            matches.append({'type': 'schema', 'title': schema, 'url': url})
            matches.extend([_table_match(table, schema) for table in tables])
            continue
        tables = [_table_match(table, schema) for table in tables if q in table.lower()]
        matches.extend(tables)
    return matches


@navigator.route('')
def index():
    if 'q' in request.args:
        matches = _search(request.args['q'].lower())
        return make_response({'matches': matches}, template='schemas/search.html')
    schemas = inspector.get_schema_names()
    context = {
        'schemas': sorted(schemas)
    }
    return make_response(context, template='schemas/index.html')


@navigator.route('/<schema>/tables')
def tables(schema):
    tables = inspector.get_table_names(schema=schema)
    context = OrderedDict([
        ('schema', schema),
        ('tables', sorted(tables))
    ])
    return make_response(context, template='schemas/tables.html')


@navigator.route('/<schema>/tables/<table>')
def table(schema, table):
    primary_keys = inspector.get_primary_keys(table, schema=schema)
    columns = inspector.get_columns(table, schema=schema)
    indexes = inspector.get_indexes(table, schema=schema)
    indexed_columns = set(chain(*[index['column_names'] for index in indexes]))

    for column in columns:
        name = column['name']
        column['primary_key'] = name in primary_keys
        column['indexed'] = name in indexed_columns

    context = OrderedDict([
        ('schema', schema),
        ('table', table),
        ('oid', inspector.get_table_oid(table, schema=schema)),
        ('columns', columns),
        ('primary_keys', primary_keys),
        ('foreign_keys', inspector.get_foreign_keys(table, schema=schema)),
        ('indexes', indexes),
    ])
    return make_response(context, template='schemas/table.html')


# TODO: Add indexes stats
@navigator.route('/<schema>/tables/<table>/stats')
def table_stats(schema, table):
    query = PGStats.query.filter(PGStats.schema == schema, PGStats.table == table)
    rows = query.all()
    context = OrderedDict([
        ('schema', schema),
        ('table', table),
        ('columns', [{'column': stats.to_dict()} for stats in rows])
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
    context = {
        'column': stats.to_dict()
    }
    return make_response(context, template='schemas/column_stats.html')


@navigator.route('/<schema>/tables/<table>/columns/<column>/stats', methods=['POST'])
def update_column_stats(schema, table, column):
    db.session.execute('ANALYZE {}.{} ({})'.format(schema, table, column))
    db.session.commit()
    return ''

