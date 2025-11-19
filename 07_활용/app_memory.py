"""
회비 관리 앱 - 메모리 기반 버전 (데이터베이스 불필요)
데이터를 메모리에만 저장하는 간단한 버전
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Dict
import json
import os

class MemoryStorage:
    """메모리 기반 데이터 저장소"""
    
    def __init__(self):
        self.members = []
        self.payments = []
        self.next_member_id = 1
        self.next_payment_id = 1
    
    def add_member(self, name: str, phone: str, join_date: str) -> int:
        """회원 추가"""
        member = {
            'id': self.next_member_id,
            'name': name,
            'phone': phone,
            'join_date': join_date,
            'created_at': datetime.now().isoformat()
        }
        self.members.append(member)
        self.next_member_id += 1
        return member['id']
    
    def get_all_members(self) -> List[Dict]:
        """모든 회원 조회"""
        return self.members.copy()
    
    def get_member(self, member_id: int) -> Dict:
        """특정 회원 조회"""
        for member in self.members:
            if member['id'] == member_id:
                return member
        return None
    
    def delete_member(self, member_id: int) -> bool:
        """회원 삭제"""
        for i, member in enumerate(self.members):
            if member['id'] == member_id:
                # 관련 납부 기록도 삭제
                self.payments = [p for p in self.payments if p['member_id'] != member_id]
                del self.members[i]
                return True
        return False
    
    def add_payment(self, member_id: int, amount: float, payment_date: str,
                   month: int, year: int, status: str = 'paid') -> int:
        """회비 납부 추가"""
        payment = {
            'id': self.next_payment_id,
            'member_id': member_id,
            'amount': amount,
            'payment_date': payment_date,
            'month': month,
            'year': year,
            'status': status,
            'created_at': datetime.now().isoformat()
        }
        self.payments.append(payment)
        self.next_payment_id += 1
        return payment['id']
    
    def get_all_payments(self, year: int = None, month: int = None) -> List[Dict]:
        """회비 납부 기록 조회"""
        result = []
        for payment in self.payments:
            if payment['status'] != 'paid':
                continue
            if year and payment['year'] != year:
                continue
            if month and payment['month'] != month:
                continue
            
            # 회원 이름 추가
            member = self.get_member(payment['member_id'])
            payment_copy = payment.copy()
            payment_copy['member_name'] = member['name'] if member else '알 수 없음'
            result.append(payment_copy)
        
        return sorted(result, key=lambda x: (x['year'], x['month'], x['payment_date']), reverse=True)
    
    def get_statistics(self) -> Dict:
        """통계 정보"""
        total_members = len(self.members)
        total_amount = sum(p['amount'] for p in self.payments if p['status'] == 'paid')
        total_payments = len([p for p in self.payments if p['status'] == 'paid'])
        
        return {
            'total_members': total_members,
            'total_amount': total_amount,
            'total_payments': total_payments
        }
    
    def save_to_file(self, filename: str = 'membership_data.json'):
        """데이터를 파일로 저장"""
        data = {
            'members': self.members,
            'payments': self.payments,
            'next_member_id': self.next_member_id,
            'next_payment_id': self.next_payment_id
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename: str = 'membership_data.json'):
        """파일에서 데이터 로드"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.members = data.get('members', [])
                self.payments = data.get('payments', [])
                self.next_member_id = data.get('next_member_id', 1)
                self.next_payment_id = data.get('next_payment_id', 1)

class SimpleAnalyzer:
    """간단한 분석기 (데이터베이스 불필요)"""
    
    def __init__(self, storage: MemoryStorage):
        self.storage = storage
    
    def analyze_monthly_payment_rate(self, year: int, month: int) -> Dict:
        """월별 납부율 분석"""
        all_members = self.storage.get_all_members()
        payments = self.storage.get_all_payments(year=year, month=month)
        
        total_members = len(all_members)
        paid_member_ids = set(p['member_id'] for p in payments)
        paid_members = len(paid_member_ids)
        unpaid_members = total_members - paid_members
        
        total_amount = sum(p['amount'] for p in payments)
        payment_rate = (paid_members / total_members * 100) if total_members > 0 else 0
        
        return {
            'year': year,
            'month': month,
            'total_members': total_members,
            'paid_members': paid_members,
            'unpaid_members': unpaid_members,
            'payment_rate': round(payment_rate, 2),
            'total_amount': total_amount
        }
    
    def get_unpaid_members(self, year: int, month: int) -> List[Dict]:
        """미납자 목록"""
        all_members = self.storage.get_all_members()
        payments = self.storage.get_all_payments(year=year, month=month)
        paid_member_ids = set(p['member_id'] for p in payments)
        
        return [m for m in all_members if m['id'] not in paid_member_ids]
    
    def analyze_yearly_summary(self, year: int) -> Dict:
        """연간 요약"""
        payments = self.storage.get_all_payments(year=year)
        
        monthly_data = {}
        for payment in payments:
            month = payment['month']
            if month not in monthly_data:
                monthly_data[month] = {'amount': 0, 'count': 0, 'members': set()}
            monthly_data[month]['amount'] += payment['amount']
            monthly_data[month]['count'] += 1
            monthly_data[month]['members'].add(payment['member_id'])
        
        total_amount = sum(data['amount'] for data in monthly_data.values())
        total_payments = len(payments)
        
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
    
    def get_top_payers(self, limit: int = 10) -> List[Dict]:
        """상위 납부자"""
        all_members = self.storage.get_all_members()
        member_totals = {}
        
        for member in all_members:
            payments = [p for p in self.storage.payments 
                       if p['member_id'] == member['id'] and p['status'] == 'paid']
            total = sum(p['amount'] for p in payments)
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

