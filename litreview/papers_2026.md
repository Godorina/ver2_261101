# 2026년 LLM in-context symbolic regression 문헌 10편

조사일: 2026-11-01. 범위: 2026년 1~10월에 처음 공개(arXiv v1)되거나 학회에 게재된 논문. 주제는 LLM을 프롬프팅(파인튜닝 없음 또는 최소)으로 써서 데이터에서 closed-form 식을 찾는 연구.

**검증 방법.** 10편 모두 arXiv abs 페이지에서 제목, 저자, v1 날짜, comments(학회 표기)를 직접 확인했다. 방법과 수치는 arXiv HTML 전문에서 읽었다(2607.04156만 HTML이 404라서 PDF를 텍스트로 변환해 읽음). 수치는 모두 저자가 보고한 값이며 재현하지 않았다. 확인 수준이 낮은 부분은 각 항목에 **[검증 약함]**으로 표시했다.

**선정 기준.** (a) LLM이 루프 안에서 식을 제안하는 핵심 방법 5편, (b) 벤치마크 비판 1편, (c) 재료·화학·배터리 응용 4편. 순수 ICL 방법이 아니라 LLM이 GP 엔진(PySR)의 탐색 공간을 제어하는 hybrid도 (c)에 포함했다. 재료 응용이 드물어서 넣은 것이며, 해당 항목에 그 차이를 적었다.

**BAM-ICL 원고와 비교한 공통 결론.** 10편 모두 LLM은 식의 구조(skeleton, 기저 함수, 탐색 공간)만 정하고 계수는 BFGS, OLS, PySR 같은 수치 최적화기가 맞춘다. 원고처럼 LLM이 계수까지 직접 쓰고 refit을 하지 않는 방식은 2026년 문헌에서 찾지 못했다. 원고와의 차별점으로 강조할 수 있다.

---

## 요약표

| # | 논문 | 날짜 / 학회 | 분류 | LLM | 재료 관련성 |
|---|---|---|---|---|---|
| 1 | Influence-Guided Symbolic Regression (IGSR) | 2026-05-27 / ICML 2026 | (a) | GPT-4o, GPT-4o-mini 외 9종 | 중 |
| 2 | Deliberate Evolution (DE) | 2026-06-03 / ICML 2026 | (a) | Llama-3.1-8B, Qwen3-4B | 중(알루미늄 응력-변형) |
| 3 | FunctionEvolve | 2026-06-05 / arXiv | (a)+(b) | Claude Opus 4.6 외 | 상(MatSci subset 감사) |
| 4 | Programmatic Context Augmentation (ProAug) | 2026-05-04 / arXiv | (a) | Qwen3-4B/8B, DeepSeek-V3.1 | 중 |
| 5 | KeplerAgent (Think like a Scientist) | 2026-02-12 / arXiv | (a) agentic | GPT-4o-mini | 중 |
| 6 | Library Reachability in LSR-Synth | 2026-07-30 / arXiv | (b) | Qwen3-Coder, GPT-4.1 등 | 상(MatSci 25 tasks 포함) |
| 7 | LLM-PySR (controlling search) | 2026-07-05 / arXiv | (b)+(c) | GPT-5.1 | 상(Li-ion 수명) |
| 8 | DASyR-LLM | 2026-08-05 / arXiv | (c) | Qwen3-14B | 상(불균일 촉매 반응속도) |
| 9 | LangLaw | 2026-02-26 / arXiv | (c) | Intern-S1 | 최상(perovskite) |
| 10 | EO-SR | 2026-02-12 / arXiv | (c) | Gemini (버전 불명확) | 상(고무 구성방정식) |

---

## 1. Influence-Guided Symbolic Regression: Scientific Discovery via LLM-Driven Equation Search with Granular Feedback

