# Phase 0 독립 사양 추출

기준: 옛 소스와 데이터는 읽기 전용. 아래 `R`은 `/home/hgpark/whlee/hgpark/bam-icl-release`, `V`는 `/home/hgpark/whlee/hgpark/ver2_261101`, `S`는 `/home/hgpark/whlee/hgpark/mlp-icl-ft-check-v1/hull_nmo`의 절대경로를 뜻한다. 표의 데이터 파일 `:1`은 해당 JSON/바이너리 파일의 레코드 출처 표시이며, 바이너리의 경우 실제 텍스트 행이 아니다. 이 문서는 구현 계획이 아닌 옛 구현의 관측 계약이다.

## 1. BAM raw 에너지 및 힘

- `LiveBAMScalars(checkpoint)` → SHA256 전체 `e837d5120650c84313b33a9e0c40a9b0f3c952a256ffa1c932e6fbb4882406f5` 확인 → `RACECalculator(model=str(checkpoint), device="cpu")`; 로드가 regular 파라미터면 checkpoint `ema_state.shadow_params`를 순서·shape·유한성 검사 후 복사하고, EMA면 유지한다. 모델을 eval, frozen, `.double()`로 바꾸며 float32로 반올림된 비학습 Wigner 3j buffer는 출처 검증 후 e3nn float64 상수로 복원한다. `R/code/common/core/analysis/llmsr_bam_terminals.py:34`, `:53`, `:84`, `:112`, `:129`, `:151`, `:187`.
- `al50.geometry(record)`는 원자번호·PBC와 원래 positions/cell을 CPU float64 텐서로 만들고 positions에는 gradient를 켠다. `raw_cache` → `raw_energy_forces_geometry` → `_forward_geometry`: ASE Atoms → `get_graphset_to_predict([atoms], calculator.json_data["cutoff"], calculator.uniq_element, False)` → PyG `DataLoader`; 생성 그래프의 positions와 cell을 **원본 float64**로 덮어쓰고 edges 및 one-hot node_attrs를 float64로 전환한 후 `model(graph, backprop=True)`. 그래프를 만들 때 반올림된 좌표를 그대로 double 변환하는 것은 동일하지 않다. `prediction["energy"].reshape(())` 자체가 **E_NN**이고 `-autograd.grad(E_NN, positions)`가 **F_NN**이다. forward hook은 마지막 product의 0e feature 검증용이지 에너지에 원소 기준을 빼는 연산이 아니다. `R/code/common/core/al50.py:52`, `:70`, `R/code/common/core/analysis/llmsr_bam_terminals.py:251`, `:273`, `:283`, `:297`, `:331`.
- `E_BAM = E_NN + E_ref_old + E_corr_old`, 여기서 두 합은 각 원자의 `enr_avg_per_element[uniq_element[Z]]`, `e_corr[uniq_element[Z]]`를 각각 더한 것이다. `R_old = E_ref_old+E_corr_old`는 조성 전용이므로 force 0; `F_BAM=F_NN`. 실제 raw 경로는 element-wise `e_corr`를 요구한다. RACECalculator의 완성된 총에너지를 raw로 착각하면 안 된다. 캐시는 재조합과 원소별 reference 합을 `1e-9`로 확인한다. `R/code/common/core/analysis/llmsr_bam_terminals.py:306`, `:321`, `:331`; `R/code/common/core/al50.py:99`.
- geometry 검사는 완전 3D 주기·정상 cell을 요구한다. 단위는 energy eV/structure, force eV/Å. 실행 경로의 실제 dtype은 CPU float64 EMA이다. `R/code/common/core/analysis/llmsr_bam_terminals.py:162`, `:168`, `:179`; `R/code/common/core/al50.py:81`.

## 2. 기술자, 범위, 프롬프트

