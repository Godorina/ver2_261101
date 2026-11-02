# 2025년 LLM in-context symbolic regression 문헌 10편 (심층 정리)

조사일: 2026-11-01. 대상: 2025년에 처음 공개된(arXiv v1 또는 학회·저널) 논문으로, LLM이 prompting/ICL로(파인튜닝 없음 또는 최소) 데이터에서 명시적 닫힌 형태의 식을 찾는 연구.

**검증 방법.** 각 논문의 제목, 저자, 날짜를 arXiv abs 페이지에서 확인했다(Angewandte 논문만 Crossref DOI 메타데이터로 확인). 방법과 수치는 arXiv HTML/PDF 본문에서 뽑았다. 아래 수치는 모두 **저자 보고값**이며 재현하지 않았다. 검증이 약한 항목은 `⚠`로 표시했다.

**본 원고(BAM-ICL)와 비교하는 축** (`paper_context.md` 참고): (1) LLM이 식의 형태만 쓰고 계수는 optimizer가 맞추는가, 아니면 수치까지 직접 쓰는가 (2) 피드백 루프에 무엇을 넣는가(상위 후보, 점수, 잔차) (3) 도메인 지식이나 항 라이브러리를 넣는가 (4) 데이터를 원시값으로 넣는가, 요약으로 넣는가 (5) 재료·화학 응용 여부 (6) 암기와 평가 신뢰성.

**제외한 논문과 이유**
- **LLM-SR** (Shojaee et al., arXiv:2404.18400). ICLR 2025 oral이지만 1차 기록은 2024-04 arXiv(v3 2025-03)이므로 제외했다. 아래 거의 모든 논문의 기준 baseline이다.
- **ICSR** (Merler et al., arXiv:2404.19094, ACL SRW 2024), **LaSR** (Grayeli et al., arXiv:2409.09359, NeurIPS 2024), **Sharlin & Josephson, "In Context Learning and Reasoning for Symbolic Regression with LLMs"** (arXiv:2410.17448; v2 2025-03, 저널 게재는 확인 못함): 모두 2024년 최초 공개라 제외했다.

---

## 요약표

| # | 논문 | 유형 | 연도·venue | LLM이 계수까지 쓰나? | 재료/화학 |
|---|---|---|---|---|---|
| 1 | LLM-SRBench | (b) 벤치마크 | arXiv 2504.10415, ICML 2025 Oral | 해당 없음(평가한 방법은 모두 optimizer 사용) | 재료 25문제, 화학 36문제 |
| 2 | DrSR | (a) 방법 | arXiv 2506.04282 | 아니오(BFGS) | 6061 Al 응력-변형, 화학 kinetics |
| 3 | SR-Scientist | (a) 에이전트 | arXiv 2510.11661, ICLR 2026 | 아니오(BFGS 도구) | LSR-Synth 재료/화학 |
| 4 | LLM-Feynman | (c) 재료 응용+방법 | arXiv 2503.06512 | 예(Python 함수 전체를 LLM이 작성) | SAC 흡착에너지, 2D/페로브스카이트, 고체전해질 |
| 5 | From Data to Physics (o3) | (c) 화학 응용 | Angew. Chem. Int. Ed. 2025 | 에이전트가 직접 피팅 코드를 작성·실행 | MOL(금속-유기 층) 경쟁 흡착 |
| 6 | IdeaSearchFitter | (a) 방법 | arXiv 2510.08317 | 아니오(L-BFGS-B) | 물리(HEP PDF) |
| 7 | Multimodal LLM + KAN (LLM-LEx) | (a) 멀티모달 | arXiv 2505.07956 | 아니오(SciPy) | 없음 |
| 8 | NewtonBench | (b) 벤치마크 | arXiv 2510.07172, ICLR 2026 | 해당 없음(능동 실험형) | 물리 12분야 |
| 9 | EvoSLD / SLDAgent | (a) 진화 탐색 | arXiv 2507.21184 | optimizer 코드까지 LLM이 공동 진화 | 없음(ML scaling law) |
| 10 | LLM-SR for HEP | (c) 물리 응용 | arXiv 2510.03397 | 아니오(scipy/torch) | 물리(HEP) |

---

## 1. LLM-SRBench: A New Benchmark for Scientific Equation Discovery with Large Language Models

