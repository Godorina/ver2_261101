# 계층 분리 검토

## 설계와 의존 방향

- [ERROR] `code/common/features.py:10`의 `BINS_ADS`와 `# adsorption apps`는 흡착 응용별 선택을 공통 계층에 둔다. `systems/adsorption.py:89`가 이를 선택하고 있지만, 공통 계층이 시스템을 모른다는 엄격한 합의에는 맞지 않는다. 흡착용 bin 정의를 adsorption 계층으로 옮겨 `force_table`에 전달하면 수치와 프롬프트를 유지할 수 있다. `common/features.py:99`의 자기검사 입력도 이에 맞게 독립적인 숫자 배열로 두어야 한다.
- 공통 모듈은 systems를 import하지 않는다. systems는 common의 features와 prompt만 import하며 BAM을 import하거나 호출하지 않는다 (`systems/adsorption.py:6`, `systems/sodium.py:6`). BAM 호출과 시스템 선택은 `run_new.py:8-22`에 있다. 공통 프롬프트의 dispersion 항목은 특정 시스템 이름이 없는 일반 물리 항목이며 활성화 선택은 adsorption에 있다 (`common/prompt.py:21,37-39`, `systems/adsorption.py:31,89`).
- [MISSING] 세 함수만 공개한다는 인터페이스를 문자 그대로 적용하면 `systems/adsorption.py:11,61`의 `ads_goal`, `pairs`와 `systems/sodium.py:36,50`의 `lower_hull`, `hull_at`도 공개 이름이다. 상수 및 import 이름도 공개 네임스페이스에 있다. 현재 run은 세 함수 중 필요한 것만 사용하므로 실행상 역방향 의존은 없다. 공개 API 제한이 요구사항이면 내부 이름으로 명시하거나 공개 목록을 정의해야 한다.

## 평면 구조와 비교

- 구조 선택 순서, 기체를 마지막에 추가하는 방식, 에너지 복원, 기술자·프롬프트 조립, 출력 파일 및 예제 순서는 코드상 기존 경로와 대응한다 (`code/run.py:83-110`, `code/run_new.py:15-31`, `code/systems/adsorption.py:53-58`, `code/systems/sodium.py:26-33`). 공통 BAM 코드는 로드 인터페이스와 자기검사 경로를 제외하면 평면 코드와 같다. 사용자 제공의 촉매·CF4·소듐 25개 바이트 비교 결과는 독립 재실행하지 않았다. MOF 프롬프트 바이트 동등성은 계산 중이므로 미확인이다.
- [MISSING] 실행 인터페이스는 완전히 같지 않다. `code/run.py:111-112`는 소듐 BAM 평균 |dE_mix|를 표준 출력에 표시하고 `(text, check)`를 반환하지만 `code/run_new.py:32`는 해당 수치를 출력하지 않고 `main`이 `None`을 반환한다. 프롬프트 파일 내용과는 별개의 차이이므로 기존 호출자나 로그에서 이 값이 필요한지 확인해야 한다.
- 소듐 `examples()`는 기존과 달리 읽어온 각 구조의 `info`에 `role`과 `end_members`를 추가한다 (`systems/sodium.py:30-33`; 기존 `run.py:85-87`). 프롬프트 역할 및 end member 전달을 위한 변경이며 구조 좌표·에너지의 변경은 아니다. 반환된 Atoms의 메타데이터까지 동일한 인터페이스는 아니다.

## quantity

- 흡착 `quantity(app, ids, E)`는 순서대로 완성된 pair와 마지막 gas ID를 사용해 `E[loaded] - E[bare] - k*E[gas]`를 계산한다 (`systems/adsorption.py:61-74`). 소듐 `quantity(frames, E)`는 구조 메타데이터와 end member 에너지로 E_mix 및 해당 에너지 집합의 hull을 계산한다 (`systems/sodium.py:58-65`). 두 함수 모두 입력 에너지 dict를 변경하거나 BAM·파일을 호출하지 않으므로 동일 ID와 단위의 E_pred에도 적용할 수 있다. 소듐 입력에는 `examples()`가 부여하는 `frames[0].info['end_members']` 및 각 구조의 `phase`, `x`, `nMn`이 필요하다. 흡착에는 gas가 `ids[-1]`이어야 한다.
- [MISSING] 두 `quantity`의 인자와 반환 형식은 서로 다르다: 흡착은 `(app, ids, E) -> list`, 소듐은 `(frames, E) -> (dict, dict, vertices)`이다 (`systems/adsorption.py:71-74`, `systems/sodium.py:58-65`). 합의에 공통 시그니처가 명시된 것은 아니므로 현 구현 오류는 아니지만, 향후 한 경로에서 시스템별 quantity를 호출하려면 분기 또는 통일된 인터페이스가 필요하다.

## ponytail

Lean already. Ship.

## 검증

`PYTHONDONTWRITEBYTECODE=1`과 지정된 `env/bin/python`으로 `systems.adsorption`, `systems.sodium`, `common.features`, `common.prompt` 자체검사를 실행해 모두 `ok`를 확인했다. BAM 계산, 프롬프트 재생성, MOF 동등성 실행 검증은 수행하지 않았다.
