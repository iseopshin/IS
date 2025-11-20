"""
데이터 저장 모듈
SQLite 데이터베이스를 사용하여 회원 및 회비 데이터 저장
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = 'membership.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with self.get_connection() as conn:
            # 회원 테이블
            conn.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    join_date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, phone)
                )
            ''')
            
            # 회비 납부 테이블
            conn.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    status TEXT DEFAULT 'paid',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id),
                    UNIQUE(member_id, month, year)
                )
            ''')
            
            # 지출 테이블
            conn.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    amount REAL NOT NULL,
                    description TEXT,
                    expense_date TEXT NOT NULL,
                    created_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def save_member(self, name: str, phone: str, join_date: Optional[str] = None) -> int:
        """
        회원 정보 저장
        
        Returns:
            저장된 회원의 ID
        """
        if join_date is None:
            join_date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT OR REPLACE INTO members (name, phone, join_date)
                VALUES (?, ?, ?)
            ''', (name, phone, join_date))
            return cursor.lastrowid
    
    def save_payment(self, member_id: int, amount: float, payment_date: str,
                     month: int, year: int, status: str = 'paid') -> int:
        """
        회비 납부 정보 저장
        
        Returns:
            저장된 납부 기록의 ID
        """
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT OR REPLACE INTO payments 
                (member_id, amount, payment_date, month, year, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (member_id, amount, payment_date, month, year, status))
            return cursor.lastrowid
    
    def get_all_members(self) -> List[Dict]:
        """모든 회원 조회"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM members ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_member(self, member_id: int) -> Optional[Dict]:
        """특정 회원 조회"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_payments(self, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict]:
        """회비 납부 기록 조회"""
        with self.get_connection() as conn:
            query = '''
                SELECT p.*, m.name as member_name 
                FROM payments p
                JOIN members m ON p.member_id = m.id
            '''
            params = []
            
            if year and month:
                query += ' WHERE p.year = ? AND p.month = ?'
                params = [year, month]
            elif year:
                query += ' WHERE p.year = ?'
                params = [year]
            
            query += ' ORDER BY p.year DESC, p.month DESC, p.payment_date DESC'
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_member_payments(self, member_id: int) -> List[Dict]:
        """특정 회원의 납부 기록 조회"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM payments 
                WHERE member_id = ? 
                ORDER BY year DESC, month DESC
            ''', (member_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_member(self, member_id: int) -> bool:
        """회원 삭제"""
        with self.get_connection() as conn:
            conn.execute('DELETE FROM payments WHERE member_id = ?', (member_id,))
            cursor = conn.execute('DELETE FROM members WHERE id = ?', (member_id,))
            return cursor.rowcount > 0
    
    def save_expense(self, category: str, amount: float, expense_date: str,
                    subcategory: str = None, description: str = None, 
                    created_by: str = None) -> int:
        """
        지출 정보 저장
        
        Returns:
            저장된 지출 기록의 ID
        """
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO expenses 
                (category, subcategory, amount, description, expense_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, subcategory, amount, description, expense_date, created_by))
            return cursor.lastrowid
    
    def get_all_expenses(self, year: Optional[int] = None, 
                        month: Optional[int] = None,
                        category: Optional[str] = None) -> List[Dict]:
        """지출 기록 조회"""
        with self.get_connection() as conn:
            query = 'SELECT * FROM expenses WHERE 1=1'
            params = []
            
            if year and month:
                query += ' AND strftime("%Y", expense_date) = ? AND strftime("%m", expense_date) = ?'
                params.extend([str(year), f"{month:02d}"])
            elif year:
                query += ' AND strftime("%Y", expense_date) = ?'
                params.append(str(year))
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            query += ' ORDER BY expense_date DESC, created_at DESC'
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_expense(self, expense_id: int) -> Optional[Dict]:
        """특정 지출 조회"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_expense(self, expense_id: int) -> bool:
        """지출 삭제"""
        with self.get_connection() as conn:
            cursor = conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            return cursor.rowcount > 0
    
    def get_expense_statistics(self, year: Optional[int] = None) -> Dict:
        """지출 통계 정보 조회"""
        with self.get_connection() as conn:
            stats = {}
            
            # 총 지출 금액
            if year:
                cursor = conn.execute('''
                    SELECT SUM(amount) as total 
                    FROM expenses 
                    WHERE strftime("%Y", expense_date) = ?
                ''', (str(year),))
            else:
                cursor = conn.execute('SELECT SUM(amount) as total FROM expenses')
            stats['total_expenses'] = cursor.fetchone()['total'] or 0
            
            # 카테고리별 지출
            if year:
                cursor = conn.execute('''
                    SELECT category, SUM(amount) as total, COUNT(*) as count
                    FROM expenses
                    WHERE strftime("%Y", expense_date) = ?
                    GROUP BY category
                ''', (str(year),))
            else:
                cursor = conn.execute('''
                    SELECT category, SUM(amount) as total, COUNT(*) as count
                    FROM expenses
                    GROUP BY category
                ''')
            
            category_stats = {}
            for row in cursor.fetchall():
                category_stats[row['category']] = {
                    'total': row['total'],
                    'count': row['count']
                }
            stats['by_category'] = category_stats
            
            # 총 지출 건수
            if year:
                cursor = conn.execute('''
                    SELECT COUNT(*) as count 
                    FROM expenses 
                    WHERE strftime("%Y", expense_date) = ?
                ''', (str(year),))
            else:
                cursor = conn.execute('SELECT COUNT(*) as count FROM expenses')
            stats['total_expense_count'] = cursor.fetchone()['count']
            
            return stats
    
    def get_unpaid_members_detailed(self, year: Optional[int] = None, 
                                    month: Optional[int] = None) -> List[Dict]:
        """
        미납 회원 상세 정보 조회 (미납 기간 포함)
        """
        with self.get_connection() as conn:
            all_members = self.get_all_members()
            
            if year and month:
                payments = self.get_all_payments(year=year, month=month)
            elif year:
                payments = self.get_all_payments(year=year)
            else:
                # 현재 월 기준
                now = datetime.now()
                payments = self.get_all_payments(year=now.year, month=now.month)
            
            paid_member_ids = set(p['member_id'] for p in payments if p['status'] == 'paid')
            
            unpaid_members = []
            for member in all_members:
                if member['id'] not in paid_member_ids:
                    # 미납 기간 계산
                    member_payments = self.get_member_payments(member['id'])
                    if member_payments:
                        last_payment = max(member_payments, 
                                         key=lambda p: (p['year'], p['month']))
                        last_date = f"{last_payment['year']}-{last_payment['month']:02d}"
                    else:
                        last_date = member['join_date']
                    
                    unpaid_members.append({
                        **member,
                        'last_payment_date': last_date,
                        'unpaid_months': self._calculate_unpaid_months(
                            last_date, year or datetime.now().year, 
                            month or datetime.now().month
                        )
                    })
            
            return unpaid_members
    
    def _calculate_unpaid_months(self, last_date: str, current_year: int, 
                                 current_month: int) -> int:
        """미납 개월 수 계산"""
        try:
            if '-' in last_date:
                parts = last_date.split('-')
                if len(parts) >= 2:
                    last_year = int(parts[0])
                    last_month = int(parts[1])
                    months_diff = (current_year - last_year) * 12 + (current_month - last_month)
                    return max(0, months_diff)
        except:
            pass
        return 0
    
    def get_statistics(self) -> Dict:
        """전체 통계 정보 조회"""
        with self.get_connection() as conn:
            stats = {}
            
            # 총 회원 수
            cursor = conn.execute('SELECT COUNT(*) as count FROM members')
            stats['total_members'] = cursor.fetchone()['count']
            
            # 총 납부 금액
            cursor = conn.execute('SELECT SUM(amount) as total FROM payments WHERE status = "paid"')
            stats['total_amount'] = cursor.fetchone()['total'] or 0
            
            # 총 납부 건수
            cursor = conn.execute('SELECT COUNT(*) as count FROM payments WHERE status = "paid"')
            stats['total_payments'] = cursor.fetchone()['count']
            
            # 총 지출 금액
            cursor = conn.execute('SELECT SUM(amount) as total FROM expenses')
            stats['total_expenses'] = cursor.fetchone()['total'] or 0
            
            # 순수익 (수입 - 지출)
            stats['net_income'] = stats['total_amount'] - stats['total_expenses']
            
            return stats

