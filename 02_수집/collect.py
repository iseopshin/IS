"""
회비 데이터 수집 모듈
회원 정보 및 회비 납부 데이터를 수집하는 기능
"""

from datetime import datetime
from typing import Dict, Optional

class DataCollector:
    """데이터 수집 클래스"""
    
    def __init__(self):
        self.collected_data = []
    
    def collect_member_data(self, name: str, phone: str, join_date: Optional[str] = None) -> Dict:
        """
        회원 데이터 수집
        
        Args:
            name: 회원 이름
            phone: 연락처
            join_date: 가입일 (YYYY-MM-DD 형식, None이면 오늘 날짜)
        
        Returns:
            수집된 회원 데이터 딕셔너리
        """
        if join_date is None:
            join_date = datetime.now().strftime('%Y-%m-%d')
        
        member_data = {
            'name': name.strip(),
            'phone': phone.strip(),
            'join_date': join_date,
            'collected_at': datetime.now().isoformat()
        }
        
        self.collected_data.append(('member', member_data))
        return member_data
    
    def collect_payment_data(self, member_id: int, amount: float, 
                            payment_date: Optional[str] = None,
                            month: Optional[int] = None,
                            year: Optional[int] = None) -> Dict:
        """
        회비 납부 데이터 수집
        
        Args:
            member_id: 회원 ID
            amount: 납부 금액
            payment_date: 납부일 (YYYY-MM-DD 형식, None이면 오늘 날짜)
            month: 납부 월 (None이면 현재 월)
            year: 납부 연도 (None이면 현재 연도)
        
        Returns:
            수집된 납부 데이터 딕셔너리
        """
        if payment_date is None:
            payment_date = datetime.now().strftime('%Y-%m-%d')
        
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        payment_data = {
            'member_id': member_id,
            'amount': float(amount),
            'payment_date': payment_date,
            'month': month,
            'year': year,
            'status': 'paid',
            'collected_at': datetime.now().isoformat()
        }
        
        self.collected_data.append(('payment', payment_data))
        return payment_data
    
    def validate_collected_data(self) -> tuple[bool, list]:
        """
        수집된 데이터 검증
        
        Returns:
            (검증 성공 여부, 오류 메시지 리스트)
        """
        errors = []
        
        for data_type, data in self.collected_data:
            if data_type == 'member':
                if not data.get('name') or len(data['name'].strip()) == 0:
                    errors.append(f"회원 이름이 비어있습니다: {data}")
                if not data.get('phone') or len(data['phone'].strip()) == 0:
                    errors.append(f"연락처가 비어있습니다: {data}")
            
            elif data_type == 'payment':
                if data.get('amount', 0) <= 0:
                    errors.append(f"납부 금액이 유효하지 않습니다: {data}")
                if not data.get('member_id'):
                    errors.append(f"회원 ID가 없습니다: {data}")
        
        return (len(errors) == 0, errors)
    
    def get_collected_count(self) -> Dict[str, int]:
        """수집된 데이터 개수 반환"""
        counts = {'member': 0, 'payment': 0}
        for data_type, _ in self.collected_data:
            counts[data_type] += 1
        return counts
    
    def clear_collected_data(self):
        """수집된 데이터 초기화"""
        self.collected_data = []

