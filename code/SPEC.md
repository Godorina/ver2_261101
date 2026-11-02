# SPEC: LLM 호출 직전까지의 계약

Phase 0 산출물. 옛 코드에서 **무엇을 계산하고 무엇을 프롬프트에 넣는지**만 뽑았다. 옛 코드는 여기 적힌 행만 참고하고 복사하지 않는다.
경로 약칭: `R` = `/home/hgpark/whlee/hgpark/bam-icl-release`, `C` = `R/code/common/core`, `CAT` = `R/results/2_catalyst/code/code`.

## 0. 환경
- Python: **`ver2_261101/env/bin/python`** (py3.11, torch 2.8.0+cu128, e3nn 0.5.8, torch-geometric 2.7.0, ase 3.26, numpy 1.26). `bam_torch_catalyst`를 오프라인으로 복제(conda clone)한 뒤, bam_torch만 `ver2_261101/BAM-torch`(Godorina/BAM-torch f9396a8, 2026-08-25)의 editable 설치로 바꿨다. 2026-11-01 사용자 결정. 이 조합의 `E_NN`은 옛 캐시와 모든 자릿수가 일치한다. 기존 `bam_torch-260616` 환경은 editable 원본이 사라져 깨졌고, Catalyst BAM-torch는 이 체크포인트와 호환되지 않는다(readout bias). 옛 캐시는 torch 2.11.0+cu130으로 만들었다.
- ckpt: `BAM_CKPT=/home/hgpark/whlee/hgpark/past/mlp-icl-llmsr/data/checkpoints/bam-mp-core/model.pkl`, sha256 `e837d5120650c84313b33a9e0c40a9b0f3c952a256ffa1c932e6fbb4882406f5` (`C/analysis/llmsr_bam_terminals.py:35`).
- CPU, float64. 옛 코드는 `torch.set_num_threads(1)`을 썼다(`C/al50.py:75`). 기본값은 1이고 `BAM_THREADS`로 바꾼다. Phase 3의 bam.npz 844개 구조(대부분 4·8 스레드로 계산)도 옛 캐시와 |ΔE_NN| ≤ 5.7e-14 eV, |ΔF_NN| ≤ 5.3e-15 eV/Å로 일치했다(2026-11-02).
- 코드 구조: `code/common/`(구조 에너지·기술자·프롬프트 골격, 시스템을 모름) ← `code/systems/`(`adsorption.py`, `sodium.py`: `examples`, `quantity`, `prompt_parts`) ← `code/run.py`(연결).

- 데이터: `data/`는 `code/make_data.py`가 만든다(`.traj`는 무손실, JSON은 예제 선택 목록). 원천 트리의 절대경로는 이 파일 맨 위 한 줄에만 있다. 이것이 'code/에 절대경로 금지' 규칙의 유일한 예외다.

## 1. BAM: E_NN, F_NN
옛 경로: `al50.raw_cache` (`C/al50.py:74-121`) → `LiveBAMScalars.raw_energy_forces_geometry` (`C/analysis/llmsr_bam_terminals.py:331-346`).
1. 계산기 생성: `RACECalculator(model=ckpt, device="cpu")` (`:151-160`). 파라미터가 regular이면 EMA shadow로 교체한다(`load_checkpoint_ema`, `:112-127`: `ckpt["ema_state"]["shadow_params"]`를 `named_parameters()` 순서대로 copy).
2. `model.eval().double()`, `requires_grad_(False)` (`:188-190`). e3nn `_w3j_*` 버퍼를 `o3.wigner_3j(..., float64)`로 다시 채운다(`restore_analytic_precision`, `:84-109`. float32로 반올림된 상수의 정밀도 복원).
3. forward (`:207-247`, `:264-290`):
   - `get_graphset_to_predict([atoms], json_data["cutoff"], uniq_element, False)`로 그래프 구조만 만든다.
   - `graph.positions`를 float64 원좌표(`requires_grad=True`)로 교체한다.
   - `graph.cell`은 float64 `(1,3,3)`, `graph.edges`는 float64, `graph.node_attrs`는 `one_hot(species, num_species)` float64로 둔다.
   - `model(graph, backprop=True)["energy"]`가 곧 **E_NN**이다(원소 기준합이 들어가지 않은 값).
   - **F_NN = −∂E_NN/∂R** (autograd).
