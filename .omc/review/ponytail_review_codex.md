features.py:L16-17: native: ASE `neighbor_list`가 이미 `d < RC`를 적용하므로 재필터 두 줄. 반환 배열을 그대로 사용한다.
bam.py:L21-23: yagni: 호출하지 않는 `load(path=None)`의 경로 인자. `load()`에서 `BAM_CKPT`만 읽는다.
run.py:L112: delete: CLI의 `main()` 반환값을 사용하는 호출자가 없다. 반환문을 제거한다.
net: -3 lines possible.
