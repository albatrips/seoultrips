# seoultrips (가명/가제)

개발을 원하는 폴더를 만들고 아래 실행하셈

```
git clone https://github.com/albatrips/seoultrips.git

cd seoultrips

```

## 규칙

1. 개발은 '절대' main branch에서 하지말 것
   - 개별 branch 파서 작업합시다
   - 명령어:
     - git branch -> 현재 로컬 브랜치 확인
     - git checkout -b 브랜치 명 -> 브랜치 새로 파고 이동
     - git checkout 브랜치 명 -> 브랜치 이동
     - main에서 해서 커밋하면 안되는데, 일단 수정은 한 경우 -> git stash로 수정사항 다 들고 git checkout이나 -b로 브랜치 새로 판 뒤, git stash apply로 코드 옮겨담자.
     - 나머진.. 검색해보기! 브랜치만 섞지 말자
2. 커밋은 자유롭게 하되, 신중하자 -> 로그가 너무 많이 쌓여도 보기 싫을 수 있음

   - 커밋 컨벤션까지 만들진 말자...

3. 브랜치 합칠 땐, 반드시 Pull Request 고고

4. 문제가 있으면 Issue 오픈

홧팅~~
