from order_app.models import OrderModel
import json


def active_order(request):
    """
    Функция для получения всех активных заказов конкретного пользователя
    """
    order = OrderModel.objects.filter(user_id=request.user.id, activity=True)
    all_active_order = list()
    if len(order) > 1:
        for current_order in order:
            current_order_id = current_order.id
            order_data = json.loads(current_order.json_order_data)
            current_dict_order = {'order_id': current_order_id,
                                  'total_price': order_data['t_price']}
            current_dict_order.update(order_data['order_dict'])
            all_active_order.append(current_dict_order)
    elif len(order) == 1:
        order = OrderModel.objects.get(user_id=request.user.id, activity=True)
        current_order_id = order.id
        order_data = json.loads(order.json_order_data)
        current_dict_order = {'order_id': current_order_id,
                              'total_price': order_data['t_price']}
        current_dict_order.update(order_data['order_dict'])
        all_active_order.append(current_dict_order)
    else:
        return None
    return all_active_order


def all_user_order(request):
    """
    Функция для получения всех заказов конкретного пользователя
    """
    order = OrderModel.objects.filter(user_id=request.user.id)
    all_users_order = list()
    if len(order) != 0:
        for current_order in order:
            current_order_id = current_order.id
            order_data = json.loads(current_order.json_order_data)
            current_dict_order = {'order_id': current_order_id,
                                  'total_price': order_data['t_price']}
            current_dict_order.update(order_data['order_dict'])
            all_users_order.append(current_dict_order)
    else:
        return None
    return all_users_order
