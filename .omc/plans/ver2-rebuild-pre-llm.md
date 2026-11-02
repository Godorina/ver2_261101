# ver2_261101 재작성 계획: LLM 호출 직전까지 (ponytail)

상태: **pending approval** · 개정 2026-11-01 (v2: 이식에서 처음부터 다시 작성하는 방식으로 변경)
원칙: `.claude/skills/ponytail` full. 필요한가 → 이미 있나 → stdlib → 설치된 의존성(numpy, ase, bam_torch) → 한 줄 → 최소 코드.

## 1. 목표
- `code/`: 처음부터 새로 작성한다. 구조 로드 → BAM `E_NN`·`F_NN` → 잔차와 기술자 → 프롬프트 텍스트(`prompt.txt`)까지만 담는다. LLM 호출은 없다.
- `data/{1_sodium,2_catalyst,3_MOF,4_CF4}`: 실제 사용한 구조와 DFT 라벨. 형식은 **extxyz 하나로 통일**한다.
- 옛 코드(`bam-icl-release` 등)는 **사양을 읽는 참고서**로만 쓴다. 복사하거나 import하지 않는다. 원본은 읽기 전용이다.

## 2. 목표 구조 (파일 수 최소)

```
ver2_261101/
├── data/
│   ├── 1_sodium/   hull.traj (733), examples.json (end member, Na metal, 예제 21개와 role)
│   ├── 2_catalyst/ examples.traj, queries.traj, H2.traj, splits.json
│   ├── 3_MOF/      examples.traj, queries.traj, CO2.traj, splits.json
│   ├── 4_CF4/      examples.traj, queries.traj, CF4.traj, splits.json
│   └── SOURCES.md  # 파일별 원천 경로, sha256, frame 수 (표 하나)
├── code/
│   ├── make_data.py         # 원천 → data/ (결정론적)
│   ├── common/              # ① 공통: 시스템을 모른다
│   │   ├── bam.py           #   구조 에너지 E_NN, F_NN → outputs/<app>/bam.npz
│   │   ├── features.py      #   잔차, r1·각도, 히스토그램, 힘 표(기본 bin), 파라미터 범위
│   │   └── prompt.py        #   프롬프트 골격, FORM, range check
│   ├── systems/             # ② 시스템별: 에너지 dict만 받는다. examples / quantity / prompt_parts 3개만 공개
│   │   ├── adsorption.py    #   촉매 dE_H(k=½), MOF·CF4 E_ads(k=1), 0.5 Å bin, pair 표
│   │   └── sodium.py        #   E_mix, lower hull, E_above_hull
│   ├── run.py               # ③ 연결: python code/run.py <app> [group --n N] → outputs/<app>/<group>/n<N>/
│   └── SPEC.md              # Phase 0에서 옛 코드로부터 뽑은 계약 (식, 상수, 프롬프트 항목)
└── outputs/        # 산출물 (gitignore)
```
의존은 common ← systems ← run.py 한 방향이다(2026-11-01 사용자 결정: "계산은 시스템 에너지, 그 다음 시스템별 계산"). `quantity(app, frames, E)`는 순수 함수라 나중에 LLM 보정 에너지를 넣어도 그대로 쓴다. 각 파일 끝에 `assert` 기반 `__main__` 자기검사를 둔다. 테스트 프레임워크는 쓰지 않는다.

**하지 않는 것 (YAGNI, 필요해지면 추가)**: 패키지 계층, config 모듈, sealed cache·manifest 시스템, 출력 경로 가드, 응용별 클래스, 응용별 프롬프트 변형(cathode hull depth/tilt 등), refine 프롬프트.

## 3. Phase별 계획

### Phase 0: 사양 추출 (읽기 전용) → `code/SPEC.md`
옛 코드를 끝까지 읽고 **계약만** 1–2쪽으로 적는다(ponytail: 읽기는 줄이지 않는다). 참고할 파일:
- BAM: `bam-icl-release/code/common/core/analysis/llmsr_bam_terminals.py` (`create_frozen_bam_calculator`, `LiveBAMScalars._forward`). **`E_NN`(원소 기준합 `R_old`를 뺀 값)을 얻는 정확한 방법**, ckpt sha `e837d512…`, dtype.
- 기술자: `core/direct.py` (`score`, `example_table`, `prompt`), `core/force_table.py`, `physics/terms.py:bounds`. 컷오프 5 Å, 스위칭 4.5–5 Å, 히스토그램 0–5 Å, 힘 표 bin 0.25 Å(1–5 Å), r1 정의, 파라미터 범위 표.
- 목표량: 촉매·MOF·CF4의 흡착에너지 `E_ads = E(slab+mol) − E(slab) − E(mol)`, 소듐 formation energy(hull, Na metal 기준). 각 응용의 예제 구성 규칙(N=20/10/5 subset).
- 프롬프트: `results/1_sodium/data/reference/seed_prompt_v8.paper.txt`, 촉매 seed prompt(`run_cat_deh.py __main__` 출력 기록), 원고 SI S1의 프롬프트 전문(`ver2_261101/litreview/bam-icl-overleaf-20261030/si.tex`). **어떤 정보 항목이 들어가는지** 목록으로 정리한다.
- 검증용 기준값: 응용마다 구조 3개씩 옛 BAM 캐시의 `E_NN`, 그리고 예제 DFT `E_ads` 몇 개.
- **완료 기준**: SPEC.md에 식, 상수, 프롬프트 항목, 기준값이 있고, 각 항목에 원천 `파일:행`이 붙어 있다.

