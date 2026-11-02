# Phase 1 독립 검토

검토 대상 `data/`, `code/SPEC.md`, `.omc/plans/ver2-rebuild-pre-llm.md:44-51`; 원천 `R=/home/hgpark/whlee/hgpark/bam-icl-release`, `S=/home/hgpark/whlee/hgpark/mlp-icl-ft-check-v1/hull_nmo`. 빌더 `/tmp/claude-1000/-home-hgpark-whlee-hgpark-ver2-261101/d7dca3a3-f07d-4104-b048-265e5874cf8f/scratchpad/make_data.py`는 읽기만 했다. 검증은 지정된 Python `-I`에서 별도 코드를 표준입력으로 실행했으며 빌더나 `verify_data.py`를 사용하지 않았다. 배열의 shape, dtype, `tobytes()`를 대조해 signed zero도 구별했다. 대상 파일과 검토용 코드 파일은 쓰지 않았다.

## 결과

| 응용 | 그룹과 예제 | query | 판정 |
|---|---:|---:|---|
| 촉매 | 5개 × 20 = 100 | 149 | 일치. Co/Cr/Fe/Ir/Pt의 query 수는 각각 30/29/30/30/30. |
| MOF | 33개 × 21 = 693 | 134 | 일치. 각 21개는 loaded 20 + bare 1. |
| CF4 | a001 7, g100 9, g110 11 = 27 | 7 | 일치. query는 각각 1/3/3. |
| sodium | hull 733, 별도 예제 21 | — | 일치. hull frame ID 733개 모두 유일. |

`data/` 내부 symlink는 0개다. 3개 흡착 응용의 예제 frame ID는 각각 100/693/27개, query ID는 각각 149/134/7개로 중복이 없다.

- **좌표와 라벨**: 흡착 예제 820개 전체를 각 원본 `rand20.traj`의 `(group,index)`로 찾아 원자번호, 좌표, cell, pbc, DFT energy, forces의 dtype·shape·바이트를 비교했고 차이가 0건이다. 기체 3개도 해당 원천 extxyz의 동일 항목과 비트 단위로 일치한다. 흡착 query 290개는 각 group의 원천 `queries.extxyz`와 같은 순서로 원자번호·좌표·cell·pbc를 비교해 차이가 0건이며 frame ID도 일치한다. 다만 query는 원천 및 결과 모두 energy/force 라벨이 없다(아래 별도 설명).
- **sodium**: `S/data/hull.extxyz` 733개와 `data/1_sodium/hull.traj`를 순서대로 대조한 원자번호·좌표·cell·pbc와 원천 `E_DFT`, `F_DFT` 대 결과 calculator energy/forces는 모두 비트 일치한다. `targets.json`의 `phase`, `split`, `config`, `x`, `nNa`, `nMn`, `relaxed`와 frame ID도 일치한다. `S/mixprompt8/examples.json`의 21개에 대해 순서·`hull_id`·`role`, `end_members=[hull:0139,hull:0080]`가 결과 JSON과 일치하고 각 예제를 대응 hull frame에 연결해 원자번호·좌표·cell·pbc·에너지·힘이 비트 일치함도 확인했다.
- **분할과 인덱스**: 세 `splits.json`의 모든 group 및 모든 `subsets` JSON이 원천 group별 `split.json`의 `subsets`와 완전히 같다. 촉매 15개, MOF 99개, CF4 9개 subset에 대해 train+val 원소가 중복 없이 해당 `(group,index)`를 가리킴을 확인했다. MOF/CF4 모든 subset에 bare frame 0이 포함된다. 예제 `frame_id`, `config` 및 원천에 존재하는 `pair` 값도 각 원천 frame과 일치한다.
- **캐시 identity**: SPEC §5의 12개 대상 구조 각각을 새 `data/`에서 선택해 SPEC의 numbers/positions/cell/pbc SHA256을 직접 계산했다. 12개 모두 SPEC의 접두부와 일치하고, 해당 64자리 파일명이 옛 raw-cache에 존재하며 `E_nn` 12개가 SPEC 수치와 일치한다. 이는 저장된 캐시의 조회 확인이며 BAM 재계산은 아니다.
- **출처 해시**: `data/SOURCES.md`의 결과·원천 해시 접두부 143개를 직접 계산해 대조한 결과 모두 일치한다. 단 문서에는 전체 64자리 SHA256이 아니라 앞 16자리만 있다. 빌더는 `make_data.py:86-87`에서 잘라 저장한다.

