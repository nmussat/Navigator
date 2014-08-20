#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import TypeDecorator

db = SQLAlchemy()

class AnyArray(TypeDecorator):

    impl = db.TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not value:
            return '{}'
        return '{{"{}"}}'.format('","'.join(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, list):
            return value
        if not value:
            return []
        # TODO: Value should be Unicode already
        value = value.decode('utf-8')
        # TODO: Enhance field decoding (eg. core_user.created)
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