4. 원소 기준합: `R_old = Σ_i (enr_avg_per_element[s_i] + e_corr[s_i])`, `s_i = uniq_element[Z_i]` (`:335-340`). `E_BAM = E_NN + R_old`. 기준합은 좌표와 무관하므로 `F_BAM = F_NN`이다.
   - 원소별 값 `ref[Z] = enr_avg_per_element[idx] + e_corr[idx]` (`:321-329`)는 track A 프롬프트에 그대로 들어간다.
- 주의: `RACECalculator.get_potential_energy()`의 총에너지에는 기준합이 포함된다. 옛 코드는 라이브러리가 만든 그래프 좌표가 반올림된다는 이유로 원좌표를 float64로 덮어쓴다(`:207-226`). **위 3번 경로를 따른다.** 라이브러리 경로의 dtype은 미확인이다.
- 원자 수 상한: 옛 엔진은 256이고 run_rand20은 300으로 올려 썼다(`R/code/common/runner/run_rand20.py:14-15`). CF4 a001은 bare slab 270원자, slab+CF4 275원자이므로 상한은 두지 않는다.

**검증용 옛 캐시** (모두 `<dir>/fe38d25ef455347d51c68810454a3a0083ecea10fad8494a86681d27de6a33fa/<identity>.json`, 키 `E_nn`, `F_nn`, `E_ref_old`, `E_corr_old`, `E_bam`):

| 응용 | 캐시 dir |
|---|---|
| 1_sodium | `/home/hgpark/whlee/hgpark/mlp-icl-ft-check-v1/hull_nmo/mixprompt8/raw-cache` |
| 2_catalyst | `R/results/2_catalyst/data/data/raw-cache` |
| 3_MOF | `R/results/3_mof/data/method4-mof/raw-cache` |
| 4_CF4 | `R/past/4_cf4/pairs/raw-cache` |

`identity = sha256( numbers as <i8 ‖ positions <f8 ‖ cell <f8 ‖ pbc u1 )`. 각 배열은 C-order로 두고, float의 −0은 0으로 정규화한다(`C/structure_input.py:27-61`). 모든 구조가 3D 주기 경계를 가정한다.

## 2. 기술자 (프롬프트용)
대상은 컨텍스트의 예제 구조들이다. query 구조는 쓰지 않는다.
- **이웃 정의(모든 기술자 공통)**: 주기 이웃의 방향성 쌍 i→j이고 벡터는 `r_j − r_i + shift·cell`, 조건은 **`0 < r < 5` Å(strict)**다. 같은 원자의 다른 주기 이미지는 포함하고 자기 자신(shift 0)만 뺀다(`C/analysis/llmsr_dsl.py:185-201,233-247`). 정상 입력에서는 `ase.neighborlist.neighbor_list('ijdSD', atoms, 5.0)`과 같다. 옛 그래프는 0.3 Å 미만 거리가 하나라도 있으면 **입력 전체를 거부**했다(`:233-239`). 새 코드도 그 경우 예외를 낸다. bounds(r1)는 원래부터 ASE neighbor_list를 썼다.
- **잔차**: `ΔE = E_DFT − E_NN` (eV)와 `/N`. track A에서는 `E_DFT − E_BAM`도 넣는다(`C/direct.py:322-340`). 반올림은 6자리다.
- **구조 요약** (`C/al50.py:124-147`, 예제마다):
  - `distance_pair_histogram`: 원소쌍 `"Za-Zb"`(Za≤Zb, 원자번호 문자열)별 **방향성** 이웃 거리 히스토그램. bin edge `[0,1,1.5,2,2.5,3,3.5,4,4.5,5]` Å. 이웃이 이미 r<5로 걸러져 있어서 마지막 bin의 우단 포함 여부는 영향이 없다. radial 평균은 `a≤r<b`.
  - `mean_smooth_coordination`: 원자별 Σ_j sw(r_ij)의 평균. `sw = (1−x)^3 (1+3x+6x^2)` (r<5일 때, 아니면 0). `x = r^2 / ((ρ+s)(√(5^2+s^2) − s))`, `ρ = √(r^2+s^2)`, `s = 0.05` (`C/analysis/llmsr_dsl.py:14-16,108-116`).
  - `force_residual_rms_eV_per_A`: `√mean((F_DFT − F_NN)^2)`, 성분 전체에 대한 값.
  - `radial_projection_bin_means`: 이웃쌍 (i→j)마다 `(F_DFT−F_NN)_i · û_ij`의 위 bin별 평균. 비어 있으면 null.
