from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Factory
from ...factories import UserFactory
from ...factories.profile import ProfileFactory

faker = Factory.create()


class ProfileApiTest(TestCase):
    def setUp(self):
        self.profile = ProfileFactory()
        self.user2 = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile.user)

        self.namespace = 'profile_api'
        self.body = {
            'bio': faker.text()
        }
        self.retrieve_url = reverse(self.namespace + ':detail', kwargs={'user__username': self.profile.user.username})
        self.list_url = reverse(self.namespace + ':list')
        self.update_url = reverse(self.namespace + ':update', kwargs={'user__username': self.profile.user.username})
        self.update_url_use2 = reverse(self.namespace + ':update', kwargs={'user__username': self.user2.username})

    def test_list_profile_api(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, self.profile)

    def test_retrieve_single_profile_api(self):
        response = self.client.get(self.retrieve_url)
        self.assertContains(response, self.profile)

    def test_update_other_user_profile_api(self):
        response = self.client.put(self.update_url_use2, self.body)
        self.assertEqual(403, response.status_code)

    def test_update_own_profile_api(self):
        response = self.client.put(self.update_url, self.body)
        self.assertEqual(200, response.status_code)