- `score`: `E_pred=E_nn+Σ_Z n_Z c_Z+Σφ`, `F_pred=F_nn−∇Σφ`; baseline은 `E_bam,F_nn`. 구조별 residual `E_DFT−E_pred`, 에너지 지표는 `mean_s(|ΔE_s|/N_s)`, 힘 지표는 `mean_s mean_i ||F_DFT,si−F_pred,si||₂`이다. 성분별 절대오차 평균이나 전체 원자 가중 평균과 다르다. `R/code/common/core/direct.py:263`, `:279`.
- 예시 표는 frame별 `exNN`, 원소별 원자 수, 총 `E_DFT−E_NN`(eV), 그 원자당 값; track A에는 `E_DFT−E_BAM`; 구조 기술자(원소쌍 거리 histogram, 평균 smooth coordination, 잔차 힘 RMS, 거리별 radial projection 평균)를 포함한다. 원소 기준 `node_enr_avg+e_corr`, 원소별 `r1`과 각도 quantile, 전체 예시를 모은 원소쌍 힘 표 및 물리식과 JSON 형식이 prompt에 실린다. refinement에서는 이전 상위 후보와 예시 오차·남은 힘 표도 추가한다. phase 0의 seed만 재현하면 history는 없어도 된다. `R/code/common/core/direct.py:322`, `:342`, `:353`, `:363`, `:374`, `:395`; 실례 `R/results/1_sodium/data/reference/seed_prompt_v8.paper.txt:1`; `V/litreview/bam-icl-overleaf-20261030/si.tex:106`.
- 거리 그래프는 주기적 directed neighbor이며 5 Å 이내. histogram 원소쌍은 **원자번호 정렬된 무방향 pair key지만 각 directed edge를 센다**; bin 경계 `[0,1,1.5,2,2.5,3,3.5,4,4.5,5]` Å. `numpy.histogram`의 마지막 bin은 우단 포함; radial 평균은 코드상 `a≤r<b`, 빈 bin `None`. 성분별 힘 RMS는 `sqrt(mean((F_DFT−F_NN)^2))`; radial 값은 중심 atom 잔차를 중심→이웃 단위벡터에 투영해 bin 평균한다. `R/code/common/core/al50.py:124`, `:128`, `:132`, `:136`, `:140`, `:147`.
- **서로 다른 스위치에 주의**: 기술자의 `mean_smooth_coordination`은 `llmsr_dsl.radial_values`의 `rho=sqrt(r²+0.05²)`, `x=r²/((rho+0.05)(sqrt(5²+0.05²)−0.05))`, `S=(1−x)^3(1+3x+6x²)` for `r<5` else 0을 각 중심의 directed edge에 합산 후 원자 평균한다. 물리 correction 항의 스위치는 4.5 Å 이하 1, 4.5–5 Å `0.5*(1+cos(pi*(r−4.5)/0.5))`, 이후 0인 별도 cosine이다. 이 둘을 동일시하면 기술자가 달라진다. `R/code/common/core/al50.py:136`; `R/code/common/core/analysis/llmsr_dsl.py:13`, `:108`; `R/code/common/physics/terms.py:27`, `:43`.
- 힘 표는 중심 원소→이웃 원소의 **방향 있는 pair**별로 `F_res(i)·(r_j+shift−r_i)/r` 합과 개수를 누적하고 bin마다 합/개수, 빈 값 null, 중심 원소의 성분 RMS `sqrt(sum(F_res²)/(3*N_center))`를 제공한다. 기본 경계 `1.0,1.25,…,5.0` Å, 구간은 `[left,right)`; 단 촉매·MOF·CF₄의 `run_cat_deh.py`는 **0.5,0.75,…,5.0**으로 전역 override한다. 계획서의 1–5 Å만 쓰면 해당 응용의 H₂ 근접거리를 놓친다. `R/code/common/core/force_table.py:8`, `:11`, `:24`, `:38`; `R/results/2_catalyst/code/code/run_cat_deh.py:24`; `R/results/3_mof/code/method4-mof/run_cat_deh.py:29`; `R/results/4_cf4/code/src/run_cat_deh.py:33`.
- `bounds`: 모든 예제 구조의 5 Å 이내 주기적 이웃에 대해 중심 X별 가장 가까운 임의 이웃 거리의 중앙값이 `r1_X`; 정렬된 XY key에 각 X의 가장 가까운 Y 거리와 각 Y의 가장 가까운 X 거리를 함께 모아 중앙값이 `r1_XY`다(동종은 각 원자 한 번). 이웃이 없는 중심은 해당 표본에서 빠진다. 두 결과는 4 decimals로 반올림한다. 중심 X에서 `r<1.35*r1_X`인 이웃 쌍의 cos(theta) quantile 5,25,50,75,95%는 3 decimals다. 출력 prompt의 ‘median over X atoms’은 이종쌍에 대해 코드의 양방향 pooling보다 불완전하다. `R/code/common/physics/terms.py:48`, `:55`, `:60`, `:63`, `:67`, `:74`; `R/code/common/core/direct.py:359`.