- **저자**: Parshin Shojaee, Ngoc-Hieu Nguyen, Kazem Meidani, Amir Barati Farimani, Khoa D Doan, Chandan K Reddy
- **연도/venue**: 2025 (v1 2025-04-14). ICML 2025 Oral, PMLR v267, pp. 55325–55359.
- **링크**: https://arxiv.org/abs/2504.10415 · https://proceedings.mlr.press/v267/shojaee25a.html
- **LLM**: Llama-3.1-8B-Instruct, GPT-4o-mini, GPT-3.5-turbo(탐색 backbone). GPT-4o는 문제 생성과 symbolic accuracy 판정에만 썼다.
- **ICL 사용 방식**: 벤치마크라서 평가한 방법마다 다르다. Direct prompting(DataBlind, 데이터 없음), LLM-SR(문제 설명, 변수, 이전 고득점 skeleton과 점수를 프롬프트에 넣음), LaSR(개념 라이브러리 + PySR), SGA(LLM과 미분가능 시뮬레이션의 bilevel 구조).
- **탐색 루프**: 문제당 LLM 호출 1,000회로 통일. 계수는 각 방법의 optimizer가 맞춘다.
- **데이터셋**: 239문제. LSR-Transform 111개(Feynman 식 100개를 덜 익숙한 형태로 다시 씀)와 LSR-Synth 128개(화학 36, 생물 24, 물리 43, **재료 25**). 알려진 항에 합성 항을 섞어 암기를 막는다. OOD 테스트셋은 LSR-Synth에만 있다.
- **핵심 결과**: 최고 symbolic accuracy는 31.5%(LSR-Transform, LLM-SR + GPT-4o-mini). LaSR + GPT-4o-mini가 Acc0.1 50.45%, NMSE 0.0011로 가장 좋았다. LSR-Synth 재료에서는 LaSR + GPT-4o-mini가 SA 28.12%.
- **한계**: SA를 GPT-4o 판정에 의존한다(인간 판정과 일치율 94.6%, 130문제 표본). OOD는 합성 문제에서만 잰다. 평가한 backbone이 작은 모델 위주다.
- **본 원고와의 관련성**: 재료 25문제와 화학 kinetics 문제가 있고, "LLM이 식을 외워서 맞혔는가"를 통제하는 사실상 표준 설계다. BAM-ICL 원고의 contamination 논의에서 인용하기 좋다. 원고의 MLIP 보정 과제는 이 벤치마크 형식이 아니므로 직접 비교보다는 평가 설계 근거로 쓰는 편이 맞다.

## 2. DrSR: LLM based Scientific Equation Discovery with Dual Reasoning from Data and Experience

- **저자**: Runxiang Wang, Boxiao Wang, Kai Li, Yifan Zhang, Jian Cheng
- **연도/venue**: 2025 (v1 2025-06-04). arXiv only(venue 표기 없음).
- **링크**: https://arxiv.org/abs/2506.04282
- **LLM**: Mixtral-8x7B-Instruct-v0.1, LLaMA3.1-8B-Instruct(양자화, H100).
- **ICL 사용 방식**: 프롬프트 세 종류. (i) 주 생성 프롬프트: LLM-SR 프롬프트(과제 설명, 변수 제약, 평가 기준, 참조 식)에 메모리 버퍼의 고득점 식과 Idea Library에서 뽑은 아이디어를 더한다. (ii) Data-aware insight: 균등 추출한 입출력 쌍 100개를 넣고, 최고 후보가 갱신되면 잔차 y − f*(x) 100점과 직전 insight를 넣어 단조성, 비선형성, 상관을 서술하게 한다. (iii) Idea extraction: 평가한 식을 Positive/Negative/Invalid로 라벨링해 넣으면 구조화된 아이디어(JSON)를 쓴다.
- **탐색 루프**: LLM-SR의 생성-평가-저장 루프. skeleton의 계수는 BFGS로 맞추고 fitness는 −MSE. 최대 1,000 iteration(baseline은 2,000회 이상).
- **데이터셋**: Oscillation 1/2, E. coli growth, **6061-T651 알루미늄 응력-변형**, LSR-Transform 일부, LSR-Synth 화학(CRK0).
- **핵심 결과(vs LLM-SR)**: Oscillation 2 NMSE 1.8×10⁻¹² 대 4.6×10⁻⁵(Mixtral). 응력-변형 Acc 88.3% 대 68.1%(Mixtral). LLaMA에서는 72.95% 대 76.21%로 오히려 낮다. CRK0 Acc 95.2%/98.0% 대 77.6%/87.0%. 유효 식 비율은 약 0.4–0.6으로, LLM-SR(0.3 미만)보다 높다.
- **한계**: 출력이 장황하거나 과도하게 복잡해질 수 있다. BFGS가 전역해를 못 찾을 수 있다. 본문 안에서 과제 수(6개/7개)와 iteration당 후보 수(44개/4개)가 서로 맞지 않는다.
- **본 원고와의 관련성**: 잔차를 프롬프트에 다시 넣는 구조가 BAM-ICL의 refinement 프롬프트(상위 5개 후보, 점수, 잔차)와 가장 비슷한 2025년 방법이다. 금속 응력-변형 같은 재료 과제도 있다. 차이는 DrSR은 계수를 BFGS에 맡긴다는 점이다.

