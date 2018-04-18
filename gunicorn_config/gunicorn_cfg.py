import multiprocessing
import os
import sys

path = os.path.abspath('')
sys.path.append(path)

abs_path = os.path.abspath(__file__)
app = "community_bot"

project_path = os.path.join('/'.join(abs_path.split('/')[:-3]), app)

sys.path.insert(0, project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "community_bot.settings")

from django.conf import settings

procname = app
bind = "%s:%s" % (settings.HOST, settings.PORT)
workers = multiprocessing.cpu_count() * 2
worker_class = 'gevent'
max_requests = 100000
max_requests_jitter = 10000
timeout = 100
debug = settings.DEBUG
daemon = False
loglevel = 'info'
reload = settings.DEBUG