| 기본 항 | 파라미터 허용범위 | 출처 |
|---|---|---|
| Born–Mayer `B exp(-(r−r1_XY)/rho)` | `B∈[-1,1] eV`, `rho∈[0.1,1] Å` | `R/code/common/physics/terms.py:30`, `:187` |
| Morse `D[(1−exp(−a(r−r0)))²−1]` | `D∈[-1,1] eV`, `a∈[0.5,5] Å⁻¹`, `r0∈[0.8,1.2] r1_XY` | `R/code/common/physics/terms.py:32`, `:120`, `:189` |
| EAM `−A Σ_i sqrt(Σ_j exp(−beta(r−r1_X))S)` | `A∈[-1,1] eV`, `beta∈[0.5,5] Å⁻¹` | `R/code/common/physics/terms.py:33`, `:160`, `:190` |
| angle `lam Σ_(j<k)(cosθ−cos0)² Sa_j Sa_k` | `lam∈[-1,1] eV`, `cos0∈[-1,1]`; `Sa` 1 at ≤1.15 r1_X, cosine→0 at 1.35 r1_X | `R/code/common/physics/terms.py:28`, `:34`, `:168`, `:191` |
| 공통 | 원소 상수 `|c_Z|≤100 eV`; 기본 physics 항 1–8개, 동일 유형·대상 중복 금지; `r0` 경계는 곱한 뒤 4 decimals | `R/code/common/core/direct.py:39`, `R/code/common/physics/terms.py:87`, `:98`, `:115`, `:120` |

- MOF 논문용 variant는 추가로 `−C6/(r^6+R0^6)`에 4.5–5 Å switch를 곱한다. `C6∈[0,200] eV Å^6`, `R0∈[0.8,1.2]r1_XY`; 원문 평가 경로는 directed pair의 절반을 합산한다. Phase 2에서 이를 의도적으로 제외하면 **MOF 논문용 prompt와 수치가 일치하지 않음**을 사양에 명시해야 한다. `R/results/3_mof/code/method4-mof-disp/run_cat_disp.py:22`, `:28`, `:33`, `:41`; `R/results/3_mof/code/method4-mof/run_disp_llm.py:1`.
- sodium v8은 기본 4항 외 shell(`J [-0.3,0.3]`, `rs [2,5]`, `sigma [0.05,0.5]`), screened Coulomb(`A [0,2]`, `lam [1,10]`, 9–10 Å switch), site(`eps [-0.5,0.5]`, `rf [2.5,3.6]`), bond valence(`kappa [-0.5,0.5]`, `V0 [2.5,4.5]`, Mn–O `exp((1.753−r)/0.37)`)가 있다. 출력된 실제 seed 기준 `R/results/1_sodium/data/reference/seed_prompt_v8.paper.txt:4`, `:11`. Phase 0에 이를 기록하되 계획의 공통 prompt 단순화와 동일하지 않음을 명시한다.

## 3. 응용 목표량 및 예시

