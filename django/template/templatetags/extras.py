from django import template


register = template.Library()


@register.filter
def inc(a, b):
    try:
        a = int(a)
        b = int(b)
    except Exception:
        a = b = ''
    return a + b


@register.simple_tag
def division(a, b, to_int=False):
    if to_int:
        result = int(a) // int(b)
    else:
        result = float(a) / float(b)

    return result
