import unittest
import json
from flask import url_for
from base64 import b64encode
from app import create_app, db, cache
from app.models import User


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
        print '='*100

    def get_api_headers(self, username, password):
        return {'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
                'Accept': 'application/json',
                'Content-Type': 'application/json'}

    def get_tmp_user(self):
        username = 'test'
        password = 'test123'

        User.add_user(User(username=username,
                           password=password,
                           is_admin=False,
                           email='test@test.com',
                           confirmed=True))

        return username, password

    def get_token(self, username, password):
        response = self.client.post(url_for('api_1.login'),
                                    data=json.dumps({'username': username,
                                                    'password': password}),
                                    content_type='application/json')
        return json.loads(response.data)['auth_token']

    def test_token_auth(self):
        username, password = self.get_tmp_user()

        # request without token
        response = self.client.get(url_for('api_1.echo'),
                                   headers=self.get_api_headers('bad-token', ''))
        self.assertEqual(response.status_code, 401)

        # get token
        response = self.client.post(url_for('api_1.login'),
                                    data=json.dumps({'username': username,
                                                    'password': password}),
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

    def test_list_crud(self):
        username, password = self.get_tmp_user()
        user = User.query.filter_by(username=username).first()
        token = self.get_token(username, password)

        # create
        tlist_name = 'testlist'
        tlist_desc = 'list desc'
        response = self.client.post(url_for('api_1.create_list', user_id=user.id),
                                    headers=self.get_api_headers(token, ''),
                                    data=json.dumps({'name': tlist_name,
                                                     'description': tlist_desc}))

        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(user.get_task_lists()), 1)
        tlist = user.get_task_lists()[0]
        self.assertEqual(tlist.name, tlist_name)
        self.assertEqual(tlist.description, tlist_desc)

        self.assertEqual(json.loads(response.data)['list'],
                         url_for('api_1.get_list', user_id=user.id, list_id=tlist.id))
        # get
        response = self.client.get(url_for('api_1.get_list',
                                           user_id=user.id,
                                           list_id=tlist.id),
                                   headers=self.get_api_headers(token, ''),
                                   data=json.dumps({}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual({'name': tlist_name, 'description': tlist_desc},
                         json.loads(response.data))
        # update
        mod_tlist_name = 'mod_testlist'
        mod_tlist_desc = 'mod list desc'
        response = self.client.put(url_for('api_1.update_list',
                                           user_id=user.id,
                                           list_id=tlist.id),
                                   headers=self.get_api_headers(token, ''),
                                   data=json.dumps({'name': mod_tlist_name,
                                                    'description': mod_tlist_desc}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['list'],
                         url_for('api_1.get_list', user_id=user.id, list_id=tlist.id))
        self.assertEqual(len(user.get_task_lists()), 1)
        tlist = user.get_task_lists()[0]
        self.assertEqual(tlist.name, mod_tlist_name)
        self.assertEqual(tlist.description, mod_tlist_desc)

        # get
        response = self.client.get(url_for('api_1.get_list',
                                           user_id=user.id,
                                           list_id=tlist.id),
                                   headers=self.get_api_headers(token, ''),
                                   data=json.dumps({}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual({'name': mod_tlist_name, 'description': mod_tlist_desc},
                         json.loads(response.data))

        # delete
        response = self.client.delete(url_for('api_1.delete_list',
                                              user_id=user.id,
                                              list_id=tlist.id),
                                      headers=self.get_api_headers(token, ''),
                                      data=json.dumps({'name': tlist_name}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(user.get_task_lists()), 0)
