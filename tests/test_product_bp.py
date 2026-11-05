import os
import tempfile
import unittest

from app import app
from app.products.database import initialize_database


class ProductBlueprintTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(
            self.temp_dir.name,
            'products.json'
        )

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['PRODUCTS_DB_PATH'] = self.db_path

        initialize_database(self.db_path)

        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_product_list(self):
        response = self.client.get('/products/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Laptop', response.data)
        self.assertIn(b'Phone', response.data)
        self.assertIn(b'PC', response.data)

    def test_product_detail(self):
        response = self.client.get('/products/1')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Laptop', response.data)
        self.assertIn(b'1200.00', response.data)

    def test_product_not_found(self):
        response = self.client.get('/products/999')

        self.assertEqual(response.status_code, 404)

    def test_add_product(self):
        response = self.client.post(
            '/products/add',
            data={
                'name': 'Tablet',
                'content': 'Планшет для роботи та навчання.',
                'price': '450.50',
                'category': 'electronics',
                'quantity': '7'
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tablet', response.data)

    def test_edit_product(self):
        response = self.client.post(
            '/products/1/edit',
            data={
                'name': 'Updated Laptop',
                'content': 'Оновлений опис ноутбука.',
                'price': '1500.00',
                'category': 'electronics',
                'quantity': '8'
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Laptop', response.data)

    def test_delete_product(self):
        response = self.client.post(
            '/products/1/delete',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Laptop', response.data)


if __name__ == '__main__':
    unittest.main()
    