class MembershipAppMemory:
    """데이터베이스 없이 작동하는 회비 관리 앱"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("회비 관리 시스템 (메모리 버전)")
        self.root.geometry("1200x700")
        
        # 메모리 저장소 초기화
        self.storage = MemoryStorage()
        self.analyzer = SimpleAnalyzer(self.storage)
        
        # 자동 저장 파일 로드
        self.storage.load_from_file()
        
        # 종료 시 자동 저장
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # UI 생성
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        # 상단 메뉴바
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="저장", command=self.save_data)
        file_menu.add_command(label="불러오기", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="새로고침", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.on_closing)
        
        # 노트북 (탭)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 대시보드 탭
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="대시보드")
        self.create_dashboard()
        
        # 회원 관리 탭
        self.members_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.members_frame, text="회원 관리")
        self.create_members_tab()
        
        # 회비 관리 탭
        self.payments_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.payments_frame, text="회비 관리")
        self.create_payments_tab()
        
        # 분석 탭
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="분석")
        self.create_analysis_tab()
    
    def create_dashboard(self):
        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_members_label = ttk.Label(stats_frame, text="총 회원: 0명", font=("Arial", 12, "bold"))
        self.total_members_label.pack(side=tk.LEFT, padx=20)
        
        self.total_amount_label = ttk.Label(stats_frame, text="총 납부액: 0원", font=("Arial", 12, "bold"))
        self.total_amount_label.pack(side=tk.LEFT, padx=20)
        
        self.total_payments_label = ttk.Label(stats_frame, text="총 납부건수: 0건", font=("Arial", 12, "bold"))
        self.total_payments_label.pack(side=tk.LEFT, padx=20)
        
        current_frame = ttk.LabelFrame(self.dashboard_frame, text="이번 달 현황")
        current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.monthly_info_text = tk.Text(current_frame, height=10, wrap=tk.WORD)
        self.monthly_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        recent_frame = ttk.LabelFrame(self.dashboard_frame, text="최근 납부 기록")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("회원", "금액", "납부일")
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=200)
        self.recent_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_members_tab(self):
        add_frame = ttk.LabelFrame(self.members_frame, text="회원 추가")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frame, text="이름:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.member_name_entry = ttk.Entry(add_frame, width=20)
        self.member_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="연락처:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.member_phone_entry = ttk.Entry(add_frame, width=20)
        self.member_phone_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="가입일:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.member_join_date_entry = ttk.Entry(add_frame, width=15)
        self.member_join_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.member_join_date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(add_frame, text="추가", command=self.add_member).grid(row=0, column=6, padx=5, pady=5)
        
        list_frame = ttk.LabelFrame(self.members_frame, text="회원 목록")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "이름", "연락처", "가입일")
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=150)
        self.members_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(padx=10, pady=5)
        ttk.Button(btn_frame, text="삭제", command=self.delete_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="새로고침", command=self.refresh_members).pack(side=tk.LEFT, padx=5)
    
    def create_payments_tab(self):
        add_frame = ttk.LabelFrame(self.payments_frame, text="회비 납부 추가")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frame, text="회원:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.payment_member_var = tk.StringVar()
        self.payment_member_combo = ttk.Combobox(add_frame, textvariable=self.payment_member_var, width=25, state="readonly")
        self.payment_member_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="금액:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.payment_amount_entry = ttk.Entry(add_frame, width=15)
        self.payment_amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="납부일:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.payment_date_entry = ttk.Entry(add_frame, width=15)
        self.payment_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.payment_date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(add_frame, text="연도:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.payment_year_entry = ttk.Entry(add_frame, width=10)
        self.payment_year_entry.insert(0, str(datetime.now().year))
        self.payment_year_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="월:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.payment_month_entry = ttk.Entry(add_frame, width=10)
        self.payment_month_entry.insert(0, str(datetime.now().month))
        self.payment_month_entry.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Button(add_frame, text="추가", command=self.add_payment).grid(row=1, column=4, padx=5, pady=5)
        
        status_frame = ttk.LabelFrame(self.payments_frame, text="납부 현황")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.payment_status_text = tk.Text(status_frame, height=5, wrap=tk.WORD)
        self.payment_status_text.pack(fill=tk.X, padx=10, pady=10)
        
        list_frame = ttk.LabelFrame(self.payments_frame, text="납부 기록")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("회원", "금액", "납부일", "연도", "월")
        self.payments_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.payments_tree.heading(col, text=col)
            self.payments_tree.column(col, width=120)
        self.payments_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        unpaid_frame = ttk.LabelFrame(self.payments_frame, text="미납자 목록")
        unpaid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.unpaid_listbox = tk.Listbox(unpaid_frame)
        self.unpaid_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(padx=10, pady=5)
        ttk.Button(btn_frame, text="새로고침", command=self.refresh_payments).pack(side=tk.LEFT, padx=5)
    
    def create_analysis_tab(self):
        year_frame = ttk.Frame(self.analysis_frame)
        year_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(year_frame, text="연도:").pack(side=tk.LEFT, padx=5)
        self.analysis_year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(year_frame, textvariable=self.analysis_year_var, width=10, state="readonly")
        year_combo['values'] = [str(y) for y in range(2020, datetime.now().year + 2)]
        year_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(year_frame, text="조회", command=self.refresh_analysis).pack(side=tk.LEFT, padx=5)
        
        summary_frame = ttk.LabelFrame(self.analysis_frame, text="연간 요약")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.analysis_summary_text = tk.Text(summary_frame, height=8, wrap=tk.WORD)
        self.analysis_summary_text.pack(fill=tk.X, padx=10, pady=10)
        
        top_frame = ttk.LabelFrame(self.analysis_frame, text="상위 납부자")
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("순위", "회원", "총 납부액")
        self.top_payers_tree = ttk.Treeview(top_frame, columns=columns, show="headings")
        for col in columns:
            self.top_payers_tree.heading(col, text=col)
            self.top_payers_tree.column(col, width=200)
        self.top_payers_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def refresh_data(self):
        self.refresh_dashboard()
        self.refresh_members()
        self.refresh_payments()
        self.refresh_analysis()
    
    def refresh_dashboard(self):
        stats = self.storage.get_statistics()
        self.total_members_label.config(text=f"총 회원: {stats['total_members']}명")
        self.total_amount_label.config(text=f"총 납부액: {stats['total_amount']:,.0f}원")
        self.total_payments_label.config(text=f"총 납부건수: {stats['total_payments']}건")
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        analysis = self.analyzer.analyze_monthly_payment_rate(current_year, current_month)
        
        info = f"""이번 달 ({current_year}년 {current_month}월) 현황:

