#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, request
from .models import db
from .utils import make_response


query_manager = Blueprint('query_manager', __name__)


@query_manager.route('')
def index():
    query = request.args.get('query', '')
    context = {
        'query': query,
    }
    if query:
        rows = db.session.execute(query).fetchall()
        db.session.rollback()
        context['rows'] = rows
    return make_response(context, 'query_manager/index.html')
