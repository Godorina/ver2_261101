"""BAM-MP-core raw network energy E_NN and forces F_NN (no element reference sum), CPU float64 EMA. SPEC.md §1."""
import hashlib, os, re
from pathlib import Path
import numpy as np
import torch

CKPT_SHA = 'e837d5120650c84313b33a9e0c40a9b0f3c952a256ffa1c932e6fbb4882406f5'
CKPT = Path(os.environ.get('BAM_CKPT', Path(__file__).resolve().parents[2] / 'sources/past/mlp-icl-llmsr/data/checkpoints/bam-mp-core/model.pkl'))


def identity(a):
    """Old cache key: sha256 of numbers <i8, positions <f8, cell <f8, pbc u1 (-0 -> 0). SPEC §1."""
    h = hashlib.sha256()
    for arr, dt in ((a.numbers, '<i8'), (a.positions, '<f8'), (a.cell.array, '<f8'), (a.pbc, 'u1')):
        c = np.array(arr, dtype=dt, order='C', copy=True)
        if c.dtype.kind == 'f':
            c[c == 0] = 0.0
        h.update(c.tobytes())
    return h.hexdigest()


def load():
    """Frozen calculator with EMA weights in float64, and per-element reference values ref[Z] (eV)."""
    path = CKPT
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CKPT_SHA, 'BAM checkpoint sha mismatch'
    from bam_torch.tase.base_calculator import RACECalculator
    from e3nn import o3
    j = torch.load(path, map_location='cpu', weights_only=False)['input.json']
    j['predict']['model'] = str(path)  # stored as relative 'model.pkl'; some BAM-torch versions read only this
    calc = RACECalculator(json_data=j, device='cpu')
    model, ck = calc.model, calc.model_ckpt
    params = dict(model.named_parameters())
    shadows = ck['ema_state']['shadow_params']
    assert [k for k in ck['params'] if k in params] == list(params), 'checkpoint parameter order'
    assert len(shadows) == len(params) and all(v.shape == s.shape and torch.isfinite(s).all() for v, s in zip(params.values(), shadows))
    with torch.no_grad():
        if all(torch.equal(v.detach().cpu(), ck['params'][k].cpu()) for k, v in params.items()):  # regular weights loaded
            for v, s in zip(params.values(), shadows):
                v.copy_(s.to(dtype=v.dtype))
        assert all(torch.equal(v.detach().cpu(), s.cpu().to(v.dtype)) for v, s in zip(params.values(), shadows)), 'not EMA'
        model.eval().double().requires_grad_(False)
        for name, b in model.named_buffers():  # float32-rounded Wigner 3j constants -> exact float64
            m = re.search(r'(?:^|\.)_w3j_(\d+)_(\d+)_(\d+)$', name)
            if m:
                exact = o3.wigner_3j(*map(int, m.groups()), dtype=torch.float64)
                assert torch.equal(b, exact) or torch.equal(b, exact.float().double()), name
                b.copy_(exact)
    assert calc.element_wise
    ref = {int(z): float(calc.enr_avg_per_element[i]) + float(calc.e_corr[i]) for z, i in calc.uniq_element.items()}
    return calc, ref


def energy_forces(calc, atoms):
    """E_NN (eV), F_NN = -dE_NN/dR (eV/A): library graph, original float64 coordinates."""
    from bam_torch.utils.utils import get_graphset_to_predict
    from torch_geometric.loader import DataLoader
    a = atoms.copy(); a.calc = None
    g = next(iter(DataLoader(get_graphset_to_predict([a], calc.json_data['cutoff'], calc.uniq_element, False))))
    pos = torch.tensor(a.positions, dtype=torch.float64, requires_grad=True)
    g.positions = pos
    g.cell = torch.tensor(a.cell.array, dtype=torch.float64).view(1, 3, 3)
    g.edges = g.edges.to(torch.float64)
    g.node_attrs = torch.nn.functional.one_hot(g.species, num_classes=calc.model.num_species).to(torch.float64)
    e = calc.model(g, backprop=True)['energy'].reshape(())
    return float(e), -torch.autograd.grad(e, pos)[0].numpy()


def run(frames, path):
    """[(E_NN, F_NN)] and ref, cached in one npz keyed by identity and pinned to checkpoint sha + torch version."""
    path = Path(path)
    pin = hashlib.sha256(CKPT.read_bytes()).hexdigest() + ' torch ' + torch.__version__ + ' cpu float64 ema'
    db = dict(np.load(path)) if path.exists() else {}
    if str(db.get('pin', '')) != pin:
        db = {'pin': np.array(pin)}  # different model or conditions: recompute everything
    keys = [identity(a) for a in frames]
    todo = [(k, a) for k, a in zip(keys, frames) if 'E_' + k not in db or 'F_' + k not in db]
    if todo or 'ref' not in db:
        torch.set_num_threads(int(os.environ.get('BAM_THREADS', 1)))  # old runs used 1 (SPEC §0)
        calc, ref = load()
        db['ref'] = np.array(sorted(ref.items()))
        for i, (k, a) in enumerate(todo, 1):
            db['E_' + k], db['F_' + k] = energy_forces(calc, a)
            print(f'BAM {i}/{len(todo)}', flush=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, **db)  # ponytail: one npz rewritten per call, split it if structure counts reach 1e4
    ref = {int(z): float(v) for z, v in db['ref']}
    return [(float(db['E_' + k]), db['F_' + k]) for k in keys], ref


if __name__ == '__main__':  # self-check against the old cache values in SPEC §5
    from ase.io import read
    root = Path(__file__).resolve().parents[2] / 'data'
    cr = [a for a in read(root / '2_catalyst/examples.traj', ':') if a.info['group'] == 'Cr'][0]
    h2 = read(root / '2_catalyst/H2.traj')
    calc, ref = load()
    e, f = energy_forces(calc, cr)
    assert identity(cr).startswith('8eb4588c1ff4')
    assert abs(e - -36.28439344640652) < 1e-5, e
    e2, _ = energy_forces(calc, h2)
    E_bam = e2 + sum(ref[int(z)] for z in h2.numbers)
    print('ok', e, f.shape, 'H2 E_NN', e2, 'E_BAM', E_bam)
