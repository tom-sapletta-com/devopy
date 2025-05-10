```
from datetime import datetime

def execute():
    now = datetime.now()
    return f"aktualna data: {now.strftime('%Y-%m-%d')}, aktualna godzina: {now.strftime('%H:%M:%S')}"