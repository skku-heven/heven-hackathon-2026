# HEVEN 2026 해커톤 참가자 안내서

## 1. 설치와 실행 (MIT 종목)

시뮬레이터는 Docker 이미지로 배포합니다. 실행 스크립트(`run.sh`·`run.ps1`)와 이 안내서는 참가자용 저장소(https://github.com/skku-heven/heven-hackathon-2026)에 있고, 이미지는 대회 시작(17:00)에 GitHub 패키지(`ghcr.io/skku-heven/heven-hackathon-2026:2026`)로 공개됩니다.

1. Docker를 미리 설치해 옵니다.
   - Windows: [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)(WSL2 사용). BIOS에서 가상화가 켜져 있어야 합니다.
   - macOS: [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/)(Apple 칩·Intel 모두 됨).
   - Ubuntu: [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)을 설치하고 `sudo usermod -aG docker $USER` 뒤 다시 로그인합니다.
2. Docker Desktop을 켭니다(Ubuntu는 `sudo systemctl start docker`).
3. 참가자용 저장소를 받은 폴더에서 실행 스크립트를 실행합니다. 처음 한 번은 이미지(약 3 GB)를 내려받습니다. 대회장 네트워크가 느리면 운영진의 예비 USB로 받을 수 있습니다.
   - macOS·Ubuntu: `./run.sh`
   - Windows PowerShell: `.\run.ps1`
4. 브라우저에서 **http://localhost:8080** 을 엽니다(스크립트가 자동으로 엽니다). 이 화면에서 시도를 시작하고 결과를 봅니다.
5. 코드를 빌드·실행할 터미널은 `./run.sh shell`(Windows: `.\run.ps1 shell`)로 엽니다. 컨테이너 안의 Ubuntu 22.04 + ROS 2 Humble 셸입니다.
6. RViz·rqt 같은 GUI를 쓰고 싶으면 `./run.sh desktop`(Windows: `.\run.ps1 desktop`)으로 브라우저 데스크톱(**http://localhost:6080**)을 엽니다(9절). 켤 때만 돌아서 평소에는 CPU를 쓰지 않습니다.
7. 운영진이 이미지를 고쳐 다시 올리면 `./run.sh update`로 받습니다. 작업 폴더는 그대로 남습니다.

셸은 bash이고 ROS 2 환경이 미리 불러와져 있습니다. 안내서의 명령은 모두 bash 기준입니다(zsh 등 다른 셸에서는 `setup.bash` 대신 그 셸용 파일을 불러와야 합니다). 작업 폴더는 노트북의 `~/heven2026/ws`(Windows: `%USERPROFILE%\heven2026\ws`)이고, 컨테이너 안에서는 `/ws`입니다. 노트북의 편집기(VS Code 등)로 이 폴더의 코드를 고치면 됩니다. 컨테이너를 지워도 폴더는 남습니다. 결과와 이번 시도의 경로 파일은 `~/heven2026/data`(컨테이너의 `/data`)에 저장됩니다.

```bash
# 컨테이너 셸에서
cd /ws
colcon build                         # C++(rclcpp)와 Python(rclpy) 패키지 모두 빌드됩니다
source install/setup.bash
ros2 launch hk_drive bringup.launch.py      # 기본 코드(경로 추종)
```

처음 실행하면 기본 코드(`hk_drive`, Python)가 작업 폴더에 복사돼 있습니다. 같은 코드가 MORAI에서도 돕니다. `ros2 launch hk_drive bringup.launch.py` 하나로 노드 세 개가 뜨고, 토픽으로 이어집니다.

```
센서 ─▶ hk_localization ─/hk/local/odom─▶ hk_planner ─/hk/plan/local_path─▶ hk_control ─▶ /hk/control/command
              (localization.py)              (planner.py)                      (control.py)
```

| 파일 | 하는 일 | 고칠 곳 |
|---|---|---|
| `hk_drive/localization.py` | 위치 추정. GNSS·IMU·바퀴 속도로 위치·방향·속력을 구해 `/hk/local/odom`(nav_msgs/Odometry, 50 Hz)에 냅니다. 위치는 GNSS 값을 그대로, 방향은 IMU(MIT는 각속도 적분, MORAI는 자세), 속력은 바퀴 속도 센서(MORAI는 GNSS 이동 거리)입니다. | 예 |
| `hk_drive/planner.py` | 경로 계획. 전역 경로(0.5 m 간격)에서 차 앞 30 m를 잘라 `/hk/plan/local_path`(nav_msgs/Path, 20 Hz)에 냅니다. 경로 끝을 지나면 빈 경로입니다. | 예 |
| `hk_drive/control.py` | 제어. `drive()`가 0.02초마다 불리고, odom(`self.x`, `self.y`, `self.yaw`, `self.speed`)과 경로(`self.path`; `self.nearest(x, y)`로 가장 가까운 점과 경로 방향)를 보고 `accel, brake, steer`를 돌려줍니다. 조향은 Stanley, 속력은 PI, 목표 5 m/s입니다. | 예 |
| `hk_drive/course.py` | 코스·경로 파일 읽기 | 아니요 |
| `hk_drive/sim_events.py` | 시작·복귀·끝 이벤트(`/sim/events`) 받기 | 아니요 |
| `hk_drive/utm.py` | 위경도 ↔ 지도 좌표 | 아니요 |

굽은 길 감속, 지연·노면 보정, GNSS 노이즈 필터, 음영 구간을 이어 가는 추측 항법, 장애물을 비켜 가는 경로는 일부러 넣지 않았습니다. 속력을 올리거나 옵션을 켜면서 직접 고쳐 보세요. 노드 하나를 통째로 자기 코드로 바꿔도 됩니다(같은 토픽만 쓰면 됨). C++로 작성해도 됩니다(`colcon build`가 C++·Python 둘 다 빌드).

## 2. 시도

- 화면 오른쪽에서 옵션을 켜고 끄면 구성 만점과 제한시간이 바로 바뀝니다. seed를 정하고 **연습 시작**을 누릅니다. 명령줄로도 같습니다: `attempt start --seed 3 --options obstacle1,gnss_noise`
- 시도가 시작되면 `/data/current/route.csv`(이번 구성의 전역 경로, x·y m)와 `/data/current/course.json`(출발 자세, 체크포인트, 체크포인트별 복귀 자세, 미션 구역, 제한시간)이 쓰이고, 그다음 `/sim/events`에 START가 나옵니다. START를 받으면 이 파일을 다시 읽으세요. 경로 CSV의 점은 경로를 따라 0.5 m 간격입니다(MORAI `morai_global_path.csv`도 같음).
- **공터** 모드는 지름 600 m 원형 평지입니다. 시도마다 노면 하나(일반·저마찰·오르막·내리막·GNSS 음영)를 골라 공터 전체에 적용합니다. 점수·완주·제한시간 없이 자유롭게 재는 곳이고, 외곽 벽에 닿으면 감점 없이 출발 위치로 돌아갑니다. 정답 정보를 받을 수 있습니다.
- 연습은 두 방식입니다. **채점 모드**는 출발부터 달려 점수를 매기고, **연습 모드**는 고른 체크포인트(CP)의 복귀 자세에서 시작합니다(그 앞 미션은 끝난 것으로 보고 점수는 매기지 않음). 기본 코드는 START 이벤트의 `checkpoint` 값으로 시작 자세를 맞춥니다. 제한시간은 140초입니다.
- 연습에서는 일시정지·배속을 쓸 수 있습니다. 공식 시도는 1배속만 됩니다.
- **수동 모드(연습만)**: Tab으로 수동·자동을 바꿉니다. W/S 구동·제동, A/D 조향, P/R/N/1 기어, Space 급제동. 브라우저 창을 벗어나면 키를 뗀 것으로 처리합니다.

공식 시도 2회는 운영진이 팀·시도 번호·seed를 입력하고 시작합니다. 두 시도 사이에 코드와 파라미터는 바꿀 수 없고, 옵션 구성은 시도마다 고릅니다.

## 3. 토픽과 명령 (MIT·MORAI 공통)

| 토픽 | 메시지 | 비고 |
|---|---|---|
| `/hk/sensors/gps/fix` | `sensor_msgs/NavSatFix` | 20 Hz(MIT는 기본값), `gps_link`. GNSS 음영 구간에서는 나오지 않음 |
| `/hk/sensors/imu/data` | `sensor_msgs/Imu` | MIT 기본 100 Hz, 자세 없음(`orientation_covariance[0] = -1`), 가속도에 중력 포함. IMU 노이즈를 켜면 각속도에 백색 잡음 말고도 시도마다 다른 일정한 바이어스(σ 0.003 rad/s)와 천천히 변하는 드리프트(σ 0.001 rad/s, 약 1분)가 붙습니다. 적분만 하면 방향이 조금씩 틀어지고, GNSS 음영에서 특히 크게 벗어나니 바이어스를 추정해 빼세요(정지 상태 평균, GNSS 진행 방향 비교 등) |
| `/hk/sensors/wheel_speed` | `geometry_msgs/TwistStamped` | MIT만, 기본 50 Hz, `linear.x` = 후륜 바퀴 속도(부호 있음, 슬립 포함) |
| `/hk/sensors/scan` | `sensor_msgs/LaserScan` | MIT만, 기본 10 Hz, 720빔, 0.5~100 m, 미검출 `+Inf`, 최소 거리 안 `-Inf`. 빔 수·각도·거리는 고정값으로 쓰지 말고 메시지의 `angle_min`·`angle_increment`·`range_min`·`range_max`와 `len(ranges)`를 읽는다. 대회 값은 코스 JSON의 `sensors`에 있다 |
| `/hk/control/command` | `hk_morai_interfaces/CtrlCmd` | 참가자가 보냄 |
| `/sim/events` | `hk_interfaces/SimEvent` | START·END·RESPAWN·WARN. QoS reliable + transient local |
| `/dev/ground_truth` | `nav_msgs/Odometry` | 연습·공터만(공식 시도에는 없음) |

MIT 센서의 주기, LiDAR 빔 수·시야각·거리, 노이즈 σ는 지도 파라미터로 바뀔 수 있습니다. 표의 값은 기본값이고, 그 지도에서 쓰는 값은 `course.json`의 `sensors`에 있습니다.

센서 구독은 `SensorDataQoS`(best effort)로 해야 연결됩니다.

**명령(`CtrlCmd`)**: `long_cmd_type = 1`, `accel`·`brake` ∈ [0, 1], `steering` ∈ [-1, 1](±1 = 자전거 모델 앞바퀴 ±35.4°, 양수 왼쪽), `gear` P=1·R=2·N=3·D=4. 제동이 0보다 크면 구동은 0입니다. 기어는 속력 0.1 m/s 이하에서만 바뀝니다(그보다 빠르면 보류). 범위를 1e-6보다 크게 벗어나거나 NaN이면 그 명령 전체를 버리고 직전 명령을 유지합니다. 새 명령이 올 때까지 마지막 명령을 계속 적용합니다. MIT에서는 복귀하면 유지 중이던 명령이 지워지고 0.5초 뒤 새로 보낸 명령부터 따릅니다. MORAI 복귀는 아래 MORAI 규칙을 따릅니다.

**MORAI만의 규칙**: `ctrl_mode`는 무시합니다. 0.2초보다 오래된 타임스탬프의 명령은 버립니다. 운영진이 복귀를 진행하는 동안에는 브리지가 여러분의 명령 대신 제동을 보내고, 옮긴 자세를 확인하고 RESPAWN 이벤트를 보낸 직후 차단을 풀고(MIT의 0.5초 대기 없음), 그 뒤에 보낸 명령부터 전달합니다. 명령은 끊지 말고 계속(예: 50 Hz) 보내세요. MORAI는 센서 측정 시각을 주지 않아서 GPS·IMU 타임스탬프는 브리지가 받은 시각입니다. IMU 자세는 MORAI가 노이즈 없이 주는 값을 지도 격자 기준으로 돌려서 줍니다.

**시간**: MIT는 `/clock`(시뮬레이션 시간)이 있으므로 `use_sim_time:=true`, MORAI는 `/clock`이 없으므로 `use_sim_time:=false`로 실행합니다. 기본 코드의 launch 인자 `use_sim_time`으로 바꿉니다.

## 4. MORAI 종목에서 코드 실행

- 참가자용 저장소의 `participant/morai/`(운영진 PC에도 같은 파일이 있음)에 전역 경로(`morai_global_path.csv`, x·y m)와 출발점·체크포인트 14개·속도 구간(`morai_course.json`)이 있습니다.
- MORAI는 운영진 PC에서 돕니다. 자기 차례에 **소스와 설정 파일**을 USB로 가져오면 운영진이 팀 폴더에 넣고 셸을 열어 줍니다. 노트북에서 빌드한 결과물은 쓰지 않습니다(PC 구조가 다를 수 있음). 그 셸에서 `colcon build` 후 `use_sim_time:=false`로 실행합니다.
- 운영진 PC에서는 `sudo`나 시스템 `pip`를 쓸 수 없습니다. 팀 폴더 안 가상환경은 됩니다.
- 기본 코드(`hk_drive`)는 MORAI에서도 그대로 돕니다. MIT와 같은 노드 셋(localization → planner → control, Stanley + PI)이고, 코스 파일을 보고 종목을 알아서 맞춥니다(MORAI: 속도는 GNSS로 추정, 방향은 IMU 자세). MORAI용 실행 파일은 전역 경로를 **3 m/s(약 11 km/h)로 아주 천천히** 따라가 15분 제한 안에 한 바퀴(약 12분)를 돕니다. 빠르게 달리려면 직접 고쳐 보세요.
  ```bash
  ros2 launch hk_drive morai.launch.py morai_dir:=<자료 폴더>/participant/morai     # 속도를 바꾸려면 target_speed:=5.0
  ```
- 시작 전에 운영진이 차를 공식 출발점에 세워 둡니다. 시작을 누르면 `/sim/events`로 START가 오고, 측정은 차가 처음 움직인 순간부터입니다.
- GPS·IMU·명령 토픽은 MIT와 같습니다(`/hk/sensors/gps/fix`, `/hk/sensors/imu/data`, `/hk/control/command`). 속도 센서와 2D 스캔(`/hk/sensors/scan`)은 없습니다. `hk_morai_interfaces`가 MIT 이미지에 있으니 노트북에서 미리 빌드해 볼 수 있습니다.
- MORAI에는 LiDAR와 카메라가 있습니다.
  - `/hk/sensors/lidar/points`(`PointCloud2`): 16채널, 10 Hz, 360° 한 장, 필드 `x,y,z,intensity,ring`, frame `lidar_link`
  - `/hk/sensors/camera/{front,left,right,traffic_light}/compressed`(`CompressedImage`, JPEG): 일반 RGB 영상만 나옵니다(바운딩박스·깊이·분할 영상은 없음)
  - 센서 위치는 TF로 나오지 않습니다. 운영진이 공지하는 `sensor_mounts.yaml`을 보고, 필요하면 직접 TF를 쓰세요. frame_id는 `gps_link`, `imu_link`, `lidar_link`, `camera_<이름>_link`입니다.
  - `sensor_mounts.yaml`의 위치는 `base_link`가 아니라 후륜 차축 중심(`rear_axle_link`) 기준이고 단위는 m, 각도(roll·pitch·yaw)는 도입니다. `base_link` 기준으로 쓰려면 z에 파일의 `axle_height_m`(0.3685 m)을 더합니다. 예: GNSS z 1.2 → `base_link` 기준 1.5685 m.
  - 카메라 frame은 x 앞·y 왼쪽·z 위 축 규약을 쓰고, 차량에 대한 실제 방향은 그 카메라의 roll·pitch·yaw를 따릅니다(기본 왼쪽 카메라 yaw 70°).

## 5. 좌표와 센서 위치

- `map` 좌표: UTM 52N 좌표에서 종목별 원점 `origin_utm_52n`을 뺀 값(m). 원점은 코스 파일에서 읽으세요.
  - MORAI: (302595, 4124145), `morai_course.json`의 `origin_utm_52n`.
  - MIT: 지도마다 다릅니다. 출발점이 MORAI 기준 시나리오의 ego 위치에 오도록 정한 값이라, 시도마다 쓰이는 `course.json`의 `course.origin_utm_52n`을 읽어야 합니다. MORAI 원점을 MIT에 쓰면 수백 m 틀어집니다.
  - GNSS 위경도는 UTM 52N으로 바꾼 뒤 이 원점을 빼면 됩니다. 기본 코드는 `hk_drive/utm.py`의 `ll_to_map(lat, lon, origin)`에 코스 파일의 원점을 넘깁니다.
- `base_link`: 후륜 차축 중심을 지면에 내린 점. x 전방, y 좌측, z 위. yaw는 `map` +x에서 반시계.
- 센서 위치(`base_link` 기준, 기본값): GNSS·IMU (0, 0, 1.5685) m, LiDAR (1.15, 0, 1.7685) m. 두 종목 모두 TF를 발행하지 않으니 필요하면 직접 쓰세요. MORAI 카메라 위치는 `sensor_mounts.yaml`에 있습니다.

## 6. 채점 (MIT)

- 구성 만점 = (10 + 켠 옵션 점수 합) × (1 + 세트 보너스 % 합 + 도로 폭 단계 보너스 %). 기본 점수표에서 13개 옵션을 모두 켜면 도로 폭 0단계는 975점, 5단계는 1125점입니다. 조향 액추에이터 지연(+50)을 켜면 보낸 `/hk/control/command`의 조향이 250 ms 뒤에, 구동·제동 액추에이터 지연(+30)을 켜면 구동·제동·기어가 75 ms 뒤에 차에 적용됩니다(값은 `course.json`의 `steer_latency_ms`, `drive_latency_ms`). 그 사이에는 앞 명령이 유지되고, 둘 다 켜면 세트 +6%입니다. 도로 폭 단계는 0~5이며 기본 보너스는 0·4·8·12·16·20%입니다. 지도별 점수 파라미터가 다르면 화면과 배포 점수표의 값을 따릅니다.
- 벽·켜진 장애물·NPC에 차체가 닿으면 감점 사건입니다. 만점의 20%를 빼고 마지막으로 지난 체크포인트(처음이면 출발점)의 복귀 자세로 옮겨집니다. 다시 닿으면 그때마다 감점이고, 5번째에 0점·실패입니다.
- 복귀 자세는 체크포인트 선과 경로가 만나는 점, yaw는 경로 진행 방향입니다(`course.json`의 `respawn_poses`). RESPAWN 이벤트의 `checkpoint`가 몇 번째 체크포인트인지 알려 줍니다(0 = 출발점). 이때 제어기의 적분값·추정 상태를 초기화하세요.
- 켠 주차를 성공하지 않고 그 뒤 체크포인트를 지나면 바로 실패입니다. 주차는 차체 네 꼭짓점이 칸(사방 0.05 m 여유) 안, 방향 차이 20° 이하, 속력 0.05 m/s 이하가 3초 이어지면 성공입니다.
- 제한시간은 모든 구성에서 140초입니다. 넘으면 0점입니다.
- 같은 점수면 주행 시간이 짧은 쪽이 앞섭니다.

## 7. 채점 (MORAI)

- 팀마다 공식 주행 1회입니다. 운영진이 시작을 누른 뒤 차가 처음 움직인 순간부터, 체크포인트 14를 지나 도착선(출발점에서 경로에 수직인 선)을 넘을 때까지 운영진 PC 시계로 잽니다. 시작을 누르고 20초 안에 움직이지 않으면 실패입니다.
- 시도가 시작되면 PC를 조작할 수 없습니다. 공식 주행 전 준비 시간에는 YAML 같은 설정 파일과 실행 인자만 고칠 수 있고 코드는 고칠 수 없습니다.
- 제한시간은 15분입니다. 넘기면 실패이고, 도착 시각이 정확히 15분이면 완주입니다.
- 체크포인트는 공식 14개이며 각 지점 반경 3 m 안을 순서대로 지나야 통과입니다. 주행 불능이면 운영진 판단과 팀 동의로 직전 체크포인트에서 다시 출발하고, 복귀 1회당 15초 패널티입니다.
- 차로: 흰색·노란색 실선과 중앙선에 바퀴 하나라도 닿으면 15초, 닿은 상태가 3초 이어질 때마다 15초를 더합니다. 점선은 넘어도 됩니다.
- 속도: 기본 60 km/h, 체크포인트 4~5 구간 30 km/h, 체크포인트 10~12 구간(고속도로) 제한 없음. 넘는 순간 15초, 넘은 상태가 3초 이어질 때마다 15초를 더합니다.
- 총 주행 시간 = (실제 주행 시간 + 패널티) × 노이즈 배율. GPS·IMU 노이즈를 끈 시도는 GPS만 끄면 ×1.3, IMU만 끄면 ×1.1, 둘 다 끄면 ×1.5입니다.
- 완주 팀은 총 주행 시간으로 순위를 정하고, 완주 팀이 미완주 팀보다 앞섭니다. 미완주 기록은 `(꼴찌 완주 팀 시간 × 15 / 통과한 체크포인트 수 + 패널티) × 노이즈 배율`입니다. 완주 팀이 없으면 꼴찌 완주 팀 시간 대신 15분을 쓰고, 통과한 체크포인트가 없으면 MORAI 점수는 0점입니다. 미완주 팀끼리는 기록이 짧은 팀이 앞서고, 같으면 마지막 체크포인트에 먼저 닿은 팀이 앞섭니다.
- 종합 점수 = MIT 60 × (팀 MIT 점수 / 1위 MIT 점수) + MORAI 30 × (1위 MORAI 기록 / 팀 MORAI 기록) + 발표 10입니다.

## 8. 지켜야 할 것

공식 주행 코드는 위의 토픽과 경로 CSV·코스 JSON만 입력으로 써야 합니다. 이미지 안의 지도 파일, 시뮬레이터 내부 파일, 웹 화면용 연결(`localhost:8080`의 WebSocket·HTTP)을 읽으면 안 됩니다. 기술적으로 막지 않고 여러분을 믿습니다. AI 도구와 공개 코드는 써도 됩니다.

## 9. 시각화하고 싶다면 (MIT)

참가자 화면이 차·LiDAR·점수를 보여 줍니다. 내 코드의 속(추정 위치, 계획 경로 등)을 보고 싶으면 아래 방법을 씁니다. 작업 폴더(`/ws`)에 쓴 파일은 노트북의 `~/heven2026/ws`에 바로 보입니다.

- **RViz (데스크톱):** `./run.sh desktop`으로 브라우저 데스크톱(http://localhost:6080)을 열고, 그 안의 터미널에서 `ros2 launch hk_drive bringup.launch.py rviz:=true`로 기본 코드와 RViz를 함께 띄웁니다(이미 기본 코드를 띄웠으면 `rviz2 -d /ws/install/hk_drive/share/hk_drive/rviz/hk_drive.rviz`만). 추정 위치(`/hk/local/odom`, 주황), 정답 위치(연습·공터의 `/dev/ground_truth`, 초록), 계획 경로(`/hk/plan/local_path`, 파랑), LiDAR 점이 지도 위에 보입니다. 기본 코드의 localization 노드가 추정 위치를 TF(map → base_link)로 내고, launch가 센서 장착 위치(base_link → lidar_link·imu_link·gps_link)를 고정 TF로 냅니다(시뮬레이터는 TF를 내지 않습니다). rqt(`rqt_plot` 등)도 같은 터미널에서 쓸 수 있습니다. 데스크톱의 화면은 그래픽 카드 없이 그리므로 RViz를 켜 두면 CPU를 더 씁니다.
- **rosbag:** 컨테이너 셸에서 `ros2 bag record -o /ws/bags/run1 /hk/sensors/gps/fix /hk/sensors/imu/data /hk/sensors/scan /hk/control/command <내 토픽>`로 녹화하고 `Ctrl+C`로 끝냅니다. 노트북에 ROS 2가 있으면 `ros2 bag play`와 RViz로, 없으면 rosbag을 여는 데스크톱 뷰어로 봅니다. 연습·공터에서는 `/dev/ground_truth`(정답 위치)도 함께 녹화해 내 추정과 비교할 수 있습니다.
- **CSV:** 노드에서 시각·추정 위치·목표점·오차를 `/ws/log.csv`에 적고 노트북의 Python·엑셀로 그립니다. 제어 이득을 맞출 때 가장 쓸모 있습니다.
- **그림 파일:** 이미지에 OpenCV(`cv2`)가 있습니다. 위에서 본 그림을 `/ws/viz.png`로 저장하거나, 데스크톱 안에서 띄운 노드라면 `cv2.imshow` 창도 데스크톱에 뜹니다.
