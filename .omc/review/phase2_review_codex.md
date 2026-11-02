# Phase 2 독립 검토

`code/{bam,features,prompt,run}.py`, `code/SPEC.md`, 옛 `R=/home/hgpark/whlee/hgpark/bam-icl-release` 코드를 읽었다. 새 BAM forward는 실행하지 않았다. Co n5는 `outputs/2_catalyst/bam.npz`의 여섯 구조를 사용했다. 옛 기술자 코드는 새 코드와 별도 Python 프로세스로 실행하고 동일 입력과 동일 E_NN/F_NN을 제공했다. sodium 검사는 이미 존재하는 옛 raw-cache를 읽었으며 새 BAM 계산은 하지 않았다. 검증 명령은 표준입력으로 실행하고 `PYTHONDONTWRITEBYTECODE=1`을 주었다.

## 발견 사항

1. **[ERROR] 캐시가 모델과 실행 조건에 고정되지 않는다.** `code/bam.py:65-81`은 geometry identity에 해당하는 `E_` 키와 `ref`가 있으면 checkpoint SHA 검증이나 모델 코드·precision·EMA 정보 확인 없이 결과를 쓴다. 따라서 같은 구조의 NPZ가 다른 모델/정밀도로 만들어졌거나 잘못 교체돼도 현재 ckpt의 결과로 조용히 소비한다. `BAM_CKPT`가 바뀌어도 캐시 전부 hit면 `load()`조차 호출되지 않는다. 옛 raw-cache는 checkpoint·BAM 코드 해시·torch·precision pin의 fingerprint를 경로에 쓰고 각 record pin을 확인한다(`R/code/common/core/al50.py:74-95`). 현재 Co n5 캐시는 아래처럼 옛 캐시와 실제 대조해 일치했으므로 현재 6개가 잘못됐다는 뜻은 아니다. 단일 NPZ는 유지하되 최소한 checkpoint SHA와 계산 조건을 함께 저장·검증할 필요가 있다. `E_`만 있고 `F_`가 없는 불완전 캐시는 `bam.py:70,81`에서 재계산되지 않고 KeyError가 난다.
2. **[ERROR] 동종쌍 r1 설명**: `code/prompt.py:112-113`은 r1_XY를 각 원자의 ‘other element’ 최근접거리라고만 설명한다. Co n5 출력의 `r1_pair`에는 `H-H`, `C-C` 등 동종쌍이 실제 존재하므로 이 표현은 동종쌍을 설명하지 못한다. 구현 `features.py:70-77`은 동종쌍을 원자마다 한 번, 이종쌍은 양방향으로 올바르게 계산한다. SPEC §2의 동종쌍 규칙을 프롬프트 문장에도 명시하는 것이 정확하다. 옛 prompt 역시 단방향만 설명했으므로 새 prompt의 양방향 정정은 의도된 개선이다.
3. **[MISSING] EMA 및 Wigner 검증의 방어 조건이 옛 구현과 동등하지 않다.** `code/bam.py:31-44`의 `zip` 검사는 shadow 수와 named parameter 수의 일치, checkpoint 이름 순서, shadow shape·유한값을 별도로 검사하지 않는다. 따라서 길이가 짧은 shadow 목록은 나머지 파라미터가 검증되지 않은 채 통과할 수 있다. 옛 코드는 길이·순서·shape·finite 및 regular 값 일치를 확인한다(`R/code/common/core/analysis/llmsr_bam_terminals.py:112-148`). 또한 새 코드는 Wigner 버퍼가 `torch.allclose(..., atol=1e-6)`이면 교체하는 반면, 옛 코드는 exact 또는 정확히 float32로 반올림된 값임을 모든 버퍼에 대해 확인한 뒤 교체한다(`:84-109`). 잘못된 버퍼도 허용 오차 안이면 새 코드는 받아들인다. 다만 **실제 지정 checkpoint**를 로드해 forward 없이 확인한 결과 named parameter 52개와 shadow 52개, 이름 순서가 일치하고 전부 EMA와 같았으며 `_w3j_*` 116개는 복원 후 float64 exact 값과 같았다. 현재 checkpoint 결과가 틀렸다는 증거는 없다.
4. **[UNVERIFIED] Co 이외 출력의 실제 생성과 BAM 수치**: MOF, CF4, sodium을 대상으로 새 BAM forward 또는 새 output 생성을 실행하지 않았다. 해당 경로의 코드와 기존 데이터·옛 캐시를 검토했지만 다른 시스템의 E_NN/F_NN 계산 성공, GPU/다른 BAM 라이브러리 버전, Phase 3 전수 검증은 이번 결과에 포함되지 않는다. 현재 체크포인트에서는 `/tmp/bamgh-read` 경로로 모델 로드만 확인했다.
5. **[SIMPLIFY]** `run.adsorption(app, group, n, E_dft, E_bam, ids)`의 `group`과 `n`은 함수 본문에서 사용하지 않는다(`code/run.py:14-32,99`). 제거하면 실제 필요한 입력만 남는다. pair별 `q(E_dft,...)`와 `q(E_bam,...)`도 각 행에서 두 번 호출되므로 필요하면 한 번씩만 계산해 행을 구성할 수 있다. 로직이나 가독성을 해치지 않는 범위의 선택적 정리다.

## 기술자 비교

