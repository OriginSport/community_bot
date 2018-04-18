from django.conf import settings
from redlock import RedLockFactory

join_contest_lock = RedLockFactory(connection_details=[{
    'host':
    settings.REDLOCK_REDIS_SERVER,
    'port':
    settings.REDLOCK_REDIS_PORT,
    'password':
    settings.REDLOCK_REDIS_PAS,
    'db':
    0
}])
