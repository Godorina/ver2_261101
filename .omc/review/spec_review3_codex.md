# SPEC 최종 확인

범위는 `spec_review2_codex.md`의 미해결 항목과 이번 수정에서 새로 생긴 오류다. `S=code/SPEC.md`, `R=/home/hgpark/whlee/hgpark/bam-icl-release`, `C=R/code/common/core`, `CAT=R/results/2_catalyst/code/code`. 문구의 바이트 단위 일치는 요구하지 않는다. UNVERIFIED 2의 전수 재계산은 요청대로 Phase 3 범위로 둔다.

| 이전 항목 | 판정 | 근거 |
|---|---|---|
| MISSING 2: role·pair 번호 | **RESOLVED** | S:94-95에 MOF/CF4 `unpaired` fallback이 추가됐다. 원천의 예제 표는 해당 fallback을 쓴다(`R/results/3_mof/code/method4-mof/run_cat_deh.py:70-74`; `R/results/4_cf4/code/src/run_cat_deh.py:74-78`). 다만 fallback 발생 가능성에 관한 새 문구는 아래 오류 2 참조. |
| MISSING 3: 응용별 표 필드 | **RESOLVED** | S:97에 세 응용의 실제 키, 반올림, 평균이 들어갔다. `CAT/run_cat_deh.py:69-74`; `R/results/3_mof/code/method4-mof/run_cat_deh.py:75-80`; `R/results/4_cf4/code/src/run_cat_deh.py:79-84`. |
| MISSING 5: r1·round | **RESOLVED** | S:52,54-55,62에 r1_element 4자리, angle 필터의 비반올림값, r0 경계의 이중 반올림을 지정했다. `R/code/common/physics/terms.py:63-77,120-124`. |
| MISSING 6: FORM | **PARTIAL** | S:61,63-64가 FORM의 정확한 원천 및 전문 사용, `c_Z` 최소 4자리, 파서 제한과 EAM 평가 차이를 명시한다(`R/code/common/physics/terms.py:159-166,187-199`; `C/direct.py:39-40,346-350`). 다만 FORM 전문은 여전히 SPEC 본문에 실리지 않아, **SPEC 파일만** 읽고 수식과 JSON 필드를 복원할 수는 없다. 명시된 옛 원천을 읽는 방식이라면 해당 정보는 충분히 찾을 수 있다. |
| MISSING 7: 주기 이미지 | **RESOLVED** | S:39에 주기 이미지, self 제거, 정상 입력의 cutoff, 0.3 Å 미만 시 입력 거부와 bounds의 ASE 경로를 구분했다. `C/analysis/llmsr_dsl.py:192-201,233-247`; `R/code/common/physics/terms.py:48-53,65-70`. 다만 인용 행의 새 오류는 아래 1 참조. |
| MISSING 11: variant·sodium goal | **RESOLVED** | S:100이 MOF dispersion을 기본으로 정하고 switch와 방향성 쌍의 ½을 명시한다(`R/results/3_mof/code/method4-mof-disp/run_cat_disp.py:22-27,33-41`). S:111,113은 세 gate·hull score와 v8 확장 제외를 기본 계약으로 명시하며 v8 재현을 보장하지 않는다고 구분한다. 간략화 goal의 근거는 `R/results/1_sodium/code/mixprompt8/run_mix8.py:125-133`이다. ‘사용자 확인 대기’라는 단서는 기본값을 잠정으로 표시한다. 실제 v8은 뒤에서 goal과 평가가 추가 변경되므로 이 기본 계약과 구별해야 한다(`run_mix8.py:497-522,761-817`). |
| UNVERIFIED 2: 전수 확인·calculator dtype | **RESOLVED** | S:23은 dtype을 미확인으로 표시한다. cache 및 DFT 전수 재계산은 이번 요청에 따라 판정 범위 밖이며, 이 판정은 수치의 전수 검증을 뜻하지 않는다. |
| OPEN: r1 원문 문구 | **RESOLVED** | S:51,53은 구현의 양방향 pooling과 원래 프롬프트의 단방향 기술 차이, 새 문구의 선택을 명시한다. `R/code/common/physics/terms.py:55-62,74`; `C/direct.py:359-362`. |
| 새 ERROR 1: 0.3 Å 미만 처리 | **RESOLVED** | S:39에 원본 graph의 입력 전체 거부가 반영되었다(`C/analysis/llmsr_dsl.py:233-239`). 새로 붙인 인용에는 아래 오류 1이 있다. |
| 새 ERROR 2: FORM 행 수 | **RESOLVED** | S:61은 13줄이다. 원천 `R/code/common/physics/terms.py:187-199`의 FORM 문자열도 13줄이다. |

## 이번 수정에서 새로 생긴 오류

1. **[ERROR] 0.3 Å 거부의 행 번호** — S:39는 거부 조건의 출처를 `:192-201`로 적었으나 그 행은 neighbor list 작성 및 self edge 제거다. 실제 거리 계산과 `<0.3` 예외는 `C/analysis/llmsr_dsl.py:233-239`다. 조건의 설명 자체는 맞다.
2. **[ERROR] 촉매 fallback 발생 가능성** — S:95의 ‘짝이 없는 예제의 fallback은 촉매 …, MOF와 CF4 …다(정상 입력에서는 발생하지 않는다)’는 괄호를 세 응용 전체에 적용하면 틀리다. 촉매 N=5는 정상 지원 설정이며 5개 slab/slab-H frame에서 적어도 하나는 짝이 없으므로 `slab (no partner)`가 정상적으로 발생한다. `CAT/run_cat.py:20,35-47`; `CAT/run_cat_deh.py:27-34,64-68`. 괄호가 MOF/CF4에만 해당한다는 뜻이었다면 대상을 명확히 한정해야 한다.
