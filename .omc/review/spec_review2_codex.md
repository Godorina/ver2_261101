# SPEC 재확인

판정 기준: RESOLVED = 해당 지적이 반영되어 Phase 2 계약이 충분히 정해짐; PARTIAL = 핵심은 반영됐지만 지적한 부분이나 실행에 필요한 조건이 남음; OPEN = 실질적 수정이 없음. 문구의 바이트 일치는 요구하지 않되 정보와 위치는 유지한다. `S=code/SPEC.md`, `R=/home/hgpark/whlee/hgpark/bam-icl-release`, `C=R/code/common/core`, `CAT=R/results/2_catalyst/code/code`.

## 이전 ERROR 1–7

| 항목 | 판정 | 근거 |
|---|---|---|
| ERROR 1 예제 수 | **RESOLVED** | S:87-89는 촉매 N+1, MOF/CF4 N+2를 구분한다. `R/results/3_mof/code/method4-mof/run_cat.py:40-52`, `.../run_cat_h2.py:29-32`; `R/results/4_cf4/code/src/run_cat.py:43-55`, `.../run_cat_h2.py:33-36`. |
| ERROR 2 JSON | **RESOLVED** | S:55에 `allow_nan=False`가 명시되었다. 바이트 직렬화는 요구되지 않는다. `C/llm_dispatch.py:22-23`. |
| ERROR 3 prompt 위치 | **RESOLVED** | S:68에 goal·domain·목표량 표와 range check의 위치를 정했다. 촉매 원천 `CAT/run_cat_deh.py:78-95`, `CAT/run_cat_deh2.py:48-56`. |
| ERROR 4 힘 표 키 | **RESOLVED** | S:47에서 실제 나타난 방향성 쌍과 구조 간 합집합으로 수정했다. `C/force_table.py:25-34,38-47`. |
| ERROR 5 5 Å 경계 | **RESOLVED** | S:39,42는 `<5` 선행 필터를 명시한다. `C/analysis/llmsr_dsl.py:233-247`. |
| ERROR 6 sodium 표 | **RESOLVED** | S:104는 Na 및 end members 제외, `(x,phase)` 정렬, x 4자리·에너지 2자리를 명시한다. `R/results/1_sodium/code/mixprompt8/run_mix8.py:48-49,97-107`. |
| ERROR 7 range check | **RESOLVED** | S:96은 prompt상 기술과 실제 80점 검사 및 angle 처리의 차이를 구분한다. `CAT/run_cat_deh2.py:23-34,48-56`. |

## 이전 MISSING 1–11

| 항목 | 판정 | 근거 및 남은 사항 |
|---|---|---|
| MISSING 1 예제·번호 순서 | **RESOLVED** | S:89-90에 split 순서, 마지막 gas, 순차 ex 번호 및 sodium의 examples 순서가 있다. `C/direct.py:322-331`; `R/results/3_mof/code/method4-mof/run_cat.py:43-52`, `.../run_cat_h2.py:29-32`; `R/results/1_sodium/code/mixprompt8/run_mix8.py:40-46`. |
| MISSING 2 role·pair 번호 | **PARTIAL** | S:91-92,107에 주요 role과 번호는 들어갔다. 그러나 MOF/CF4에서 매칭되지 않은 예제의 fallback `unpaired`는 빠졌다(`R/results/3_mof/code/method4-mof/run_cat_deh.py:70-74`; `R/results/4_cf4/code/src/run_cat_deh.py:74-78`). 정상 입력에서는 bare와 gas가 필수이므로 fallback이 실행되지 않을 수 있다. CF4 bare의 전문도 생략부호로만 썼지만 원천 위치가 지정돼 있다. |
| MISSING 3 응용별 표 필드 | **PARTIAL** | S:94는 4자리·평균·gas 번호를 해결했으나 `<bare 이름>`, `<목표>`라는 placeholder만 있다. JSON 정보 항목의 정확한 키가 필요한 구현에는 촉매 `slab`, `slab+H`, `dE_H_DFT_eV`, `dE_H_BAM_eV`; MOF `bare_MOF`, `MOF+CO2`, `E_ads_DFT_eV`, `E_ads_BAM_eV`; CF4 `bare_slab`, `slab+CF4`, 같은 E_ads 키를 적어야 한다(`CAT/run_cat_deh.py:69-74`; `R/results/3_mof/code/method4-mof/run_cat_deh.py:75-80`; `R/results/4_cf4/code/src/run_cat_deh.py:79-84`). |
| MISSING 4 힘 RMS | **RESOLVED** | S:49가 해당 키가 나온 구조의 모든 중심 원자와 RMS 4자리 집계를 정확히 명시한다. `C/force_table.py:27-34,38-47`. |
| MISSING 5 r1·round | **PARTIAL** | S:53-54가 각도 필터의 반올림 전 r1과 Python `round`를 해결했다. `r1_element` 출력 4자리와, 검증 시 **반올림된** `r1_pair`의 0.8배·1.2배를 다시 4자리로 반올림하는 규칙은 S:52,61에 여전히 명시되어 있지 않다(`R/code/common/physics/terms.py:63-77,120-124`). 후자는 Phase 5 검증에도 영향을 준다. |
| MISSING 6 FORM | **PARTIAL** | S:60이 원천 FORM 전문을 사용하도록 지시해 출력 항의 식·필드·중복 규칙은 원천을 찾아 재현할 수 있다(`R/code/common/physics/terms.py:187-199`). 다만 SPEC 자체에 전문이 없고 최소 소수 4자리 `c_Z` 지시(`C/direct.py:346-350`)가 빠져 있어 SPEC만으로 모든 prompt 정보 항목을 복원할 수 없다. `|c_Z|≤100`은 원천 파서 제약이며 FORM 텍스트에 있는 지시가 아니다(`C/direct.py:39-40`; `R/code/common/physics/terms.py:87-94`). 실제 EAM의 `sqrt(rho+1e-12)`와 FORM의 `sqrt(rho)` 차이도 여전히 명시되지 않았다(`terms.py:159-166,190`); 수치 항 평가가 Phase 5면 그때 필요하다. |
| MISSING 7 주기 이미지 | **PARTIAL** | S:39는 shift 벡터와 자기 이미지 처리를 추가했다. 다만 새로 기술한 0.3 Å 미만 처리에는 원천과 차이가 있다(아래 새 오류 1). |
| MISSING 8 hull 알고리즘 | **RESOLVED** | S:104-106은 순서, 동률 처리, 외적, 보간, 반올림 후 통계와 꼭짓점을 포함한다. `R/results/1_sodium/code/mixprompt8/run_mix8.py:52-72,97-113`. |
| MISSING 9 gas 경로·구성 | **RESOLVED** | S:84,90,92-93이 입력 위치, energy/force, ID·role·마지막 순서를 지정한다. `R/results/3_mof/code/method4-mof/run_cat_h2.py:23-32`; `R/results/4_cf4/code/src/run_cat_h2.py:27-36`. 입력을 새 데이터 패키지 어디에 복사할지는 배치 선택으로, 이 단계에서 gas 정보 재현의 필수 조건은 아니다. |
| MISSING 10 cache identity | **RESOLVED** | S:35의 identity 산출식과 S:112의 ‘구조에서 재계산하여 전체 identity로 조회’ 규칙이면 접두부 검색이 필요 없다. 완전 식별자는 기존 추출에도 연결된다. `C/structure_input.py:27-61`. |
| MISSING 11 variant·sodium goal | **PARTIAL** | S:108은 sodium에 energy-only goal 교체를 지정하지만, 실제 goal의 세 gate(원자당 energy, E_mix, range check)와 통과 후보의 hull score 선택 규칙을 S에 풀어 쓰지 않는다(`R/results/1_sodium/code/mixprompt8/run_mix8.py:125-133`). S:110은 v8 확장 제외와 동시에 ‘결정 필요’라고 하여 최종 범위가 모호하며, S:97은 MOF dispersion 항을 적었으나 base/disp variant 선택을 확정하지 않았다. 허용된 단순화 자체는 오류가 아니나 어떤 prompt를 작성할지 선택이 계약으로 고정돼야 한다. |

