import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from .models import Item, Review
from .forms import ItemForm, ReviewForm


class AddItemView(View):
    """View для создания товара."""

    def post(self, request):
        request_data = json.loads(request.body.decode())
        form = ItemForm(request_data)
        if form.is_valid():
            item = Item.objects.create(
                title=request_data['title'],
                description=request_data['description'],
                price=request_data['price']
            )
            item.save()
            return HttpResponse(json.dumps({"id": item.id}), status=201)
        else:
            return HttpResponse('запрос не прошел валидацию'
                                , status=400)


class PostReviewView(View):
    """View для создания отзыва о товаре."""

    def post(self, request, item_id):
        request_data = json.loads(request.body.decode())
        form = ReviewForm(request_data)
        if not form.is_valid():
            return HttpResponse('запрос не прошел валидацию',
                                status=400)

        item = Item.objects.filter(pk=item_id)

        if not item:
            return HttpResponse('товара с таким id не существует',
                                status=404)

        review = Review.objects.create(
            grade=request_data['grade'],
            text=request_data['text'],
            item=item[0]
        )
        review.save()
        return HttpResponse(json.dumps({"id": review.id}), status=201)


class GetItemView(View):
    """View для получения информации о товаре.

    Помимо основной информации выдает последние отзывы о товаре, не более 5
    штук.
    """

    def get(self, request, item_id):
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
        return HttpResponse(json.dumps(data), status=200)
