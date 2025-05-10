```
import datetime
def execute():
    now = datetime.datetime.now()
    return f"Actual date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"