from collections import defaultdict

from django.http import HttpResponse


def generate_shopping_cart_report(ingredients):
    ingredient_list = defaultdict(int)
    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        measurement_unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['amount']
        key = (name, measurement_unit)
        ingredient_list[key] += amount
    shopping_cart_list = '\n'.join(
        [
            f'{name} ({measurement_unit}) - {amount}'
            for (name, measurement_unit), amount in ingredient_list.items()
        ]
    )
    response = HttpResponse(shopping_cart_list, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=shopping_cart.txt'
    return response
