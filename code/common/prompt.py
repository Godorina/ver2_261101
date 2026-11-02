"""Common seed-prompt skeleton (SPEC.md §3). System text (goal, domain, target table) comes from systems/*. r1 description is the two-way one."""
import json

SYSTEM = ('You are a physicist writing an explicit energy correction for a frozen interatomic potential. '
          'You answer with one JSON object only and never write code.')

FORM = '''f = sum over atoms i of c_{Z_i} + sum over the physics terms you choose (1..8 terms, each a JSON object):
  {"type":"born_mayer","pair":"X-Y","B":<eV>,"rho":<A>}             B exp(-(r - r1_XY)/rho), B in [-1,1], rho in [0.1,1]
  {"type":"morse","pair":"X-Y","D":<eV>,"a":<1/A>,"r0":<A>}         D [(1 - exp(-a (r - r0)))^2 - 1], D in [-1,1], a in [0.5,5], r0 in [0.8,1.2] x r1_XY
  {"type":"eam","element":"X","A":<eV>,"beta":<1/A>}               -A sqrt(rho_i) for X atoms, rho_i = sum_j exp(-beta (r_ij - r1_X)), A in [-1,1], beta in [0.5,5]
  {"type":"angle","center":"X","lam":<eV>,"cos0":<number>}          lam sum over neighbour pairs j<k of X atoms (cos theta_jik - cos0)^2, lam in [-1,1], cos0 in [-1,1]
Pair terms are summed over every pair of atoms of the two elements within 5 A; all terms go smoothly to zero at 5 A
(angles use neighbours within 1.15 to 1.35 x r1_X). r1_XY and r1_X are the first-neighbour distances listed below.
At most one term of each type per pair or element. These terms correct the residual E_DFT - E_NN; they are not a full
potential, so their energies should be of the size of the residuals.
Forces are F = F_NN - df/dR. c_Z alone never changes forces; every physics term does.
Goal: a candidate counts only if BOTH its example energy error (mean |E_DFT - E_pred| per atom) AND its example force error
(mean over structures of the mean atomic |F_DFT - F_pred|) are lower than those of the original potential on the same
examples. Among those, the lowest force error wins.'''
BASE_GOAL = 'Among those, the lowest force error wins.'
DISP = ('  {"type":"dispersion","pair":"X-Y","C6":<eV A^6>,"R0":<A>}       -C6 / (r^6 + R0^6), C6 in [0,200], R0 in [0.8,1.2] x r1_XY '
        '(London dispersion with Becke-Johnson damping; attractive only)\n')
ANCHOR = 'The structures you will be evaluated on are different structures of the same elements; their DFT energies are not available.\n'


def probe(where):
    return ('Range check: the evaluation structures can contain pair distances that do not occur in the examples' + where +
            ', down to about 0.9 x the sum of covalent radii. For every term, the force on an isolated pair of its two elements is computed\n'
            'from 0.9 x (sum of covalent radii) to 5 A; a candidate counts only if this force stays at or below 3 eV/A for every term.\n'
            'Prefer terms that stay smooth at short distances.')


def enc(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def seed(symbols, ref, table, bounds, ftable, bins, goal, domain, target, disp=False):
    """symbols: element symbols by Z; ref: {symbol: BAM per-element value}; goal replaces the base goal sentence (or the whole Goal paragraph)."""
    form = FORM.replace('Pair terms are summed', DISP + 'Pair terms are summed') if disp else FORM
    form = form[:form.index('Goal:')] + goal if goal.startswith('Goal') else form.replace(BASE_GOAL, goal)
    schema = ('{"candidates":[{"c":{' + ','.join(f'"{s}":<number>' for s in symbols) + '},'
              '"terms":[{"type":"morse","pair":"X-Y","D":<number>,"a":<number>,"r0":<number>}],"rationale":"<one short sentence>"}]}')
    return (f'''Task: write an explicit energy correction f for a frozen neural interatomic potential.
E_pred = E_NN + f. E_NN is the raw neural-network energy of a structure.
You must write every number yourself. Nothing is fitted after your answer: your numbers are used exactly as written.
{form}
The correction must reproduce E_DFT - E_NN of the example structures below. Use enough decimal places (at least 4 for c_Z).
{ANCHOR}{domain}
The original potential uses fixed per-element values (node_enr_avg + e_corr), in eV: {enc(ref)}.
With c_Z equal to these values and no other terms, f reproduces the original potential exactly. Each example also lists E_DFT - E_BAM, the original potential error. You may start from these values and change them.

Examples ({len(table)} structures):
{enc(table)}

First-neighbour distances in the examples (r1_XY: median, over X atoms and over Y atoms, of the distance to the nearest atom of the other element,
or for X-X over X atoms of the nearest other X; r1_X: median nearest-neighbour distance of X atoms) and quantiles of cos theta between neighbours of X within 1.35 x r1_X, all in Angstrom:
{enc(bounds)}
Distance histograms count directed periodic neighbours with bin edges [0,1,1.5,2,2.5,3,3.5,4,4.5,5] Angstrom. Radial projections are projections of atomic residual forces F_DFT - F_NN.

Residual forces F_DFT - F_NN of the original potential on all examples, per centre-neighbour element pair (key X-Y: X atoms, projected toward Y neighbours): mean projection of the atom's residual force on the unit vector from the atom to each neighbour, per distance bin with edges {bins.tolist()} Angstrom (positive: the true force pulls the atom toward neighbours at that distance more than E_NN does, so the correction should add attraction there), the number of neighbour pairs per bin, and the RMS of residual force components:
{enc(ftable)}
{target}
Return exactly this JSON shape with 1..5 distinct candidates, no markdown:
{schema}
Each rationale at most 200 characters.''')


if __name__ == '__main__':  # self-check: goal replacement (sentence or whole paragraph) and dispersion insertion happen once
    import numpy as np
    t = seed(['H'], {'H': -1.0}, [], {}, {}, np.array([1.0, 1.25]), 'NEW GOAL.', 'DOMAIN\n', 'TARGET\n', disp=True)
    assert t.count('NEW GOAL.') == 1 and BASE_GOAL not in t and t.count('"type":"dispersion"') == 1
    assert t.index(ANCHOR) < t.index('DOMAIN') < t.index('Examples (') < t.index('TARGET') < t.index('Return exactly')
    s = seed(['Na'], {'Na': -1.0}, [], {}, {}, np.array([1.0]), 'Goal (other): X.', '', '')
    assert s.count('Goal') == 1 and 'BOTH its example energy error' not in s
    print('ok')