## 3. SR-Scientist: Scientific Equation Discovery With Agentic AI

- **저자**: Shijie Xia, Yuhan Sun, Pengfei Liu
- **연도/venue**: 2025 (v1 2025-10-13). ICLR 2026(arXiv comments 기준).
- **링크**: https://arxiv.org/abs/2510.11661 · 코드 https://github.com/GAIR-NLP/SR-Scientist
- **LLM**: Qwen3-Coder-480B-A35B, GLM-4.5-Air, GPT-OSS-120B, GPT-OSS-20B, Qwen3-Coder-30B-A3B. RL 실험만 Qwen3-Coder-30B(및 Qwen3-8B/14B/32B)로 했다.
- **ICL 사용 방식**: 문제 설명, 변수, 데이터 분석 도구 사용 예시 코드, 현재 MAPE 목표를 넣는다. 매 iteration 시작 시 experience buffer의 top-K 식과 MAPE를 in-context 예시로 준다. 원시 데이터는 프롬프트에 넣지 않고, 에이전트가 code interpreter로 직접 분석한다.
- **탐색 루프**: ReAct식 장기 에이전트. 최대 40 iteration × 25 turn(LLM 호출 약 1,000회). 도구는 데이터 분석기(통계, 잔차)와 식 평가기(상수 자리를 비운 skeleton을 받아 scipy BFGS로 피팅, 파라미터 최대 10개) 두 가지다. RL 단계(GRPO, 합성 문제 1,024개)는 선택 사항이다.
- **데이터셋**: LSR-Synth 129문제(화학 36, 생물 24, 물리 44, 재료 25). ID/OOD 둘 다.
- **핵심 결과 (Acc0.01 / Acc0.001)**: GPT-OSS-120B 기준 SR-Scientist 63.57/49.35, LLM-SR 28.16/11.37, LaSR 16.02/10.08, PySR 29.46/14.47. 데이터 분석 도구를 빼면 35.66으로 떨어진다. RL로 30B 모델이 32.30에서 40.92로 오른다.
- **한계**: 텍스트 전용이라 plot을 볼 수 없다. 노이즈가 있으면 정확도가 크게 떨어진다. 상위 식만 보므로 나쁜 식을 다시 탐색할 수 있다. 본 결과는 ICL이지만 RL 확장은 파인튜닝이다.
- **본 원고와의 관련성**: 데이터를 프롬프트에 직접 넣지 않고 도구로 분석하는 설계가, 예제를 표로 넣는 BAM-ICL과 대조된다. LSR-Synth 전체에서 큰 이득을 보고하므로(**[정정]** 6–35%p는 재료 하위셋만의 결과가 아님) "에이전트형 대 단발 ICL" 논의의 비교 대상이다.

## 4. LLM-Feynman: Leveraging Large Language Models for Universal Scientific Formula and Theory Discovery

