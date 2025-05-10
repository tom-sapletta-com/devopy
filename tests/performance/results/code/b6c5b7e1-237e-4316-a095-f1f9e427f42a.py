```
from datetime import datetime

def execute():
    now = datetime.now()
    print(now.strftime("%Y-%m-%d %H:%M:%S"))
    return now.strftime("%Y-%m-%d %H:%M:%S")