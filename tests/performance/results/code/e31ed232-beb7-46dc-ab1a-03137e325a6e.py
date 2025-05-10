```
import datetime
def execute():
    now = datetime.datetime.now()
    return f'Current date and time: {now.strftime("%Y-%m-%d %H:%M:%S")}'