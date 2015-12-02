import unittest
import json
from flask import url_for
from base64 import b64encode
from app import create_app, db, cache


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('test')

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
                'Accept': 'application/json',
                'Content-Type': 'application/json'
               }

    def test_token_auth(self):
        # add user
        from app.models import User
        username = 'test'
        password = 'test123'

        User.add_user(User(username=username,
                           password=password,
                           is_admin=False,
                           email='test@test.com',
                           confirmed=True))

        # request without token
        response = self.client.get(url_for('api_1.echo'),
                                   headers=self.get_api_headers('bad-token', ''))
        self.assertEqual(response.status_code, 401)

        # get token
        response = self.client.post(url_for('api_1.login'),
                                   data=json.dumps({'username': username, 'password': password}),
                                   content_type='application/json')
        json_response = json.loads(response.data)

        token = json_response['auth_token']
        self.assertIsNotNone(token)
        self.assertIsNotNone(response.headers[2])
        self.assertEqual(cache.get(json_response['auth_token']),
                         User.query.filter_by(username=username).first().id)

        # request with correct token
        response = self.client.get(url_for('api_1.echo'),
                                   headers=self.get_api_headers(token, ''),
                                   data=json.dumps({'data': 'echo test'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['data'], 'echo test')
