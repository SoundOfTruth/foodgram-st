import os

from django.contrib.auth import get_user_model
from django.core.management import call_command


if os.getenv('LOAD_TEST_DATA', 'true').lower() == 'true':
    User = get_user_model()
    is_empty = User.objects.count() == 0

    if is_empty:
        test_user = User(
            email='test@test.test', username='test', first_name='test', last_name='test'
        )

        test_user.set_password('passfortest')
        test_user.save()

        admin_user = User(
            email='admin@admin.admin',
            username='admin',
            first_name='admin',
            last_name='admin',
            is_staff=True,
            is_superuser=True,
        )

        admin_user.set_password('passfortest')
        admin_user.save()
        print('Users inserted')

        call_command('loaddata', 'data/recipes.json')

        print('Recipes inserted')
    else:
        print('The table is not empty')