- **힘 표** (`C/force_table.py`; 예제 전체 합산; seed에서는 잔차가 `F_DFT − F_NN`, `C/direct.py:285-294`):
  - 키는 원소쌍 `"X-Y"`(X=중심, Y=이웃; 방향성)다(`by_pair=True`). **실제로 나타난 (중심, 이웃) 쌍만** 키가 되고, 예제 전체로는 그 합집합이다. bin은 `np.digitize`로 `[left,right)`이다.
  - bin은 `arange(1.0, 5.0001, 0.25)`(base, `:8`)이다. **흡착 3응용은 `arange(0.5, 5.0001, 0.25)`** (`CAT/run_cat_deh.py:25`).
  - 출력(`:39-48`): `mean_projected_residual_eV_per_A`(bin별 합/개수, 4자리, 빈 bin은 null), `neighbour_pairs`, `residual_force_rms_eV_per_A = √(Σsq / (3·atoms))`, 4자리. Σsq와 atoms는 **그 키가 나타난 구조들에서만** 해당 구조의 X 원자 전체를 합산한다. 그래서 같은 X라도 Y에 따라 값이 다를 수 있다(`C/force_table.py:27-34,38-47`).
- **r1과 각도** (`R/code/common/physics/terms.py:48-73`, `ase.neighborlist`, rc=5 Å):
  - `r1_pair["X-Y"]`: 원자번호로 정렬한 키 X-Y에 대해, 모든 X 원자의 최근접 Y 거리와 모든 Y 원자의 최근접 X 거리를 **함께** 모은 뒤 median(동종쌍은 원자마다 한 번), 4자리. 5 Å 안에 이웃이 없는 원자는 빠진다.
  - `r1_element[X]`: X 원자들의 최근접 거리 median, 4자리.
  - 옛 프롬프트 문구는 r1_XY를 "median over X atoms of the nearest Y"(단방향)로 설명했지만 실제 계산은 양방향이다(`C/direct.py:359-362`). **새 프롬프트는 양방향 정의를 바르게 쓴다**(옛 프롬프트와 다른 정보 차이).
  - `angle_cos_quantiles_5_25_50_75_95[X]`: X 중심에서 `d < 1.35·r1_X`인 이웃쌍의 cos θ 분위수, 3자리. 필터에는 **반올림 전** r1_X를 쓴다.
  - 반올림은 Python `round()`다. track A `ref`도 `round(v,6)`이며 고정소수점 표기가 아니다.
- 프롬프트 내 JSON 직렬화: `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False)` (`C/llm_dispatch.py:22-23`). NaN이나 inf가 있으면 예외를 낸다.

## 3. 프롬프트 (base, seed 단계)
골격은 `C/direct.py:342-393`이다. 순서는 다음과 같다.
1. Task 문단: `E_pred = E_NN + f`, "every number yourself / nothing is fitted".
2. `FORM` (`terms.py:187-200`): **전문을 그대로 쓴다**(13줄 텍스트이며 식, JSON 필드, 범위, 중복 금지, `F = F_NN − df/dR`, "잔차 보정이지 전체 퍼텐셜이 아님"을 담고 있다). 프롬프트 계약이지 코드 이식이 아니다. 요점:
   - B, D, A, λ, cos0 ∈ [−1,1]; ρ ∈ [0.1,1]; a, β ∈ [0.5,5]; r0 ∈ [0.8,1.2]·r1_XY. r0 범위는 **반올림된** r1_XY에 0.8과 1.2를 곱한 뒤 다시 4자리로 반올림한다(`terms.py:120-124`; 검사는 Phase 5).
   - Task 문단에는 "Use enough decimal places (at least 4 for c_Z)"가 들어간다(`C/direct.py:346-350`). `|c_Z| ≤ 100`은 파서의 제약일 뿐 프롬프트 문구는 아니다.
   - FORM은 EAM을 `sqrt(rho)`로 적지만, 실제 평가는 `sqrt(rho + 1e-12)`다(`terms.py:159-166`; Phase 5).
   - 항은 최대 8개다(`MAX_TERMS`). 스위치는 4.5→5 Å, 각도항은 1.15→1.35·r1_X.
   - Goal 문장: E·F 오차가 모두 BAM보다 낮아야 하고, 그중 F 오차가 최소인 후보가 선택된다.