### Phase 1: data/
1. 원천(계획 v1 §2의 매핑, 아래 요약)에서 ASE로 읽어 응용별 extxyz로 쓴다. DFT 에너지와 힘은 `info`/`arrays`에, 역할과 그룹은 `info`에 넣는다.
   - 1_sodium: `mlp-icl-ft-check-v1/hull_nmo/data/hull.extxyz`, `.../mixprompt8/examples.json` (메타데이터 x, nNa, nMn, relaxed는 프레임에서 직접 계산. 2026-11-02 사용자 수정. 옛 `targets.json`과 733개 전부 일치)
   - 2_catalyst: `bam-icl-release/results/2_catalyst/data/data/{inputs_pairs,inputs_h2}`
   - 3_MOF: `bam-icl-release/results/3_mof/data/method4-mof/{inputs_pairs,inputs_co2}`
   - 4_CF4: `bam-icl-release/past/4_cf4/pairs/{inputs_pairs,inputs_cf4}`
2. 변환 스크립트는 `code/make_data.py`로 남긴다(2026-11-01 사용자 결정. 재현성 때문). 실행하면 `data/`와 `SOURCES.md`(원천과 결과의 sha256, frame 수)를 다시 만들고, 출력은 결정론적이다. 형식은 extxyz 대신 `.traj`다(extxyz는 좌표를 1e-8 Å로 반올림해 옛 캐시 identity가 깨진다).
- **완료 기준**: frame 수가 맞는다(촉매 예제 100·테스트 149, MOF 693·134, CF4 27·7, 소듐 733·예제 21). 원천과 결과의 에너지·힘 최대 차이가 0이다. `data/`에 symlink가 0개다.

### Phase 2: code/ 작성
- (처음엔 평면 파일 4개로 썼고, Phase 3 계산 후 위 3층 구조로 나눴다. 124개 프롬프트가 바이트 단위로 같음을 확인하고 평면 파일을 지웠다.)
- `common/bam.py`: ckpt 로드는 1회. `RACECalculator` 또는 SPEC에서 확인한 최소 경로로 `E_NN`, `F_NN`을 구한다. 결과 `bam.npz` 자체가 캐시다(있으면 건너뜀). `# ponytail: npz 1개 캐시, 구조 수 10^4 넘으면 분할`.
- `features.py`: numpy와 `ase.neighborlist`만 쓴다. SPEC의 식을 그대로 옮긴다.
- `prompt.py`: f-string 템플릿 1개. 응용 차이는 목표량 블록 하나다.
- `run.py`: argparse 하나. `outputs/<app>/{bam.npz, examples.json, prompt.txt}`.
- **완료 기준**: 각 파일의 `__main__` 자기검사가 통과한다. LLM·HTTP 코드가 0이다. 절대경로가 0이다(ckpt는 `BAM_CKPT` 환경변수).

### Phase 3: 계산과 대조
1. `python code/run.py <app>` 4회(CPU, 백그라운드).
2. 대조:
   - `E_NN`이 SPEC 기준값과 |Δ| < 1e-5 eV/structure
   - 예제 `E_ads`가 SPEC 기준값과 일치
   - prompt.txt에 SPEC의 정보 항목이 모두 들어 있음(문구는 달라도 된다)
- **완료 기준**: 세 항목 모두 PASS이고, 불일치는 원인이 기록돼 있다.

### Phase 4: 리뷰
- `ponytail-review`로 더 지울 곳을 찾는다(`net: -N lines`). `ponytail-debt`로 남긴 지름길 목록을 만든다.
- 정확성 리뷰는 `oh-my-claudecode:code-reviewer`와 codex(herdr `litcodex`)에 맡긴다. 작성자가 직접 승인하지 않는다.
- 최상위 `README.md`는 10줄 안팎이다: 구조, 명령 4개, `BAM_CKPT`.

## 4. 위험과 대응

| 위험 | 대응 |
|---|---|
| `E_NN` 정의를 잘못 옮김(R_old 처리) | Phase 0 SPEC에 원천 행을 명시한다. Phase 3에서 옛 캐시 값과 대조한다 |
| 처음부터 다시 쓰다가 프롬프트 정보 누락 | SPEC의 항목 목록을 체크리스트로 Phase 3에서 대조한다 |
| 단순화로 응용별 차이(소듐 hull 선택 규칙 등)가 빠짐 | 의도한 생략이다. `ponytail:` 주석으로 남기고 Phase 5(LLM 단계)에서 필요하면 추가한다 |
| 원본 오염 | 쓰기는 `ver2_261101/` 아래로만 한다 |
| ckpt가 크고(410 MB) GPU 드라이버가 불일치 | CPU 기본. ckpt는 data에 넣지 않는다 |

## 5. 열린 결정 (기본값)
1. 소듐 쿼리셋: hull 733만. bigq와 NMO traj는 제외한다.
2. MOF dispersion: data는 하나로 두고, code에서는 Phase 5로 미룬다(LLM 단계의 항 라이브러리 문제).
3. 프롬프트: base protocol 하나만. 응용별 변형은 필요가 확인된 뒤 추가한다.
