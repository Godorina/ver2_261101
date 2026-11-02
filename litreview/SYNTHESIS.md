# ICL 기반 LLM Symbolic Regression 문헌 종합 (2025–2026, 각 10편)

작성일: 2026-11-01. 출처 파일: `papers_2025.md`, `papers_2026.md`(Claude 에이전트), `codex_candidates.md`, `codex_review.md`(codex --yolo 독립 목록과 교차검토), `paper_context.md`(BAM-ICL 원고, Overleaf 최신본 2026-10-30. Mac의 Aside로 가져옴).
수치는 모두 저자 보고값이며 재현하지 않았다.

## 1. 선정 목록

| 연도 | # | 논문 | arXiv / DOI | 유형 | 계수 처리 | 적합도 (codex 0–3) |
|---|---|---|---|---|---|---|
| 2025 | 1 | LLM-SRBench | 2504.10415 | 벤치마크 | 방법별 optimizer | 2 |
| 2025 | 2 | DrSR | 2506.04282 | 방법 | BFGS | 3 |
| 2025 | 3 | SR-Scientist | 2510.11661 | 에이전트 | BFGS 도구 | 3 |
| 2025 | 4 | LLM-Feynman | 2503.06512 | 재료 응용 | LLM이 함수를 작성. refit 여부 미확인 | 3 |
| 2025 | 5 | From Data to Physics (o3) | 10.1002/anie.202512151 | 화학(MOL 흡착) | 에이전트가 피팅 코드 실행 | 2 |
| 2025 | 6 | IdeaSearchFitter | 2510.08317 | 방법 | L-BFGS-B | 3 |
| 2025 | 7 | Multimodal LLM + KAN | 2505.07956 | 멀티모달 | SciPy | 3 |
| 2025 | 8 | NewtonBench | 2510.07172 | 벤치마크 | 능동 실험형 | 2 |
| 2025 | 9 | EvoSLD / SLDAgent | 2507.21184 | 진화 탐색 | LLM이 쓴 optimizer를 실행 | 2 |
| 2025 | 10 | LLM-SR for HEP | 2510.03397 | 물리 응용 | scipy/torch | 3 |
| 2026 | 1 | IGSR (ICML) | 2605.29184 | 방법 | OLS | 3 |
| 2026 | 2 | Deliberate Evolution (ICML) | 2606.04360 | 방법 | BFGS | 3 |
| 2026 | 3 | FunctionEvolve | 2606.07704 | 방법 + 벤치마크 감사 | VarPro/OLS 등 | 3 |
| 2026 | 4 | Programmatic Context Augmentation | 2605.03101 | 방법 | LLM-SR식 적합 | 3 |
| 2026 | 5 | KeplerAgent | 2602.12259 | 에이전트 | PySR/SINDy | 2 |
| 2026 | 6 | Library Reachability | 2607.28684 | 비판적 분석 | — | 2 |
| 2026 | 7 | LLM-PySR | 2607.04156 | 분석 + 배터리 | PySR | 2 |
| 2026 | 8 | DASyR-LLM | 2608.05120 | 촉매 반응속도 | PySR + L-BFGS-B | 3 |
| 2026 | 9 | LangLaw | 2602.22967 | 재료(perovskite) | PySR | 2 |
| 2026 | 10 | EO-SR | 2603.19241 | 구성방정식 | GP-SR | 1 |

교체를 고려할 후보(codex 제안):
- DoLQ (2605.07323, ODE, 3점)는 EO-SR(1점)과 바꿀 만하다.
- LLM-Meta-SR (2505.18602)
- PNAS SR-LLM (10.1073/pnas.2516995122): 403 차단으로 미확인.

## 2. 교차검토로 바로잡은 내용

