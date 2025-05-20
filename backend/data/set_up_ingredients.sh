case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

python manage.py shell -c "exec(open('data/load_ingredients.py').read())"
echo "script executed"