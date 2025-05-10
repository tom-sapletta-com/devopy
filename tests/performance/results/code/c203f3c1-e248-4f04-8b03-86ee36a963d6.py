import datetime  # biblioteka do obsługi obliczeniowej
from typing import Callable, Union
  
def execute() -> str :    
    return f"Aktualna data i godzina to {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."  # zwraca aktualną datę i godzinę