- **촉매**: `ΔE_H=E(slab+H)−E(slab)−0.5 E(H2)`, DFT/BAM/후보별로 동일 식. 잔차 조합 역시 `R_loaded−R_slab−0.5R_H2`. 금속 Co, Fe, Cr, Ir, Pt별 `rand20.traj`의 `split.json` train+val 인덱스를 쓰며 N=20/10/5는 **slab 또는 slab+H 구조 수**, 같은 configuration의 완전 pair 수가 아니다. 여기에 H₂ 1구조 추가, 에너지 −6.98887582 eV. 스크립트는 완전한 pair만 adsorption table과 평균에 쓴다. 분할 16/4, 8/2, 4/1; `subsets`가 있으면 그 인덱스를 우선한다. `R/results/2_catalyst/code/code/run_cat.py:20`, `:35`; `R/results/2_catalyst/code/code/run_cat_h2.py:1`, `:19`, `:25`; `R/results/2_catalyst/code/code/run_cat_deh.py:27`, `:36`, `:62`.
- **MOF**: `E_ads=E(MOF+CO2)−E(bare MOF)−E(CO2)`. MOF당 N=20/10/5 loaded 구조 + 공통 bare 1 + gas CO₂ 1; `rand20.traj`에 bare가 추가로 포함되며 `subsets`의 train+val로 선택한다. CO₂ DFT 에너지는 아래 기준값 참조. 원문 DFT reference에 D3 포함, 평가 CO₂ site는 별도 선택이다. `R/results/3_mof/code/method4-mof/run_cat.py:25`, `:40`, `:52`; `R/results/3_mof/code/method4-mof/run_cat_h2.py:23`, `:29`; `R/results/3_mof/code/method4-mof/run_cat_deh.py:72`, `:84`.
- **CF₄**: `E_ads=E(slab+CF4)−E(bare slab)−E(CF4)`; 동일 원소 상수는 상쇄된다. surface별 loaded g110=10, g100=8, a001=6 구조와 bare 1, gas 1. 별도로 nested loaded N=5,3 시험. bare는 각 surface에서 공유, 가스는 전체 공유한다. 초기 DFT reference에는 dispersion을 쓰지 않는다. `R/results/4_cf4/code/src/run_cat.py:28`, `:43`; `R/results/4_cf4/code/src/run_cat_h2.py:27`, `:33`; `R/results/4_cf4/code/src/run_cat_deh.py:76`, `:88`; `R/results/4_cf4/code/src/run_nsub_cf4.py:1`, `:33`.
- **소듐**: `x=N_Na/N_Mn`, `e=E_structure/N_Mn`; `E_mix(x)=1000[e(x)−x e_P2(x=1)−(1−x)e_P2(x=0)]` meV per MnO₂ f.u. 최종 코드는 끝점 `hull:0139`(x=0), `hull:0080`(x=1)을 사용하며 초반 `hull:0336` 선언은 뒤에서 덮어쓴다. lower convex hull과 에너지 위 hull을 구성한다. 21 예시는 P2 20개(양 끝점 포함)와 `hull:0732` Na metal이다. Na metal은 mixing energy의 기준점이 아니라 전압 `V=−[e(x2)−e(x1)−(x2−x1)E_Na/atom]/[(x2−x1)e]`에 쓰인다. `R/results/1_sodium/code/mixprompt8/run_mix8.py:29`, `:40`, `:52`, `:66`, `:468`; `S/mixprompt8/examples.json:1`; `V/litreview/bam-icl-overleaf-20261030/main.tex:654`, `:660`, `:666`.
- seed prompt의 응용 블록은 adsorption DFT/BAM/차이 및 완전 pair 대응, 또는 sodium 조성·phase·mixing/hull·depth/tilt·단위 항 응답을 담는다. sodium 실제 v8 최종 스크립트는 앞부분 함수 재정의와 5 seed+30 refine 등 뒤쪽 설정이 우선이다. 계획의 LLM 직전 최소 공통 블록은 이러한 종전 응용별 선택·추가 term 전체를 재현하는 것은 아니다. `R/results/2_catalyst/code/code/run_cat_deh.py:62`; `R/results/1_sodium/code/mixprompt8/run_mix8.py:95`, `:468`, `:573`, `:590`; `R/results/1_sodium/data/reference/seed_prompt_v8.paper.txt:20`.

## 4. 구체적인 raw-cache 대조값

공통 fingerprint 디렉터리 `F=fe38d25ef455347d51c68810454a3a0083ecea10fad8494a86681d27de6a33fa`. 파일은 `<cache-root>/<F>/<identity>.json`, 내부 `E_nn`이 아래 값이고 `E_bam`은 별개다. `identity`는 숫자 `<i8`, positions `<f8`, cell `<f8`, PBC `u1` 배열을 C 순서로 연결하여 SHA256(부동소수 signed zero를 +0으로 정규화)한 64자리다. 전체 pin은 checkpoint SHA, 옛 BAM 코드 해시, torch 버전, CPU float64 EMA의 직렬화 해시라서 코드/버전이 바뀌면 F가 달라질 수 있다. `R/code/common/core/structure_input.py:27`, `:49`; `R/code/common/core/al50.py:81`, `:89`, `:99`. 아래 값은 옛 JSON을 직접 읽은 것이며 재계산값이 아니다.

