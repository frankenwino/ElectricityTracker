from datetime import datetime
from time import sleep

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_message(message: str) -> None :
    print(f"{now()} - {message}")
    
def do_wait(wait_time: int, reason: str=None) -> None:
    if reason is None:
        print(f"{now()} - Waiting {wait_time} seconds")
    else:
        print(f"{now()} - Waiting {wait_time} seconds. {reason.capitalize()}")
    
    sleep(wait_time)