- **저자**: Zhilong Song, Qionghua Zhou, Chunjin Ren, Chongyi Ling, Minggang Ju, Jinlan Wang (Southeast Univ.)
- **연도/venue**: 2025 (v1 2025-03-09, v2 2025-07-25). arXiv only, cond-mat.mtrl-sci. ⚠ 제목 불일치: abs 메타데이터는 "...Formula and Theory Discovery"이고 v2 PDF는 "...Formula and Knowledge Discovery"이다.
- **링크**: https://arxiv.org/abs/2503.06512
- **LLM**: Falcon-Mamba-7B, ChemLLM-20B(화학·재료 데이터로 파인튜닝된 공개 모델, 이 논문이 파인튜닝한 것은 아님), LLaMA3-8B. Falcon-Mamba는 성능이 낮아 이후 실험에서 뺐다.
- **ICL 사용 방식**: 피처 X, 타깃 y, 각 피처·타깃의 **물리적 의미와 차원(domain knowledge)**을 구조화한 프롬프트로 넣어 Python 함수 형태의 식 N개를 생성한다. 이후 손실이 낮은 상위 30개 식, 그 손실값, 데이터와 의미·차원을 다시 넣어 iteration마다 새 식 10개를 생성한다(기본 500 iteration). LLM이 각 식에 해석 가능성 점수 S(0–1)를 매기는 self-evaluation을 한다.
- **탐색 루프**: 손실 L = α·N(E) + β·N(C) + γ·S(오차, 복잡도, 해석 가능성). 마지막에 Pareto front를 뽑는다. 앞단 피처 엔지니어링은 Matminer/Automatminer 상호정보 선택, LLM이 Matminer 기술자를 추천, 정체 시 피처 확장이다. 뒷단은 LLM + MCTS(UCB)로 식의 물리적 해석을 다듬는다. 원문 기준 별도 계수 피팅 단계가 명확히 기술돼 있지 않고 LLM이 함수 전체를 작성한다(⚠ 본문 일부만 확인).
- **데이터셋**: 단일원자촉매(Cu/Ag 담지) H, OH, CO, N **흡착에너지** DFT 데이터(ablation), Feynman Lectures 식 100개(쉬움)와 20개(어려움), 2D 재료 합성 가능성(151:150), 페로브스카이트 합성 가능성, 2D GW 밴드갭, **리튬 고체전해질 이온전도도**.
- **핵심 결과**: SAC 흡착에너지에서 domain knowledge와 self-evaluation을 쓰면 SISSO, PySR보다 R²와 MAE가 좋고 복잡도는 비슷하다. Feynman 식 재발견은 노이즈 10⁻²에서 쉬운 과제 86%, 어려운 과제 90%(AI-Feynman 67%, 55%). 2D 합성 가능성 식은 정확도 0.93, F1 0.94(E_hull만 쓰면 0.60). 페로브스카이트는 1.00.
- **한계**: 평가가 자체 데이터셋 위주이고, LLM-SR 같은 LLM baseline과 비교하지 않았다. 피어리뷰를 거치지 않았다. 해석 가능성 점수가 LLM의 자기평가라 순환 논리 위험이 있다.
- **본 원고와의 관련성**: 2025년 재료 응용 중 가장 가까운 논문이다. 촉매 흡착에너지와 고체전해질을 다루고, LLM이 수치까지 포함한 식 전체를 쓴다는 점에서 BAM-ICL과 겹친다. 차이는 BAM-ICL이 frozen MLIP 위의 보정항을 쓰는 반면, LLM-Feynman은 기술자로 물성을 직접 회귀한다는 점이다.

## 5. From Data to Physics: An Agentic Large Language Model Solves a Competitive Adsorption Puzzle

- **저자**: Bingling Dai, Yuhang Song, Yue Zhan, Yibin Jiang, Cheng Wang (Xiamen Univ.)
- **연도/venue**: 2025. *Angewandte Chemie International Edition* 65(2), Crossref 게재일 2025-11-13. 프리프린트는 ChemRxiv 2025-05, 제목 "Data to Physics in Minutes: ...".
- **링크**: https://doi.org/10.1002/anie.202512151 · https://chemrxiv.org/engage/chemrxiv/article-details/6810f51ee561f77ed453c69b
- **LLM**: OpenAI o3(추론·코딩 에이전트, 블로그 요약에 따르면 deep research 포함).
- **ICL 사용 방식**: 실험 데이터와 간결한 문제 서술만 주었다. o3가 물리 모델을 가설로 세우고, 식을 유도하고, 피팅 코드를 작성·실행하고, 가정을 수정하는 과정을 한 세션 안에서 반복했다(블로그 요약 기준 29분).
- **탐색 루프**: 에이전트의 자기 반복(가설 → 유도 → 코드 피팅 → 진단 → 수정). 정형화된 진화 탐색이나 MCTS는 아니다.
- **데이터셋**: 카복실산 십여 종이 금속-유기 층(MOL)에 경쟁 흡착하는 실험 데이터.
- **핵심 결과**: Langmuir 경쟁 흡착에 site accessibility 같은 구조 제약을 더한 3-파라미터 모델을 얻었다. 십여 개 분자 전체에서 실험과 맞았다. 저자들이 몇 달 동안 풀지 못한 문제였다고 한다.
- **한계**: 사례 하나다. 공개 요약에 정량 적합 지표가 없다. 재현성과 run 간 분산이 보고되지 않았다.
- **⚠ 검증 수준**: 서지(제목, 저자, 저널, DOI, 초록)는 Crossref로 확인했다. 본문(프롬프트, 수치)은 유료벽 때문에 읽지 못해 방법 세부는 초록과 대학·블로그 요약에 의존한다.
- **본 원고와의 관련성**: MOF 계열 흡착을 LLM이 닫힌 식으로 모델링한 화학 저널 사례라, BAM-ICL의 MOF CO2 흡착 응용과 바로 연결된다. 정형 SR보다는 "LLM이 과학적 모델을 쓴다"는 서사의 근거로 인용하기 좋다.

