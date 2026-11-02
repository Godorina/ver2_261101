# Phase 2 수정 확인

이전 검토의 네 항목과 수정으로 생긴 오류만 확인했다. 검증은 지정된 Python 환경에서 표준입력으로 실행했고, NPZ 재계산 분기는 파일 입출력과 BAM 계산을 메모리 mock으로 대체했다. 실제 checkpoint나 output은 수정하지 않았으며 새 BAM forward는 수행하지 않았다.

| 항목 | 판정 | 확인 내용 |
|---|---|---|
| ERROR 1: 캐시 pin과 불완전 쌍 | **RESOLVED** | `code/bam.py:66-85`는 실제 checkpoint 파일 SHA256, torch 버전, CPU/float64/EMA 표시를 pin으로 비교한다. pin이 다르면 기존 DB를 비우고 요청 frame을 계산하며, E 또는 F가 없으면 해당 frame을 계산한다. in-memory mock으로 정상 hit에서는 재계산 0회, pin 불일치·E 누락·F 누락에서는 각각 1회인 것을 확인했고 pin 불일치 시 다른 이전 항목도 버려졌다. 실제 Co NPZ pin도 현재 파일 SHA와 torch 버전에 일치한다. 기존 지적의 옛 BAM 코드 해시와 달리 새 pin에는 구현 코드·BAM 라이브러리 해시는 없으므로 그런 코드만 바뀌는 경우는 자동 무효화되지 않는다. 이번에 명시된 SHA+torch 계약의 범위에서 해결 판정이다. |
| ERROR 2: 동종쌍 r1 설명 | **RESOLVED** | `code/prompt.py:112-113`과 실제 Co n5 prompt에 X-X는 X 원자별 가장 가까운 다른 X를 쓴다는 문장이 추가됐다. 이종쌍 양방향과 동종쌍 한 번의 계산 규칙(`code/features.py:70-77`)을 설명한다. |
| MISSING 3: EMA·Wigner 검증 | **PARTIAL** | `code/bam.py:31-44`에 shadow 수, 각 shape·finite 및 Wigner exact 또는 `exact.float().double()` 조건이 추가되어 요청된 세부 수정은 반영됐다. 다만 이전 지적에 포함된 **checkpoint parameter 이름 순서 검사**는 여전히 없다. 옛 구현은 `stored_names == list(parameters)`를 검사한다(`R/code/common/core/analysis/llmsr_bam_terminals.py:112-123`). 현재 지정 checkpoint의 52개 이름 순서가 맞는 것은 이전 검토에서 확인했으므로 현재 결과 오류를 뜻하지 않는다. 새 코드는 Wigner도 각 버퍼를 검사한 직후 교체하며, 옛 코드는 모든 버퍼를 검증한 후 교체한다(`R/.../llmsr_bam_terminals.py:92-108`). |
| SIMPLIFY 5: adsorption 인자·중복 산술 | **RESOLVED** | `code/run.py:14,27-31,101`에서 미사용 `group,n` 인자를 제거하고 각 pair의 DFT/BAM 목표량을 한 번씩 계산한다. Co n5에서 생성한 역할과 pair 블록을 포함하여 현재 코드로 메모리에서 재구성한 prompt가 저장된 `outputs/2_catalyst/Co/n5/prompt.txt`와 완전히 일치했다. |

## 수정으로 새로 생긴 오류

확인한 변경과 위 제한된 동적 검사에서는 새 오류를 발견하지 못했다. 예전 prompt의 별도 스냅샷이 없어 재생성 전후에 r1 설명 두 줄만 바뀌었다는 바이트 단위 주장은 독립 확인하지 못했다. 현재 prompt는 현 코드와 일치하고 Co n5 역할 및 pair 표를 재현한다.
