import datetime
import pytz

BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def get_beijing_time():
    return datetime.datetime.now(BEIJING_TZ)

def get_beijing_timestamp():
    return get_beijing_time().timestamp()

def format_beijing_time(dt=None):
    if dt is None:
        dt = get_beijing_time()
    elif isinstance(dt, datetime.datetime) and dt.tzinfo is None:
        dt = BEIJING_TZ.localize(dt)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def format_beijing_date(dt=None):
    if dt is None:
        dt = get_beijing_time()
    elif isinstance(dt, datetime.datetime) and dt.tzinfo is None:
        dt = BEIJING_TZ.localize(dt)
    return dt.strftime('%Y-%m-%d')

def to_beijing_time(dt):
    if dt.tzinfo is None:
        return BEIJING_TZ.localize(dt)
    return dt.astimezone(BEIJING_TZ)