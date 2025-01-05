from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Article, Tag

class ArticleTests(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = get_user_model().objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        # 테스트를 위한 로그인
        self.client.force_authenticate(user=self.user)
        
        # 테스트용 태그 생성
        self.tag = Tag.objects.create(name='웨딩')

    def test_create_article(self):
        # 테스트용 이미지 파일 생성 (선택사항)
        # image = SimpleUploadedFile(
        #     name='test_image.jpg',
        #     content=b'',  # 빈 이미지
        #     content_type='image/jpeg'
        # )

        data = {
            'title': '테스트 게시물',
            'content': '테스트 내용입니다.',
            'is_public': True,
            'tags': [self.tag.id],
            # 'image': image,  # 이미지는 선택사항
        }
        response = self.client.post('/api/articles/', data, format='json')
        print("Response Data:", response.data)  # 디버깅용
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(Article.objects.get().title, '테스트 게시물')

    def test_get_article_list(self):
        # 게시물 목록 조회 테스트
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)

    def test_update_article(self):
        # 게시물 수정 테스트
        article = Article.objects.create(
            author=self.user,
            title='원본 제목',
            content='원본 내용'
        )
        data = {'title': '수정된 제목', 'content': '수정된 내용'}
        response = self.client.patch(
            f'/api/articles/{article.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.get().title, '수정된 제목')
