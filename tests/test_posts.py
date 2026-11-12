import unittest

from app import create_app, db
from app.posts.models import Post


class PostsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_post(self, title='Тестовий допис', is_active=True):
        with self.app.app_context():
            post = Post(
                title=title,
                content='Текст тестового допису',
                category='news',
                is_active=is_active,
                author='Test User'
            )
            db.session.add(post)
            db.session.commit()
            return post.id

    def test_post_list(self):
        self.create_post()

        response = self.client.get('/post')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Тестовий допис'.encode(), response.data)

    def test_create_post(self):
        response = self.client.post(
            '/post/create',
            data={
                'title': 'Новий допис',
                'content': 'Текст нового допису',
                'publish_date': '2026-11-12T10:30',
                'category': 'news',
                'is_active': 'y',
                'submit': 'Зберегти'
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Новий допис'.encode(), response.data)

        with self.app.app_context():
            post = Post.query.filter_by(title='Новий допис').first()
            self.assertIsNotNone(post)

    def test_post_detail(self):
        post_id = self.create_post()

        response = self.client.get(f'/post/{post_id}')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Тестовий допис'.encode(), response.data)
        self.assertIn('Текст тестового допису'.encode(), response.data)

    def test_update_post(self):
        post_id = self.create_post()

        response = self.client.post(
            f'/post/{post_id}/update',
            data={
                'title': 'Оновлений допис',
                'content': 'Оновлений текст',
                'publish_date': '2026-11-12T12:00',
                'category': 'tech',
                'is_active': 'y',
                'submit': 'Зберегти'
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Оновлений допис'.encode(), response.data)

        with self.app.app_context():
            post = db.session.get(Post, post_id)
            self.assertEqual(post.title, 'Оновлений допис')
            self.assertEqual(post.category, 'tech')

    def test_delete_post(self):
        post_id = self.create_post()

        response = self.client.post(
            f'/post/{post_id}/delete',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Допис успішно видалено!'.encode(), response.data)

        with self.app.app_context():
            post = db.session.get(Post, post_id)
            self.assertIsNone(post)

    def test_post_not_found(self):
        response = self.client.get('/post/999')

        self.assertEqual(response.status_code, 404)

    def test_inactive_post_not_in_list(self):
        self.create_post(title='Неактивний допис', is_active=False)

        response = self.client.get('/post')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Неактивний допис'.encode(), response.data)


if __name__ == '__main__':
    unittest.main()
