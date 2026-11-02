"""Prompt descriptors of the example structures: residuals, structure summary, residual force table, r1/angles. SPEC.md §2."""
from collections import Counter
import numpy as np
from ase.data import chemical_symbols as SYM
from ase.neighborlist import neighbor_list

RC = 5.0
HIST = [0, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
BINS = np.round(np.arange(1.0, 5.0001, 0.25), 2)  # default force-table bins; systems may pass their own


def edges(a):
    """Directed periodic neighbours i->j, 0 < r < 5 A (self images kept). Rejects contacts below 0.3 A like the old graph."""
    i, j, d, D = neighbor_list('ijdD', a, RC)  # ASE excludes d == RC
    if (d < 0.3).any():
        raise ValueError('atoms closer than 0.3 A')
    return i, j, d, D


def switch(r, s=0.05):
    """C2 compact switch of the old smooth coordination (llmsr_dsl.radial_values)."""
    rho = np.sqrt(r * r + s * s)
    x = r * r / ((rho + s) * (np.sqrt(RC ** 2 + s * s) - s))
    return np.where(r < RC, (1 - x) ** 3 * (1 + 3 * x + 6 * x * x), 0.0)


def example_entry(k, a, e_nn, f_nn, ref):
    """One row of the examples table (track A). a carries DFT energy/forces."""
    n, z = len(a), a.numbers
    d_nn, d_bam = a.get_potential_energy() - e_nn, a.get_potential_energy() - e_nn - sum(ref[int(x)] for x in z)
    res = a.get_forces() - f_nn
    i, j, d, D = edges(a)
    proj = np.sum(res[i] * D / d[:, None], axis=1)
    lo, hi = np.minimum(z[i], z[j]), np.maximum(z[i], z[j])
    hist = {f'{p}-{q}': np.histogram(d[(lo == p) & (hi == q)], HIST)[0].tolist() for p, q in sorted(set(zip(lo.tolist(), hi.tolist())))}
    radial = [float(proj[(d >= p) & (d < q)].mean()) if ((d >= p) & (d < q)).any() else None for p, q in zip(HIST[:-1], HIST[1:])]
    return {'example': f'ex{k:02d}', 'n_atoms': n, 'composition': {SYM[x]: c for x, c in sorted(Counter(z.tolist()).items())},
            'E_DFT_minus_E_NN_eV': round(d_nn, 6), 'per_atom_eV': round(d_nn / n, 6), 'E_DFT_minus_E_BAM_eV': round(d_bam, 6),
            'structure': {'distance_pair_histogram': hist,
                          'mean_smooth_coordination': float(np.bincount(i, switch(d), n).mean()),
                          'force_residual_rms_eV_per_A': float(np.sqrt(np.mean(res ** 2))),
                          'radial_projection_bin_means': radial}}


def force_table(frames, residuals, bins):
    """Residual force projected toward neighbours, per centre-neighbour element pair, summed over all examples."""
    nb, acc = len(bins) - 1, {}
    for a, res in zip(frames, residuals):
        z = a.numbers
        i, j, d, D = edges(a)
        proj = np.sum(res[i] * D / d[:, None], axis=1)
        k = np.digitize(d, bins) - 1
        for e, y in sorted(set(zip(z[i].tolist(), z[j].tolist()))):  # only pairs present in this structure
            sel = (z[i] == e) & (z[j] == y) & (k >= 0) & (k < nb)
            t = acc.setdefault((e, y), {'sum': np.zeros(nb), 'count': np.zeros(nb), 'sq': 0.0, 'atoms': 0})
            t['sum'] += np.bincount(k[sel], proj[sel], nb); t['count'] += np.bincount(k[sel], minlength=nb)
            t['sq'] += float((res[z == e] ** 2).sum()); t['atoms'] += int((z == e).sum())
    return {f'{SYM[e]}-{SYM[y]}': {'mean_projected_residual_eV_per_A': [round(s / c, 4) if c else None for s, c in zip(t['sum'], t['count'])],
                                   'neighbour_pairs': [int(c) for c in t['count']],
                                   'residual_force_rms_eV_per_A': round(float(np.sqrt(t['sq'] / (3 * t['atoms']))), 4)}
            for (e, y), t in sorted(acc.items())}


def bounds(frames):
    """r1_XY (both directions pooled), r1_X and neighbour angle cosines, from the examples only (terms.py:48-73)."""
    pair, elem = {}, {}
    for a in frames:
        i, j, d = neighbor_list('ijd', a, RC); z = a.numbers
        for atom in range(len(a)):
            sel = i == atom
            if sel.any():
                elem.setdefault(int(z[atom]), []).append(float(d[sel].min()))
                for y in set(z[j[sel]].tolist()):
                    pair.setdefault(tuple(sorted((int(z[atom]), y))), []).append(float(d[sel & (z[j] == y)].min()))
    r1 = {x: float(np.median(v)) for x, v in elem.items()}
    cos = {}
    for a in frames:
        i, j, D, d = neighbor_list('ijDd', a, RC)
        for atom in range(len(a)):
            x = int(a.numbers[atom]); sel = (i == atom) & (d < 1.35 * r1[x])
            v = D[sel] / d[sel][:, None]; c = v @ v.T
            cos.setdefault(x, []).extend(c[np.triu_indices(len(v), 1)].tolist())
    return {'r1_pair': {f'{SYM[p]}-{SYM[q]}': round(float(np.median(v)), 4) for (p, q), v in sorted(pair.items())},
            'r1_element': {SYM[x]: round(v, 4) for x, v in sorted(r1.items())},
            'angle_cos_quantiles_5_25_50_75_95': {SYM[x]: [round(float(q), 3) for q in np.quantile(v, [.05, .25, .5, .75, .95])]
                                                  for x, v in sorted(cos.items()) if v}}


if __name__ == '__main__':  # self-check on a hand-checkable periodic dimer chain
    from ase import Atoms
    a = Atoms('HH', positions=[[0, 0, 0], [0.74, 0, 0]], cell=[3.0, 3.0, 3.0], pbc=True)
    i, j, d, D = edges(a)
    assert np.all((d > 0) & (d < RC)) and np.isclose(d.min(), 0.74)
    assert switch(np.array([0.0]))[0] == 1.0 and switch(np.array([5.0]))[0] == 0.0
    b = bounds([a])
    assert b['r1_pair'] == {'H-H': 0.74} and b['r1_element'] == {'H': 0.74}
    res = np.array([[1.0, 0, 0], [-1.0, 0, 0]])  # pulls the pair together: +1 projected toward the partner
    t = force_table([a], [res], np.array([0.5, 0.75, 1.0]))['H-H']
    assert t['mean_projected_residual_eV_per_A'][0] == 1.0 and t['neighbour_pairs'][0] == 2  # [0.5,0.75) bin, both directions
    assert t['residual_force_rms_eV_per_A'] == round(np.sqrt(2 / 6), 4)
    print('ok')
