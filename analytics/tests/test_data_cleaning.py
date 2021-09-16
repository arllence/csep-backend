from django.test import TestCase, Client
from django.urls import reverse, resolve
import json
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase


class FileTransferTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_file_copier(self):
        url = reverse('data-cleaning-file-transfer')
        payload = {}
        app_response = self.client.post(url, data=payload)
        self.assertEqual(app_response.status_code, 200)


# python manage.py test --keepdb analytics.tests.test_data_cleaning.FileTransferTest.test_file_copier
