from datetime import datetime

def execute():
    now = datetime.now()
    return f"Aktualna data to {now.strftime('%Y-%m-%d')} a aktualna godzina to {now.strftime('%H:%M')}"