총 회원: {analysis['total_members']}명
납부: {analysis['paid_members']}명
미납: {analysis['unpaid_members']}명
납부율: {analysis['payment_rate']:.1f}%
총 납부액: {analysis['total_amount']:,.0f}원"""
        
        self.monthly_info_text.delete(1.0, tk.END)
        self.monthly_info_text.insert(1.0, info)
        
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        recent_payments = self.storage.get_all_payments()[:10]
        for payment in recent_payments:
            self.recent_tree.insert("", tk.END, values=(
                payment['member_name'],
                f"{payment['amount']:,.0f}원",
                payment['payment_date']
            ))
    
    def refresh_members(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        members = self.storage.get_all_members()
        for member in members:
            self.members_tree.insert("", tk.END, values=(
                member['id'],
                member['name'],
                member['phone'],
                member['join_date']
            ))
        
        self.payment_member_combo['values'] = [f"{m['id']}: {m['name']} ({m['phone']})" for m in members]
    
    def refresh_payments(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        analysis = self.analyzer.analyze_monthly_payment_rate(current_year, current_month)
        unpaid_members = self.analyzer.get_unpaid_members(current_year, current_month)
        
        status = f"""{current_year}년 {current_month}월 납부 현황:
납부율: {analysis['payment_rate']:.1f}%
납부: {analysis['paid_members']}명 / 미납: {analysis['unpaid_members']}명
총 납부액: {analysis['total_amount']:,.0f}원"""
        
        self.payment_status_text.delete(1.0, tk.END)
        self.payment_status_text.insert(1.0, status)
        
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        payments = self.storage.get_all_payments(year=current_year, month=current_month)
        for payment in payments:
            self.payments_tree.insert("", tk.END, values=(
                payment['member_name'],
                f"{payment['amount']:,.0f}원",
                payment['payment_date'],
                payment['year'],
                payment['month']
            ))
        
        self.unpaid_listbox.delete(0, tk.END)
        for member in unpaid_members:
            self.unpaid_listbox.insert(tk.END, f"{member['name']} ({member['phone']})")
    
    def refresh_analysis(self):
        year = int(self.analysis_year_var.get())
        yearly_summary = self.analyzer.analyze_yearly_summary(year)
        top_payers = self.analyzer.get_top_payers(10)
        
        summary = f"""{year}년 연간 요약:

