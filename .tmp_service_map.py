import re
from pathlib import Path

text = Path('docker-compose.yml').read_text(encoding='utf-8').splitlines()

services = {}
current = None
in_services = False
section = None
for line in text:
    if re.match(r'^services:\s*$', line):
        in_services = True
        continue
    if not in_services:
        continue

    m = re.match(r'^  ([a-zA-Z0-9_-]+):\s*$', line)
    if m:
        current = m.group(1)
        services[current] = {'depends_on': set(), 'env': set()}
        section = None
        continue

    if current is None:
        continue

    if re.match(r'^    depends_on:\s*$', line):
        section = 'depends_on'
        continue
    if re.match(r'^    environment:\s*$', line):
        section = 'environment'
        continue

    # leave section when dedented to service-level child
    if re.match(r'^    [a-zA-Z0-9_-]+:\s*$', line) and section in ('depends_on','environment'):
        section = None

    if section == 'depends_on':
        dm = re.match(r'^      ([a-zA-Z0-9_-]+):\s*$', line)
        if dm:
            services[current]['depends_on'].add(dm.group(1))

    if section == 'environment':
        em = re.match(r'^      -\s*([A-Z0-9_]+)', line)
        if em:
            env = em.group(1)
            if env.endswith('_ADDR'):
                services[current]['env'].add(env)

service_names = set(services.keys())

def infer_target(var):
    base = var[:-5]  # strip _ADDR
    cands = [base.lower().replace('_','-'), base.lower().replace('_',''), base.lower()]
    # special exacts
    extras = {
        'productcatalog': 'product-catalog',
        'productreviews': 'product-reviews',
        'frauddetection': 'fraud-detection',
        'frontendproxy': 'frontend-proxy',
        'loadgenerator': 'load-generator',
        'valkey': 'valkey-cart',
        'postgres': 'postgresql',
    }
    cands += [extras.get(cands[1], ''), extras.get(cands[2], '')]

    for c in cands:
        if c and c in service_names:
            return c
    # fuzzy: collapse dashes
    collapsed = {s.replace('-',''): s for s in service_names}
    key = base.lower().replace('_','')
    if key in collapsed:
        return collapsed[key]
    return None

edges_dep = []
edges_env = []
for src, data in services.items():
    for dst in sorted(data['depends_on']):
        if dst in service_names:
            edges_dep.append((src, dst))
    for var in sorted(data['env']):
        dst = infer_target(var)
        if dst and dst != src:
            edges_env.append((src, dst, var))

print('SERVICES:', len(service_names))
print('DEPENDENCY_EDGES:', len(edges_dep))
print('ENV_ADDR_EDGES:', len(edges_env))
print('\nTop direct dependency examples:')
for e in edges_dep[:30]:
    print(f'- {e[0]} -> {e[1]}')

print('\nTop env-address wiring examples:')
for e in edges_env[:30]:
    print(f'- {e[0]} -> {e[1]} ({e[2]})')

print('\nMERMAID:')
print('graph LR')
for s in sorted(service_names):
    print(f'  {s.replace("-","_")}["{s}"]')

for src, dst in sorted(set(edges_dep)):
    print(f'  {src.replace("-","_")} --> {dst.replace("-","_")}')

for src, dst, var in sorted(set(edges_env)):
    print(f'  {src.replace("-","_")} -. "{var}" .-> {dst.replace("-","_")}')
