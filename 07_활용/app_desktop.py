"""
회비 관리 앱 - 데스크톱 애플리케이션
Tkinter를 사용한 GUI 버전
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sys
import os

# 프로젝트 루트를 경로에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(parent_dir, '03_저장'))
sys.path.insert(0, os.path.join(parent_dir, '02_수집'))
sys.path.insert(0, os.path.join(parent_dir, '04_처리'))
sys.path.insert(0, os.path.join(parent_dir, '05_분석'))
sys.path.insert(0, os.path.join(parent_dir, '06_시각화'))

from database import DatabaseManager
from collect import DataCollector
from processor import DataProcessor
from analyzer import DataAnalyzer
from visualizer import DataVisualizer

class MembershipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("회비 관리 시스템")
        self.root.geometry("1200x700")
        
        # 모듈 초기화
        db_path = os.path.join(parent_dir, 'membership.db')
        self.db = DatabaseManager(db_path)
        self.collector = DataCollector()
        self.processor = DataProcessor()
        self.analyzer = DataAnalyzer(self.db)
        self.visualizer = DataVisualizer()
        
        # UI 생성
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        # 상단 메뉴바
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="새로고침", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        
        # 메뉴 메뉴
        menu_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="메뉴", menu=menu_menu)
        menu_menu.add_command(label="대시보드", command=self.show_dashboard)
        menu_menu.add_command(label="회원 관리", command=self.show_members)
        menu_menu.add_command(label="회비 관리", command=self.show_payments)
        menu_menu.add_command(label="분석", command=self.show_analysis)
        
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
        # 통계 카드
        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_members_label = ttk.Label(stats_frame, text="총 회원: 0명", font=("Arial", 12, "bold"))
        self.total_members_label.pack(side=tk.LEFT, padx=20)
        
        self.total_amount_label = ttk.Label(stats_frame, text="총 납부액: 0원", font=("Arial", 12, "bold"))
        self.total_amount_label.pack(side=tk.LEFT, padx=20)
        
        self.total_payments_label = ttk.Label(stats_frame, text="총 납부건수: 0건", font=("Arial", 12, "bold"))
        self.total_payments_label.pack(side=tk.LEFT, padx=20)
        
        # 이번 달 현황
        current_frame = ttk.LabelFrame(self.dashboard_frame, text="이번 달 현황")
        current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.monthly_info_text = tk.Text(current_frame, height=10, wrap=tk.WORD)
        self.monthly_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 최근 납부 기록
        recent_frame = ttk.LabelFrame(self.dashboard_frame, text="최근 납부 기록")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 트리뷰
        columns = ("회원", "금액", "납부일")
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=200)
        self.recent_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_members_tab(self):
        # 회원 추가 폼
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
        
        # 회원 목록
        list_frame = ttk.LabelFrame(self.members_frame, text="회원 목록")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "이름", "연락처", "가입일")
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=150)
        self.members_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 버튼
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(padx=10, pady=5)
        ttk.Button(btn_frame, text="삭제", command=self.delete_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="새로고침", command=self.refresh_members).pack(side=tk.LEFT, padx=5)
    
    def create_payments_tab(self):
        # 회비 납부 추가 폼
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
        
        # 납부 현황
        status_frame = ttk.LabelFrame(self.payments_frame, text="납부 현황")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.payment_status_text = tk.Text(status_frame, height=5, wrap=tk.WORD)
        self.payment_status_text.pack(fill=tk.X, padx=10, pady=10)
        
        # 납부 기록
        list_frame = ttk.LabelFrame(self.payments_frame, text="납부 기록")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("회원", "금액", "납부일", "연도", "월")
        self.payments_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.payments_tree.heading(col, text=col)
            self.payments_tree.column(col, width=120)
        self.payments_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 미납자 목록
        unpaid_frame = ttk.LabelFrame(self.payments_frame, text="미납자 목록")
        unpaid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.unpaid_listbox = tk.Listbox(unpaid_frame)
        self.unpaid_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 버튼
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(padx=10, pady=5)
        ttk.Button(btn_frame, text="새로고침", command=self.refresh_payments).pack(side=tk.LEFT, padx=5)
    
    def create_analysis_tab(self):
        # 연도 선택
        year_frame = ttk.Frame(self.analysis_frame)
        year_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(year_frame, text="연도:").pack(side=tk.LEFT, padx=5)
        self.analysis_year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(year_frame, textvariable=self.analysis_year_var, width=10, state="readonly")
        year_combo['values'] = [str(y) for y in range(2020, datetime.now().year + 2)]
        year_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(year_frame, text="조회", command=self.refresh_analysis).pack(side=tk.LEFT, padx=5)
        
        # 연간 요약
        summary_frame = ttk.LabelFrame(self.analysis_frame, text="연간 요약")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.analysis_summary_text = tk.Text(summary_frame, height=8, wrap=tk.WORD)
        self.analysis_summary_text.pack(fill=tk.X, padx=10, pady=10)
        
        # 상위 납부자
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
        stats = self.db.get_statistics()
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
        
        # 최근 납부 기록
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        recent_payments = self.db.get_all_payments()[:10]
        for payment in recent_payments:
            self.recent_tree.insert("", tk.END, values=(
                payment['member_name'],
                f"{payment['amount']:,.0f}원",
                payment['payment_date']
            ))
    
    def refresh_members(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        members = self.db.get_all_members()
        for member in members:
            self.members_tree.insert("", tk.END, values=(
                member['id'],
                member['name'],
                member['phone'],
                member['join_date']
            ))
        
        # 회비 관리의 회원 콤보박스 업데이트
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
        
        # 납부 기록
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        payments = self.db.get_all_payments(year=current_year, month=current_month)
        for payment in payments:
            self.payments_tree.insert("", tk.END, values=(
                payment['member_name'],
                f"{payment['amount']:,.0f}원",
                payment['payment_date'],
                payment['year'],
                payment['month']
            ))
        
        # 미납자 목록
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
        
        # 상위 납부자
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
        
        member_data = self.collector.collect_member_data(name, phone, join_date)
        is_valid, processed_data, errors = self.processor.process_member_data(member_data)
        
        if not is_valid:
            messagebox.showerror("오류", "\n".join(errors))
            return
        
        try:
            self.db.save_member(processed_data['name'], processed_data['phone'], processed_data['join_date'])
            messagebox.showinfo("성공", "회원이 추가되었습니다.")
            self.member_name_entry.delete(0, tk.END)
            self.member_phone_entry.delete(0, tk.END)
            self.member_join_date_entry.delete(0, tk.END)
            self.member_join_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            self.refresh_members()
            self.refresh_dashboard()
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
                self.db.delete_member(member_id)
                messagebox.showinfo("성공", "회원이 삭제되었습니다.")
                self.refresh_members()
                self.refresh_dashboard()
                self.refresh_payments()
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
            
            payment_data = self.collector.collect_payment_data(member_id, amount, payment_date, month, year)
            is_valid, processed_data, errors = self.processor.process_payment_data(payment_data)
            
            if not is_valid:
                messagebox.showerror("오류", "\n".join(errors))
                return
            
            self.db.save_payment(
                processed_data['member_id'],
                processed_data['amount'],
                processed_data['payment_date'],
                processed_data['month'],
                processed_data['year'],
                processed_data['status']
            )
            messagebox.showinfo("성공", "회비 납부가 등록되었습니다.")
            self.payment_amount_entry.delete(0, tk.END)
            self.payment_date_entry.delete(0, tk.END)
            self.payment_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            self.refresh_payments()
            self.refresh_dashboard()
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력해주세요.")
        except Exception as e:
            messagebox.showerror("오류", str(e))
    
    def show_dashboard(self):
        self.notebook.select(0)
    
    def show_members(self):
        self.notebook.select(1)
    
    def show_payments(self):
        self.notebook.select(2)
    
    def show_analysis(self):
        self.notebook.select(3)

def main():
    root = tk.Tk()
    app = MembershipApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()

