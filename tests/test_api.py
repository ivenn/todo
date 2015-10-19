import unittest
import json
from flask import url_for
from base64 import b64encode
from app import create_app, db


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
        return {'Authorization': username + ':' + password,
                'Accept': 'application/json',
                'Content-Type': 'application/json'}

    def test_token_auth(self):
        # add user
        from app.models import User
        User.add_user(User(username='test',
                           password='test',
                           is_admin=False,
                           email='test@test.com',
                           confirmed=True))

        # request without token
        #response = self.client.get(url_for('api_1.test'),
        #                           headers=self.get_api_headers('bad-token', ''))
        #print response.status_code

        response = self.client.get(url_for('api_1.get_token'), 
                                   data=json.dumps({'username':'test', 'password':'test'}),
                                   content_type='application/json')
        print response
        json_response = json.loads(response.data)
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

