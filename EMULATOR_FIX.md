# 시뮬레이터 작동 문제 해결

## 발견된 문제들

### 1. AndroidManifest.xml 설정 누락
- **문제**: 메인 AndroidManifest.xml에 인터넷 권한이 없었음
- **해결**: `INTERNET` 및 `ACCESS_NETWORK_STATE` 권한 추가

### 2. HTTP (Cleartext Traffic) 차단
- **문제**: Android 9 (API 28) 이상에서는 HTTP 트래픽이 기본적으로 차단됨
- **해결**: 
  - `android:usesCleartextTraffic="true"` 추가
  - `network_security_config.xml` 파일 생성하여 에뮬레이터용 HTTP 허용

### 3. 앱 라벨 설정
- **문제**: 앱 이름이 기본값으로 표시됨
- **해결**: `android:label="회비 관리"`로 변경

## 수정된 파일들

1. **mobile_app/membership_app/android/app/src/main/AndroidManifest.xml**
   - 인터넷 권한 추가
   - usesCleartextTraffic 설정 추가
   - networkSecurityConfig 추가
   - 앱 라벨 변경

2. **mobile_app/membership_app/android/app/src/main/res/xml/network_security_config.xml** (신규)
   - 에뮬레이터용 HTTP 허용 설정
   - localhost, 10.0.2.2 허용

## 테스트 방법

1. **앱 재빌드**:
   ```bash
   cd mobile_app/membership_app
   flutter clean
   flutter pub get
   flutter run
   ```

2. **API 서버 실행 확인**:
   ```bash
   cd 07_활용
   python api_server.py
   ```

3. **에뮬레이터에서 확인**:
   - 앱이 정상적으로 실행되는지 확인
   - API 연결이 되는지 확인
   - 데이터 로딩이 정상인지 확인

## 추가 확인 사항

### 네트워크 연결 테스트
에뮬레이터에서 다음을 확인하세요:
1. 에뮬레이터의 브라우저에서 `http://10.0.2.2:5000/api/health` 접속 시도
2. API 서버가 실행 중인지 확인
3. 방화벽이 포트 5000을 차단하지 않는지 확인

### 로그 확인
```bash
flutter logs
```
또는 Android Studio의 Logcat에서 네트워크 관련 오류 확인

## 문제가 계속되면

1. **에뮬레이터 재시작**
2. **앱 완전 삭제 후 재설치**
3. **API 서버 재시작**
4. **포트 충돌 확인**: `netstat -ano | findstr :5000`