| 처음 주장 | 정정 | 확인 |
|---|---|---|
| no-refit 사례는 LLM-Feynman과 EvoSLD뿐이다 | EvoSLD는 optimizer를 실행하므로 해당하지 않는다. LLM-Feynman은 미확인이다 | codex가 v1 원문 확인 |
| SR-Scientist가 재료 하위셋에서 6–35%p 이득 | 전체 벤치마크 결과를 재료 결과로 옮긴 것 | codex |
| NewtonBench는 전통 SR과 비교하지 않았다 | v3 부록 E.5에서 PySR, LLM-SR과 비교한다 | codex |
| Library Reachability 77.7%가 SR-Scientist 63.6%보다 높다 | 예산과 조건이 달라 직접 비교할 수 없다 | codex |
| 2026 논문은 모두 LLM이 skeleton, optimizer가 계수 | 벤치마크와 분석 논문은 역할이 달라 일반화할 수 없다. 방법 논문에 한해서는 성립한다 | codex |

정정 내용은 `papers_2025.md`, `papers_2026.md` 본문에도 `[정정]`으로 표시했다.

## 3. 목록 밖에서 새로 확인한 핵심 선행연구 (원고 인용 권장)

1. **LMX: Language Model Crossover: Variation through Few-Shot Prompting.** Meyerson et al., arXiv:2302.12170 (2023-02-23).
   - SR 실험에서 부모 식 7개를 few-shot으로 넣으면 LLM이 **상수까지 텍스트로 직접** 쓴다. 별도 상수 최적화는 서술되어 있지 않다(Claude가 원문 HTML로 확인).
   - 원고의 "LLM이 모든 수치를 작성, fitter 없음" 설계의 가장 직접적인 선행연구다. 이미 인용 중인 OPRO, words-to-numbers와 함께 묶어야 한다.
2. **A thermodynamic correction layer for machine learning interatomic potentials.** Menon, Sanchez Ortega, Drautz, arXiv:2610.34551 (2026-10-25).
   - foundation GRACE를 **재학습하지 않고** 가산 보정층을 붙인다. 보정은 선형 ACE를 수치로 적합한 것이고 LLM은 쓰지 않는다(Claude가 abs로 확인).
   - "frozen MLIP + 가산 보정"이라는 구조 자체는 최초가 아니라는 근거다. 원고는 차별점을 "보정식을 LLM이 ICL로 작성하고 refit하지 않음"으로 좁혀야 한다.
3. 인접 연구(codex 제시, 미검증): SR + RL 원자간 퍼텐셜(npj Comput. Mater. s41524-025-01952-4), BIC 기반 SR(STAM 2024).

## 4. BAM-ICL 원고에 주는 시사점

### 4.1 포지셔닝
- 이 조사에서 **frozen MLIP 잔차를 LLM이 ICL로 closed-form 보정하고 계수를 refit하지 않는 동일 조합은 찾지 못했다.** "최초"라고 단정하기보다 "조사 범위에서 동일 조합을 발견하지 못함"으로 쓰는 것이 안전하다.
- 원고의 설계는 세 계보가 만나는 지점에 있다.
  - LLM이 수치를 직접 생성: OPRO, words-to-numbers, LMX
  - LLM-SR 계열 식 탐색: LLM-SR, ICSR, DrSR, IGSR
  - frozen MLIP 보정: Menon 2026
- IGSR은 물리 항 라이브러리의 선형결합 구조와 항별 피드백이라는 점에서 가장 비슷한 방법 논문이다.

### 4.2 리뷰어가 요구할 대조 실험
1. **refit ablation.** 선택된 항의 계수를 다시 fitting하면 어떻게 되는가. 방법 논문은 모두 optimizer를 쓰므로 반드시 나올 질문이다. bulk SI에 이미 LPSCl 비교가 있다(LM이 쓴 계수 6.91, fitting한 계수 7.81 meV/atom). 비-bulk 본에서도 꺼내 쓰는 방안은 §5-2를 참고.
2. **LLM 없는 라이브러리 탐색.** 같은 φ_t 라이브러리에서 무작위 또는 greedy로 항을 고르고 계수를 적합하는 대조군. Library Reachability는 고정 어휘만으로 LSR-Synth를 높은 비율로 풀었다.
3. **암기와 contamination.** Born–Mayer와 Morse는 교과서 형태라 암기 문제가 적다. 그래도 LLM-SRBench, NewtonBench의 설계를 인용해 논의할 필요가 있다.

