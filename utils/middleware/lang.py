from django.conf import settings


class LangMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'GET':
            lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        elif request.method == 'POST':
            lang = request.POST.get('lang', settings.LANGUAGE_CODE)

        if lang not in [i[0] for i in settings.LANGUAGES]:
            lang = settings.LANGUAGE_CODE

        request.LANGUAGE_CODE = lang
        response = self.get_response(request)
        return response
