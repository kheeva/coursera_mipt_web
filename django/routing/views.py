from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@require_http_methods(["GET"])
@csrf_exempt
def simple_route(request):
    return HttpResponse('')


def slug_route(request, slug):
    return HttpResponse(slug)


def sum_route(request, num_1, num_2):
    return HttpResponse(int(num_1) + int(num_2))


@require_http_methods(["GET"])
def sum_get_method(request):
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')

    try:
        a = int(a)
        b = int(b)
    except ValueError:
        return HttpResponseBadRequest()

    return HttpResponse(a + b)


@require_http_methods(["POST"])
@csrf_exempt
def sum_post_method(request):
    a = request.POST.get('a', '')
    b = request.POST.get('b', '')

    try:
        a = int(a)
        b = int(b)
    except ValueError:
        return HttpResponseBadRequest()

    return HttpResponse(a + b)
