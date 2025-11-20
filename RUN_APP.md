# 앱 실행 가이드

## 실행 순서

### 1단계: API 서버 실행

**새 터미널 창을 열고:**
```powershell
cd C:\Users\User\my_story\07_활용
python api_server.py
```

서버가 `http://localhost:5000`에서 실행됩니다.
**이 터미널은 계속 열어두세요!**

### 2단계: 안드로이드 에뮬레이터 실행

**방법 1: Flutter 명령어 사용**
```powershell
flutter emulators --launch Medium_Phone_API_36.1
```

**방법 2: Android Studio 사용**
- Android Studio 열기
- Tools > Device Manager
- "Medium Phone API 36.1" 선택 후 실행 버튼 클릭

에뮬레이터가 완전히 부팅될 때까지 기다리세요 (1-2분 소요)

### 3단계: Flutter 앱 실행

**새 터미널 창을 열고:**
```powershell
cd C:\Users\User\my_story\mobile_app\membership_app
flutter run
```

또는 특정 에뮬레이터를 지정:
```powershell
flutter run -d Medium_Phone_API_36.1
```

## 빠른 실행 스크립트

### Windows 배치 파일 생성

`run_app.bat` 파일을 만들고:
```batch
@echo off
echo API 서버를 시작합니다...
start "API Server" cmd /k "cd /d C:\Users\User\my_story\07_활용 && python api_server.py"

timeout /t 3

echo 에뮬레이터를 시작합니다...
flutter emulators --launch Medium_Phone_API_36.1

timeout /t 15

echo Flutter 앱을 시작합니다...
cd /d C:\Users\User\my_story\mobile_app\membership_app
flutter run
```

## 문제 해결

### API 서버가 실행되지 않는 경우
```powershell
# 패키지 설치 확인
pip install flask flask-cors

# 서버 수동 실행
cd C:\Users\User\my_story\07_활용
python api_server.py
```

### 에뮬레이터가 실행되지 않는 경우
```powershell
# 사용 가능한 에뮬레이터 확인
flutter emulators

# 에뮬레이터 수동 실행
flutter emulators --launch Medium_Phone_API_36.1
```

### Flutter 앱이 실행되지 않는 경우
```powershell
# Flutter 환경 확인
flutter doctor

# 패키지 재설치
cd C:\Users\User\my_story\mobile_app\membership_app
flutter pub get

# 앱 실행
flutter run
```

### 연결 오류가 발생하는 경우
1. API 서버가 실행 중인지 확인: `http://localhost:5000/api/health`
2. `lib/services/api_service.dart`에서 주소 확인:
   - 에뮬레이터: `http://10.0.2.2:5000/api`
   - 실제 기기: `http://YOUR_COMPUTER_IP:5000/api`

## 현재 실행 중인 프로세스

- ✅ API 서버: 백그라운드에서 실행 중
- ✅ 에뮬레이터: 시작 중
- ✅ Flutter 앱: 실행 중

## 확인 사항

1. API 서버가 정상 작동하는지 확인:
   - 브라우저에서 `http://localhost:5000/api/health` 접속
   - `{"status": "ok"}` 응답이 나와야 함

2. 에뮬레이터가 완전히 부팅되었는지 확인:
   - 에뮬레이터 화면이 나타나고 홈 화면이 보여야 함

3. Flutter 앱이 설치되었는지 확인:
   - 에뮬레이터에 "회비 관리" 앱이 설치되어야 함


