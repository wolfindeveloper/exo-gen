import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

a = json.loads(Path('graphify-out/.graphify_analysis.json').read_text(encoding='utf-8'))
print('=== TOP 15 COMMUNITIES ===')
sorted_c = sorted(a['communities'].items(), key=lambda x: len(x[1]), reverse=True)
for k, v in sorted_c[:15]:
    print(f'  C{k}: {len(v)} nodes')

print()
print('=== GOD NODES (top 10) ===')
for g in a['gods'][:10]:
    print(f'  {g.get("id","?")} - {g.get("label","?")} (score: {g.get("score","?")})')

print()
print('=== SURPRISING CONNECTIONS (top 5) ===')
for s in a['surprises'][:5]:
    source = s.get('source', '?')
    target = s.get('target', '?')
    rel = s.get('relation', '?')
    why = s.get('why', '')
    print(f'  {source} --[{rel}]--> {target}')
    print(f'    {why[:200]}')