- **저자:** Evgeny S. Saveliev et al. (Mihaela van der Schaar 그룹)
- **날짜 / 학회:** arXiv v1 2026-05-27, **ICML 2026**
- **링크:** [arXiv:2605.29184](https://arxiv.org/abs/2605.29184)
- **LLM:** GPT-4o(메인 벤치마크, 25 seeds), GPT-4o-mini(LLM-SRBench, 문제당 5 seeds). 부록에서 open-weight 모델 포함 총 9개 backbone을 비교.
- **ICL 방식:** Propose LLM에 들어가는 것: 변수의 도메인 설명, 현재 활성 항들, 지금까지의 최고 식, 이전 iteration 이력(어떤 항을 남기거나 버렸고 MSE가 어떻게 변했는지). LLM은 기저 함수 후보를 약 5개(첫 라운드 10개) 낸다. 에이전트 변형에서는 Prune LLM이 항별 (ψ_j, w_j, Δ_j)를 받아 제거할 항을 고른다. 원시 데이터 포인트를 프롬프트에 넣는지는 본문에 없고, 템플릿은 부록 B.7에 있다.
- **탐색 루프:** LLM이 기저 함수 제안 → OLS 선형모델 적합 → 각 항의 influence Δ_j 계산(validation에서 해당 가중치를 0으로 놓았을 때 늘어나는 오차) → 상위 K=6 항 유지 → MCTS(UCT)로 확장. 30회 확장, 노드당 자식 5개.
- **데이터셋:** LLM-SRBench 128문제(Physics, Biology, Material Science, Chemistry), 폐암 PKPD 3종, Covasim(COVID-19), Warfarin 약동학, RNA Pol II pausing(263 features).
- **핵심 결과:** 6개 데이터셋 평균 순위 1.17(ICL 3.83, ICSR 4.17, LaSR 6.33, PySR 6.17, LLM-SR 7.00). Lung Cancer MSE 5.64e-5 vs LLM-SR 33.4. LLM-SRBench ID NMSE 평균 순위 1.35 vs LLM-SR 3.71. Symbolic accuracy는 1.17 vs 1.29로 차이가 작다. ablation에서 influence feedback을 빼면 NMSE가 0.000787에서 0.293으로 나빠진다. DNA methylation과 Pol II pausing의 관계를 찾았고 wet-lab에서 지지됐다.
- **한계:** 식이 기저 함수의 선형결합으로 제한되어 중첩된 비선형 구조는 어렵다. LLM prior에 없는 형태는 나오기 어렵다. parsimony 항이 없다.
- **재료 ICL-SR 관련성:** 원고의 `f_q = Σ n_Z c_Z + Σ φ_t`처럼 "물리 항 라이브러리의 선형결합" 구조라는 점이 가장 비슷하다. 항별 influence 피드백은 원고의 refinement 프롬프트(상위 후보 + 점수 + 잔차)를 항 단위로 세분화하는 확장으로 인용할 수 있다.

## 2. Deliberate Evolution: Agentic Reasoning for Sample-Efficient Symbolic Regression with LLMs

- **저자:** Xinyu Pang et al. (Bo Han, Changshui Zhang)
- **날짜 / 학회:** arXiv v1 2026-06-03, **ICML 2026**
- **링크:** [arXiv:2606.04360](https://arxiv.org/abs/2606.04360)
- **LLM:** Llama-3.1-8B-Instruct, Qwen3-4B-Instruct-2507 (vLLM, T=0.8)
- **ICL 방식:** 프롬프트에 들어가는 것: 문제 맥락, 선택된 parent 식, 선택된 연산자, 진단 보고서(변수 범위, 주기성, 상호작용, parent 잔차 패턴, 차원 검사), reflective memory(성공 motif, 실패 유형, 정체 요약). 이전 식과 점수는 parent, elite 집합, memory를 통해 간접적으로 들어간다.
- **탐색 루프:** island population에서 Boltzmann 선택 → 연산자(refine/mutate/crossover/regenerate)를 탐색 상태별 categorical policy로 선택(개선량으로 곱셈 갱신) → LLM이 skeleton 제안 → BFGS로 상수 적합. stagnation monitor가 있다.
- **데이터셋:** LLM-SRBench 240문제(LSR-Transform, LSR-Synth: Physics/Chemistry/Biology/MatSci), 노이즈(1%, 5%), 실제 알루미늄 응력-변형 데이터.
- **핵심 결과:** Qwen3-4B, LSR-Transform에서 NMSE 0.115(LaSR 0.183), Acc0.01 50.45%(30.91%). Llama3.1-8B, LSR-Transform에서 NMSE 0.112(LLM-SR 0.242). 샘플 예산은 baseline의 40%(400 vs 1000 LLM samples). 진단 도구를 빼면 Physics NMSE가 4.37e-4에서 2.52e-2로 나빠진다.
- **한계:** open-weight 모델 2개만 시험했다. 수렴 보장이 없다. LLM 추론 때문에 GP보다 느리다. 노이즈는 Gaussian만 다뤘다.
- **재료 ICL-SR 관련성:** 작은 open-weight LLM으로도 진단 정보와 메모리를 문맥에 넣으면 큰 개선이 난다는 근거다. 원고의 로컬 Qwen 4-bit 결과를 해석할 때 인용할 수 있다. 알루미늄 응력-변형 실데이터 사례도 재료 쪽 비교점이다.

## 3. FunctionEvolve: Structure-Guided Symbolic Regression with LLMs

- **저자:** Zeyu Xia, Jun Zhu, Dong Yan
- **날짜 / 학회:** arXiv v1 2026-06-05 (학회 표기 없음)
- **링크:** [arXiv:2606.07704](https://arxiv.org/abs/2606.07704)
- **LLM:** Claude Opus 4.6(주력). GPT-5.2-medium, DeepSeek-V4-Pro, Qwen3.6-27B, Llama-3.1-8B도 시험.
- **ICL 방식:** Generator는 과제 배경, 변수 의미, 도메인 지식 요약을 받아 SymPy 식을 JSON으로 낸다. Selector는 evolution-tree 요약(AST, 파라미터 수, 깊이, 연산자 수, **train** NMSE, 적합 계수)만 받고, test/OOD 오차는 의도적으로 넣지 않는다. Mutator는 parent의 AST, 규칙 기반 후보, 탐색 이력을 받는다. 원시 데이터는 프롬프트에 넣지 않는다.
- **탐색 루프:** expression tree 기반 진화. 구조 요약으로 다양한 parent 선택 → 하위식을 보존하는 국소 tree 편집 → 구조 지문으로 중복 제거 → 구조 인지 계수 적합(variable projection + OLS, DE/CMA-ES, L-BFGS, 상수 snapping 후 재적합). 최대 30 iterations.
- **데이터셋:** LLM-SRBench synthetic 129문제, AI-Feynman 120문제.
- **핵심 결과:** Claude Opus 4.6으로 SA@50 107/129(82.9%), SA@1 55.8%. 각각 같은 backbone baseline의 4.5배, 기존 최고 top-1(PiT-PO)의 3.6배. LLM 없는 변형은 SA@50 29. 과제당 LLM 호출 약 67회(LLM-SR 1000회). AI-Feynman은 120/120.
- **벤치마크 감사(재료 관련 중요):** LLM-SRBench MatSci 25문제는 모두 ε(strain)와 T를 쓰는데, 표본이 train/test/OOD 전부에서 T ≈ 273 + 500ε로 1차원에 붕괴해 있다(상관 1과의 차이 < 2.7e-12). 그래서 온도 의존성은 식별할 수 없고, Arrhenius 인자 exp(−c/T)는 상수처럼 보인다. MatSci 성적이 낮은 이유(SA@50 15/25)를 일부 설명한다.
- **한계:** 정답 형태를 만들어도 1순위로 뽑지 못하는 ranking gap이 있다. 노이즈에 약하다(5% 노이즈에서 SA@50 40). 함수족이 elementary로 한정된다. AI-Feynman은 사전학습 데이터와 겹칠 수 있다.
- **재료 ICL-SR 관련성:** "LLM-SRBench의 재료 subset으로는 재료 SR 능력을 제대로 잴 수 없다"는 근거를 준다. 원고가 실제 재료계(cathode, 촉매, MOF)로 평가한 이유를 정당화하는 데 직접 쓸 수 있다.

## 4. Programmatic Context Augmentation for LLM-based Symbolic Regression

- **저자:** Hao Liu et al. (Atharva Sehgal, Yisong Yue: LaSR 저자진 포함)
- **날짜 / 학회:** arXiv v1 2026-05-04 (학회 표기 없음)
- **링크:** [arXiv:2605.03101](https://arxiv.org/abs/2605.03101)
- **LLM:** Qwen3-4B-Instruct-2507, Qwen3-8B, DeepSeek-V3.1 (LLM-SR 프레임워크 위에서). 별도 실험으로 Qwen3 SFT(DeepSeek-V3.1에서 distill)도 했다.
- **ICL 방식:** 매 iteration마다 LLM이 분석 코드 템플릿(기술통계, 상관, log/exp/sin/cos 변환과 변수 조합의 R²)을 보고 분석 코드를 작성한다. 그 코드를 데이터에 실행한 결과를 "informative signals"로 문맥에 추가한다. 여기에 과제 설명, 변수의 물리적 의미, 경험 버퍼(과거 가설과 개선 궤적)를 합친 프롬프트로 식 skeleton을 생성한다.
- **탐색 루프:** LLM-SR식 진화 버퍼. 파라미터는 train-train split에서 적합하고, fitness는 train-val split의 −NMSE.
- **데이터셋:** LLM-SRBench 부분집합(LSR-Transform 17개, LSR-Synth 16개, MatSci 포함), 3 seeds.
- **핵심 결과:** LSR-Transform 평균 NMSE, DeepSeek-V3.1에서 LLM-SR 0.230 → ProAug 0.067(약 3배). Qwen3-4B에서 0.258 → 0.145. LSR-Synth, Qwen3-4B에서 0.480 → 0.027. run 간 분산이 크게 줄었다.
- **한계:** 분석 연산이 고정 템플릿이다. 약한 모델은 긴 문맥에 압도될 수 있다. 생성 코드가 실행되지 않을 때가 있다. 평가 문제 수가 적다(33문제).
- **재료 ICL-SR 관련성:** 원시 데이터 대신 요약 통계나 잔차를 문맥에 넣는 설계(원고 비교 축 4)의 직접 비교 대상이다. 원고의 "BAM 오차·잔차 힘 표"가 손으로 설계한 context augmentation에 해당한다고 위치시킬 수 있다.

## 5. Think like a Scientist: Physics-guided LLM Agent for Equation Discovery (KeplerAgent)

- **저자:** Jianke Yang et al. (Rose Yu)
- **날짜 / 학회:** arXiv v1 2026-02-12, v2 2026-02-24 (학회 표기 없음)
- **링크:** [arXiv:2602.12259](https://arxiv.org/abs/2602.12259)
- **LLM:** GPT-4o-mini(에이전트, LLM-SR baseline, 시각 subagent, SA 판정 모두)
- **ICL 방식:** 문맥에 들어가는 것: 시스템 프롬프트, 도구 명세, 회귀 목표와 데이터 설명, 작업공간 파일 목록, experience log(모든 도구 호출, 인자, 결과 요약). 도구 출력도 들어간다: Python 요약통계와 플롯, 시각 subagent의 플롯 해석, 대칭성 행렬 A.
- **탐색 루프:** ReAct 루프로 JSON tool call을 낸다(step당 최대 3개). 도구는 Python 인터프리터, 시각 subagent, 대칭성 발견(작은 MLP surrogate), PySINDy(equivariant 옵션), PySR. LLM이 PySR template(예: f(x1,x2)+g(x3))과 SINDy library를 설정한다. MAPE < 0.1%이거나 호출 상한에 닿으면 멈춘다.
- **데이터셋:** LSR-Transform 111문제, 자체 DiffEq(ODE/PDE 10계, 20개 식, clean과 noisy).
- **핵심 결과:** LSR-Transform SA: KeplerAgent@3 42.34%, @1 35.14%, PySR 37.84%, LLM-SR 31.53%. 토큰은 LLM-SR의 1/5~1/2. DiffEq SA clean/noisy: 75%/45%(PySR 40/15, LLM-SR 30/10).
- **한계:** 도구 수가 늘면 문맥이 커진다. 선형 대칭만 다룬다. 단일 base model이다. SA를 LLM judge가 판정한다.
- **재료 ICL-SR 관련성:** LLM이 식을 직접 쓰지 않고 물리 구조(대칭성)를 추출해 탐색을 제약하는 방식이다. 원고가 φ_t 라이브러리(Born–Mayer, Morse, EAM)로 함수 공간을 제약한 것과 같은 "physics prior로 공간 축소" 계열로 묶어 논의할 수 있다.

## 6. Library Reachability in LSR-Synth: How Anti-Memorization Design Changes the Measurement of Symbolic Discovery

- **저자:** Zhan'ao Yao et al. (12인)
- **날짜 / 학회:** arXiv v1 2026-07-30 (학회 표기 없음)
- **링크:** [arXiv:2607.28684](https://arxiv.org/abs/2607.28684)
- **LLM:** 주 실험 LLM은 본문에 이름이 없다(API 접근). backbone 점검으로 Qwen3-Coder-480B, GPT-4.1, GLM-4.6, DeepSeek-V3.1을 썼고, SA 판정은 GPT-OSS-120B(10회 투표).
- **ICL 방식(평가 대상):** LLM이 변수명과 도메인 맥락을 받아 원자 항(atomic terms) 후보를 제안한다(L1). L2에서는 변수를 익명화하고 도메인 설명을 제거한다(semantic blinding).
- **탐색 루프 / 실험 설계:** 같은 탐색과 예산에서 후보 출처만 바꿔 비교한다. BANK는 LaSR/PySR 연산자로 만든 고정 어휘(변수 1/2/3개일 때 후보 10/30/60개), LLM은 LLM 후보, UNION은 둘의 합집합. 추가로 library weakening(다항식만 남긴 BANK-Poly), 연산자 family knockout과 sham knockout 대조를 했다.
- **데이터셋:** LSR-Synth 129문제(생물 24, 물리 44, 화학 36, **재료 25**), 4 seeds, 516 task-seed 쌍.
- **핵심 결과:** 의미 정보를 전혀 쓰지 않는 BANK-LaSR이 Acc0.01 **77.71%**다(**[정정]** SR-Scientist 63.57%와는 예산과 탐색 조건이 달라 직접 비교할 수 없다). LLM 성공 257건 중 254건은 BANK도 성공해서 LLM만 푼 문제는 3건뿐이다. UNION은 77.33~77.71%로 거의 변화가 없다. 다만 어휘를 다항식으로 약화하면 LLM 후보가 Acc0.01을 27.52%에서 58.14%로 끌어올린다. 즉 LLM prior는 어휘 커버리지가 깨졌을 때만 크게 기여한다.
- **한계:** knockout은 15문제 pilot이고 CI가 0을 포함한다. 어휘와 예산을 저자가 선택했다. 단일 OOD split만 썼다. 저자들도 "LLM이 일반적으로 불필요하다"고 주장하지는 않는다.
- **재료 ICL-SR 관련성:** 원고의 리뷰어가 "LLM이 아니라 φ_t 라이브러리가 일을 한 것 아니냐"고 물을 수 있다는 점을 미리 보여준다. 같은 라이브러리에서 LLM 없이 하는 탐색(무작위나 greedy 항 선택)을 대조군으로 넣으라는 권고로 직접 이어진다.

## 7. Language models guide symbolic equation discovery by controlling search (LLM-PySR)

- **저자:** Zikai Xie, Wenmei Li, Man Luo, Jun Jiang, Linjiang Chen (USTC 화학·재료과학부)
- **날짜 / 학회:** arXiv v1 2026-07-05 (학회 표기 없음)
- **링크:** [arXiv:2607.04156](https://arxiv.org/abs/2607.04156)
- **LLM:** GPT-5.1(모든 LLM 기반 조건). 출력 repair와 DrSR extractor에는 GPT-4o-mini.
- **ICL 방식:** LLM에 과학적 맥락과 experience memory(이전 iteration의 결정적 피드백과 후보 평가 요약)를 주고, 변수 부분집합, 연산자, 변환, 복잡도(탐색 깊이) 스케줄을 구조화된 형태로 제안하게 한다. LLM reviewer는 의미와 해석성 점수를 보조로만 매긴다.
- **탐색 루프:** LLM이 탐색 공간을 계획하면 결정적 검증을 거쳐 PySR이 열거하고 상수를 적합한다(population 128, 100~500 iterations 적응). 이어서 수치 지표 gate로 유지 여부를 정하고, 그 결과를 메모리로 요약한다. 최대 10회 반복 후 ablation pruning으로 단순화한다. LLM의 역할을 5가지로 바꿔 비교했다: equation author, candidate decider, search controller, full-stack(LLM-SR, DrSR), no-LLM(PySR).
- **데이터셋:** AI-Feynman 74식, DrSR의 복잡 식 7개(oscillator, bactgrow, stress-strain, LSR 사례), **Severson et al. LFP/흑연 셀 124개 수명 데이터**(41/43/40 분할).
- **핵심 결과:** AI-Feynman Acc0.1: controller 0.958, decider 0.952, PySR 0.922, author 0.892, LLM-SR 0.892, DrSR 0.665. 토큰은 LLM-SR의 4.1%, DrSR의 3.2%. author와 full-stack은 익숙한 식(CRK0, oscillator1)은 거의 맞히지만 낯선 식(bactgrow, stressstrain)에서 붕괴했다. 저자들은 이를 암기된 prior에 묶인 증거로 해석한다. 배터리에서는 log10(N_life) = 9.535x + 4.475|x+0.0411| + 3.208(x = ΔQ_100−10 최소값)을 찾았고, 독립 test 40셀에서 RMSE 0.0772, R² 0.831.
- **한계:** 복잡 식 suite가 7개뿐이다. 배터리 특성 11개는 사람이 사전에 추출했다. 수치 지표가 표에 mean ± s.d.로만 있다. 학회 미게재 preprint다.
- **재료 ICL-SR 관련성:** 화학·재료 그룹이 "LLM은 식을 쓰지 말고 탐색만 제어하라"고 주장하는 논문이다. LLM이 계수까지 쓰는 원고의 설계와 정반대 입장이라 반드시 인용하고 반박하거나 대비해야 할 논문이다. 배터리 응용은 원고의 Na cathode 사례와 직접 비교된다.

## 8. DASyR-LLM: Domain-Aware Symbolic Regression with LLMs for Kinetic Model Discovery

- **저자:** Roberto Aliaga Medina, Paulina Quintanilla, Antonio del Rio Chanona (Imperial)
- **날짜 / 학회:** arXiv v1 2026-08-05 (학회 표기 없음)
- **링크:** [arXiv:2608.05120](https://arxiv.org/abs/2608.05120)
- **LLM:** Qwen3-14B(thinking mode, T=0.6). iteration마다 3개 인스턴스를 병렬로 돌린다. ablation의 소형 LLM 이름은 읽은 범위에서 확인하지 못했다.
- **ICL 방식:** 2단계 프롬프트. Step 1 critique에는 반응식, 화학종 이름, SR 상위 5개 후보와 적합 파라미터, NLL/AIC, 가역성 같은 부가 정보, few-shot 형식 예시가 들어간다. Step 2에서는 critique를 더해 구조가 서로 다른 rate expression 3개를 메커니즘 근거와 함께 제안한다. 원시 실험 데이터는 넣지 않는다.
- **탐색 루프:** ADoK-S 기반. PySR로 농도 궤적과 rate law를 2단계로 적합 → ODE 적분 기반 L-BFGS-B 재적합(20 restarts) → AIC 순위 → 상위 2개 모델의 예측 차이를 최대화하는 MBDoE로 다음 실험 조건 결정. 12 iterations.
- **데이터셋:** in silico 4개 사례. 촉매 3개(toluene hydrodealkylation의 Langmuir–Hinshelwood, N2O 분해, 가역 이성질화)와 bioprocess(Monod) 1개. σ=0.1 노이즈.
- **핵심 결과:** 정답 모델까지 필요한 iteration이 baseline SR보다 41.7~79.3% 줄었다(실험 1회 = iteration 1회이므로 실험 수 절감). 16 run 중 9 run에서 LLM이 정답 구조를 직접 제안했다. validation R² > 0.98.
- **한계:** 합성 데이터만 썼다. LLM은 하나뿐이다. LLM 출력을 수동으로 파싱했다. 실제 wet-lab 검증이 없다.
- **재료 ICL-SR 관련성:** 촉매 표면 반응(Langmuir–Hinshelwood 흡착 항)에서 LLM의 화학 지식이 구조 제안에 직접 기여한다는 2026년 근거다. 원고의 dual-atom 촉매 H 흡착 사례와 같은 도메인이다. 상위 후보 + 점수를 넣는 프롬프트 구성도 원고와 거의 같다.

## 9. Discovery of Interpretable Physical Laws in Materials via Language-Model-Guided Symbolic Regression (LangLaw)

- **저자:** Yifeng Guan et al. (Lei Bai, Wan-jian Yin, Mao Su; Shanghai AI Lab)
- **날짜 / 학회:** arXiv v1 2026-02-26 (physics.comp-ph; 학회 표기 없음)
- **링크:** [arXiv:2602.22967](https://arxiv.org/abs/2602.22967)
- **LLM:** Intern-S1(주력. 다른 LLM 결과는 Supplementary S5에 있다고 함). LLM-SR baseline은 GPT-4o.
- **ICL 방식:** LLM이 feature 설명(전기음성도, 원자 반경, 이온화 에너지 등)을 보고 물리적으로 무의미한 feature를 제거한다. 매 라운드 feature 부분집합, 최대 tree 깊이, 진화 iteration 수를 정한다. experience pool(이전 식, feature set, 하이퍼파라미터, 오차; top-k=15)을 문맥에 넣어 다음 지시를 개선한다. LLM이 식 구조를 직접 제안하는지는 본문에 명시되어 있지 않다. **[검증 약함: 프롬프트 세부는 Supplementary S2에 있고 읽지 못함]**
- **탐색 루프:** LLM이 제약을 설정 → PySR(31 populations, size 27, max size 30, L1 loss) → Pareto front 채점 → experience pool → LLM이 전략을 갱신. 오차 < 0.001이거나 100라운드에서 멈춘다.
- **데이터셋:** perovskite bulk modulus(HI-SISSO 데이터, 7,308개), double perovskite band gap(745개), OER 활성(GPSR 데이터, 18점).
- **핵심 결과:** 유효 탐색 공간 약 10^5배 축소(보충자료 수치). bulk modulus: 복잡도 17, ID MAE 0.0739(HI-SISSO 복잡도 26, MAE 0.090). OOD RMSE 0.0851(HI-SISSO 0.411, ALIGNN 0.167). band gap: RMSE 0.672 eV에서 복잡도 19(SISSO는 같은 RMSE에 복잡도 39). LLM-SR(GPT-4o)은 세 과제 모두 복잡도 54~70에 오차도 더 컸다.
- **한계:** OER은 18점뿐이라 OOD에서 GPSR보다 약간 나쁘고 복잡도도 더 높다. 초록의 "모두 우월" 주장보다 실제 결과가 약하다. 명시적 limitations 절이 없다. 재현에 필요한 세부가 보충자료에 있다.
- **재료 ICL-SR 관련성:** 2026년에 나온 재료 특화 LLM-SR 논문 중 가장 직접적이다(perovskite, 촉매 OER). SISSO와 LLM-SR을 같은 재료 데이터에서 비교했으므로 원고의 재료 결과와 나란히 놓을 수 있는 baseline 축이다.

## 10. Engineering-Oriented Symbolic Regression: LLMs as Physics Agents for Discovery of Simulation-Ready Constitutive Laws (EO-SR)

- **저자:** Yue Wu, Tianhao Su, Mingchuan Zhao, Shunbo Hu, Deng Pan
- **날짜 / 학회:** arXiv v1 2026-02-12 (ID는 2603이지만 v1 날짜는 2월 12일; 학회 표기 없음)
- **링크:** [arXiv:2603.19241](https://arxiv.org/abs/2603.19241)
- **LLM:** 본문은 "Gemini3-pro"라고 쓰지만 참고문헌은 Gemini 2.5 보고서를 가리킨다. **[검증 약함: 정확한 모델 버전 불명확]**
- **ICL 방식:** 도메인 라벨("Isotropic Hyperelasticity")만 주면 LLM이 파라메트릭 지식으로 invariant 매핑, 연산자 제외(sin/cos), Drucker 안정성(Hessian PSD) 제약을 실행 가능한 코드로 만든다. 탐색이 끝나면 Pareto 상위 후보를 받아 물리적 해석 가능성을 감사한다. LLM은 진화 루프 밖에 있다(전처리와 후처리).
- **탐색 루프:** GP-SR(island, 100 iterations, 30 populations, 최대 18 nodes)이 탐색하고, 목적함수는 적합 오차 + 복잡도 + 표본점의 제약 위반 ReLU² 벌점이다. 최종 선택은 Pareto와 LLM 판단을 결합한다.
- **데이터셋:** Treloar(1944) 고무의 단축 인장, 등이축 인장(학습), 순수 전단(zero-shot test).
- **핵심 결과:** Mooney-Rivlin 선형 기저 + 유리함수 locking 항으로 된 새 법칙을 찾았다(파라미터 4개, 학습 MSE ≈ 0.008, 순수 전단 zero-shot MSE ≈ 0.0048). Yeoh N=3은 ET MSE 0.206. Abaqus FE에서 Ogden N=3은 수렴에 실패했고 발견 식은 λ=3.0까지 수렴했다.
- **한계:** 데이터셋이 하나다. 볼록성은 표본점에서만 강제되며 저자들도 interstitial instability를 인정한다. 최종 선택이 LLM 판단에 의존해 재현성이 떨어진다. 독점 모델에 의존한다.
- **재료 ICL-SR 관련성:** LLM이 식이 아니라 열역학 제약을 쓰는 방식이다. 원고처럼 물리 항과 파라미터 범위로 함수 공간을 제약하는 설계와 비교된다. "발견 식이 시뮬레이션에 바로 쓸 수 있는가"(원고의 MLIP 보정이 MD에 쓰일 수 있는가)라는 평가 축을 제공한다. ICL-SR의 좁은 정의에서는 가장 거리가 먼 항목이다.

---

## Runner-up 5편 (모두 arXiv abs 페이지에서 확인)

1. **A-SR: Self-Evolving Agentic LLMs for Symbolic Regression via Hierarchical Coordination**: Zhao et al., 2026-08-05. [arXiv:2608.04872](https://arxiv.org/abs/2608.04872). 역할별 에이전트를 쓰고 run 안에서는 weight를 고정한 채 적응한다. LSR-Synth Acc0.01 25.79% → 48.30%(Llama3.1-8B). LoRA distillation을 포함해 순수 ICL은 아니다.
2. **EvoMO-SR: Multiobjective LLM-based Evolution of Symbolic Expressions with substructure guidance**: Rossetti et al. (Bäck, van Stein), 2026-09-28. [arXiv:2609.36187](https://arxiv.org/abs/2609.36187). LLM-SR식 skeleton 생성 + 외부 최적화기 + 다목적 선택. Llama-3.1-8B로 LSR-Synth 8개 설정 중 7개에서 최고.
3. **InsightSR: Refining Symbolic Regression Search Spaces via Parallel Semantic and Structural LLM Guidance**: Ling et al., 2026-08-26. [arXiv:2608.25291](https://arxiv.org/abs/2608.25291). PySR 주위에서 LLM이 차원 일관 skeleton과 비선형 feature 변환을 제안한다. Feynman 정확 복원 95%, LSR-Transform 80.18%.
4. **L2G-SR: Learning to Guide LLM-based Symbolic Regression**: Huang et al., 2026-10-14. [arXiv:2610.20685](https://arxiv.org/abs/2610.20685). 학습된 구조 검증기(tree edit distance)를 수치 오차와 결합해 parent를 선택한다. LLM-SRBench SOTA를 주장한다.
5. **STRIDE: A Self-Reflective Agent Framework for Reliable Automatic Equation Discovery**: Su et al., 2026-05-18. [arXiv:2605.17790](https://arxiv.org/abs/2605.17790). 데이터 인지 생성, mixed-fitting 평가, critic-executor repair, 다양성 유지 semantic memory.

**그 밖에 확인했지만 순위 밖인 2026년 논문:** MOT-SR [arXiv:2607.29561](https://arxiv.org/abs/2607.29561)(다목적, 도구 증강, EMRI 궤도 응용), AutoSR [arXiv:2608.16876](https://arxiv.org/abs/2608.16876)(Research State + MCTS 에이전트, cp3-bench). 둘 다 abs 페이지를 확인했다.

## 의도적으로 제외한 논문

- **SR-Scientist** (arXiv:2510.11661, ICLR 2026): 학회는 2026이지만 arXiv v1이 2025-10이라 2025 목록으로 분류했다(`codex_candidates.md` 참고).
- **PiT-PO** (arXiv:2602.10576): 2026년 논문이지만 탐색 중 RL로 LLM weight를 갱신해 ICL 범위 밖이다. abs 페이지는 직접 열지 않았고 검색 결과로만 확인했다.
- **DIGEST** (arXiv:2610.33880), **SymbolicLM** (arXiv:2609.33594): 파인튜닝·학습 기반. 이번 조사에서 abs 페이지를 직접 확인하지 않았다(`codex_candidates.md`에서 확인했다고 기록됨).
- **Prior-Guided SR (PG-SR)** (arXiv:2602.13021): abs 페이지 초록에 LLM 언급이 없어 제외했다.
- **Knowledge integration for physics-informed SR using pre-trained LLMs** (Scientific Reports 2026, s41598-026-35327-6): 저널판은 2026이지만 arXiv v1(2509.03036)이 2025이고, nature.com 페이지가 로그인으로 리다이렉트되어 확인하지 못했다.

## 원고(BAM-ICL)에 주는 시사점 요약

1. **계수 직접 작성은 2026년 문헌에도 없다.** 10편 모두 OLS, BFGS, PySR로 계수를 맞춘다. 원고의 "no refit" 설계는 새로운 점이지만, 리뷰어가 "refit을 하면 더 좋지 않나"를 물을 것이다. ablation이 필요하다.
2. **반대 입장의 논문이 있다.** LLM-PySR(#7)은 LLM이 식을 쓰거나 고르면 취약하다고 주장한다. 원고는 이에 대한 응답이 필요하다(물리 항 라이브러리로 제약해서 취약성을 줄였다는 식으로).
3. **라이브러리 대조군.** Library Reachability(#6)를 보면 "같은 φ_t 라이브러리에서 LLM 없는 탐색"을 대조군으로 넣어야 한다.
4. **재료 벤치마크의 한계.** FunctionEvolve(#3)의 MatSci collinearity 감사는 실제 재료계로 평가한 원고의 선택을 지지한다.
5. **같은 도메인의 비교 대상.** DASyR-LLM(#8, 촉매 반응속도), LangLaw(#9, perovskite·OER), LLM-PySR(#7, 배터리)은 원고의 촉매와 cathode 사례 바로 옆에 놓일 2026년 비교점이다.
