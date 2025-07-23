import os

CPU_COUNT = os.cpu_count() * 4 or 4
MAX_THREADS = int(os.getenv("MAX_THREADS", CPU_COUNT))