3. 평가 구조 안내 문장.
4. track A: 원소별 `ref[Z]`(6자리)와 "c_Z = ref면 BAM 재현".
5. `Examples (N structures):` 뒤에 §2 예제 표 JSON.
6. r1과 각도 JSON(설명 문장 포함), 히스토그램과 radial projection 설명, 힘 표 JSON(설명 문장 포함).
7. 응용별 블록(§4). 옛 코드는 이를 세 군데에 나눠 넣었다: Goal 문장은 FORM 안에서 교체, 도메인 문단은 3번 바로 뒤, 목표량 표는 6번 뒤(`CAT/run_cat_deh.py:78-95`, range check는 Goal 부분, `CAT/run_cat_deh2.py:48-56`). **새 코드도 이 위치를 따른다.** 문구는 바이트 단위로 같을 필요가 없다(계획 §3 Phase 3).
8. 응답 스키마: `{"candidates":[{"c":{...},"terms":[...],"rationale":"..."}]}`, 후보 1..5개, rationale ≤200자.
- SYSTEM: "You are a physicist ... one JSON object only and never write code." (`:56-57`)
- refine 단계(`history_for`)는 LLM 응답이 있어야 만들 수 있으므로 **Phase 5로 넘긴다**.

### FORM 전문 (`terms.py:187-199`, `%d` → 8)
```
f = sum over atoms i of c_{Z_i} + sum over the physics terms you choose (1..8 terms, each a JSON object):
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
examples. Among those, the lowest force error wins.
```

## 4. 응용별 차이

### 흡착 3응용 (공통 템플릿, `CAT/run_cat*.py`)

| | 2_catalyst | 3_MOF | 4_CF4 |
|---|---|---|---|
| 그룹(컨텍스트) | metal ∈ {Co,Fe,Cr,Ir,Pt} | MOF 33개 | surface ∈ {g110,g100,a001} |
| 예제 | pair마다 (slab, slab+H) | 공유 bare MOF 1 + MOF+CO2 N | 공유 bare slab 1 + slab+CF4 N |
| 기체 | H2 (`inputs_h2/H2.extxyz`) | CO2 (forces 0, 형상 가정) | CF4 (DFT single point) |
| 목표량 | `dE_H = E(slab+H) − E(slab) − ½E(H2)` | `E_ads = E(MOF+CO2) − E(bare) − E(CO2)` | `E_ads = E(slab+CF4) − E(slab) − E(CF4)` |
| N | 20/10/5 (`split.json` subsets, `CAT/run_cat.py:20,35-49`) | 20/10/5 | 10/8/6, 5, 3 |
| frame id | `<M>-pair:p<k>:slab`, `...:slab-H`, `H2:dft-relaxed` | `<MOF>-pair:ref:mof`, `...:p<k>:mof-CO2`, `CO2:gas` | `...:ref:slab`, `...:p<k>:slab-CF4`, `CF4:gas` |
| 도메인 문단 | `CAT/run_cat_deh.py:78-83` | `R/results/3_mof/code/method4-mof-disp/run_cat_deh.py` `CAT` | `R/results/4_cf4/code/src/run_cat_deh.py` `CAT` |

- 예제 수: 촉매는 N + 기체 1. MOF와 CF4는 loaded N + 공유 bare 1 + 기체 1 = **N+2**.
  - 촉매의 N은 **구조 수**(slab 또는 slab+H)이지 pair 수가 아니다.
  - 선택은 `split.json`의 `subsets[str(N)].train` 다음에 `.val`을 **정렬하지 않고 이어 붙인다**(없으면 `train_idx[:nt]+val_idx[:nv]`). MOF와 CF4의 bare(frame 0)는 이 인덱스 목록에 들어 있다.
- **순서와 번호**: 위 순서대로 예제를 놓고 기체를 **마지막에** 붙인다. `ex01`부터 차례로 번호를 준다(`C/direct.py:322-331`). 소듐은 `examples.json` 순서를 그대로 쓴다.
- **pair와 role**: 원래 p 번호를 숫자순으로 정렬한 뒤 **완전한 pair에만** 1부터 다시 번호를 준다.
  - role은 촉매 `slab of pair j` / `slab+H of pair j` / `H2 molecule` / `slab (no partner)`, MOF `bare MOF (reference shared by every pair)` / `MOF+CO2 of pair j` / `gas CO2 molecule`, CF4는 MOF와 같은 꼴로 `bare slab ...` / `slab+CF4 of pair j` / `gas CF4 molecule`이다. 짝이 없는 예제의 fallback은 촉매 `slab (no partner)`, MOF와 CF4 `unpaired`다. 촉매에서는 정상적으로 발생한다(예: N=5이면 짝 없는 frame이 생긴다). MOF와 CF4에서는 bare와 기체가 항상 있으므로 정상 입력에서 발생하지 않는다(`CAT/run_cat_deh.py:27-34,64-68`, MOF와 CF4는 각 `run_cat_deh.py`의 `pairs_of`와 `example_table`).
