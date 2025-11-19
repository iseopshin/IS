# 회비 관리 시스템 - 7단계 데이터 처리 프로젝트

## 프로젝트 개요
회비 관리를 체계적으로 수행할 수 있는 웹 애플리케이션으로, 데이터 처리의 7단계 프로세스를 구현합니다.

## 7단계 프로세스

### 1. 기획 (Planning)
- **위치**: `01_기획/`
- **내용**: 프로젝트 목표, 요구사항, 기술 스택 정의
- **파일**: `requirements.md`

### 2. 수집 (Collection)
- **위치**: `02_수집/`
- **내용**: 회원 정보 및 회비 납부 데이터 수집 모듈
- **파일**: `collect.py`
- **기능**: 
  - 회원 데이터 수집
  - 회비 납부 데이터 수집
  - 데이터 검증

### 3. 저장 (Storage)
- **위치**: `03_저장/`
- **내용**: SQLite 데이터베이스를 사용한 데이터 저장
- **파일**: `database.py`
- **기능**:
  - 회원 정보 저장/조회
  - 회비 납부 기록 저장/조회
  - 통계 정보 조회

### 4. 처리 (Processing)
- **위치**: `04_처리/`
- **내용**: 데이터 검증, 변환, 계산 처리
- **파일**: `processor.py`
- **기능**:
  - 전화번호, 이름, 금액 검증
  - 데이터 포맷팅
  - 납부율 계산
  - 월별 그룹화

### 5. 분석 (Analysis)
- **위치**: `05_분석/`
- **내용**: 통계 분석 기능
- **파일**: `analyzer.py`
- **기능**:
  - 월별 납부율 분석
  - 미납자 목록 조회
  - 연간 요약 분석
  - 회원별 납부 이력 분석
  - 상위 납부자 조회
  - 납부 추이 분석

### 6. 시각화 (Visualization)
- **위치**: `06_시각화/`
- **내용**: 차트 및 그래프 생성
- **파일**: `visualizer.py`
- **기능**:
  - 납부율 도넛 차트
  - 월별 추이 라인 차트
  - 연간 요약 바 차트
  - 상위 납부자 차트

### 7. 활용 (Utilization)
- **위치**: `07_활용/`
- **내용**: Flask 웹 애플리케이션 통합
- **파일**: `app.py`, `api_server.py`, `app_desktop.py`, `app_memory.py`
- **기능**:
  - 대시보드
  - 회원 관리
  - 회비 관리
  - 분석 및 리포트

## 설치 및 실행

### 1. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행 방법

#### 방법 1: 웹 브라우저 버전 (Flask)
```bash
cd 07_활용
python app.py
```
웹 브라우저에서 `http://localhost:5000` 접속

#### 방법 2: 데스크톱 앱 버전 (Tkinter GUI)
```bash
cd 07_활용
python app_desktop.py
```
별도의 브라우저 없이 독립적인 창에서 실행됩니다. (SQLite 데이터베이스 필요)

#### 방법 3: 메모리 버전 (데이터베이스 불필요)
```bash
cd 07_활용
python app_memory.py
```
데이터베이스 없이 작동하며, 데이터는 JSON 파일로 저장됩니다.

#### 방법 4: API 서버 (모바일 앱용)
```bash
cd 07_활용
python api_server.py
```
모바일 앱과 통신하기 위한 RESTful API 서버

## 주요 기능

### 회원 관리
- 회원 등록/수정/삭제
- 회원 정보 조회

### 회비 관리
- 월별 회비 납부 기록
- 납부 상태 관리
- 미납자 목록 조회

### 통계 및 분석
- 월별 납부율 계산
- 연간 통계 요약
- 납부 추이 분석
- 상위 납부자 조회

### 시각화
- 납부 현황 차트
- 월별 추이 그래프
- 연간 통계 차트

## 기술 스택
- **웹 버전**: Python Flask, HTML, CSS, JavaScript, Bootstrap 5, Chart.js
- **데스크톱 버전**: Python Tkinter (GUI)
- **모바일 앱**: Flutter / React Native (준비 중)
- **API 서버**: Flask RESTful API
- **Database**: SQLite (개발), PostgreSQL (프로덕션 권장)
- **공통**: Python 3.x

## 모바일 앱 배포 준비

앱스토어와 구글플레이 배포를 위한 구조가 준비되었습니다:
- `07_활용/api_server.py` - 모바일 앱용 RESTful API 서버
- `mobile_app/membership_app/` - Flutter 모바일 앱 프로젝트
- `DEPLOYMENT.md` - 배포 가이드 참고

## 프로젝트 구조
```
my_story/
├── 01_기획/
│   └── requirements.md
├── 02_수집/
│   └── collect.py
├── 03_저장/
│   └── database.py
├── 04_처리/
│   └── processor.py
├── 05_분석/
│   └── analyzer.py
├── 06_시각화/
│   └── visualizer.py
├── 07_활용/
│   ├── app.py (웹 버전)
│   ├── app_desktop.py (데스크톱 버전)
│   ├── app_memory.py (메모리 버전)
│   ├── api_server.py (API 서버)
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── members.html
│       ├── payments.html
│       └── analysis.html
├── mobile_app/
│   └── membership_app/ (Flutter 앱)
├── requirements.txt
├── membership.db (자동 생성)
└── README.md
```

## 사용 방법

1. **회원 등록**: 회원 관리 페이지에서 회원 정보 입력
2. **회비 납부**: 회비 관리 페이지에서 납부 기록 추가
3. **현황 확인**: 대시보드에서 전체 현황 확인
4. **분석**: 분석 페이지에서 상세 통계 및 차트 확인

## 데이터 구조

### 회원 테이블 (members)
- id: 회원 ID (자동 증가)
- name: 이름
- phone: 연락처
- join_date: 가입일
- created_at: 생성일시

### 회비 납부 테이블 (payments)
- id: 납부 ID (자동 증가)
- member_id: 회원 ID (외래키)
- amount: 납부 금액
- payment_date: 납부일
- month: 납부 월
- year: 납부 연도
- status: 납부 상태 (paid/unpaid)
- created_at: 생성일시
