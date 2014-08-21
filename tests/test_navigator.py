#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sqlalchemy
import unittest

from flask import json
from navigator.app import create_app


def _batch_sql(engine, statements):
    conn = engine.connect()
    for statement in statements:
        conn.execute('COMMIT')
        conn.execute(statement)
    conn.close()


class NavigatorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = create_app(__name__)
        if not app.config['TESTING']:
            raise Exception('Not in Testing context')
        engine = sqlalchemy.create_engine(app.config['MASTER_DATABASE_URI'])
        statements = [
            'DROP DATABASE IF EXISTS {}'.format(app.config['TEST_DATABASE_NAME']),
            'CREATE DATABASE {}'.format(app.config['TEST_DATABASE_NAME']),
        ]
        _batch_sql(engine, statements)
        engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        statements = [
            'CREATE TABLE test (id integer PRIMARY KEY, value integer)',
            'INSERT INTO test SELECT generate_series(1, 100), ROUND(random() * 10)',
        ]
        _batch_sql(engine, statements)

    # TODO: dandling connections prevents dropping test database
    # @classmethod
    # def tearDownClass(cls):
    #     app = create_app(__name__)
    #     engine = sqlalchemy.create_engine(app.config['MASTER_DATABASE_URI'])
    #     statements = ['DROP DATABASE IF EXISTS {}'.format(app.config['TEST_DATABASE_NAME'])]
    #     _batch_sql(engine, statements)

    def setUp(self):
        app = create_app(__name__)
        self.client = app.test_client()

    def tearDown(self):
        self.client = None

    def test_schema(self):
        response = self.client.get('/schemas/', content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('public', response.data)

    def test_tables(self):
        response = self.client.get('/schemas/public/tables', content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('test', response.data)

    def test_table(self):
        response = self.client.get('/schemas/public/tables/test', content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('test', response.data)

    def test_table_stats(self):
        response = self.client.post('/schemas/public/tables/test/stats', content_type='application/json')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/schemas/public/tables/test/stats', content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('test', response.data)

    def test_table_column_stats(self):
        response = self.client.post('/schemas/public/tables/test/columns/id/stats', content_type='application/json')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/schemas/public/tables/test/columns/id/stats', content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('test', response.data)

if __name__ == '__main__':
    unittest.run()