- Co n5의 slab 5개와 H2 1개 각각에 대해 `features.example_entry`의 structure를 옛 `al50.structural_summary`와 직접 비교했다. 거리 히스토그램 및 force RMS는 일치하고, smooth coordination과 radial projection의 부동소수 차이만 30개 값에서 나타났다. 최대 절댓값 차이는 **8.881784197001252e-16**이다. numpy와 torch 연산 순서 차이 수준이며 비트 동일하다고 주장할 수는 없다. `code/features.py:13-45`; `R/code/common/core/al50.py:124-147`; `R/code/common/core/analysis/llmsr_dsl.py:108-116,185-201,233-247`.
- 같은 여섯 구조의 `bounds`는 옛 `terms.bounds`와 전체 JSON 값이 정확히 같았다. 이종쌍 양방향 pooling, 동종쌍 한 번, 각도 필터의 반올림 전 median 및 출력 round가 대응한다(`code/features.py:67-89`; `R/code/common/physics/terms.py:48-77`).
- 전체 구조의 `force_table`은 옛 `force_table.force_table` + `aggregate`와 **전체 값이 정확히 같았다**. 0.5–5 Å, 0.25 Å bin, 실제 등장 키, 구조별 중심 원자 RMS 분모와 4자리 반올림을 확인했다(`code/features.py:48-64`; `R/code/common/core/force_table.py:8-47`).
- 일반 입력에서 ASE의 방향성 periodic edge 및 shift는 옛 graph와 부합한다. 0.3 Å 미만 입력 거부도 대응한다. 위 동적 비교는 Co n5에 한정되며, cutoff 경계·초소형 주기 셀의 모든 특수 입력을 전수 비교한 것은 아니다.

## Co n5 prompt와 원천의 정보 차이

`outputs/2_catalyst/Co/n5/prompt.txt`에는 SYSTEM, task·FORM·교체된 4중 gate/range check, 평가 구조 안내 뒤 촉매 domain, track A 기준값, 예제 6개, r1/각도, 히스토그램·radial projection 설명, 0.5–5 Å force table, H2와 두 완전 pair 표, 응답 스키마가 SPEC §3–4 순서로 있다(`code/prompt.py:94-122`; `R/results/2_catalyst/code/code/run_cat_deh.py:62-95`; `.../run_cat_deh2.py:48-56`). 출력 예제 역할은 pair 1·2, 짝 없는 slab, 마지막 H2다.

옛 cache의 `E_bam`과 DFT를 넣어 계산한 두 pair의 목표량 표는 출력 JSON과 정확히 같으며, 각 예제의 `E_DFT−E_BAM` 6자리 및 role도 같다. 예: pair 1 DFT −0.0216, BAM −0.4757, delta 0.4541 eV; pair 2 각각 0.0005, −0.5462, 0.5467 eV, 평균 0.5004 eV. 같은 구조들의 새 NPZ와 옛 JSON 비교에서 E_NN 차이는 6개 모두 0, F_NN 최대 차이는 **1.8041124150158794e-15 eV/Å**였다. 옛 코드의 ref·corr 따로 합산과 새 코드의 원자별 합산은 연산 순서가 달라 경계에 놓인 다른 경우 마지막 반올림 자리가 달라질 가능성은 있다.

옛 `run_cat_deh2`와의 실질적 정보 차이는 새 r1_XY 설명이 이종쌍 양방향 pooling을 정확히 드러내는 점(SPEC에서 의도)과 위 동종쌍 설명의 불명확성이다. 그 외 조사한 goal·range·domain·예제·기술자·pair 표·schema의 정보 항목과 배치는 대응한다. SYSTEM은 새 `prompt.txt` 맨 앞에 합쳐져 있으나 옛 전송에서는 별도 SYSTEM 메시지였다. 문구 줄바꿈과 위의 1e-15 이하 수치 차이는 바이트 동일 요구가 없으므로 별도 오류로 보지 않는다. 원천 wrapper를 통째로 실행해 prompt 전체를 비교한 것은 아니다.

## 응용 구성 및 sodium

`run.py:81-104`는 원천 split의 train 다음 val 순서로 frame을 선택하고 gas를 마지막에 붙인다. `adsorption`은 p 번호 숫자순 완전 pair만 번호를 재부여하고, MOF/CF4 공유 bare, 각 role, gas 계수 ½/1을 처리한다(`run.py:14-32`). `pool[i]`가 `info.index==i`임을 assert하므로 순서가 다른 입력을 조용히 잘못 읽지는 않는다.

sodium은 순서대로 21개 예제를 읽고 metal과 두 끝점을 제외해 E_mix와 두 hull을 만든다(`run.py:35-78`). 기존 sodium raw-cache의 E_bam 21개와 현 DFT 데이터를 입력한 독립 실행에서, 생성된 18행 mixing/hull JSON이 옛 `R/results/1_sodium/data/reference/seed_prompt_v8.paper.txt` 표와 정확히 같았다. mean |delta E_mix| **51.80**, mean |E_above_hull error| **9.31**, hull score **30.56 meV/f.u.** 및 DFT/BAM hull 꼭짓점 목록도 일치한다. sodium의 v8 고유 추가 항목을 생략하는 것은 SPEC에서 정한 단순화이며 v8 전체 prompt 재현을 뜻하지 않는다.
