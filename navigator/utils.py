#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import sqlalchemy

from flask import render_template, request


class SQLTypeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, sqlalchemy.sql.sqltypes.NullType):
            return 'NULL'
        if isinstance(obj, sqlalchemy.types.TypeEngine):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def make_response(context, template=None):
    if request.is_json or request.is_xhr:
        return json.dumps(context, cls=SQLTypeEncoder)
    if template:
        return render_template(template, **context)