### 4.3 반드시 답해야 할 반대 입장
- **LLM-PySR (USTC, 2607.04156).** "LLM이 식을 쓰거나 고르면 낯선 식에서 무너지므로 탐색만 제어해야 한다"고 주장하고, 배터리 수명 사례도 있다. 가능한 응답: 원고는 물리 항 라이브러리와 파라미터 범위로 함수 공간을 제약하고, BAM보다 나은 후보만 남기는 선택 규칙으로 실패 시 BAM으로 되돌아간다. 실제로 cathode 10-call 조건에서 20 run 중 17 run이 BAM을 유지했다.

### 4.4 원고를 지지하는 근거
- **FunctionEvolve.** LLM-SRBench MatSci 25문제는 온도와 변형률이 완전히 공선적이라 온도 의존성을 식별할 수 없다. 합성 벤치마크 대신 실제 재료계(cathode, 촉매, MOF, CF4)로 평가한 선택의 근거가 된다.
- **Deliberate Evolution.** 작은 open-weight 모델도 진단 정보와 메모리를 문맥에 넣으면 크게 개선된다. Qwen3.8-27B 결과를 해석할 때 인용할 수 있다.
- **Programmatic Context Augmentation.** 원시 데이터 대신 분석 신호를 문맥에 넣는 방식이다. 원고의 잔차 힘 표는 손으로 설계한 context augmentation으로 위치시킬 수 있다.
- **같은 도메인 비교점.** DASyR-LLM(촉매), LangLaw(perovskite, OER), LLM-Feynman(SAC 흡착, 고체전해질), Angewandte o3(MOL 흡착)은 원고의 촉매·MOF 사례와 나란히 놓인다.

### 4.5 추가 인용 우선순위
원고의 현재 인용: merler2024icsr, shojaee2025llmsr, romera2024funsearch, yang2024opro, vacareanu2024words.
1. 필수: LMX(2302.12170), Menon 2026(2610.34551), LLM-PySR(2607.04156), LLM-SRBench(2504.10415)
2. 강력 권장: IGSR, Library Reachability, DrSR, LLM-Feynman
3. 선택: FunctionEvolve, Angewandte o3, DASyR-LLM, LangLaw, Deliberate Evolution

## 5. Overleaf 최신본(10/30) 기준 구체적 수정 제안

Mac의 Aside로 받은 최신본(`bam-icl-overleaf-20261030/main.tex`)을 기준으로 정리했다. 10/23 대비 바뀐 점은 세 가지다.
- 초록에 4개 LM의 결과 범위가 들어갔다.
- Intro에 기여 목록이 생겼고, "모든 계수를 external fitting 없이 쓴다"를 핵심 주장으로 내세운다.
- Methods에 "모델에 도구가 없어 코드를 돌려 계수를 맞출 수 없다"는 문장이 추가됐다.