이전 검토의 **번호 없는 MISSING: r1 원문 설명 충돌**은 **OPEN**이다. S:51은 구현의 양방향 pooling을 맞게 기술하지만, `C/direct.py:359-362`의 실제 prompt는 X→Y만 설명한다는 사실은 여전히 없다. 문구를 달리 써도 되므로 새 prompt에서는 양방향 정의를 바르게 적는 선택이 가능하며, 과거 prompt와의 정보 차이를 명시하면 된다.

## 이전 UNVERIFIED 2건

| 항목 | 판정 | 근거 |
|---|---|---|
| UNVERIFIED 1 버전·thread 영향 | **RESOLVED** | S:7,9는 수치 차이 크기와 thread 영향이 미확인임을 명시하고 Phase 3에서 측정하도록 했다. 미확인을 해결한 것이 아니라 근거 없는 확정 주장을 제거한 판정이다. |
| UNVERIFIED 2 전수 확인 및 calculator dtype | **PARTIAL** | S:23이 라이브러리 경로 dtype을 미확인으로 표시해 이전의 dtype 단정을 제거했다. 다만 기존 검토에서 전수 확인하지 않았던 전체 인용·12개 캐시·DFT 값의 별도 독립 재검증 결과는 S에 없다. 그 정확성은 이 재확인에서도 전수 재계산하지 않았다. |

## 수정 과정에서 새로 생긴 오류

1. **[ERROR] 이웃의 0.3 Å 미만 처리** — S:39의 ‘모든 기술자 공통 `0 < r < 5`’와 ‘ASE neighbor_list와 같은 정의’는 예외 처리까지 포함하면 원천과 다르다. 구조 요약 및 힘 표의 `dsl._geometry`는 그래프에서 0.3 Å 미만 거리가 하나라도 있으면 그 이웃만 제외하는 것이 아니라 **전체 입력에 예외를 발생**시킨 후, 유효 거리의 `<5` graph를 만든다(`C/analysis/llmsr_dsl.py:192-201,233-247`). 반면 bounds는 ASE `neighbor_list`를 직접 사용한다(`R/code/common/physics/terms.py:48-53,65-70`). 정상 데이터에서 차이가 발생하는지는 별도다. 유효 입력에서는 방향·periodic image 규칙은 맞다.
2. **[ERROR] FORM 행 수** — S:60의 ‘14줄’은 실제 FORM 문자열과 다르다. 원천 `R/code/common/physics/terms.py:187-199`의 `FORM`은 `splitlines()` 기준 **13줄**이다. 본질적인 정보나 위치에는 영향이 없다.

이 재확인은 이전 지적과 새로 추가된 기술의 원천 대조에 한정했다. 기존에 있던 모든 식과 인용의 전체 재감사는 수행하지 않았다.
