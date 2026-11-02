# Phase 1 수정 확인

지정 Python `-I`에서 검증 코드를 표준입력으로 직접 실행했다. `make_data.py`와 기존 검증 코드는 실행하지 않았다. 배열은 dtype·shape·원시 바이트를 비교했다.

- **H2 frame_id: RESOLVED.** `data/2_catalyst/H2.traj`와 원천 `inputs_h2/H2.extxyz` 모두 `H2:dft-relaxed`다. 원자번호, 좌표, cell, pbc, energy, forces도 비트 단위로 일치한다.
- **전체 SHA256: RESOLVED.** `data/SOURCES.md`의 결과와 원천 SHA256 총 143개가 모두 64자리이며 해당 파일에서 다시 계산한 전체 SHA256과 일치한다.
- **재빌드 회귀: 확인 범위에서 불일치 0건.** 원천별 비교 결과는 이전 검증과 같다. 촉매 5그룹 예제 100·query 149, MOF 33그룹 예제 693·query 134, CF4 3그룹 예제 27·query 7의 원자번호·좌표·cell·pbc가 원천과 비트 일치한다. 예제의 energy·forces와 기체 3개의 라벨도 원천과 비트 일치한다. query는 원천과 결과 모두 라벨이 없어 geometry와 ID를 비교했다.
- 세 응용의 모든 `splits.json`은 원천 `split.json`의 subsets와 동일하며 모든 예제의 `(group,index)` 대응과 `frame_id`, `config`, 원천에 있는 `pair`가 일치한다.
- sodium hull 733개는 원천의 geometry·energy·forces와 비트 일치하며, 21개 예제의 순서·ID·role·end members와 각 구조의 geometry·라벨도 원천과 일치한다. end members는 `hull:0139`, `hull:0080`이다. symlink는 0개다.

이전 빌드의 전체 파일 스냅샷과 직접 비교한 것은 아니다. 원천을 공통 기준으로 이전 검토와 이번 검토를 각각 수행했으므로 위에 열거한 데이터의 변경 여부를 확인할 수 있다. H2의 frame_id와 SOURCES 해시 표기는 요청된 수정이다.
