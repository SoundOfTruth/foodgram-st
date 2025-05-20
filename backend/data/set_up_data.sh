case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

python manage.py shell -c "exec(open('data/create_users.py').read())"
python manage.py loaddata data/recipes.json
echo "script executed"