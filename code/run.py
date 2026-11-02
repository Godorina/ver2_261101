"""Seed prompt for one context, no LLM call (SPEC.md). Layers: common/ (structure energies, descriptors, prompt skeleton)
-> systems/ (system quantities and text) -> this file (wiring).
    python code/run.py 2_catalyst Co --n 20      # group = metal / MOF / surface; sodium has one context: python code/run.py 1_sodium
Writes outputs/<app>/<group>/n<N>/{prompt.txt, examples.json}; BAM values cached in outputs/<app>/bam.npz."""
import argparse, json
from pathlib import Path
from ase.data import chemical_symbols as SYM
from common import bam, features as ft, prompt as pr
from systems import adsorption, sodium

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = {'1_sodium': sodium, '2_catalyst': adsorption, '3_MOF': adsorption, '4_CF4': adsorption}


def main(app, group, n):
    S = SYSTEMS[app]
    frames = S.examples(app, group, n)
    ids = [a.info['frame_id'] for a in frames]
    ef, ref = bam.run(frames, ROOT / 'outputs' / app / 'bam.npz')                      # common: structure energies
    E_dft = {k: a.get_potential_energy() for k, a in zip(ids, frames)}
    E_bam = {k: e + sum(ref[int(z)] for z in a.numbers) for k, a, (e, _) in zip(ids, frames, ef)}
    p = S.prompt_parts(app, frames, E_dft, E_bam)                                       # system: quantities and text
    table = [dict(ft.example_entry(i, a, e, f, ref), role=r) for i, (a, (e, f), r) in enumerate(zip(frames, ef, p['roles']), 1)]
    zs = sorted({int(z) for a in frames for z in a.numbers})
    text = pr.seed([SYM[z] for z in zs], {SYM[z]: round(ref[z], 6) for z in zs}, table, ft.bounds(frames),
                   ft.force_table(frames, [a.get_forces() - f for a, (_, f) in zip(frames, ef)], p['bins']), p['bins'],
                   p['goal'], p['domain'], p['target'], p['disp'])
    out = ROOT / 'outputs' / app / (group or 'all') / f'n{n or len(frames)}'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'prompt.txt').write_text(pr.SYSTEM + '\n\n' + text)
    (out / 'examples.json').write_text(json.dumps({'ids': ids, 'E_NN': [e for e, _ in ef], 'ref': ref}, indent=1))
    print(out / 'prompt.txt', len(text), 'chars')


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('app', choices=list(SYSTEMS))
    a.add_argument('group', nargs='?')
    a.add_argument('--n', type=int)
    a = a.parse_args()
    assert (a.app == '1_sodium') == (a.group is None) == (a.n is None), 'adsorption apps need group and --n; sodium needs neither'
    main(a.app, a.group, a.n)
