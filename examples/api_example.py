#!/usr/bin/env python3
import requests
import json

# Przykład wysłania zadania do API devopy
def send_task_to_api(task, docker=False):
    url = "http://localhost:5000/run"
    payload = {
        "task": task,
        "docker": docker
    }
    
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    task = "pobierz dane z api i zapisz do excela"
    result = send_task_to_api(task)
    print(json.dumps(result, indent=2))