1. **Intro 491행의 관련연구 문단(인용 5개)을 보강한다.** 491행은 "최초"를 명시하지 않고, 495–500행도 기여를 서술할 뿐이다. 하지만 LM이 수치를 직접 생성한 선행연구(LMX)와 frozen MLIP 보정 선행연구(Menon)와의 차이를 설명하지 않는다. 차별점은 다음 **조합**으로 서술한다: 처방된 물리 라이브러리와 범위 안에서, 예제와 피드백으로 frozen BAM의 보정항과 조정 가능한 계수를 LM이 쓰고, 외부 평가로 선택된 후보를 계수 refit 없이 적용한다. 조합의 최초성은 단정하지 않는다.
   - 권장 문안(codex 교차검토로 수정한 판):
     > *Language models have generated numerical candidate solutions [Vacareanu; OPRO] and, in few-shot evolutionary symbolic regression, expressions containing numerical constants [LMX]. Several LLM-guided equation-discovery methods separately fit the coefficients of proposed equation structures [LLM-SR; DrSR], and LLM-SRBench evaluates such methods across scientific domains [LLM-SRBench]. For foundation interatomic potentials, an additive correction layer has been fitted while keeping the base potential fixed [Menon 2026]. Here we investigate a distinct combination: a frozen language model selects terms from a prescribed physical library and writes their adjustable coefficients from labeled examples and feedback, and an externally evaluated candidate is applied without a subsequent coefficient fit.*
   - 수정 이유:
     - LMX는 "constants written in prompts"가 아니라 "LLM conditioned on few-shot parent expressions generates constants"이다.
     - LLM-SRBench는 벤치마크이므로 "fitting한다"의 근거로 쓰지 않는다. 계수 fitting의 근거는 DrSR과 LLM-SR에 붙인다.
2. **refit 질문에는 이미 답이 있다. 비-bulk 본에서 꺼내 쓴다.** `si.tex` "Written versus fitted numbers"(bulk 분기에만 있음)에 비교가 있다. LPSCl에서 같은 Born–Mayer 4항을 Adam 800 step으로 fitting했다. 예제 오차는 같았지만(2.02 대 2.07 meV/atom), query에서는 LM이 쓴 계수가 더 나았다(에너지 MAE **6.91 대 7.81** meV/atom, 차이 +0.90 [+0.72, +1.09]; 힘은 0.1835 대 0.1836으로 같음). 예제가 파라미터를 고정하지 못한다는 해석도 함께 있다.
   - 현재 `\bulkfalse`라서 이 절이 숨겨져 있다. 리뷰어 질문에 대비해 비-bulk SI에도 한 절 남기거나, 본문에 한 문장 언급하는 것을 권한다(SI 절 번호 조정 필요).
   - 한 context, LM run 1회, fitting 1회의 비교라는 한계를 같이 적는다.
   - "LM 없는 라이브러리 탐색" 대조군은 아직 없다. 추가 실험 후보다.
3. **표현을 다듬을 곳.**
   - bulk 초록 479행의 "every number chosen by the model"은 사람이 정한 컷오프, 범위, 예제 기반 기준 거리(547–555행)와 충돌한다. "every adjustable coefficient of the correction"으로 고친다. 481, 496행의 "all numerical coefficients"도 같은 뜻으로 통일한다.
   - "no fitting"과 "no search/selection"을 구분한다. 계수 회귀는 없지만 예제 점수로 후보를 거르고 refinement를 한다(598행). "최적화 없이 발견"처럼 읽히는 문장은 피한다.
   - 594–598행의 "No tools ... cannot run code to fit the coefficients"는 유지한다. 557행의 무보정 서술과 함께 두면 에이전트형 피팅(SR-Scientist, Angewandte o3)과의 경계가 분명해진다.
4. **LLM-PySR에 대한 응답은 실제 결과가 지지하는 범위로 한정한다.** 라이브러리·범위 제약과 BAM fallback(555, 598행)은 근거가 된다. 그러나 선택 규칙은 **예제에서의** 개선만 보장한다. cathode에서는 구조 순위, hull, 전압이 악화된 사례가 있다(852–856행). "unseen query에서 BAM보다 나쁘지 않다"는 주장은 하지 않는다. 17/20 BAM 유지도 cathode 10-call 설정에 한정된 보수성의 증거일 뿐이다.

## 6. 남은 검증 과제
- LLM-Feynman 전체 구현에 계수 피팅이 있는지(PDF 후반부와 코드).
- PNAS SR-LLM 서지와 방법(403 차단).
