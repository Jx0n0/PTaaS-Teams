import os
import time

import psycopg

host = os.getenv('POSTGRES_HOST', 'db')
port = int(os.getenv('POSTGRES_PORT', '5432'))
user = os.getenv('POSTGRES_USER', 'ptaas')
password = os.getenv('POSTGRES_PASSWORD', 'ptaas')
dbname = os.getenv('POSTGRES_DB', 'ptaas')

max_attempts = int(os.getenv('DB_WAIT_MAX_ATTEMPTS', '30'))
interval = float(os.getenv('DB_WAIT_INTERVAL', '1'))

for attempt in range(1, max_attempts + 1):
    try:
        with psycopg.connect(host=host, port=port, user=user, password=password, dbname=dbname):
            print('Database is ready')
            break
    except Exception as exc:  # noqa: BLE001
        print(f'[{attempt}/{max_attempts}] waiting for database {host}:{port} ({exc})')
        time.sleep(interval)
else:
    raise SystemExit('Database is not ready in time')