## 6. Iterated Agent for Symbolic Regression (IdeaSearchFitter)

- **저자**: Zhuo-Yang Song, Zeyu Cai, Shutao Zhang, Jiashen Wei, Jichen Pan, Shi Qiu, Qing-Hong Cao, Tie-Jiun Hou, Xiaohui Liu, Ming-xing Luo, Hua Xing Zhu (IdeaSearch Collaboration, PKU 등)
- **연도/venue**: 2025 (v1 2025-10-09). arXiv only, physics.comp-ph.
- **링크**: https://arxiv.org/abs/2510.08317
- **LLM**: 10개 LLM 앙상블(gpt-5-mini, gpt-5, qwen3, qwen-plus, gemini-2.5-flash, deepseek-v3, grok-4, doubao, gemini-2.5-pro ×2). 식 변환기는 gemini-2.5-flash.
- **ICL 사용 방식**: 전처리 단계에서 데이터와 불확도의 진단 리포트를 만들고, 메타데이터와 경계조건 같은 사전지식을 LLM이 맥락 요약으로 확장한다. 매 epoch마다 현재 상위 아이디어를 seed로 프롬프트에 넣는다. LLM은 **자연어 근거(rationale)**와 스케치 식을 쓰고, 추출기 LLM이 이를 정규 기호식, 파라미터 이름, 범위, 단위로 바꾼다.
- **탐색 루프**: multi-island 진화(8–12 island, 5–30 epoch). 변이는 모두 LLM이 하고 tree mutation/crossover는 껐다. 계수는 SciPy L-BFGS-B(범위 [-10, 10])로 맞춘다. 최종 선택은 reduced χ² 대 복잡도 Pareto front.
- **데이터셋**: Feynman SR Database(120문제, 노이즈 0–0.1), PMLB 실데이터 8개, CT18NNLO parton distribution function.
- **핵심 결과**: FSReD 복원율은 노이즈 없음에서 82.5%(PySR 48.3%, AI-Feynman 53.3%), 노이즈 0.1에서 71.7%(PySR 25.8%). PDF ū 외삽(Q = 100 GeV)에서 χ² 37.2(PySR 129.0).
- **한계**: 상용 LLM API에 의존한다. 차원 해석의 이득이 작다. PMLB는 8개뿐이다. baseline은 차원 해석을 끄고 돌렸다.
- **본 원고와의 관련성**: 단위와 범위를 붙이고 자연어 근거로 식을 유도하는 설계는, BAM-ICL이 최근접 거리로 파라미터 범위를 정하는 방식과 비슷하다. 여러 LLM을 앙상블로 쓰는 점은 원고의 "단일 LM" 한계와 대비된다.

## 7. Symbolic Regression with Multimodal Large Language Models and Kolmogorov Arnold Networks

