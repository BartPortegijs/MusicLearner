import datetime
import pytz

def split_into_chunks(list, chunk_size):
    chunks = [list[i:(i+chunk_size)] for i in range(0,len(list), chunk_size)]
    return chunks

def date_from_today(days = 0):
    if days is not None:
        return (datetime.date.today() + datetime.timedelta(days=days)).strftime('%d-%m-%Y')
    else:
        return None

def datestring_to_date(datestring):
    return datetime.datetime.strptime(datestring, '%d-%m-%Y')

def timestampstring_to_timestamp(timestampstring):
    date_time = datetime.datetime.strptime(timestampstring, '%Y-%m-%d %H:%M:%S')
    return int(datetime.datetime.timestamp(date_time))

def timestampstring_to_timestamp_milliseconds(timestampstring):
    try:  
        date_time = datetime.datetime.strptime(timestampstring, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        date_time = datetime.datetime.strptime(timestampstring, '%Y-%m-%dT%H:%M:%SZ')
    date_time = transform_utc_to_local(date_time)
    return int(datetime.datetime.timestamp(date_time))

def transform_utc_to_local(datetime):
    local_timezone = pytz.timezone("Europe/Amsterdam")
    utc_timezone = pytz.timezone('UTC')
    datetime = utc_timezone.localize(datetime, is_dst=None)
    return datetime.astimezone(local_timezone)
