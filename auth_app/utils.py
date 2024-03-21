from .models import AnonymousUser


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
    print(request.session.session_key)
    print("SESSION KEY", session_key)
    print("IP_ADRESS", ip_address)

    if session_key:
        try:
            anonymous = AnonymousUser.objects.get(session_key=session_key)
            anonymous.ip_address = ip_address
            anonymous.save(update_fields=['ip_address'])
        except Exception:
            anonymous = AnonymousUser.objects.create(ip_address=ip_address, session_key=session_key)
        return anonymous
   # if not request.session.session_key:
    #     session_key = request.session.create()
    #     print("SESSION AFTER CREATE", request.session.session_key)
    #     if session_key:
    #         try:
    #             anonymous = AnonymousUser.objects.get(session_key=session_key)
    #             anonymous.ip_address = ip_address
    #             anonymous.save(update_fields=['ip_address'])
    #         except Exception:
    #             anonymous = AnonymousUser.objects.create(ip_address=ip_address, session_key=session_key)
    #         return anonymous