총 납부 금액: {yearly_summary['total_amount']:,.0f}원
총 납부 건수: {yearly_summary['total_payments']}건
월평균 납부액: {yearly_summary['average_monthly']:,.0f}원

월별 현황:
"""
        for month_data in yearly_summary['monthly_summary']:
            if month_data['amount'] > 0:
                summary += f"{month_data['month']}월: {month_data['amount']:,.0f}원 ({month_data['paid_members']}명)\n"
        
        self.analysis_summary_text.delete(1.0, tk.END)
        self.analysis_summary_text.insert(1.0, summary)
        
        for item in self.top_payers_tree.get_children():
            self.top_payers_tree.delete(item)
        
        for idx, payer in enumerate(top_payers, 1):
            self.top_payers_tree.insert("", tk.END, values=(
                idx,
                payer['member']['name'],
                f"{payer['total_amount']:,.0f}원"
            ))
    
    def add_member(self):
        name = self.member_name_entry.get().strip()
        phone = self.member_phone_entry.get().strip()
        join_date = self.member_join_date_entry.get().strip()
        
        if not name or not phone:
            messagebox.showerror("오류", "이름과 연락처를 입력해주세요.")
            return
        
        try:
            self.storage.add_member(name, phone, join_date)
            messagebox.showinfo("성공", "회원이 추가되었습니다.")
            self.member_name_entry.delete(0, tk.END)
            self.member_phone_entry.delete(0, tk.END)
            self.member_join_date_entry.delete(0, tk.END)
            self.member_join_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            self.refresh_members()
            self.refresh_dashboard()
            self.save_data()
        except Exception as e:
            messagebox.showerror("오류", str(e))
    
    def delete_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 회원을 선택해주세요.")
            return
        
        item = self.members_tree.item(selected[0])
        member_id = item['values'][0]
        member_name = item['values'][1]
        
        if messagebox.askyesno("확인", f"'{member_name}' 회원을 삭제하시겠습니까?"):
            try:
                self.storage.delete_member(member_id)
                messagebox.showinfo("성공", "회원이 삭제되었습니다.")
                self.refresh_members()
                self.refresh_dashboard()
                self.refresh_payments()
                self.save_data()
            except Exception as e:
                messagebox.showerror("오류", str(e))
    
    def add_payment(self):
        member_str = self.payment_member_var.get()
        if not member_str:
            messagebox.showerror("오류", "회원을 선택해주세요.")
            return
        
        member_id = int(member_str.split(':')[0])
        amount_str = self.payment_amount_entry.get().strip()
        payment_date = self.payment_date_entry.get().strip()
        year_str = self.payment_year_entry.get().strip()
        month_str = self.payment_month_entry.get().strip()
        
        if not amount_str:
            messagebox.showerror("오류", "금액을 입력해주세요.")
            return
        
        try:
            amount = float(amount_str)
            year = int(year_str) if year_str else datetime.now().year
            month = int(month_str) if month_str else datetime.now().month
            
            self.storage.add_payment(member_id, amount, payment_date, month, year)
            messagebox.showinfo("성공", "회비 납부가 등록되었습니다.")
            self.payment_amount_entry.delete(0, tk.END)
            self.payment_date_entry.delete(0, tk.END)
            self.payment_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            self.refresh_payments()
            self.refresh_dashboard()
            self.save_data()
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력해주세요.")
        except Exception as e:
            messagebox.showerror("오류", str(e))
    
    def save_data(self):
        try:
            self.storage.save_to_file()
            messagebox.showinfo("성공", "데이터가 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {str(e)}")
    
    def load_data(self):
        try:
            self.storage.load_from_file()
            messagebox.showinfo("성공", "데이터가 불러와졌습니다.")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("오류", f"불러오기 실패: {str(e)}")
    
    def on_closing(self):
        self.save_data()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MembershipAppMemory(root)
    root.mainloop()

if __name__ == '__main__':
    main()

