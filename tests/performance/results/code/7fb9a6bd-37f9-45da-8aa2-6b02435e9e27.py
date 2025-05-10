```
from datetime import datetime

def execute():
    now = datetime.now()
    print(f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    return now.strftime('%Y-%m-%d %H:%M:%S')