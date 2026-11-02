# 실행 프롬프트 (새 Claude Code 세션에 붙여넣기)

`/home/hgpark/whlee/hgpark/ver2_261101`에서 Claude Code를 새로 연다. 그래야 `.claude/skills/ponytail`이 잡힌다. 아래 블록을 붙여넣고, Phase마다 마지막 줄만 바꾼다.

---

```
/ponytail full

BAM-ICL의 LLM 호출 직전까지(구조 → BAM E_NN·F_NN → 잔차·기술자 → prompt.txt)를 처음부터 새로 작성한다.

계획서(먼저 전부 읽을 것): /home/hgpark/whlee/hgpark/ver2_261101/.omc/plans/ver2-rebuild-pre-llm.md
목표 구조, Phase별 완료 기준, "하지 않는 것" 목록을 따른다. 벗어나야 하면 이유를 한 줄로 적고 먼저 묻는다.

규칙
1. 옛 코드(bam-icl-release, paper_bam-icl, mlp-icl-llmsr-force-v2, mlp-icl-ft-check-v1, past/)는 사양을 읽는 데만 쓴다. 복사, import, 수정 모두 금지. 쓰기는 ver2_261101/ 아래에서만 한다.
2. ponytail 사다리를 지킨다: 필요한가 → 이미 있나 → stdlib → numpy/ase/bam_torch → 한 줄 → 최소 코드. 클래스, 설정 모듈, 캐시 시스템, 패키지 계층은 만들지 않는다. 의도한 지름길에는 `# ponytail: <한계>, <업그레이드 조건>`을 단다.
3. 단, 이해는 줄이지 않는다. Phase 0에서 옛 코드를 끝까지 읽고 code/SPEC.md에 식, 상수, 프롬프트 정보 항목, 검증 기준값을 원천 `파일:행`과 함께 적는다. 특히 BAM E_NN(원소 기준합 R_old 제외)을 얻는 방법을 정확히 옮긴다.
4. LLM, HTTP 호출 코드는 쓰지 않는다. 절대경로를 쓰지 않는다. ckpt는 환경변수 BAM_CKPT로 받는다.
   BAM_CKPT=/home/hgpark/whlee/hgpark/past/mlp-icl-llmsr/data/checkpoints/bam-mp-core/model.pkl (sha e837d512…)
5. BAM 계산은 Phase 3에서만, CPU로, run_in_background로 실행한다. 새 LLM, FT, GPU 작업은 하지 않는다.
6. 각 파일에 assert 기반 __main__ 자기검사를 하나 둔다. 그 이상의 테스트 프레임워크는 쓰지 않는다. skip이나 TODO는 완료로 치지 않는다.
7. Phase가 끝날 때마다 멈추고 보고한다: 완료 기준별 PASS/FAIL과 근거 명령, 만든 파일과 줄 수. 다음 Phase는 내 승인 후에 시작한다.
8. Phase 4의 승인 리뷰는 직접 하지 않는다. /ponytail-review, /ponytail-debt, oh-my-claudecode:code-reviewer 에이전트, herdr codex(`herdr agent prompt litcodex "..."`)에 맡긴다.

이번 실행 범위: Phase 0만
```

---

## 범위 문구 (마지막 줄 교체용)
- `이번 실행 범위: Phase 0만` — 옛 코드 읽기 → code/SPEC.md (읽기 전용)
- `이번 실행 범위: Phase 1만` — data/ extxyz 4세트와 SOURCES.md
- `이번 실행 범위: Phase 2만` — code/ 4개 파일과 자기검사
- `이번 실행 범위: Phase 3만` — 계산(CPU, 백그라운드)과 SPEC 기준값 대조
- `이번 실행 범위: Phase 4만` — ponytail-review, ponytail-debt, 정확성 리뷰 2개, README
