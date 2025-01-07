from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import User

class AccountTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'nickname': 'testnick'
        }
        
    def test_register(self):
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_login(self):
        # 사용자 생성
        User.objects.create_user(**self.user_data)
        
        # 로그인
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_detail(self):
        # 사용자 생성 및 인증
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        # 사용자 정보 조회
        url = reverse('user-detail')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_delete_account(self):
        # 사용자 생성 및 인증
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        # 계정 삭제
        url = reverse('delete-account')
        response = self.client.delete(url, {
            'password': self.user_data['password']
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0) 

    def test_change_password(self):
        # 사용자 생성 및 인증
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        # 비밀번호 변경
        url = reverse('change-password')
        data = {
            'old_password': self.user_data['password'],
            'new_password': 'newpass123'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 새 비밀번호로 로그인 테스트
        login_url = reverse('token_obtain_pair')
        login_data = {
            'email': self.user_data['email'],
            'password': 'newpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)