"""Sodium-ion cathode P2 Na_xMnO2: mixing energy per MnO2 f.u. and the convex hull from structure energies. SPEC.md §4."""
import json
from pathlib import Path
import numpy as np
from ase.io import read
from common import features as ft, prompt as pr
__all__ = ['examples', 'quantity', 'prompt_parts']  # the system interface run.py uses

DATA = Path(__file__).resolve().parents[2] / 'data' / '1_sodium'

SODIUM_DOMAIN = ('\nSome examples are relaxed structures of Na_xMnO2 (x = Na/Mn) in the P2, P2\' and OP4 phases, including the two end members\n'
                 'MnO2 (x = 0) and NaMnO2 (x = 1), and one Na metal structure. The goal of this task is energy only. The quantity of interest is the\n'
                 'mixing energy per MnO2 formula unit,\n'
                 '  E_mix(x) = E(Na_xMnO2) - x E(NaMnO2) - (1 - x) E(MnO2),\n'
                 'and the convex hull, the lower envelope of E_mix versus x; E_above_hull of a structure is its E_mix minus the hull value at its x.\n'
                 'The hull shape decides which compositions are stable and the voltage. The per-element values c_Z cancel exactly in E_mix, so only\n'
                 'the physics terms can change the hull. A single pair term mostly shifts the whole hull up or down; to change its shape, terms must\n'
                 'act differently at different x, for example through the local environment (eam on Mn or Na, Na-Na, Na-Mn or O-centred angle terms).\n'
                 'The evaluation structures are other relaxed Na_xMnO2 structures of the same phases.\n')
SODIUM_GOAL = ('Goal (energy only; forces are recorded but not used for selection): a candidate counts only if (1) its example energy error\n'
               '(mean |E_DFT - E_pred| per atom) is lower than that of the original potential, (2) its E_mix error (mean |E_mix_DFT - E_mix_pred|\n'
               'over the relaxed Na_xMnO2 examples, meV per formula unit) is lower than that of the original potential, and (3) it passes the range\n'
               'check below.\n' + pr.probe('') + '\nAmong the candidates that pass, the lowest hull score wins: hull score = mean of the E_mix error and the\n'
               'E_above_hull error (mean |E_above_hull_DFT - E_above_hull_pred| over the relaxed examples, each hull built from the example set).')


def examples(app=None, group=None, n=None):
    """The 21 examples in examples.json order; role and end members carried in atoms.info."""
    hull = {a.info['frame_id']: a for a in read(DATA / 'hull.traj', ':')}
    spec = json.loads((DATA / 'examples.json').read_text())
    frames = [hull[e['hull_id']] for e in spec['examples']]
    for a, e in zip(frames, spec['examples']):
        a.info.update(role=e['role'], end_members=spec['end_members'])
    return frames


def _lower_hull(pts):
    best = {}
    for p in pts:
        k = round(p[0], 6)
        if k not in best or p[1] < best[k][1]:
            best[k] = p
    h = []
    for p in sorted(best.values(), key=lambda p: (p[0], p[1])):
        while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
            h.pop()
        h.append(p)
    return h


def _hull_at(h, x):
    for a, b in zip(h, h[1:]):
        if a[0] <= x <= b[0]:
            return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]) if b[0] > a[0] else min(a[1], b[1])
    return h[0][1] if x <= h[0][0] else h[-1][1]



def quantity(app, frames, E):
    """E_mix (meV/f.u.), E_above_hull and hull vertices of the relaxed examples (no Na metal, no end members) from E {frame_id: eV}."""
    info = {a.info['frame_id']: a.info for a in frames}
    k0, k1 = frames[0].info['end_members']
    rel = [k for k in info if info[k]['phase'] != 'Na_metal' and k not in (k0, k1)]
    em = {k: 1000 * (E[k] / info[k]['nMn'] - info[k]['x'] * E[k1] / info[k1]['nMn'] - (1 - info[k]['x']) * E[k0] / info[k0]['nMn']) for k in rel}
    h = _lower_hull([(0.0, 0.0, k0), (1.0, 0.0, k1)] + [(info[k]['x'], em[k], k) for k in em])
    return em, {k: em[k] - _hull_at(h, info[k]['x']) for k in em}, sorted(p[2] for p in h)


def prompt_parts(app, frames, E_dft, E_bam):
    """Roles, energy-only goal, domain paragraph and the E_mix / hull table (run_mix8.py:97-114)."""
    ids = [a.info['frame_id'] for a in frames]; info = {a.info['frame_id']: a.info for a in frames}
    name = {k: f'ex{i:02d}' for i, k in enumerate(ids, 1)}
    k0, k1 = frames[0].info['end_members']
    (Ed, aD, vD), (Eb, aB, vB) = quantity(app, frames, E_dft), quantity(app, frames, E_bam)
    rows = [{'example': name[k], 'x': round(info[k]['x'], 4), 'phase': info[k]['phase'], 'E_mix_DFT_meV_per_fu': round(Ed[k], 2),
             'E_mix_BAM_meV_per_fu': round(Eb[k], 2), 'delta_E_mix_meV_per_fu': round(Ed[k] - Eb[k], 2),
             'E_above_hull_DFT_meV_per_fu': round(aD[k], 2), 'E_above_hull_BAM_meV_per_fu': round(aB[k], 2)}
            for k in sorted(Ed, key=lambda k: (info[k]['x'], info[k]['phase']))]
    m1 = np.mean([abs(r['delta_E_mix_meV_per_fu']) for r in rows])
    m2 = np.mean([abs(r['E_above_hull_DFT_meV_per_fu'] - r['E_above_hull_BAM_meV_per_fu']) for r in rows])
    target = (f'\nMixing energies and hull of the relaxed Na_xMnO2 examples (end members MnO2 = {name[k0]}, NaMnO2 = {name[k1]}; '
              f'E_mix per MnO2 formula unit; delta = E_mix_DFT - E_mix_BAM; E_above_hull from the lower hull of the example set):\n' + pr.enc(rows) +
              f'\nOriginal potential on these examples: mean |delta E_mix| = {m1:.2f} meV/f.u., mean |E_above_hull error| = {m2:.2f} meV/f.u., '
              f'hull score = {0.5 * (m1 + m2):.2f} meV/f.u.\n'
              f'DFT hull vertices of the example set: {[name[k] for k in vD]}; original-potential hull vertices: {[name[k] for k in vB]}.\n')
    return dict(roles=[a.info['role'] for a in frames], goal=SODIUM_GOAL, domain=SODIUM_DOMAIN, target=target, bins=ft.BINS, disp=False)


if __name__ == '__main__':  # self-check (python -m systems.sodium): hull of a hand-made set
    h = _lower_hull([(0.0, 0.0, 'a'), (1.0, 0.0, 'b'), (0.5, -10.0, 'c'), (0.5, -5.0, 'd'), (0.25, 0.0, 'e')])
    assert [p[2] for p in h] == ['a', 'c', 'b']                  # d loses the tie at x=0.5, e lies above the hull
    assert _hull_at(h, 0.25) == -5.0 and _hull_at(h, 0.75) == -5.0
    print('ok')
