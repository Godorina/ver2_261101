"""Adsorption systems: catalyst H, MOF CO2, CF4 on Al2O3. Target E(loaded) - E(bare) - k E(gas) from structure energies. SPEC.md §4."""
import json, re
from pathlib import Path
import numpy as np
from ase.io import read
from common import features as ft, prompt as pr
__all__ = ['examples', 'quantity', 'prompt_parts']  # the system interface run.py uses

DATA = Path(__file__).resolve().parents[2] / 'data'
BINS = np.round(np.arange(0.5, 5.0001, 0.25), 2)  # force-table bins from 0.5 A for short H/F contacts (run_cat_deh.py:25)


def _goal(q, where):
    return (f'A candidate also counts only if its {q} error (mean |{q}_DFT - {q}_pred| over the example pairs) is lower than that of the\n'
            f'original potential.\n{pr.probe(where)}\nAmong the candidates that pass all four checks, the lowest {q} error wins.')


# Adsorption apps: target symbol, gas, bare/loaded keys and roles, definition, domain paragraph, range-check examples.
CONF = {
    '2_catalyst': dict(
        q='dE_H', k=0.5, gas='H2', bare='slab', loaded='slab+H', suffix='slab-H', role_gas='H2 molecule',
        role_bare='slab of pair {j}', role_loaded='slab+H of pair {j}', role_none='slab (no partner)',
        defn='dE_H = E(slab+H) - E(slab) - 1/2 E(H2)', where=' (H closer to a metal, H bonded to N or C, other metal-N distances)',
        domain=('\nThe examples are pairs of the same dual-atom catalyst without H (slab) and with one adsorbed H (slab+H), plus the isolated\n'
                'H2 molecule. The quantity of interest is the hydrogen adsorption energy\n'
                '  dE_H = E(slab+H) - E(slab) - 1/2 E(H2).\n'
                'The per-element values c_Z cancel exactly in dE_H; only terms that involve H change it (pair terms with H, and the H-H term,\n'
                'which acts only in H2). The evaluation structures are other N arrangements of the same catalyst (each metal bonded to 0-4 N,\n'
                'total 0-6), as slab and slab+H pairs.\n')),
    '3_MOF': dict(
        q='E_ads', k=1.0, gas='CO2', bare='bare_MOF', loaded='MOF+CO2', suffix='mof-CO2', role_gas='gas CO2 molecule',
        role_bare='bare MOF (reference shared by every pair)', role_loaded='MOF+CO2 of pair {j}', role_none='unpaired',
        defn='E_ads = E(MOF+CO2) - E(bare MOF) - E(CO2)', where=' (CO2 at other sites, closer to metal or linker atoms)', disp=True,
        domain=('\nThe examples are one metal-organic framework (MOF): its empty, relaxed framework (bare MOF, the reference shared by every\n'
                'pair), frames of the same framework with one adsorbed CO2 molecule (MOF+CO2) taken from several relaxations started at\n'
                'different adsorption sites, and the isolated CO2 molecule. The quantity of interest is the CO2 adsorption energy\n'
                '  E_ads = E(MOF+CO2) - E(bare MOF) - E(CO2).\n'
                'The per-element values c_Z cancel exactly in E_ads; only structure-dependent terms change it (mainly terms between CO2 atoms\n'
                'and framework atoms, plus framework terms that differ between the loaded and the bare geometry). The DFT reference includes a\n'
                'D3 dispersion correction. The evaluation structures are CO2 at other adsorption sites of the same MOF.\n')),
    '4_CF4': dict(
        q='E_ads', k=1.0, gas='CF4', bare='bare_slab', loaded='slab+CF4', suffix='slab-CF4', role_gas='gas CF4 molecule',
        role_bare='bare slab (reference shared by every pair)', role_loaded='slab+CF4 of pair {j}', role_none='unpaired',
        defn='E_ads = E(slab+CF4) - E(bare slab) - E(CF4)', where=' (CF4 at other sites, closer to surface Al or O atoms)',
        domain=('\nThe examples are one Al2O3 surface slab: its relaxed bare slab (the reference shared by every pair), frames of the same\n'
                'slab with one CF4 molecule placed at different positions, orientations and heights above the surface (slab+CF4), and the\n'
                'isolated CF4 molecule. The quantity of interest is the CF4 adsorption energy\n'
                '  E_ads = E(slab+CF4) - E(bare slab) - E(CF4).\n'
                'The per-element values c_Z cancel exactly in E_ads; only structure-dependent terms change it (mainly terms between CF4 atoms\n'
                'and surface atoms, plus slab terms that differ between the loaded and the bare geometry). The DFT reference has no dispersion\n'
                'correction. The evaluation structures are CF4 adsorbed at other sites of the same surface.\n')),
}


