import threading

# eigene Instanz pro Thread, die session speichern kann - darauf haben Threads sonst keinen Zugriff
_thread_local = threading.local() # erzeugt Objekt, das für jeden Thread eigene Instanz hat (thread-lokaler Speicher)

def set_access_token(token: str):
    _thread_local.access_token = token

def get_access_token() -> str:
    return getattr(_thread_local, 'access_token', None)