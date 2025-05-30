python manage.py shell -c "exec(open('data/load_ingredients.py').read())"
python manage.py shell -c "exec(open('data/create_users.py').read())"
python manage.py loaddata recipes.json