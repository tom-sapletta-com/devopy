from datetime import datetime

def execute():
    now = datetime.now()
    return f"Actual date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"