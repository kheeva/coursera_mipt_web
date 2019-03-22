import json

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Item, Review

from jsonschema import validate
from jsonschema.exceptions import ValidationError


ADD_ITEM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",

	"properties": {

        "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 64,
            "pattern": "^(?!\s*$).+",
        },

        "description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1024,
            "pattern": "^(?!\s*$).+",
        },

        "price": {
            "anyOf": [
                {"type": "integer", "minimum": 1, "maximum": 1000000,},
                {"type": "string", "pattern": "^(1000000|[1-9][0-9]{0,5})$"}
            ]
        }
    },
    "required": ["title", "description", "price"]
}

ADD_REVIEW_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",

	"properties": {

        "text": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1024,
            "pattern": "^(?!\s*$).+",
        },

        "grade": {
            "anyOf": [
                {"type": "integer", "minimum": 1, "maximum": 10,},
                {"type": "string", "pattern": "^(10|[1-9])$"}
            ]
        }
    },
    "required": ["text", "grade"]
}


@method_decorator(csrf_exempt, name='dispatch')
class AddItemView(View):
    """View для создания товара."""

    def post(self, request):
        try:
            request_data = json.loads(request.body)
            validate(request_data, ADD_ITEM_SCHEMA)
        except json.JSONDecodeError:
            return JsonResponse({'errors': 'Invalid JSON'}, status=400)
        except ValidationError:
            return JsonResponse({'errors': 'запрос не прошел валидацию'}, status=400)
        else:
            item = Item.objects.create(
                title=request_data['title'],
                description=request_data['description'],
                price=int(request_data['price'])
            )
            item.save()
            return JsonResponse({"message": "товар успешно сохранен",
                                 "id": item.id}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class PostReviewView(View):
    """View для создания отзыва о товаре."""

    def post(self, request, item_id):
        try:
            request_data = json.loads(request.body)
            validate(request_data, ADD_REVIEW_SCHEMA)
        except json.JSONDecodeError:
            return JsonResponse({'errors': 'Invalid JSON'}, status=400)
        except ValidationError:
            return JsonResponse({'errors': 'запрос не прошел валидацию'}, status=400)
        else:
            item = Item.objects.filter(pk=item_id)
            if not item:
                return JsonResponse(
                    {'error': 'товара с таким id не существует'}, status=404)

            review = Review.objects.create(
                grade=request_data['grade'],
                text=request_data['text'],
                item=item[0]
            )
            review.save()
            return JsonResponse({"message": "товар успешно сохранен",
                                 "id": review.id},
                                status=201)


class GetItemView(View):
    """View для получения информации о товаре.

    Помимо основной информации выдает последние отзывы о товаре, не более 5
    штук.
    """

    def get(self, request, item_id):
        try:
            item_id = int(item_id)
        except ValueError:
            return HttpResponse('товара с таким id не существует',
                                status=404)
        else:
            item = Item.objects.filter(pk=item_id)
            if not item:
                return HttpResponse('товара с таким id не существует',
                                    status=404)
            item = item[0]
            reviews_qs = Review.objects.filter(item=item).order_by('-pk')[:5]

            review_list = [{"id": r.id, "text": r.text, "grade": r.grade} for r in reviews_qs]

            data = {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price": item.price,
                "reviews": review_list
            }
            return JsonResponse(data, status=200)
