*This project has been created as part of the 42 curriculum by donkim.*

# get_next_line

## Description

`get_next_line(fd)`는 파일 디스크립터에서 다음 한 줄을 `\n`을 기준으로 반환합니다. EOF이거나 에러가 나면 `NULL`을 반환합니다. 보너스 파트는 static 변수 하나만 사용해서 여러 fd를 번갈아 읽을 수 있습니다.

## Instructions

```sh
cc -Wall -Wextra -Werror -D BUFFER_SIZE=42 get_next_line.c get_next_line_utils.c main.c
cc -Wall -Wextra -Werror -D BUFFER_SIZE=42 get_next_line_bonus.c get_next_line_utils_bonus.c main.c
```

## Algorithm

fd마다 static 버퍼를 두어 반환되지 않은 데이터를 보관합니다. 매 호출마다 버퍼가 비어 있을 때만 읽고, 첫 번째 `\n`까지의 부분을 반환하고, 나머지를 버퍼 앞으로 옮깁니다. EOF가 되면 멈춥니다.

- **static 버퍼:** 한 번의 `read` 후 남은 데이터를 호출 사이에 유지하기 위해 쓰입니다.
- **chunk 단위 이어 붙이기:** 어떤 `BUFFER_SIZE`와 줄 길이에서도 동작합니다. 청크마다 재할당이 한 번 생기는 비용은 코드와 에러 처리가 단순해지는 대가로 감수했습니다.
- **보너스:** `static char *buf[OPEN_MAX]`에 fd별로 malloc한 버퍼를 두고 EOF에서 free합니다. static 2차원 배열은 `BUFFER_SIZE=10000000`일 때 약 10GB가 되어 링크에 실패합니다.

## Resources

- `man 2 read`, `man 3 malloc`
- AI 사용: Claude를 코드 리뷰와 단순화, 보너스 적용, 테스트 케이스 작성, 이 README 초안 작성에 사용했습니다. 모든 코드는 작성자가 검토하고 이해했습니다.