import csv
import io


def get_csv_data(ingredients):
    stream = io.StringIO()
    writer = csv.writer(stream)
    for ingredient in ingredients:
        name = ingredient['recipe__recipe_ingredients__ingredient__name']
        measurement_unit = ingredient[
            'recipe__recipe_ingredients__ingredient__measurement_unit']
        amount = ingredient['amount']
        payload = [f'{name} ({measurement_unit})', amount]
        writer.writerow(payload)
    return stream.getvalue()
