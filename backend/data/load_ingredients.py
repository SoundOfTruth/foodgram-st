
import json

from recipes.models import Ingredient

is_empty = Ingredient.objects.count() == 0

if is_empty:
    Ingredients_list = []
    with open('data/ingredients.json', encoding='utf-8') as f:
        ingredients = json.load(f)
    for ingredient in ingredients:
        Ingredients_list.append(
            Ingredient(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit']
            )
        )
    Ingredient.objects.bulk_create(Ingredients_list)
    print(f'Inserted {len(Ingredients_list)} ingredients objects')
else:
    print('The table is not empty')
