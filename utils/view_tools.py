import json

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.template import Context, loader

from .useragents import UserAgent


def get_param(request):
    if request.method == "POST":
        try:
            data = json.loads(request.raw_post_data)
        except:
            data = request.POST.copy()
        return data
    else:
        return request.GET.copy()


get_args = get_param


def get_user_from_session_id(session_id):
    try:
        session = Session.objects.get(session_key=session_id)
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)
    except:
        user = AnonymousUser()
    return user


def wrap_request(request):
    """
    Add  user_agent attribute for request
    """
    request.user_agent = UserAgent(request.META.get('HTTP_USER_AGENT'))
    return request.user_agent.browser, request.user_agent.version


def check_browser_support(request):
    browser, version = wrap_request(request)
    if settings.BROWSER_SUPPORT_CONFIG.get(browser):
        version_prefix = version.split('.')[0]
        if version_prefix.isdigit():
            if int(version_prefix) < \
                    settings.BROWSER_SUPPORT_CONFIG.get(browser):
                return False
    return True


def check_mobile_platform(request):
    wrap_request(request)
    if request.user_agent.platform in settings.MOBILE_PLATFORMS:
        return True
    return False


def JSONResponse(data, dump=True):
    return HttpResponse(
        json.dumps(data) if dump else data,
        content_type='application/json',
    )


def ok_json(data={}):
    return JSONResponse({'ok': True, 'data': data})


def fail_json(err=0, description=''):
    return JSONResponse({'ok': False, 'reason': {'err': err, 'desc': description}})


def list_jsonify(data):
    return JSONResponse(data)


def render_template(template_name, kwargs={}, context_instance=None):
    t = loader.get_template(template_name)
    if context_instance:
        context_instance.update(kwargs)
    else:
        context_instance = Context(kwargs)
    return t.render(context_instance)


def get_real_ip(request):
    return request.META.get('HTTP_X_REAL_IP', request.META['REMOTE_ADDR'])
