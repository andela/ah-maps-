import factory
from faker import Factory
from django.contrib.auth import get_user_model

faker = Factory.create()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = faker.first_name()
    email = faker.email()
    password = factory.PostGenerationMethodCall('set_password', '1234abcd')
    is_activated = True