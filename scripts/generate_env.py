import pathlib
import secrets
path = pathlib.Path('.env')
if path.exists():
    raise SystemExit('.env already exists; existing credentials preserved')
values = {k: secrets.token_hex(n) for k,n in [('POSTGRES_PASSWORD',24),('NEO4J_PASSWORD',24),('MINIO_ACCESS_KEY',12),('MINIO_SECRET_KEY',24)]}
path.write_text(''.join(k+'='+v+'\n' for k,v in values.items()),encoding='utf-8')
print('Generated .env; secrets were not printed.')