- **저자**: Thomas R. Harvey, Fabian Ruehle, Kit (Cristofero S.) Fraser-Taliente, James Halverson (IAIFI)
- **연도/venue**: 2025 (v1 2025-05-12). arXiv only.
- **링크**: https://arxiv.org/abs/2505.07956
- **LLM**: gpt-4o(OpenRouter). 로컬 모델은 llama3.3:70b-instruct-q4_K_M, codestral, mistral v0.3(ollama).
- **ICL 사용 방식**: 원시 수치 대신 **함수 그래프 이미지**를 넣는다. 현재 population에서 softmax로 뽑은 두 함수를 Python lambda로 보여 주고, 세 번째 lambda를 완성하게 한다(FunSearch식 prompting). scipy.special 사용을 유도해 Bessel 함수 같은 특수함수도 제안할 수 있다.
- **탐색 루프**: GA(population 25, 10세대). 계수는 SciPy optimizer로 맞춘다. 다변수 문제는 KAN을 학습·가지치기한 뒤 각 edge의 1변수 함수를 LLM-LEx로 맞추고, sympy와 LLM으로 단순화해 재피팅한다(KAN-LEx).
- **데이터셋**: Mathematica로 무작위 생성한 1변수 함수 20개, 그리고 KAN 예제(exp[sin(πx)+y²], xy, xy/z).
- **핵심 결과**: 정확 복원 gpt-4o 12/20, codestral 12/20, Mathematica FindFormula 8/20. gpt-4o로 20문제 약 22분이 걸렸고 run당 약 0.5달러.
- **한계**: 1변수 중심이다. 노이즈 0.03에서 실패한다. 표본이 성기면 aliasing이 생긴다. KAN-LEx는 실패 사례를 거의 고치지 못했다. 저자 스스로 SOTA를 넘을 것으로 기대하지 않는다고 썼다.
- **본 원고와의 관련성**: plot을 입력으로 쓰는 멀티모달 ICL-SR의 대표 2025년 사례다. 원고의 잔차 "표" 입력과 대비되며, 잔차 그래프 입력을 추가 실험 아이디어로 쓸 수 있다.

## 8. NewtonBench: Benchmarking Generalizable Scientific Law Discovery in LLM Agents

- **저자**: Tianshi Zheng, Kelvin Kiu-Wai Tam, Newt Hue-Nam K. Nguyen, Baixuan Xu, Zhaowei Wang, Jiayang Cheng, Hong Ting Tsang, Weiqi Wang, Jiaxin Bai, Tianqing Fang, Yangqiu Song, Ginny Y. Wong, Simon See (HKUST, NVIDIA)
- **연도/venue**: 2025 (v1 2025-10-08). ICLR 2026.
- **링크**: https://arxiv.org/abs/2510.07172
- **LLM**: GPT-4.1-mini, GPT-4.1, o4-mini, GPT-5-mini, GPT-5, DeepSeek-V3, DeepSeek-R1, QwQ-32B, Qwen3-235B, Gemini-2.5-flash, Gemini-2.5-pro.
- **ICL 사용 방식**: 정적 데이터셋을 주지 않는다. 에이전트가 `run_experiment` 도구로 입력을 골라 시뮬레이터 출력을 받는다(최대 10라운드 × 20입력). 프롬프트에는 도구 문법, 목표, 보조 법칙을 넣는다. 조건은 vanilla와 Python interpreter 사용 두 가지다.
- **탐색 루프**: 에이전트가 직접 실험을 설계하고 가설을 세운다. counterfactual law shift(알려진 법칙을 체계적으로 변형)로 암기를 막는다.
- **데이터셋**: 물리 12분야, shifted law 108개 × 시스템 복잡도 3단계 = 324과제. 지표는 symbolic accuracy(LLM judge, 인간과 98.3% 일치)와 RMSLE.
- **핵심 결과**: GPT-5 vanilla 75.9%로 최고(Complex/Hard 40.3%). non-reasoning 모델은 10% 미만이다. 코드 도구는 약한 모델에는 도움이 되지만 강한 모델은 조기 exploitation 때문에 오히려 떨어진다. 노이즈 10⁻⁴만으로 GPT-5-mini가 12–16%p 떨어진다.
- **한계**: 물리만 다룬다. 고정 예산이다. (**[정정]** v3 부록 E.5에서는 PySR과 LLM-SR을 비교한다.) exploration 분석은 상관관계 수준이다.
- **본 원고와의 관련성**: reasoning 모델과 non-reasoning 모델 사이의 큰 격차, 그리고 노이즈 민감도는 BAM-ICL이 여러 LLM을 비교할 때 해석 근거가 된다. 암기 방지 설계(counterfactual)도 contamination 논의에 인용할 수 있다.

