"""Build data/ from the read-only old trees (SPEC.md §4): python code/make_data.py
Lossless .traj; every write is re-read and compared bit-for-bit; writes data/SOURCES.md."""
import hashlib, json
from pathlib import Path
import numpy as np
from ase.io import read, write
from ase.calculators.singlepoint import SinglePointCalculator

H = Path(__file__).resolve().parents[1] / 'sources'  # copies of the old source trees (same relative layout as under /home/hgpark/whlee/hgpark)
R = H / 'bam-icl-release'; OUT = Path(__file__).resolve().parents[1] / 'data'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows = []  # SOURCES.md


def frame(a, info, e=None, f=None):
    """Copy with only energy/forces kept (labels) and extra info."""
    if a.calc is not None and e is None:
        e, f = a.get_potential_energy(), a.get_forces()
    b = a.copy(); b.calc = None; b.info.update(info)
    if e is not None:
        b.calc = SinglePointCalculator(b, energy=float(e), forces=np.asarray(f, float))
    return b


def save(path, frames, sources):
    path.parent.mkdir(parents=True, exist_ok=True)
    write(path, frames)
    back = read(path, ':')
    assert len(back) == len(frames)
    for a, b in zip(frames, back):  # bit-exact round trip
        assert np.array_equal(a.numbers, b.numbers) and np.array_equal(a.positions, b.positions)
        assert np.array_equal(a.cell.array, b.cell.array) and np.array_equal(a.pbc, b.pbc)
        if a.calc is not None:
            assert a.get_potential_energy() == b.get_potential_energy() and np.array_equal(a.get_forces(), b.get_forces())
    rows.append((path.relative_to(OUT), len(frames), sha(path), sources))


def adsorption(app, base, gas_src, gas_name):
    groups = sorted(d.name for d in (base / 'inputs_pairs/examples').iterdir() if d.is_dir())
    ex, qs, splits, srcs = [], [], {}, []
    for g in groups:
        src = base / 'inputs_pairs/examples' / g / 'rand20.traj'; sp = json.loads((src.parent / 'split.json').read_text())
        assert sp['source_sha256'] == sha(src), g
        ex += [frame(a, {'group': g, 'index': i}) for i, a in enumerate(read(src, ':'))]
        splits[g] = sp['subsets']
        q = base / 'inputs_pairs/queries' / g / 'queries.extxyz'
        qs += [frame(a, {'group': g}) for a in read(q, ':')]
        srcs += [src, q]
    save(OUT / app / 'examples.traj', ex, srcs[0::2])
    save(OUT / app / 'queries.traj', qs, srcs[1::2])
    g = read(gas_src); g.info.setdefault('frame_id', f'{gas_name}:gas')  # keep source id (H2:dft-relaxed); SPEC id otherwise
    save(OUT / app / f'{gas_name}.traj', [frame(g, {})], [gas_src])
    (OUT / app / 'splits.json').write_text(json.dumps(splits, indent=1))
    rows.append((Path(app) / 'splits.json', len(splits), sha(OUT / app / 'splits.json'), [s.parent / 'split.json' for s in srcs[0::2]]))
    return len(groups), len(ex), len(qs)


print('2_catalyst', adsorption('2_catalyst', R / 'results/2_catalyst/data/data', R / 'results/2_catalyst/data/data/inputs_h2/H2.extxyz', 'H2'))
print('3_MOF', adsorption('3_MOF', R / 'results/3_mof/data/method4-mof', R / 'results/3_mof/data/method4-mof/inputs_co2/CO2.extxyz', 'CO2'))
print('4_CF4', adsorption('4_CF4', R / 'past/4_cf4/pairs', R / 'past/4_cf4/pairs/inputs_cf4/CF4.extxyz', 'CF4'))

# 1_sodium: hull set with labels, metadata from the extxyz frame itself; examples = ordered hull ids with roles
S = H / 'mlp-icl-ft-check-v1/hull_nmo'


def meta(a):
    """phase/split/config as written in the extxyz; nNa, nMn counted; x = Na/Mn (None for Na metal); relaxed = fmax < 0.05 eV/A.
    Matches the old targets.json on all 733 frames, values and types."""
    s = a.get_chemical_symbols(); nNa, nMn = s.count('Na'), s.count('Mn')
    fmax = float(np.linalg.norm(a.arrays['F_DFT'], axis=1).max())
    return {'frame_id': a.info['frame_id'], **{k: a.info[k] for k in ('phase', 'split', 'config')},
            'x': nNa / nMn if nMn else None, 'nNa': nNa, 'nMn': nMn, 'relaxed': fmax < 0.05}


hull = [frame(a, meta(a), a.info['E_DFT'], a.arrays['F_DFT']) for a in read(S / 'data/hull.extxyz', ':')]
for b in hull:  # drop source-only keys
    for k in ('E_DFT', 'src_index', 'source_frame'): b.info.pop(k, None)
    b.arrays.pop('F_DFT', None)
save(OUT / '1_sodium/hull.traj', hull, [S / 'data/hull.extxyz'])
E = json.loads((S / 'mixprompt8/examples.json').read_text())
by = {b.info['frame_id']: b for b in hull}
for r in E['examples']:  # examples.json records must be the hull frames, bit for bit
    b = by[r['hull_id']]
    assert np.array_equal(b.numbers, r['numbers']) and np.array_equal(b.positions, np.array(r['positions']))
    assert np.array_equal(b.cell.array, np.array(r['cell'])) and b.get_potential_energy() == r['E_dft'] and np.array_equal(b.get_forces(), np.array(r['F_dft']))
ex = {'end_members': E['end_members'], 'na_metal': 'hull:0732',
      'examples': [{'hull_id': r['hull_id'], 'role': r['role']} for r in E['examples']]}
(OUT / '1_sodium/examples.json').write_text(json.dumps(ex, indent=1))
rows.append((Path('1_sodium/examples.json'), len(ex['examples']), sha(OUT / '1_sodium/examples.json'), [S / 'mixprompt8/examples.json']))
print('1_sodium', len(hull), len(ex['examples']))

lines = ['# data sources', '', 'Built once from read-only sources (SPEC.md §4). `.traj` = ASE trajectory, lossless; labels as energy/forces (eV, eV/Å).',
         'Adsorption `examples.traj` frames carry info `group` and `index` (frame index in that group\'s source rand20.traj, which `splits.json` refers to). Queries carry no labels.', '',
         '| file | frames/groups | sha256 | sources (sha256) |', '|---|---|---|---|']
for p, n, h, srcs in rows:
    lines.append(f'| `{p}` | {n} | `{h}` | ' + '<br>'.join(f'`{s}` (`{sha(s)}`)' for s in srcs) + ' |')
(OUT / 'SOURCES.md').write_text('\n'.join(lines) + '\n')
print('ok')
