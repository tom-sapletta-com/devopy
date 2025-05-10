from datetime import datetime

def execute():
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    print(f"Current date: {current_date}, Current time: {current_time}")
    return f"{current_date} {current_time}"