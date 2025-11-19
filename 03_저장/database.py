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
            
            return stats

