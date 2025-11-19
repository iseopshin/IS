# 회비 관리 앱 - 기획 문서

## 프로젝트 목표
회비 관리를 체계적으로 수행할 수 있는 웹 애플리케이션 개발

## 주요 기능 요구사항

### 1. 회원 관리
- 회원 등록/수정/삭제
- 회원 정보: 이름, 연락처, 가입일

### 2. 회비 납부 관리
- 월별 회비 납부 기록
- 납부 금액 입력
- 납부일 기록
- 납부 상태 (납부/미납)

### 3. 통계 및 분석
- 월별 납부율 계산
- 미납자 목록
- 총 수입 통계
- 회원별 납부 이력

### 4. 시각화
- 월별 납부율 차트
- 납부 현황 그래프
- 수입 추이 그래프

### 5. 리포트
- 월별 리포트 생성
- 미납자 리포트
- 연간 통계 리포트

## 기술 스택
- Backend: Python Flask
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Visualization: Chart.js

## 데이터 구조
- 회원(Members): id, name, phone, join_date
- 회비 납부(Payments): id, member_id, amount, payment_date, month, year, status