## 9. EvoSLD: Automated Neural Scaling Law Discovery with Large Language Models (현재 제목 "Can Language Models Discover Scaling Laws?")

- **저자**: v1은 Haowei Lin, Xiangyu Wang, Jianzhu Ma, Yitao Liang. v5는 James Zou 등을 더해 11명.
- **연도/venue**: 2025 (v1 2025-07-27, v5 2026-01-22). arXiv only. 후속판에서는 방법 이름이 SLDAgent로 바뀌었다.
- **링크**: https://arxiv.org/abs/2507.21184 · 코드 https://github.com/linhaowei1/SLD
- **LLM**: o4-mini-2025-04-16(v1). 후속판 leaderboard에는 gpt-5 등도 있다.
- **ICL 사용 방식**: 부모 (식, optimizer) 쌍과 다른 고득점 쌍을 점수와 함께 넣고, scaling law 연구 배경과 데이터 통계(점 개수, 변수 범위)를 넣는다.
- **탐색 루프**: AlphaEvolve식(OpenEvolve 구현), 50세대, 3 island, 20세대마다 10% migration. **식 서브루틴과 optimizer 서브루틴을 함께 진화**시킨다. 초기값은 단순 power law와 BFGS다.
- **데이터셋**: v1은 vocabulary size, SFT, domain mixture, MoE, data-constrained pretraining 5개 시나리오. 후속판은 5,000개 이상의 실험, 8과제(SLDBench).
- **핵심 결과(v1)**: 2개 시나리오에서 인간이 만든 법칙을 정확히 재발견했고, 나머지에서는 NMSE가 더 낮았다(domain mixture 0.0007 대 0.0669). PySR은 control variable이 있는 문제를 다루지 못한다. optimizer 공동 진화로 SFT와 MoE의 NMSE가 약 1자릿수 줄었다.
- **한계**: 공개 논문에서 모은 데이터만 쓰고 능동 실험이 없다. 사전학습 데이터 누출 가능성이 있다. 일부 법칙은 외삽이 나쁘다. 대상이 물리·재료가 아닌 ML scaling law다.
- **본 원고와의 관련성**: "계수 피팅 방법까지 LLM이 쓴다"는 설계가, refit 없이 LLM이 수치를 직접 쓰는 BAM-ICL과 LLM-SR(skeleton + BFGS) 사이의 중간 지점이다. 수치 처리 설계를 논의할 때 비교 대상이 된다.

## 10. Foundation models for equation discovery in high energy physics

- **저자**: Manuel Morales-Alvarado (INFN Trieste / SISSA, 단독)
- **연도/venue**: 2025 (v1 2025-10-03). arXiv only, hep-ph.
- **링크**: https://arxiv.org/abs/2510.03397
- **LLM**: GPT-4o(LLM-SR backbone).
- **ICL 사용 방식**: LLM-SR 프로그램 템플릿을 쓴다. docstring에 회귀 대상과 물리 제약(예: pT → 0에서 A0 → 0)을 넣고, 변수 설명(bin 중심, 값, 불확도), `evaluate` 손실(가중 χ²), 초기 프로그램 prior(정보 있는 유리함수 형태와 정보 없는 형태를 ablation으로 비교)를 넣는다.
- **탐색 루프**: LLM-SR 100 iteration, experience buffer. 계수는 numpy/scipy 또는 torch로 최적화하고, 파라미터는 4–10개로 제한한다.
- **데이터셋**: MadGraph 의사데이터. e⁺e⁻→μ⁺μ⁻ 각분포(내삽, 외삽), Drell–Yan 각계수 A0(pT), A4(pT,|y|), A4(pT,|y|,m).
- **핵심 결과**: 외삽에서 LLM-SR 손실 1.46×10⁻⁶ 대 PySR 2.42×10⁻². LLM-SR은 올바른 cos²θ 형태를 찾았고 PySR은 복잡한 유리함수를 냈다. 해석식이 없는 각계수에 대해서도 간결한 식을 얻었다.
- **한계**: PySR보다 느리다. 하이퍼파라미터와 프롬프트 설계에 민감하다. 도메인 지식의 정량 이득이 작고, 주로 외삽과 물리적 타당성을 개선한다. 계통 불확도는 다루지 않았다.
- **본 원고와의 관련성**: 범용 ICL-SR을 특정 과학 분야에 그대로 적용한 2025년 사례로, BAM-ICL처럼 "도메인 데이터 + 물리 제약 프롬프트" 구성이다. 도메인 지식이 정확도보다 외삽에 효과적이라는 관찰은 원고의 OOD 논의와 비교할 만하다.

