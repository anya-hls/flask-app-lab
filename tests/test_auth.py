import unittest

from app import create_app, db
from app.users.models import User


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_user(self, username='anna_halas', email='anna@gmail.com', password='123456'):
        with self.app.app_context():
            user = User(
                username=username,
                email=email,
                password=User.hash_password(password)
            )
            db.session.add(user)
            db.session.commit()

    def register(self, username='anna_halas', email='anna@gmail.com', password='123456', confirm='123456'):
        return self.client.post(
            '/users/register',
            data={
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': confirm,
                'submit': 'Зареєструватися'
            },
            follow_redirects=True
        )

    def login(self, email='anna@gmail.com', password='123456'):
        return self.client.post(
            '/users/login',
            data={
                'email': email,
                'password': password,
                'submit': 'Увійти'
            },
            follow_redirects=True
        )

    def test_register_page_loads(self):
        response = self.client.get('/users/register')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Реєстрація'.encode(), response.data)

    def test_login_page_loads(self):
        response = self.client.get('/users/login')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Вхід'.encode(), response.data)

    def test_register_saves_user_with_hashed_password(self):
        response = self.register()

        self.assertEqual(response.status_code, 200)
        self.assertIn('створено'.encode(), response.data)

        with self.app.app_context():
            user = db.session.scalar(db.select(User).where(User.email == 'anna@gmail.com'))
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'anna_halas')
            self.assertNotEqual(user.password, '123456')
            self.assertTrue(user.check_password('123456'))
            self.assertFalse(user.check_password('wrong'))

    def test_register_duplicate_email(self):
        self.create_user()

        response = self.register(username='other_user')

        self.assertIn('уже існує'.encode(), response.data)

        with self.app.app_context():
            count = len(db.session.scalars(db.select(User)).all())
            self.assertEqual(count, 1)

    def test_register_duplicate_username(self):
        self.create_user()

        response = self.register(email='other@gmail.com')

        self.assertIn('уже існує'.encode(), response.data)

    def test_register_password_mismatch(self):
        response = self.register(confirm='654321')

        self.assertIn('Паролі не збігаються'.encode(), response.data)

        with self.app.app_context():
            self.assertEqual(len(db.session.scalars(db.select(User)).all()), 0)

    def test_login_success(self):
        self.create_user()

        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Вітаємо, anna_halas'.encode(), response.data)
        self.assertIn('anna@gmail.com'.encode(), response.data)

    def test_login_wrong_password(self):
        self.create_user()

        response = self.login(password='wrong_password')

        self.assertIn('Неправильний email або пароль'.encode(), response.data)

    def test_logout(self):
        self.create_user()
        self.login()

        response = self.client.get('/users/logout', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Ви вийшли із системи'.encode(), response.data)

        protected = self.client.get('/users/account')
        self.assertEqual(protected.status_code, 302)
        self.assertIn('/users/login', protected.headers['Location'])

    def test_account_requires_login(self):
        response = self.client.get('/users/account')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login', response.headers['Location'])

    def test_users_list_requires_login(self):
        response = self.client.get('/users/list')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login', response.headers['Location'])

    def test_users_list_for_authenticated(self):
        self.create_user()
        self.login()

        response = self.client.get('/users/list')

        self.assertEqual(response.status_code, 200)
        self.assertIn('anna_halas'.encode(), response.data)

    def test_authenticated_user_redirected_from_register(self):
        self.create_user()
        self.login()

        response = self.client.get('/users/register')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/account', response.headers['Location'])


if __name__ == '__main__':
    unittest.main()
    