## Phase 2의 데이터 가용성과 차이

1. **[ERROR] H2 frame ID가 SPEC 및 원천과 다르다.** 원천 H2는 `H2:dft-relaxed`지만 `data/2_catalyst/H2.traj`에는 `H2:gas`가 저장되어 있다. 빌더 `make_data.py:49`가 gas 이름에 `:gas`를 무조건 붙인 결과다. `code/SPEC.md` 흡착 frame id 표와 `CAT/run_cat_deh.py:27-34,64-68`의 기존 ID 사용과 불일치한다. 수치 라벨과 geometry는 일치하며, Phase 2에서 `H2:dft-relaxed`로 정규화하면 원천 ID와 호환된다.
2. **[MISSING] 흡착 query의 DFT 에너지와 힘**: 149+134+7개 모두 결과에 calculator가 없고, 선택한 원천 `inputs_pairs/queries/*/queries.extxyz`에도 없다. 따라서 `data/`만으로 이 query들의 DFT 대비 에너지·힘 오차나 실제 query 정답을 평가할 수 없다. 이는 원천의 라벨 없는 query를 그대로 보존한 것이며 seed의 예제 프롬프트 작성에는 필요하지 않다. Phase 1의 ‘원천과 결과의 에너지·힘 최대 차이 0’은 존재하는 라벨에만 확인 가능하다. **[UNVERIFIED]** 별도 원천에 query 정답 라벨이 존재하는지와 사용 권한·매핑은 이번 비교로 확인하지 않았다.
3. 흡착 예제의 `frame_id`와 `config`는 전부 존재한다. 촉매는 `pair`도 전부 존재한다. MOF와 CF4에는 별도의 `pair` 속성이 없어도 기존 ID의 `:p<k>:` 및 `:ref:`로 pair와 bare reference를 구성할 수 있다(`R/results/3_mof/code/method4-mof/run_cat_deh.py:31-40`; `R/results/4_cf4/code/src/run_cat_deh.py:35-44`). query의 info는 `frame_id`, `group`만 있지만 기존 query config는 ID 경로에서 도출된다(`R/results/3_mof/code/method4-mof/run_cat.py:31-36`). 따라서 예제 작성에 별도 config/pair 파일이 필수라는 증거는 없다.
4. sodium 결과 `examples.json`은 원천 21개 레코드 전문을 복사하지 않고 `hull_id`, `role`을 저장한다. 좌표와 라벨은 `hull.traj`에서 해당 ID로 복원할 수 있고, 순서·role·end member와 정확한 구조/라벨을 위에서 확인했다. 옛 예제의 `frame_id` 네임스페이스와 레코드 전문을 바이트 그대로 재현하려면 원천 또는 별도의 규칙이 필요하지만, ex 번호와 입력 특징을 구성하는 데는 hull 결합으로 충분하다.
5. **[MISSING] 전체 SHA256 기록**: 계획 `.omc/plans/ver2-rebuild-pre-llm.md:48-49`의 원천·결과 sha 기록과 달리 `data/SOURCES.md:6-8`은 열 이름이 sha256임에도 모든 값을 16자리 접두부로만 기록한다. 접두부는 모두 일치하지만 완전한 SHA256 64자리의 기록과는 다르다. 각 파일이 존재하는 현재는 해시를 다시 계산할 수 있다.

## `.traj` 전환 판단

계획 Phase 1은 extxyz를 명시했으므로 `.traj`는 **형식 변경**이다. 그러나 ASE extxyz 기본 writer로 원본 흡착 예제 전체를 메모리의 문자열에 쓴 후 다시 읽어 SPEC identity를 재계산하는 별도 실험에서 MOF는 **693/693** identity가 바뀌었고 좌표 최대 절댓값 차이는 `5.000000413701855e-09 Å`였다. 촉매는 **0/100**, CF4는 **0/27**이 바뀌었으므로 모든 응용에서 실제로 깨진다는 뜻은 아니다. 이 실험은 ASE의 해당 기본 extxyz writer와 원천 값에 한정된다. 새 `.traj`에서 SPEC의 12개 옛 캐시 파일을 모두 찾은 사실과 합치며, 정확한 부동소수 좌표와 cache identity 보존을 위한 `.traj` 선택은 타당하다. 각 원천이 원래 extxyz인 query와 sodium은 이미 그 파일에 기록된 좌표를 기준으로 비교했다.
