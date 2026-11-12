# heven-hackathon-2026

HEVEN 2026 Docker 배포본 기반 참가자 실행 환경·스켈레톤·사용 문서.

## 빠른 시작 (MIT 종목)

1. Docker를 설치하고 켭니다(Windows·macOS: Docker Desktop, Ubuntu: Docker Engine). 자세한 방법은 [참가자 안내서](docs/participant-guide.md) 1절.
2. 이 저장소를 내려받고 그 폴더에서 실행합니다. 처음 한 번은 시뮬레이터 이미지(약 3.5 GB, `ghcr.io/skku-heven/heven-hackathon-2026:2026`)를 내려받습니다.

```bash
./run.sh            # macOS·Ubuntu  (Windows PowerShell: .\run.ps1)
```

3. 브라우저에 시뮬레이터 화면 **http://localhost:8080** 이 열립니다. 작업 폴더 `~/heven_hackathon_2026`에 기본 코드가 들어갑니다.

```
~/heven_hackathon_2026/
├── mit_ws/      MIT 코드 (컨테이너 /mit_ws), 기본 코드 hk_mit
├── morai_ws/    MORAI 코드 (컨테이너 /morai_ws, 빌드 확인용), 기본 코드 hk_morai
└── data/        결과·이번 시도 경로 파일 (컨테이너 /data)
```

| 명령 | 하는 일 |
|---|---|
| `./run.sh shell` | 컨테이너 셸(ROS 2 Humble). `cd /mit_ws && colcon build && source install/setup.bash && ros2 launch hk_mit bringup.launch.py` |
| `./run.sh desktop` | 브라우저 데스크톱 **http://localhost:6080** (RViz·rqt·터미널, 켤 때만 돔) |
| `./run.sh update` | 새로 올라온 이미지 받기(작업 폴더는 그대로) |
| `./run.sh stop` | 끄기 |

Windows에서 스크립트 실행이 막히면 `powershell -ExecutionPolicy Bypass -File .\run.ps1`로 실행합니다.

MORAI는 운영진 PC에서 돕니다. 자기 차례에 `morai_ws/src`를 USB로 가져오세요. 코스 파일은 `hk_morai/course/`에 들어 있고, 자세한 방법은 [참가자 안내서](docs/participant-guide.md) 4절에 있습니다.

## 배포 경계

개발 저장소 [heven-hackathon-2026-dev](https://github.com/skku-heven/heven-hackathon-2026-dev)가 검증한 Docker 이미지(GitHub 패키지)를 사용한다. `run.sh`·`run.ps1`·안내서는 개발 저장소의 `deployment/`, `docs/participant-guide.md`에서 복사한다. 기본 코드(`hk_mit`, `hk_morai`, MORAI 코스 파일 포함)는 이미지 안에 있고 `run.sh`가 작업 폴더로 복사한다. StrictDoc은 OFF이며 요구사항 정본을 중복 관리하지 않는다.

## 협업 설정

저장소 전용 Notion·Discord 알림/멘션·Codex 자동 리뷰는 OFF다. Project 상태 전환은 사용한다.

- 이 repository의 Notion hub: 사용 안 함 (NOTION_MODE=disabled)
- [공통 Notion 가이드](https://app.notion.com/p/39c3bf068300807c9e5bcf6b469f94ee)
