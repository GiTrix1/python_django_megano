from django import template

register = template.Library()


@register.filter
def subtract(value, arg) -> str:
    """
    Данная функция возвращает строку, используемую для цикла for в шаблоне.
    Необходима для получения результата вычитания value из arg
    """
    num = int(arg) - int(value)
    return ''.join([f'{i}' for i in range(num)])


@register.filter
def getrange(value, arg) -> str:
    """
    Данная функция возвращает строку, используемую для цикла for в шаблоне.
    """
    num = int(value)
    return ''.join([f'{i}' for i in range(num)])
