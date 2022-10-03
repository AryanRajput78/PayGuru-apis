from django.http import HttpResponse

class welcome():
    def __init__(self) -> None:
        return HttpResponse('Welcome to Hikvision API gateway.\n Use "/device/" or "/user/ to navigate."')
