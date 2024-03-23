from .models import AnonymousUser, CartItem
from whatsapp_api_client_python import API


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def save_anonymous(request):
    ip_address = get_client_ip(request)
    session_key = request.session.session_key
    if session_key:
        try:
            anonymous = AnonymousUser.objects.get(session_key=session_key)
            anonymous.ip_address = ip_address
            anonymous.save(update_fields=['ip_address'])
        except Exception:
            anonymous = AnonymousUser.objects.create(ip_address=ip_address, session_key=session_key)
        return anonymous


def order_texter(order):
    order_items = CartItem.objects.filter(order=order)
    text = (f"👤 `{order.name}`\n"
            f"📞 {order.mobile}\n\n"
            f"⚡️ `Заказ {order.id}`\n"
            f"➖➖➖➖➖➖➖\n")
    sum = 0
    for i in order_items:
        text += f"🆔 *{i.product.id}* \n"
        text += f"🎫 *{i.product.title}*\n"
        text += f"🎞 *{i.quantity}шт*\n"
        text += f"✨ *{i.color if i.color else 'Цвет не указан'} *\n"
        text += f"\n🛒 *{int(i.product.price) * int(i.quantity)} сом*\n"
        text += f"➖➖➖➖➖➖➖\n"
        sum += i.product.price * i.quantity
    text += f"\n*TOTAL SUM: {sum}*c"
    return text


def whatsapp_sender(order):
    text = order_texter(order)
    greenAPI = API.GreenAPI(
        "7103919749", "ff1c0c10b0a549be9aabf026064da3d6b57f4fe078c2438aa0"
    )
    response = greenAPI.sending.sendPoll(
        "996559001201@c.us",
        f"{text}",
        [
            {"optionName": "Обзвонен"},
            {"optionName": "Отклонен"}
        ]
    )

    response = greenAPI.sending.sendPoll(
        "996550566307@c.us",
        f"{text}",
        [
            {"optionName": "Обзвонен"},
            {"optionName": "Отклонен"}
        ]
    )
    # import requests
    #
    # url = "https://api.green-api.com/waInstance{{idInstance}}/sendMessage/{{apiTokenInstance}}"
    #
    # payload = "{\r\n\t\"chatId\": \"11001234567@c.us\",\r\n\t\"message\": \"I use Green-API to send this message to you!\"\r\n}"
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    #
    # response = requests.request("POST", url, headers=headers, data=payload)
    #
    # print(response.text.encode('utf8'))
