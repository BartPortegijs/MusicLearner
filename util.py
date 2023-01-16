import datetime
import pytz


def split_into_chunks(list_to_split, chunk_size):
    chunks = (list_to_split[i:(i + chunk_size)] for i in range(0, len(list_to_split), chunk_size))
    return chunks


def current_timestamp(str_format=True, seconds=0):
    time = datetime.datetime.now()
    time += datetime.timedelta(seconds=seconds)
    if str_format:
        time = time.strftime("%Y-%m-%d %H:%M:%S")
    return time


def date_from_today(days=0):
    if days is not None:
        return (datetime.date.today() + datetime.timedelta(days=days)).strftime('%Y-%m-%d')


def previous_quarter():
    minutes = 15
    dt = current_timestamp(str_format=False)
    dt = dt.replace(minute=int(dt.minute / minutes) * minutes, second=0, microsecond=0)
    dt -= datetime.timedelta(minutes=minutes)
    return dt


def string_to_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')


def string_to_timestamp(timestamp_string):
    date_time = datetime.datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S')
    return datetime.datetime.timestamp(date_time)


def string_to_timestamp_milliseconds(timestamp_string):
    try:
        date_time = datetime.datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        date_time = datetime.datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%SZ')
    date_time = transform_utc_to_local(date_time)
    return datetime.datetime.timestamp(date_time)


def transform_utc_to_local(date_time):
    local_timezone = pytz.timezone("Europe/Amsterdam")
    utc_timezone = pytz.timezone('UTC')
    date_time = utc_timezone.localize(date_time, is_dst=None)
    return date_time.astimezone(local_timezone)


def first_timestamp_higher_bool(timestamp_milliseconds, timestamp):
    if type(timestamp_milliseconds) == str:
        timestamp_milliseconds = string_to_timestamp_milliseconds(timestamp_milliseconds)
    else:
        timestamp_milliseconds = datetime.datetime.timestamp(timestamp_milliseconds)
    if type(timestamp) == str:
        timestamp = string_to_timestamp(timestamp)
    else:
        timestamp = datetime.datetime.timestamp(timestamp)
    return timestamp_milliseconds > timestamp
