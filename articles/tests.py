from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Article, Tag, Comment
from django.urls import reverse

class ArticleTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 테스트용 태그들 생성
        self.tag1 = Tag.objects.create(name='웨딩')
        self.tag2 = Tag.objects.create(name='스냅')
        
        # 테스트용 게시물 생성
        self.article = Article.objects.create(
            author=self.user,
            title='테스트 게시물',
            content='테스트 내용'
        )
        self.article.tags.add(self.tag1)

    def test_create_article(self):
        data = {
            'title': '새 게시물',
            'content': '새로운 내용입니다.',
            'is_public': True,
            'tags': [self.tag1.id, self.tag2.id]
        }
        response = self.client.post('/api/articles/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(response.data['tags'], [self.tag1.id, self.tag2.id])

    def test_get_article_list(self):
        # 게시물 목록 조회 테스트
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)  # 페이지네이션 적용
        self.assertIn('likes_count', response.data['results'][0])
        self.assertIn('comments_count', response.data['results'][0])
        self.assertNotIn('comments', response.data['results'][0])  # 목록에서는 댓글 제외

    def test_get_article_detail(self):
        # 댓글 추가
        Comment.objects.create(
            article=self.article,
            author=self.user,
            content='테스트 댓글'
        )
        
        # 상세 조회 테스트
        response = self.client.get(f'/api/articles/{self.article.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.data)
        self.assertEqual(len(response.data['comments']), 1)

    def test_filter_articles(self):
        # 필터링 테스트
        response = self.client.get(f'/api/articles/?tags={self.tag1.name}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get('/api/articles/?tags=없는태그')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_search_articles(self):
        # 검색 테스트
        response = self.client.get('/api/articles/?search=테스트')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get('/api/articles/?search=없는내용')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_like_article(self):
        # 좋아요 테스트
        response = self.client.post(f'/api/articles/{self.article.id}/like/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.likes.count(), 1)

        # 좋아요 취소 테스트
        response = self.client.post(f'/api/articles/{self.article.id}/like/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.likes.count(), 0)

    def test_update_article(self):
        # 게시물 수정 테스트
        data = {
            'title': '수정된 제목',
            'content': '수정된 내용',
            'tags': [self.tag2.id]
        }
        response = self.client.patch(
            f'/api/articles/{self.article.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], '수정된 제목')
        self.assertEqual(response.data['tags'], [self.tag2.id])