- 기체 입력: H2는 `R/results/2_catalyst/data/data/inputs_h2/H2.extxyz`, CO2는 `R/results/3_mof/data/method4-mof/inputs_co2/CO2.extxyz`, CF4는 `R/past/4_cf4/pairs/inputs_cf4/CF4.extxyz`이다. 에너지와 힘을 그대로 읽는다(CO2 힘은 0).
- 추가 표(`CAT/run_cat_deh.py:64-76`): pair마다 `{pair, <bare 키>, <loaded 키>, <목표>_DFT_eV, <목표>_BAM_eV, delta_eV}`. 키는 촉매 `slab`, `slab+H`, `dE_H_DFT_eV`, `dE_H_BAM_eV`; MOF `bare_MOF`, `MOF+CO2`, `E_ads_DFT_eV`, `E_ads_BAM_eV`; CF4 `bare_slab`, `slab+CF4`, `E_ads_DFT_eV`, `E_ads_BAM_eV`이다. 각 값은 4자리로 반올림하고, mean |delta|는 **반올림된 delta**로 계산해 4자리로 쓴다. 기체의 ex 번호를 표 설명에 넣는다.
- Goal 교체(`:84-86`): E·F·목표량 오차가 모두 BAM보다 낮아야 하고, 그중 목표량 오차가 최소인 후보가 선택된다.
- Range check 문단(`CAT/run_cat_deh2.py:23,48-52`): 프롬프트 문구로는 "고립 원자쌍의 힘이 0.9·(공유결합 반지름 합)~5 Å에서 ≤ 3 eV/Å"이다. 실제 검사는 이 구간 `linspace(...,80)`의 80개 점에서 하며, angle 항은 0으로 친다. 검사 자체는 LLM 응답 평가에 속하므로 Phase 5에서 다룬다. 응용마다 괄호 속 예시만 다르다.
- **MOF는 dispersion 변형을 기본으로 한다**(원고 본 결과). 원천 스위치는 다른 pair 항과 같은 S(r)(4.5→5 Å)이고, 평가할 때 방향성 쌍 합에 ½을 곱한다(Phase 5). FORM에 한 줄을 추가한다: `{"type":"dispersion","pair":"X-Y","C6":..,"R0":..}  −C6/(r^6+R0^6), C6∈[0,200], R0∈[0.8,1.2]·r1_XY` (`R/results/3_mof/code/method4-mof-disp/run_cat_disp.py:22-27`).

### 1_sodium (`R/results/1_sodium/code/mixprompt8/run_mix8.py`)
- 예제 21개(`examples.json`): x 6개 × Na 배열 3개, end member MnO2(`hull:0139`)와 NaMnO2(**`hull:0080`**), Na metal(`hull:0732`). 위치, `E_dft`, `F_dft`가 레코드 안에 들어 있다.
  - ⚠ `run_mix8.py:30`의 `E1='hull:0336'`은 `:469`에서 `'hull:0080'`으로 덮어쓰인다. `examples.json`의 `end_members`도 `['hull:0139','hull:0080']`이다(codex 교차검토로 정정).
  - Na metal은 E_mix의 기준점이 아니다. 전압 계산(`:468` 이후)과 원소 Na 정보에 쓰인다.
- 목표량(`:66-75`): `E_mix(x) = 1000·(E/nMn − x·E(NaMnO2)/nMn' − (1−x)·E(MnO2)/nMn'')` meV/f.u. 하한 볼록껍질은 `lower_hull`, `E_above_hull = E_mix − hull(x)`.
- 추가 표(`:97-114`): Na metal과 end member 2개를 **뺀** 완화 구조만 `(x, phase)` 순으로 정렬해 넣는다. 필드는 `{example, x(4자리), phase, E_mix_DFT, E_mix_BAM, delta, E_above_hull_DFT, E_above_hull_BAM}`(에너지 2자리).
  - mean |delta|는 2자리로 반올림한 delta로 계산한다. mean |E_ah err|는 각각 2자리로 반올림한 값의 차이로 계산한다. hull score = ½(둘의 합). DFT와 BAM의 hull 꼭짓점 목록도 넣는다.
  - lower hull(`:52-72`): x는 `round(x,6)`으로 묶어 최저값만 남긴다. 외적이 `<=0`이면 pop한다. 꼭짓점 사이는 선형 보간한다. 끝점 (0,0), (1,0)을 넣는다.
  - role은 21개 예제 모두에 `examples.json`의 `role`을 단다.
