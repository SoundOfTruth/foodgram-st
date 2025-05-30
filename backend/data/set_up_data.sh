python manage.py shell -c "exec(open('data/create_users.py').read())"
python manage.py loaddata data/recipes.json