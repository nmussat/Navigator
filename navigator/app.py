#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask

def register_blueprints(app):
    from .navigator import navigator
    app.register_blueprint(navigator, url_prefix='/schemas')
    from .query import query_manager
    app.register_blueprint(query_manager, url_prefix='/query_manager')

def register_extension(app):
    from .assets import assets
    assets.init_app(app)
    from .models import db
    db.init_app(app)

def create_app(name):
    app = Flask(name, template_folder='navigator/templates', static_folder='navigator/static')
    app.config.from_object('settings')
    app.config.from_envvar('APP_SETTINGS')
    register_extension(app)
    register_blueprints(app)
    return app
