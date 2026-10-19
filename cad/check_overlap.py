import Part, glob, os, itertools

parts = {}
for f in sorted(glob.glob('/home/filip/sub-mission/cad/cq/*.step')):
    n = os.path.basename(f)[:-5]
    if n == 'probe_assembly':
        continue
    try:
        parts[n] = Part.read(f)
    except Exception as e:
        print("skip", n, e)

print("parts loaded:", len(parts))
names = list(parts)
hits = []
for a, b in itertools.combinations(names, 2):
    try:
        v = parts[a].common(parts[b]).Volume
    except Exception:
        continue
    if v > 50:
        hits.append((round(v, 1), a, b))

hits.sort(reverse=True)
print("\noverlaps > 50 mm3:")
for v, a, b in hits:
    print("  %10.1f mm3   %s <-> %s" % (v, a, b))
if not hits:
    print("  none")