- Goal: 소듐은 "energy only"로 교체한다(`:125-133`). gate는 (1) 원자당 예제 에너지 오차 < BAM, (2) E_mix 오차 < BAM, (3) range check 통과다. 통과한 후보 중에서는 hull score가 가장 낮은 후보가 선택된다. 힘은 기록만 하고 선택에는 쓰지 않는다.
- 도메인 문단 `MIXP` (`:116-124`).
- **계약(기본값, 사용자 확인 대기)**: 이번 재작성은 소듐을 위 base + E_mix/hull 표 + Goal로 만들고 **v8 고유 장치는 넣지 않는다.** 따라서 v8 프롬프트와 같지 않고, 논문 cathode 결과의 재현을 보장하지 않는다. 제외하는 v8 장치: 항 4종 추가(shell, screened_coulomb, site, bond_valence; `terms_v4.py`), 오차 분해, 같은 x 안의 순위 표, target curve의 대칭·반대칭(tilt) 분해, 항별 효과(sensitivity) 표, "previous attempts" 문단. 기준 프롬프트는 `R/results/1_sodium/data/reference/seed_prompt_v8.paper.txt` (60 KB, 섹션은 1, 11, 20, 31, 57, 63, 66–76, 78, 89, 112–119, 127행).

## 5. 검증 기준값 (codex가 옛 캐시와 원본 traj에서 직접 읽음. 64자리 identity와 원천 frame은 `.omc/review/spec_codex.md` §4. Phase 3은 identity를 재계산해 캐시 dir에서 직접 찾으므로 접두부만 적는다)

| 구조 | identity (앞 12자리) | E_NN (eV) |
|---|---|---:|
| 촉매 `Cr/rand20.traj` #0 slab | `8eb4588c1ff4` | -36.28439344640652 |
| 촉매 #1 slab-H | `f73dab1bb2ae` | -36.225465992347026 |
| 촉매 #2 slab | `f1d1b959213e` | -37.86691919429271 |
| MOF `XAFFOB/rand20.traj` #0 bare | `958608d9406e` | -43.91745693495782 |
| MOF #1 | `c2db93795149` | -43.51251634360281 |
| MOF #2 | `06ab0f8ac403` | -43.5422996740986 |
| CF4 `a001/rand20.traj` #0 slab | `95e71f10edcb` | -265.4089516298824 |
| CF4 #1 | `05e7bcd86e45` | -259.2618295229794 |
| CF4 #2 | `46ff6274d40e` | -259.7773443542737 |
| 소듐 hull:0732 Na metal | `ad9ec18146ef` | 3.0021439121329307 |
| 소듐 hull:0139 MnO2 | `6d4d3dce9aee` | 30.349423585254343 |
| 소듐 hull:0080 NaMnO2 | `8c2dcb6c2caf` | 9.481234707437725 |

DFT 목표량 기준값:
- 촉매 Cr pair 1 dE_H = -0.54634484, pair 2 = -0.70198304 eV (H2 E = -6.98887582)
- MOF XAFFOB p1, p2 = 0.16461304684216, 0.14064819684230 eV (CO2 E = -22.990396)
- CF4 a001 p1, p2 = 4.31113552000009, 3.72042759000009 eV (CF4 E = -25.61387988)

## 6. Phase 3 대조 항목
1. 모든 구조의 `E_NN`과 `F_NN`이 옛 캐시와 일치한다(|ΔE| < 1e-5 eV, max|ΔF| < 1e-5 eV/Å). identity로 조회한다.
2. 흡착 예제의 `delta_eV`와 소듐의 `delta_E_mix`가 옛 프롬프트 값과 일치한다(소듐 BAM mean |delta E_mix| = 51.80 meV/f.u., `seed_prompt_v8.paper.txt:75`).
3. 새 prompt.txt에 §3의 1–8항과 §4의 응용별 블록이 모두 들어 있다.
