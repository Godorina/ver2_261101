# LLM 기반 symbolic regression 문헌 후보

조사 기준일: 2026-11-01. 연도는 arXiv 최초 제출 연도(v1)를 기준으로 한다. 각 항목의 제목·저자·제출 연도·초록을 연결된 arXiv abs 페이지에서 확인했다. [검증]은 서지와 논문 실재 확인을 뜻하며 성능 주장이나 연구 결과의 독립 재현을 뜻하지 않는다. 초록은 이후 개정판의 내용일 수 있다. ICL을 좁게 정의한 논문뿐 아니라 데이터·평가 피드백을 문맥에 넣는 에이전트, 벤치마크 및 관련 학습·탐색 보조 연구도 포함하며, 해당 차이를 명시한다.

## 2025년 후보 10편

1. **LLM-Feynman: Leveraging Large Language Models for Universal Scientific Formula and Theory Discovery** — Zhilong Song, Qionghua Zhou, Chunjin Ren, Chongyi Ling, Minggang Ju, Jinlan Wang (2025). [arXiv:2503.06512](https://arxiv.org/abs/2503.06512). **[검증]** LLM 기반 특성 생성과 식 탐색 및 자기평가를 결합해 재료과학을 포함한 데이터와 도메인 지식으로 해석 가능한 식을 찾는다.
2. **LLM-SRBench: A New Benchmark for Scientific Equation Discovery with Large Language Models** — Parshin Shojaee, Ngoc-Hieu Nguyen, Kazem Meidani, Amir Barati Farimani, Khoa D Doan, Chandan K Reddy (2025). [arXiv:2504.10415](https://arxiv.org/abs/2504.10415). **[검증]** 물리·화학·생물·재료의 239개 문제를 통해 암기와 데이터 기반 식 발견을 구별하려는 벤치마크다.
3. **Symbolic Regression with Multimodal Large Language Models and Kolmogorov Arnold Networks** — Thomas R. Harvey, Fabian Ruehle, Kit Fraser-Taliente, James Halverson (2025). [arXiv:2505.07956](https://arxiv.org/abs/2505.07956). **[검증]** 함수 그래프를 본 멀티모달 LLM이 식을 제안하고 수치 최적화·진화 탐색 및 KAN을 결합한다.
4. **LLM-Meta-SR: In-Context Learning for Evolving Selection Operators in Symbolic Regression** — Hengzhe Zhang, Qi Chen, Bing Xue, Wolfgang Banzhaf, Mengjie Zhang (2025). [arXiv:2505.18602](https://arxiv.org/abs/2505.18602). **[검증]** ICL로 식 자체가 아닌 진화형 SR의 선택 연산자를 설계하는 인접 메타 학습 연구다.
5. **DrSR: LLM based Scientific Equation Discovery with Dual Reasoning from Data and Experience** — Runxiang Wang, Boxiao Wang, Kai Li, Yifan Zhang, Jian Cheng (2025). [arXiv:2506.04282](https://arxiv.org/abs/2506.04282). **[검증]** 데이터의 구조적 특징과 이전 식의 성능에 대한 반성을 피드백으로 결합하며 물리·화학·재료 등에서 평가한다.
6. **Can Large Language Models Adequately Perform Symbolic Reasoning Over Time Series?** — Zewen Liu, Juntong Ni, Xianfeng Tang, Max S.Y. Lau, Qi He, Wenpeng Yin, Wei Jin (2025; 저자는 확인 당시 최신판 기준). [arXiv:2508.03963](https://arxiv.org/abs/2508.03963). **[검증]** 다변량 SR 등을 포함하는 시계열 SymbolBench와 LLM·유전 프로그래밍 결합 추론을 제안한다.
7. **Finetuning Large Language Model as an Effective Symbolic Regressor** — Yingfan Hua, Ruikun Li, Jun Yao, Guohang Zhuang, Shixiang Tang, Bin Liu, Wanli Ouyang, Yan Lu (2025). [arXiv:2508.09897](https://arxiv.org/abs/2508.09897). **[검증]** SymbArena 데이터와 전용 파인튜닝으로 식 복원 능력을 높이는 연구로, 순수 추론 시 ICL과 구분된다.
8. **Knowledge Integration for Physics-informed Symbolic Regression Using Pre-trained Large Language Models** — Bilge Taskin, Wenxiong Xie, Teddy Lazebnik (2025). [arXiv:2509.03036](https://arxiv.org/abs/2509.03036). **[검증]** LLM의 식 평가를 SR 손실에 반영하여 낙하·진동·전자기파의 물리 지식을 통합한다.
9. **Iterated Agent for Symbolic Regression** — Zhuo-Yang Song, Zeyu Cai, Shutao Zhang, Jiashen Wei, Jichen Pan, Shi Qiu, Qing-Hong Cao, Tie-Jiun Hou, Xiaohui Liu, Ming-xing Luo, Hua Xing Zhu (2025). [arXiv:2510.08317](https://arxiv.org/abs/2510.08317). **[검증]** 자연어 근거에 따라 LLM이 진화 탐색의 후보 식을 생성하며 고에너지 물리의 파톤 분포에도 적용한다.
10. **SR-Scientist: Scientific Equation Discovery With Agentic AI** — Shijie Xia, Yuhan Sun, Pengfei Liu (2025; ICLR 2026). [arXiv:2510.11661](https://arxiv.org/abs/2510.11661). **[검증]** LLM 에이전트가 코드를 작성해 데이터를 분석하고 식을 평가·반복 개선하며, 강화학습도 탐구한다.

## 2026년 후보 10편

1. **Think like a Scientist: Physics-guided LLM Agent for Equation Discovery** — Jianke Yang, Ohm Venkatachalam, Mohammad Kianezhad, Sharvaree Vadgama, Rose Yu (2026). [arXiv:2602.12259](https://arxiv.org/abs/2602.12259). **[검증]** KeplerAgent가 대칭성 등 물리적 구조를 도구로 추출해 PySR·PySINDy 탐색을 제약한다.
2. **Programmatic Context Augmentation for LLM-based Symbolic Regression** — Hao Liu, Xiao-Wen Yang, Atharva Sehgal, Yixin Wang, Lan-Zhe Guo, Yu-Feng Li, Yisong Yue (2026). [arXiv:2605.03101](https://arxiv.org/abs/2605.03101). **[검증]** 코드로 데이터와 상호작용하여 스칼라 오차 이상의 분석 정보를 LLM 탐색 문맥에 추가한다.
3. **Discovering Ordinary Differential Equations with LLM-Based Qualitative and Quantitative Evaluation** — Sum Kyun Song, Bong Gyun Shin, Jae Yong Lee (2026). [arXiv:2605.07323](https://arxiv.org/abs/2605.07323). **[검증]** 다중 에이전트가 정성·정량 평가와 계수 최적화를 반복해 관측 데이터의 상미분방정식을 찾는다.
4. **Influence-Guided Symbolic Regression: Scientific Discovery via LLM-Driven Equation Search with Granular Feedback** — Evgeny S. Saveliev, Samuel Holt, Nabeel Seedat, David L. Bentley, Jim Weatherall, Mihaela van der Schaar (2026). [arXiv:2605.29184](https://arxiv.org/abs/2605.29184). **[검증]** LLM이 만든 기저 함수의 개별 기여도를 이용해 MCTS로 희소한 식을 탐색한다.
5. **Deliberate Evolution: Agentic Reasoning for Sample-Efficient Symbolic Regression with LLMs** — Xinyu Pang, Zhanke Zhou, Xuan Li, Fangrui Lv, Shanshan Wei, Sen Cui, Bo Han, Changshui Zhang (2026). [arXiv:2606.04360](https://arxiv.org/abs/2606.04360). **[검증]** 적응적 탐색 연산자, 구조 진단과 반성 메모리로 LLM의 식 제안을 유도한다.
6. **Language models guide symbolic equation discovery by controlling search** — Zikai Xie, Wenmei Li, Man Luo, Jun Jiang, Linjiang Chen (2026). [arXiv:2607.04156](https://arxiv.org/abs/2607.04156). **[검증]** LLM이 PySR의 변수·연산자·탐색 범위를 설정하고 배터리 수명 데이터에 간결한 관계식을 적용한다.
7. **A-SR: Self-Evolving Agentic LLMs for Symbolic Regression via Hierarchical Coordination** — Wenxiao Zhao, Dong Liu, Kaiyi Xu, Feng Liu, Zhen Zhao, Fei Ben, Shu Wang, Wenhao Li, Ying Nian Wu, Fenghua Ling, Haobo Li, Lei Bai (2026). [arXiv:2608.04872](https://arxiv.org/abs/2608.04872). **[검증]** 역할별 에이전트와 성능 피드백·메모리를 조정해 과학 분야의 식 탐색을 개선한다.
8. **SymbolicLM: Training Language Models as Symbolic Regressors** — Jun Yao, Yingfan Hua, Ruikun Li, Shixiang Tang, Bin Liu, Wanli Ouyang, Yan Lu (2026). [arXiv:2609.33594](https://arxiv.org/abs/2609.33594). **[검증]** 수치·기호·물리 설명을 이용해 LLM을 학습시키고 추론 시 정량 피드백으로 식을 개선한다. 전용 학습을 포함한다.
9. **L2G-SR: Learning to Guide LLM-based Symbolic Regression** — Letian Huang, Xiangyu Wang, Haowei Lin, Di He (2026). [arXiv:2610.20685](https://arxiv.org/abs/2610.20685). **[검증]** 학습된 구조 검증기가 식의 구조적 유사도를 평가하여 LLM의 후보 선택과 수정을 유도한다.
10. **DIGEST: Discovery-Guided LLM Tuning for Symbolic Regression** — Kaifeng Jin, Ruizhong Qiu, Zihao Li, Xiao Lin, Dongqi Fu, Yinglong Xia, Hong Li, Hanghang Tong (2026). [arXiv:2610.33880](https://arxiv.org/abs/2610.33880). **[검증]** LLM의 디코더를 유전 프로그래밍의 기호 생성 정책으로 활용하고 발견한 식으로 온라인 갱신한다. 파라미터 갱신이 있어 순수 ICL과 구분된다.

## 배경: 요청에 언급된 2024년 선행연구

아래 논문들은 핵심 계보이지만 최초 제출이 2024년이므로 위 연도별 10편에 포함하지 않았다.

- **LLM-SR: Scientific Equation Discovery via Programming with Large Language Models** — Parshin Shojaee, Kazem Meidani, Shashank Gupta, Amir Barati Farimani, Chandan K Reddy (2024 최초 공개, ICLR 2025). [arXiv:2404.18400](https://arxiv.org/abs/2404.18400). **[검증]** 프로그램 형태의 식을 LLM으로 생성하고 데이터 평가와 진화 탐색을 반복한다.
- **In-Context Symbolic Regression: Leveraging Large Language Models for Function Discovery** — Matteo Merler, Katsiaryna Haitsiukevich, Nicola Dainese, Pekka Marttinen (2024). [arXiv:2404.19094](https://arxiv.org/abs/2404.19094). **[검증]** 기존 후보와 점수를 문맥으로 제공해 함수 형태를 반복 개선하고 외부 최적화기로 계수를 추정한다.
- **Symbolic Regression with a Learned Concept Library** — Arya Grayeli, Atharva Sehgal, Omar Costilla-Reyes, Miles Cranmer, Swarat Chaudhuri (2024). [arXiv:2409.09359](https://arxiv.org/abs/2409.09359). **[검증]** LaSR은 유망한 식에서 LLM으로 재사용 가능한 개념을 추출하여 식 탐색에 되돌린다.
