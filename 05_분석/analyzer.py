"""
데이터 분석 모듈
회비 데이터의 통계 분석 기능
"""

from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

class DataAnalyzer:
    """데이터 분석 클래스"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def analyze_monthly_payment_rate(self, year: int, month: int, 
                                     expected_amount: float = 0) -> Dict:
        """
        월별 납부율 분석
        
        Args:
            year: 연도
            month: 월
            expected_amount: 예상 납부 금액 (회원 수 * 개인 납부액)
        
        Returns:
            분석 결과 딕셔너리
        """
        all_members = self.db.get_all_members()
        payments = self.db.get_all_payments(year=year, month=month)
        
        total_members = len(all_members)
        paid_members = len(set(p['member_id'] for p in payments if p['status'] == 'paid'))
        unpaid_members = total_members - paid_members
        
        total_amount = sum(p['amount'] for p in payments if p['status'] == 'paid')
        
        payment_rate = (paid_members / total_members * 100) if total_members > 0 else 0
        
        return {
            'year': year,
            'month': month,
            'total_members': total_members,
            'paid_members': paid_members,
            'unpaid_members': unpaid_members,
            'payment_rate': round(payment_rate, 2),
            'total_amount': total_amount,
            'expected_amount': expected_amount,
            'completion_rate': (total_amount / expected_amount * 100) if expected_amount > 0 else 0
        }
    
    def get_unpaid_members(self, year: int, month: int) -> List[Dict]:
        """
        미납자 목록 조회
        
        Returns:
            미납자 정보 리스트
        """
        all_members = self.db.get_all_members()
        payments = self.db.get_all_payments(year=year, month=month)
        
        paid_member_ids = set(p['member_id'] for p in payments if p['status'] == 'paid')
        unpaid_members = [
            member for member in all_members 
            if member['id'] not in paid_member_ids
        ]
        
        return unpaid_members
    
    def analyze_yearly_summary(self, year: int) -> Dict:
        """
        연간 요약 분석
        
        Returns:
            연간 통계 정보
        """
        payments = self.db.get_all_payments(year=year)
        
        monthly_data = defaultdict(lambda: {'amount': 0, 'count': 0, 'members': set()})
        
        for payment in payments:
            if payment['status'] == 'paid':
                month_key = payment['month']
                monthly_data[month_key]['amount'] += payment['amount']
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['members'].add(payment['member_id'])
        
        total_amount = sum(data['amount'] for data in monthly_data.values())
        total_payments = sum(data['count'] for data in monthly_data.values())
        
        # 월별 데이터 정리
        monthly_summary = []
        for month in range(1, 13):
            if month in monthly_data:
                data = monthly_data[month]
                monthly_summary.append({
                    'month': month,
                    'amount': data['amount'],
                    'count': data['count'],
                    'paid_members': len(data['members'])
                })
            else:
                monthly_summary.append({
                    'month': month,
                    'amount': 0,
                    'count': 0,
                    'paid_members': 0
                })
        
        return {
            'year': year,
            'total_amount': total_amount,
            'total_payments': total_payments,
            'monthly_summary': monthly_summary,
            'average_monthly': total_amount / 12 if len(monthly_data) > 0 else 0
        }
    
    def analyze_member_payment_history(self, member_id: int) -> Dict:
        """
        회원별 납부 이력 분석
        
        Returns:
            회원 납부 통계
        """
        member = self.db.get_member(member_id)
        if not member:
            return None
        
        payments = self.db.get_member_payments(member_id)
        
        total_amount = sum(p['amount'] for p in payments if p['status'] == 'paid')
        total_payments = len([p for p in payments if p['status'] == 'paid'])
        
        # 최근 12개월 납부 현황
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        recent_payments = {}
        for payment in payments:
            if payment['status'] == 'paid':
                key = f"{payment['year']}-{payment['month']:02d}"
                recent_payments[key] = payment['amount']
        
        return {
            'member': member,
            'total_amount': total_amount,
            'total_payments': total_payments,
            'average_amount': total_amount / total_payments if total_payments > 0 else 0,
            'recent_payments': recent_payments,
            'payment_history': payments
        }
    
    def get_top_payers(self, limit: int = 10) -> List[Dict]:
        """
        납부 금액 상위 회원 조회
        
        Returns:
            상위 납부자 리스트
        """
        all_members = self.db.get_all_members()
        member_totals = defaultdict(float)
        
        for member in all_members:
            payments = self.db.get_member_payments(member['id'])
            total = sum(p['amount'] for p in payments if p['status'] == 'paid')
            member_totals[member['id']] = {
                'member': member,
                'total_amount': total
            }
        
        sorted_members = sorted(
            member_totals.values(),
            key=lambda x: x['total_amount'],
            reverse=True
        )
        
        return sorted_members[:limit]
    
    def get_payment_trend(self, months: int = 12) -> List[Dict]:
        """
        납부 추이 분석 (최근 N개월)
        
        Returns:
            월별 납부 추이 데이터
        """
        current_date = datetime.now()
        trend_data = []
        
        for i in range(months - 1, -1, -1):
            year = current_date.year
            month = current_date.month - i
            
            if month <= 0:
                month += 12
                year -= 1
            
            payments = self.db.get_all_payments(year=year, month=month)
            total_amount = sum(p['amount'] for p in payments if p['status'] == 'paid')
            count = len([p for p in payments if p['status'] == 'paid'])
            
            trend_data.append({
                'year': year,
                'month': month,
                'amount': total_amount,
                'count': count,
                'label': f"{year}-{month:02d}"
            })
        
        return trend_data