def examples(app, group, n):
    """Split order train + val of one group, then the gas molecule last (SPEC §4)."""
    pool = [a for a in read(DATA / app / 'examples.traj', ':') if a.info['group'] == group]
    s = json.loads((DATA / app / 'splits.json').read_text())[group][str(n)]
    assert all(pool[i].info['index'] == i for i in s['train'] + s['val'])
    return [pool[i] for i in s['train'] + s['val']] + [read(DATA / app / f"{CONF[app]['gas']}.traj")]


def _pairs(app, ids):
    """Complete (bare, loaded) pairs in p order; MOF/CF4 share one ':ref:' bare, catalyst pairs have their own slab."""
    suffix, ref, P = CONF[app]['suffix'], next((k for k in ids if ':ref:' in k), None), {}
    for k in ids:
        m = re.search(r':p(\d+):(.+)$', k)
        if m:
            P.setdefault(int(m[1]), {})[m[2]] = k
    return [(ref or d.get('slab'), d[suffix]) for _, d in sorted(P.items()) if suffix in d and (ref or 'slab' in d)]


def quantity(app, frames, E):
    """Target per complete pair from structure energies E {frame_id: eV} (E_DFT, E_BAM or a corrected E); gas is the last frame."""
    ids = [a.info['frame_id'] for a in frames]; gas, k = ids[-1], CONF[app]['k']
    return [E[b] - E[a] - k * E[gas] for a, b in _pairs(app, ids)]


def prompt_parts(app, frames, E_dft, E_bam):
    """Roles, goal, domain paragraph and the adsorption-pair table for the seed prompt."""
    c, ids = CONF[app], [a.info['frame_id'] for a in frames]
    name, gas, pr_ = {k: f'ex{i:02d}' for i, k in enumerate(ids, 1)}, ids[-1], _pairs(app, ids)
    role = {gas: c['role_gas']}
    for j, (a, b) in enumerate(pr_, 1):
        role[a] = c['role_bare'].format(j=j); role[b] = c['role_loaded'].format(j=j)
    rows = [{'pair': j, c['bare']: name[a], c['loaded']: name[b], f"{c['q']}_DFT_eV": round(d, 4), f"{c['q']}_BAM_eV": round(m, 4),
             'delta_eV': round(d - m, 4)} for j, ((a, b), d, m) in enumerate(zip(pr_, quantity(app, frames, E_dft), quantity(app, frames, E_bam)), 1)]
    target = (f"\nAdsorption pairs in the examples ({c['gas']} = {name[gas]}; {c['defn']}; delta = {c['q']}_DFT - {c['q']}_BAM; "
              f"mean |delta| of the original potential = {np.mean([abs(r['delta_eV']) for r in rows]):.4f} eV):\n" + pr.enc(rows) + '\n')
    return dict(roles=[role.get(k, c['role_none']) for k in ids], goal=_goal(c['q'], c['where']), domain=c['domain'],
                target=target, bins=BINS, disp=c.get('disp', False))


if __name__ == '__main__':  # self-check (run from code/: python -m systems.adsorption): pairing rules on synthetic ids
    cat = ['Co-pair:p2:slab-H', 'Co-pair:p1:slab', 'Co-pair:p1:slab-H', 'Co-pair:p3:slab', 'H2:dft-relaxed']
    assert _pairs('2_catalyst', cat) == [('Co-pair:p1:slab', 'Co-pair:p1:slab-H')]  # p2, p3 incomplete
    mof = ['X-pair:ref:mof', 'X-pair:p2:mof-CO2', 'X-pair:p1:mof-CO2', 'CO2:gas']
    assert _pairs('3_MOF', mof) == [('X-pair:ref:mof', 'X-pair:p1:mof-CO2'), ('X-pair:ref:mof', 'X-pair:p2:mof-CO2')]
    from ase import Atoms
    frames = [Atoms('H', info={'frame_id': k}) for k in cat]
    assert quantity('2_catalyst', frames, {'Co-pair:p1:slab': 1.0, 'Co-pair:p1:slab-H': 3.0, 'H2:dft-relaxed': 2.0}) == [1.0]
    print('ok')
