import datetime

def execute():
    now = datetime.datetime.now()
    print(f"Actual date: {now.date()}, Actual time: {now.time()}")
    return now