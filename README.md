CSVKit (진행률 표시기 개선 프로젝트)
이 프로젝트는 csvkit의 csvsort 기능에 tqdm을 이용한 진행률 표시기를 추가합니다.

🚀 팀원 개발 환경 설정 가이드 (Windows + PowerShell)
프로젝트를 다운로드한 후, 아래 단계를 순서대로 실행하세요.

1. 프로젝트 폴더로 이동
터미널을 열고, setup.py 파일이 있는 이 프로젝트 폴더로 이동합니다.

PowerShell

cd C:\경로\csvkit_project
2. PowerShell 보안 정책 변경 (최초 1회)
PowerShell에서 가상 환경 활성화 스크립트(.ps1)를 실행할 수 있도록 허용합니다.

PowerShell

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

3. 가상 환경 생성 및 활성화
프로젝트 폴더 내에 venv라는 이름의 파이썬 가상 환경을 만듭니다.

PowerShell

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
.\venv\Scripts\Activate
(터미널 프롬프트 맨 앞에 (venv)가 나타나면 성공입니다.)

4. 수정한 csvkit 및 필요 라이브러리 설치

pip install -r requirements.txt

pip install tqdm

pip install -e.

5. 테스트 데이터 생성
시연에 필요한 500만 줄짜리 대용량 CSV 파일을 생성합니다. (make_data.py가 프로젝트 폴더에 있어야 합니다.)

PowerShell

python make_data.py

6. 최종 테스트
이제 csvsort 명령어를 실행하여 진행률 표시기가 정상적으로 동작하는지 확인합니다.

PowerShell

# 기능 시연 (진행률 표시기만 보기)
csvsort -c 1 large_file.csv | Out-Null

# 파이프라인 검증 (데이터가 깨지지 않는지 확인)
csvsort -c 1 large_file.csv | Select-Object -First 5