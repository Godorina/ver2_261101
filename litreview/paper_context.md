# BAM-ICL 원고 요약 (문헌 비교 기준)

출처: Overleaf `bam-icl` 프로젝트(id 6accf9ed322029c6b0fa5865, 최종 수정 2026-10-30). Mac의 Aside(born:2222 reverse SSH → `aside mcp`)로 소스 zip을 받아 `bam-icl-overleaf-20261030/main.tex`, `si.tex`로 저장했다. 이전 기준이었던 10/23 스냅샷은 `mlp-icl-llmsr-force-v2/.../overleaf_qwen4llm/main.tex`.

- 제목: *Language-Model-Written Physical Corrections for a Pretrained Interatomic Potential* (Chang Woo Myung 외, SKKU)
- 핵심: frozen BAM-MP-core에서 `E = E_NN + f_q`, `f_q = Σ n_Z c_Z + Σ φ_t` (1–8개 항)
  - φ_t 라이브러리: Born–Mayer, Morse, EAM, bond-angle. MOF에는 dispersion 항을 추가한다.
  - **LLM이 모든 계수를 쓰고, 이후 coefficient fitting은 없다.** 10/30본은 "No tools are available to the models, so they cannot run code to fit the coefficients"를 명시한다.
  - 기여 목록(Intro): (1) frozen LM이 쓴 명시적 물리 보정으로 BAM을 task-specific하게 적응시킨다. (2) 응용별 절차로, LM이 처방된 라이브러리에서 항을 고르고 모든 계수를 external fitting 없이 쓴다.
  - 루프: 초기 5회 + refinement 5회 호출, 호출당 후보 최대 5개. refinement에는 상위 5개 후보와 그 예제 오차를 넣는다. 호출 사이 대화 기록은 없다.
  - 선택:
    - base: 예제에서 E와 F 오차가 모두 BAM보다 낮은 후보 중 F 오차가 최소인 것
    - 흡착 3계: E, F, 흡착에너지 오차가 모두 BAM보다 낮고 range check(원자쌍 힘 ≤ 3 eV/Å)를 통과한 후보 중 흡착에너지 오차가 최소인 것
    - cathode: hull 기준
    - 통과 후보가 없으면 BAM을 쓴다
  - LLM: Claude Sonnet 5.5, Gemini 3.8 Flash, GPT-5.6 Luna, Qwen3.8-27B (Q4_K_M, 로컬)
- 결과(초록, 4개 LM 범위):

  | 응용 | 지표 | LM 보정 | BAM | Fine-tuning |
  |---|---|---|---|---|
  | P2 NaxMnO2 cathode | formation energy MAE (meV/f.u.) | 31.68–54.22 | 59.66 | 39.13 |
  | DAC H 흡착 | MAE (eV) | 0.220–0.342 | 0.428 | 0.406 |
  | MOF CO2 흡착 (33개 전체) | MAE (eV) | 0.162–0.215 | 0.260 | 0.337 |
  | MOF CO2 흡착 (예제 site가 아닌 22개) | MAE (eV) | 0.194–0.228 | 0.261 | 0.315 |
  | CF4/Al2O3 | MAE (eV) | 0.086–0.182 | 0.228 | 0.183 |

- 현재 인용된 LLM/SR 문헌(Intro 491행 한 문단): vacareanu2024words, yang2024opro, merler2024icsr, shojaee2025llmsr, romera2024funsearch. bib는 main.tex 안의 filecontents에 들어 있다.

## 문헌 비교 축
1. LLM이 식 형태만 쓰는가, 수치까지 쓰는가 (optimizer 유무)
2. 피드백 루프 구성 (점수, 잔차, 상위 후보)
3. 물리 항 라이브러리와 파라미터 범위로 함수 공간을 제약하는가
4. 원시 데이터를 넣는가, 요약과 잔차를 넣는가
5. 재료, 화학, 원자간 퍼텐셜 응용 여부
6. 암기, contamination, 평가 신뢰성
