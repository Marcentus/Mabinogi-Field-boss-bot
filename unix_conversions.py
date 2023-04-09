from datetime import datetime, date
import settings

async def parse_user_time_input_to_unix(time_string):
    if (time_string == "now" or time_string == None):
        unix_time = int(datetime.now().timestamp()) # Set last killed time to current unix timestamp
    else:
        unix_time = None
    return unix_time

async def convert_boss_window_string_to_unix(window_string):
    start_time_str, end_time_str = window_string.split(" - ")

    today = date.today()

    start_time = datetime.strptime(start_time_str, "%H:%M")
    start_time = datetime.combine(today, start_time.time())
    start_timestamp = int(start_time.timestamp()) + settings.field_raid_time_offset

    end_time = datetime.strptime(end_time_str, "%H:%M")
    end_time = datetime.combine(today, end_time.time())
    end_timestamp = int(end_time.timestamp()) + settings.field_raid_time_offset

    time_list = [start_timestamp, end_timestamp]
    return time_list