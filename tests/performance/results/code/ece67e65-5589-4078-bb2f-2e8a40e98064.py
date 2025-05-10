from datetime import datetime

def execute():
    now = datetime.now()
    return f"Current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}"