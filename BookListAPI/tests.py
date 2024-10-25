from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth.models import User, Group
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy

# Create your tests here.
sample_users = {
    'pooya':
        {'username': 'pooya', 'password': 'poy api', 'email': 'poy.ieie@gmail.com', },
    'ali':
        {'username': 'ali', 'email': 'ali.@gmail.com', 'password': 'ali api'},
}


class SecretTest(APITestCase):
    global sample_users
    
    def setUp(self):
        self.base_url = 'http://127.0.0.1:8000'
        self.login_url = reverse_lazy('login')
        self.secret_url = reverse_lazy('book-list-api:secret')
        self.client = APIClient()
        self.manager_group = Group.objects.create(name='manager')
        self.manager_user = User.objects.create_user(**sample_users['pooya'])
        self.manager_user.save()
        self.manager_user.groups.add(self.manager_group)

        self.non_manager_user = User.objects.create_user(**sample_users['ali'])
        self.non_manager_user.save()

    def __get_token(self, user_credentials) -> str:
        """ login user and return token """
        response = self.client.post(
            path=self.login_url,
            data=user_credentials,
        )
        response_data = response.data

        token = response_data['auth_token']
        return token

    def test_manager_request(self):
        token = self.__get_token(sample_users['pooya'])
        response = self.client.get(
            self.secret_url,
            headers={'Authorization': f'Token {token}'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['secret_message'], 'The secret of night')

    def test_non_manager_request(self):
        token = self.__get_token(sample_users['ali'])
        response = self.client.get(self.secret_url,
                                   headers={'Authorization': f'Token {token}'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response_data = response.json()
        self.assertEqual(response_data['secret_message'], 'You are not authorized')

    def test_ensure_json_is_default_content_type(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.headers['Content-Type'], 'application/json')