from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import bancoApi
from django.core.files.uploadedfile import SimpleUploadedFile


class UploadViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.upload_url = reverse('upload')
        self.valid_file_content = "0000000070                              Palmer Prosacco00000007530000000003     1836.7420210308\n"
        
    def test_uploadTest(self):
        file = SimpleUploadedFile("data.txt", self.valid_file_content.encode('utf-8'), content_type="text/plain")
        response = self.client.post(self.upload_url, {'file': file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        #verifica banco
        self.assertTrue(bancoApi.objects.exists())
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        
        #verificacao dos dados
        self.assertEqual(len(data), 1)
        user_data = data[0]
        self.assertEqual(user_data['user_id'], 70)
        self.assertEqual(user_data['name'], 'Palmer Prosacco')
        self.assertEqual(len(user_data['orders']), 1)
        
        order = user_data['orders'][0]
        self.assertEqual(order['order_id'], 753)
        self.assertEqual(order['total'], '1836.74')
        self.assertEqual(order['date'], '2021-03-08')
        self.assertEqual(len(order['products']), 1)
        
        product = order['products'][0]
        self.assertEqual(product['product_id'], 3)
        self.assertEqual(product['value'], '1836.74')

    def test_uploadNoFileTest(self):
        response = self.client.post(self.upload_url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'mensagem': 'Nenhum arquivo localizado'})

    def test_allViewTest(self):
        file = SimpleUploadedFile("data.txt", self.valid_file_content.encode('utf-8'), content_type="text/plain")
        self.client.post(self.upload_url, {'file': file}, format='multipart')

        all_url = reverse('all')
        response = self.client.get(all_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_id'], 70)

    def test_orderViewTest(self):
        file = SimpleUploadedFile("data.txt", self.valid_file_content.encode('utf-8'), content_type="text/plain")
        self.client.post(self.upload_url, {'file': file}, format='multipart')

        order_url = reverse('order', kwargs={'order_id': 753})
        response = self.client.get(order_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['orders'][0]['order_id'], 753)
        self.assertEqual(data['orders'][0]['total'], '1836.74')

    def test_orderNoOrderTest(self):
        order_url = reverse('order', kwargs={'order_id': 999})
        response = self.client.get(order_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_dateViewTest(self):
        file = SimpleUploadedFile("data.txt", self.valid_file_content.encode('utf-8'), content_type="text/plain")
        self.client.post(self.upload_url, {'file': file}, format='multipart')

        date_url = reverse('date') + '?start_date=20210301&end_date=20210308'
        response = self.client.get(date_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_id'], 70)
        self.assertEqual(data[0]['orders'][0]['date'], '2021-03-08')

    def test_dateNoParamsTest(self):
        date_url = reverse('date')
        response = self.client.get(date_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'periodo de data não informado'})