| 응용 / 원본 구조와 0-based frame | identity = JSON 파일명(확장자 제외) | E_NN (eV/structure) |
|---|---|---:|
| 촉매 `Cr/rand20.traj` #0 `Cr-pair:p1:slab` | `8eb4588c1ff4a2d3e07baec557859fdc8f938916b5c19a7faa4c5b47755fac3d` | -36.28439344640652 |
| 촉매 같은 파일 #1 `Cr-pair:p1:slab-H` | `f73dab1bb2aea0e95dfd0d4154b6fc2185a444a3415397c45a89fba59dc6fae8` | -36.225465992347026 |
| 촉매 같은 파일 #2 `Cr-pair:p2:slab` | `f1d1b959213ea457d85746d2960c026173b8315e043de55c9f4c195adce12093` | -37.86691919429271 |
| MOF `XAFFOB/rand20.traj` #0 `XAFFOB-pair:ref:mof` | `958608d9406ed4325bb3b15f312c5b96ea9c0d3569689ea45c656293ce6ceb07` | -43.91745693495782 |
| MOF 같은 파일 #1 `XAFFOB-pair:p1:mof-CO2` | `c2db93795149394459ea3a9640877aaa5cffe26a4e79333bd464e391e2f3196b` | -43.51251634360281 |
| MOF 같은 파일 #2 `XAFFOB-pair:p2:mof-CO2` | `06ab0f8ac403b999a4e1a4085cf409ca22e0eadc9ec5562442c0d9077ab071fb` | -43.5422996740986 |
| CF₄ `a001/rand20.traj` #0 `a001-pair:ref:slab` | `95e71f10edcbb03865dc4725f7f3e835b933a7f3bd1010062ed18f97e3ef5d15` | -265.4089516298824 |
| CF₄ 같은 파일 #1 `a001-pair:p1:slab-CF4` | `05e7bcd86e45f210dfdf1180a934a9a73a04265c2fec879cbc2b6e2c734d50a7` | -259.2618295229794 |
| CF₄ 같은 파일 #2 `a001-pair:p2:slab-CF4` | `46ff6274d40e393b4ae257f6ab6cd081043c3664c4e5699a866ed8d719519f2e` | -259.7773443542737 |
| sodium `mix2-nmo:hull:0732`, Na metal | `ad9ec18146ef6c681ce0f827d0af8fd760fe35a5dcd2208189a2e20b50b351f0` | 3.0021439121329307 |
| sodium `mix2-nmo:hull:0139`, P2 x=0 | `6d4d3dce9aee619805df09d21e44299e9f832f687cb950c72442aa0caf4eed20` | 30.349423585254343 |
| sodium `mix2-nmo:hull:0080`, P2 x=1 | `8c2dcb6c2caf6e15de4f2ae8f5ab006432c69a850c34101d32f546b1d354e020` | 9.481234707437725 |

캐시 root 및 구조 원천(각 캐시 JSON:1):

- 촉매 root `R/results/2_catalyst/data/data/raw-cache`; 구조 `R/results/2_catalyst/data/data/inputs_pairs/examples/Cr/rand20.traj` frame 0,1,2; 해당 선택 규칙 `R/results/2_catalyst/code/code/run_cat.py:35`.
- MOF root `R/results/3_mof/data/method4-mof/raw-cache`; 구조 `R/results/3_mof/data/method4-mof/inputs_pairs/examples/XAFFOB/rand20.traj` frame 0,1,2; `R/results/3_mof/code/method4-mof/run_cat.py:40`.
- CF₄ root `R/past/4_cf4/pairs/raw-cache`; 구조 `R/past/4_cf4/pairs/inputs_pairs/examples/a001/rand20.traj` frame 0,1,2; `R/results/4_cf4/code/src/cf4_prepare.py:12`, `R/results/4_cf4/code/src/run_cat.py:43`.
- sodium root `S/mixprompt8/raw-cache`; 구조와 identity `S/mixprompt8/examples.json:1`의 처음 세 records; 로더 `R/results/1_sodium/code/mixprompt8/run_mix8.py:40`. 문서의 기준 `<1e−5 eV/structure` 검사는 동일 구조 좌표와 checkpoint·EMA·정밀도를 사용해야 한다.

**예시 DFT 목표값 (eV, 원본 ASE 읽기 후 산술 계산):**

| 데이터 | loaded − bare − gas | 값 |
|---|---|---:|
| 촉매 Cr pair 1 | `−503.50995720 − (−499.46917445) − 0.5*(−6.98887582)` | -0.54634484 |
| 촉매 Cr pair 2 | `R/results/2_catalyst/data/data/inputs_pairs/examples/Cr/rand20.traj` frame 2,3; H₂ `R/results/2_catalyst/data/data/inputs_h2/H2.extxyz:1` | -0.70198304 |
| MOF XAFFOB pair 1,2 | frames 1,2 각각 − frame 0 − CO₂ `−22.990396`; 원천 위 XAFFOB traj와 `R/results/3_mof/data/method4-mof/inputs_co2/CO2.extxyz:1` | 0.16461304684216; 0.14064819684230 |
| CF₄ a001 pair 1,2 | frames 1,2 각각 − frame 0 − CF₄ `−25.61387988`; 원천 위 a001 traj와 `R/past/4_cf4/pairs/inputs_cf4/CF4.extxyz:1` | 4.31113552000009; 3.72042759000009 |

이 값은 구조별 단일점 예시 adsorption energy이지 relaxation한 query의 성능 지표가 아니다. 수식과 라벨 역할은 각각 `R/results/2_catalyst/code/code/run_cat_deh.py:70`, `R/results/3_mof/code/method4-mof/run_cat_deh.py:72`, `R/results/4_cf4/code/src/run_cat_deh.py:76`.
