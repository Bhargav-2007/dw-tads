"""Validate local fixtures without modifying them."""
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'tests/data'
names = ['forum_posts.json','marketplace_listings.json','onion_scans.json','blockchain_txs.json','seed_graph.json','demo_users.json','expected_outcomes.json']
failed = []
for name in names:
    path = root / name
    try:
        json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError,ValueError) as exc:
        failed.append(f'{path}: {exc}')
path = root / 'seed_targets.txt'
try:
    if len(path.read_text().splitlines()) != 8:
        failed.append(f'{path}: expected 8 lines')
except OSError as exc:
    failed.append(f'{path}: {exc}')
if failed:
    raise SystemExit('\n'.join(failed))
print('All eight fixture files validated.')
