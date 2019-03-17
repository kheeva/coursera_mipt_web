from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@require_http_methods(["GET", 'POST'])
@csrf_exempt
def echo(request):
    data = request.GET if request.method == 'GET' else request.POST
    method = request.method.lower()
    context = {
        'data': data,
        'method': method,
        'xprint': request.META.get('HTTP_X_PRINT_STATEMENT') or 'empty'
    }
    return render(request, 'echo.html', context)


def filters(request):
    return render(request, 'filters.html', context={
        'a': request.GET.get('a', 1),
        'b': request.GET.get('b', 1)
    })


def extend(request):
    return render(request, 'extend.html', context={
        'a': request.GET.get('a'),
        'b': request.GET.get('b')
    })
