"""
데이터 처리 모듈
수집된 데이터의 검증, 변환, 계산 등의 처리 기능
"""

from datetime import datetime
from typing import Dict, List, Optional
import re

class DataProcessor:
    """데이터 처리 클래스"""
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """
        전화번호 형식 검증
        
        Returns:
            (유효 여부, 오류 메시지)
        """
        # 숫자와 하이픈만 허용
        phone_cleaned = re.sub(r'[-\s]', '', phone)
        if not phone_cleaned.isdigit():
            return False, "전화번호는 숫자만 입력 가능합니다"
        
        if len(phone_cleaned) < 10 or len(phone_cleaned) > 11:
            return False, "전화번호는 10자리 또는 11자리여야 합니다"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """
        이름 검증
        
        Returns:
            (유효 여부, 오류 메시지)
        """
        if not name or len(name.strip()) == 0:
            return False, "이름을 입력해주세요"
        
        if len(name.strip()) < 2:
            return False, "이름은 최소 2자 이상이어야 합니다"
        
        if len(name.strip()) > 50:
            return False, "이름은 50자 이하여야 합니다"
        
        return True, ""
    
    @staticmethod
    def validate_amount(amount: float) -> tuple[bool, str]:
        """
        금액 검증
        
        Returns:
            (유효 여부, 오류 메시지)
        """
        if amount <= 0:
            return False, "금액은 0보다 커야 합니다"
        
        if amount > 10000000:  # 1천만원 제한
            return False, "금액이 너무 큽니다"
        
        return True, ""
    
    @staticmethod
    def validate_date(date_str: str) -> tuple[bool, str]:
        """
        날짜 형식 검증 (YYYY-MM-DD)
        
        Returns:
            (유효 여부, 오류 메시지)
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, ""
        except ValueError:
            return False, "날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)"
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """전화번호 포맷팅 (010-1234-5678)"""
        phone_cleaned = re.sub(r'[-\s]', '', phone)
        if len(phone_cleaned) == 11:
            return f"{phone_cleaned[:3]}-{phone_cleaned[3:7]}-{phone_cleaned[7:]}"
        elif len(phone_cleaned) == 10:
            return f"{phone_cleaned[:3]}-{phone_cleaned[3:6]}-{phone_cleaned[6:]}"
        return phone
    
    @staticmethod
    def format_amount(amount: float) -> str:
        """금액 포맷팅 (천 단위 구분)"""
        return f"{amount:,.0f}원"
    
    @staticmethod
    def calculate_payment_rate(total_members: int, paid_members: int) -> float:
        """납부율 계산"""
        if total_members == 0:
            return 0.0
        return (paid_members / total_members) * 100
    
    @staticmethod
    def process_member_data(member_data: Dict) -> tuple[bool, Dict, List[str]]:
        """
        회원 데이터 처리 및 검증
        
        Returns:
            (성공 여부, 처리된 데이터, 오류 메시지 리스트)
        """
        errors = []
        processed_data = member_data.copy()
        
        # 이름 검증
        is_valid, error = DataProcessor.validate_name(member_data.get('name', ''))
        if not is_valid:
            errors.append(error)
        else:
            processed_data['name'] = member_data['name'].strip()
        
        # 전화번호 검증 및 포맷팅
        phone = member_data.get('phone', '')
        is_valid, error = DataProcessor.validate_phone(phone)
        if not is_valid:
            errors.append(error)
        else:
            processed_data['phone'] = DataProcessor.format_phone(phone)
        
        # 가입일 검증
        join_date = member_data.get('join_date', '')
        if join_date:
            is_valid, error = DataProcessor.validate_date(join_date)
            if not is_valid:
                errors.append(error)
        
        return (len(errors) == 0, processed_data, errors)
    
    @staticmethod
    def process_payment_data(payment_data: Dict) -> tuple[bool, Dict, List[str]]:
        """
        납부 데이터 처리 및 검증
        
        Returns:
            (성공 여부, 처리된 데이터, 오류 메시지 리스트)
        """
        errors = []
        processed_data = payment_data.copy()
        
        # 금액 검증
        amount = payment_data.get('amount', 0)
        try:
            amount = float(amount)
            is_valid, error = DataProcessor.validate_amount(amount)
            if not is_valid:
                errors.append(error)
            else:
                processed_data['amount'] = amount
        except (ValueError, TypeError):
            errors.append("금액은 숫자여야 합니다")
        
        # 날짜 검증
        payment_date = payment_data.get('payment_date', '')
        if payment_date:
            is_valid, error = DataProcessor.validate_date(payment_date)
            if not is_valid:
                errors.append(error)
        
        # 월/년 검증
        month = payment_data.get('month')
        year = payment_data.get('year')
        if month and (month < 1 or month > 12):
            errors.append("월은 1부터 12 사이여야 합니다")
        if year and year < 2000:
            errors.append("연도가 유효하지 않습니다")
        
        return (len(errors) == 0, processed_data, errors)
    
    @staticmethod
    def group_payments_by_month(payments: List[Dict]) -> Dict[str, Dict]:
        """
        납부 기록을 월별로 그룹화
        
        Returns:
            {'YYYY-MM': {total_amount, count, ...}}
        """
        grouped = {}
        for payment in payments:
            key = f"{payment['year']}-{payment['month']:02d}"
            if key not in grouped:
                grouped[key] = {
                    'year': payment['year'],
                    'month': payment['month'],
                    'total_amount': 0,
                    'count': 0,
                    'paid_members': set()
                }
            
            grouped[key]['total_amount'] += payment['amount']
            grouped[key]['count'] += 1
            grouped[key]['paid_members'].add(payment['member_id'])
        
        # set을 리스트로 변환
        for key in grouped:
            grouped[key]['paid_members'] = list(grouped[key]['paid_members'])
        
        return grouped

