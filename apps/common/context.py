import contextvars

_current_audit_context = contextvars.ContextVar('audit_request_context', default=None)


def get_current_audit_context():
    """Joriy so'rov (request) kontekstini qaytaradi."""
    return _current_audit_context.get()


def set_current_audit_context(ctx):
    """Joriy so'rov kontekstini o'rnatadi."""
    return _current_audit_context.set(ctx)


def reset_current_audit_context(token):
    """Kontekstni tozalaydi."""
    try:
        _current_audit_context.reset(token)
    except Exception:
        pass


def get_client_ip(request):
    """
    Mijozning haqiqiy IP manzilini X-Forwarded-For yoki REMOTE_ADDR orqali aniqlash.
    """
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_mac(request):
    """
    Mijozning MAC ID / Device ID sini aniqlash:
    1. HTTP headerlar orqali (X-MAC-Address, X-Device-ID, X-Machine-ID, X-Client-MAC)
    2. Mahalliy tarmoq so'rovlari bo'lsa, Linux tizimidagi ARP jadvali orqali
    """
    if not request:
        return ""

    # 1. Custom HTTP sarlavhalari (Frontend / Mobil / Desktop dasturlar uzatishi mumkin)
    headers_to_check = [
        'HTTP_X_MAC_ADDRESS',
        'HTTP_X_DEVICE_ID',
        'HTTP_X_MACHINE_ID',
        'HTTP_X_CLIENT_MAC',
        'HTTP_MAC_ADDRESS',
        'HTTP_DEVICE_ID',
    ]
    for h in headers_to_check:
        val = request.META.get(h)
        if val:
            return str(val).strip()

    # 2. Agar lokal tarmoq bo'lsa, /proc/net/arp orqali tekshirish
    ip = get_client_ip(request)
    if ip and ip not in ('127.0.0.1', 'localhost', '::1'):
        try:
            with open('/proc/net/arp', 'r') as f:
                lines = f.readlines()[1:]
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 4 and parts[0] == ip:
                        mac = parts[3]
                        if mac and mac != '00:00:00:00:00:00':
                            return mac
        except Exception:
            pass

    return ""
