from pathlib import Path
import secrets
import subprocess
p=Path('.env')
if not p.exists():
    subprocess.run(['python','scripts/generate_env.py'],check=True)
s=p.read_text(encoding='utf-8-sig')
for key in ['INTEL_ADMIN_TOKEN','INTEL_READER_TOKEN']:
    if not any(line.startswith(key+'=') for line in s.splitlines()):
        s+='\n'+key+'='+secrets.token_hex(32)+'\n'
if 'FEED_INTERVAL_SECONDS=' not in s:
    s+='FEED_INTERVAL_SECONDS=21600\n'
p.write_text(s,encoding='utf-8')
print('Online credentials ready; existing secrets preserved.')