---

## 차순위 (runner-up)

1. **LLM-Meta-SR: In-Context Learning for Evolving Selection Operators in Symbolic Regression** (Zhang, Chen, Xue, Banzhaf, Zhang; arXiv 2025-05). https://arxiv.org/abs/2505.18602. ICL을 쓰지만 식이 아니라 GP의 선택 연산자를 설계하므로 차순위로 내렸다.
2. **Knowledge Integration for Physics-informed Symbolic Regression Using Pre-trained Large Language Models** (Taskin, Xie, Lazebnik; arXiv 2025-09). https://arxiv.org/abs/2509.03036. LLM이 식을 제안하지 않고 GP 손실 안의 평가자 역할만 한다(Falcon, Mistral, Llama 2와 DEAP, gplearn, PySR).
3. **Mimicking the Physicist's Eye: A VLM-centric Approach for Physics Formula Discovery** (VIPER-R1; Liu et al.; arXiv 2025-08). https://arxiv.org/abs/2508.17380. 멀티모달 SR이지만 SFT와 RL 학습이 핵심이라 ICL 기준에서 뺐다.
4. **Can Large Language Models Adequately Perform Symbolic Reasoning Over Time Series?** (SymbolBench; Liu et al.; arXiv 2025-08). https://arxiv.org/abs/2508.03963. 다변량 SR을 포함한 시계열 벤치마크와 LLM+GP 루프를 제안한다.
5. **Finetuning Large Language Model as an Effective Symbolic Regressor** (Symbolic-R1 / SymbArena; Hua et al.; arXiv 2025-08). https://arxiv.org/abs/2508.09897. 파인튜닝 방법이라 제외했지만, prompting 기반 방법의 반복 비용을 비판하는 대조군으로 유용하다.

## 관찰 (BAM-ICL 원고 관점)

- 2025년 방법 논문(DrSR, SR-Scientist, IdeaSearchFitter, LLM-SR 응용) 대부분은 **LLM이 형태를 쓰고 BFGS/L-BFGS-B가 계수를 맞추는** 구조다. ~~LLM-Feynman과 EvoSLD뿐~~ **[정정, codex 교차검토]** EvoSLD는 LLM이 쓴 optimizer 코드를 실행해 계수를 맞추므로 no-refit 사례가 아니다. LLM-Feynman의 no-refit 여부도 미확인이다. 확인된 no-refit 선행연구는 목록 밖의 LMX(Meyerson et al. 2023, arXiv:2302.12170)이며 SYNTHESIS.md를 참고.
- 이번 조사에서 2025년에 **MLIP·원자간 퍼텐셜 보정항을 LLM ICL로 쓰는 논문은 찾지 못했다**. 재료 응용은 기술자 기반 물성 회귀(LLM-Feynman)와 흡착 모델(Angewandte o3)이 전부였다.
- 벤치마크(LLM-SRBench, NewtonBench) 모두 암기 통제를 핵심으로 삼는다. 원고에 contamination 논의를 넣을 때 두 논문을 함께 인용하는 것을 권한다.

## 검증 메모

- `⚠` **From Data to Physics (#5)**: 서지는 Crossref로 확인했다. 본문은 유료벽 때문에 읽지 못해 방법과 수치는 초록과 2차 요약에 의존한다.
- `⚠` **LLM-Feynman (#4)**: arXiv 메타데이터 제목과 PDF 제목이 다르다(Theory 대 Knowledge). PDF는 앞 12쪽만 읽었다(고체전해질과 GW 밴드갭 결과는 확인하지 않음). 계수 피팅 단계가 없다는 해석도 이 범위에 근거한다.
- **DrSR (#2)**: 본문 안에 과제 수와 iteration당 후보 수가 서로 다르게 적혀 있다.
- **IdeaSearchFitter (#6)**: LLM 목록과 피팅 방법은 HTML 부록에서 확인했다.
- 나머지는 arXiv abs와 HTML 본문으로 확인했다. venue는 arXiv comments(ICML 2025 Oral, ICLR 2026)와 PMLR 페이지 기준이다.
