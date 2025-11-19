"""
회비 관리 앱 - 메인 애플리케이션
7단계 프로세스를 통합한 Flask 웹 애플리케이션
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'membership-management-secret-key'

# 커스텀 Jinja2 필터 추가
@app.template_filter('currency')
def currency_filter(value):
    """금액을 천 단위 구분으로 포맷팅"""
    try:
        return f"{float(value):,.0f}원"
    except (ValueError, TypeError):
        return "0원"

@app.template_filter('date')
def date_filter(value, format='%Y-%m-%d'):
    """날짜 포맷팅 필터"""
    if value is None:
        return datetime.now().strftime(format)
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime(format)
        except:
            return value
    return value

# 모듈 초기화
db_path = os.path.join(parent_dir, 'membership.db')
db = DatabaseManager(db_path)
collector = DataCollector()
processor = DataProcessor()
analyzer = DataAnalyzer(db)
visualizer = DataVisualizer()

@app.route('/')
def index():
    """메인 대시보드"""
    stats = db.get_statistics()
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # 현재 월 분석
    monthly_analysis = analyzer.analyze_monthly_payment_rate(
        current_year, current_month
    )
    
    # 최근 납부 기록
    recent_payments = db.get_all_payments()[:10]
    
    # 납부 추이
    trend_data = analyzer.get_payment_trend(6)
    trend_chart = visualizer.prepare_monthly_trend_chart(trend_data)
    
    return render_template('dashboard.html',
                         stats=stats,
                         monthly_analysis=monthly_analysis,
                         recent_payments=recent_payments,
                         trend_chart=trend_chart)

@app.route('/members')
def members():
    """회원 관리 페이지"""
    all_members = db.get_all_members()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('members.html', members=all_members, today=today)

@app.route('/members/add', methods=['POST'])
def add_member():
    """회원 추가"""
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    join_date = request.form.get('join_date', '')
    
    # 데이터 수집
    member_data = collector.collect_member_data(name, phone, join_date)
    
    # 데이터 처리 및 검증
    is_valid, processed_data, errors = processor.process_member_data(member_data)
    
    if not is_valid:
        return jsonify({'success': False, 'errors': errors}), 400
    
    # 데이터 저장
    try:
        member_id = db.save_member(
            processed_data['name'],
            processed_data['phone'],
            processed_data['join_date']
        )
        return jsonify({'success': True, 'member_id': member_id})
    except Exception as e:
        return jsonify({'success': False, 'errors': [str(e)]}), 500

@app.route('/members/<int:member_id>/delete', methods=['POST'])
def delete_member(member_id):
    """회원 삭제"""
    try:
        success = db.delete_member(member_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '회원을 찾을 수 없습니다'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/payments')
def payments():
    """회비 납부 관리 페이지"""
    year = request.args.get('year', type=int) or datetime.now().year
    month = request.args.get('month', type=int) or datetime.now().month
    
    all_members = db.get_all_members()
    payments = db.get_all_payments(year=year, month=month)
    
    # 분석
    analysis = analyzer.analyze_monthly_payment_rate(year, month)
    unpaid_members = analyzer.get_unpaid_members(year, month)
    
    # 시각화
    payment_chart = visualizer.prepare_payment_rate_chart(analysis)
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('payments.html',
                         members=all_members,
                         payments=payments,
                         analysis=analysis,
                         unpaid_members=unpaid_members,
                         payment_chart=payment_chart,
                         selected_year=year,
                         selected_month=month,
                         today=today)

@app.route('/payments/add', methods=['POST'])
def add_payment():
    """회비 납부 추가"""
    member_id = request.form.get('member_id', type=int)
    amount = request.form.get('amount', type=float)
    payment_date = request.form.get('payment_date', '')
    month = request.form.get('month', type=int) or datetime.now().month
    year = request.form.get('year', type=int) or datetime.now().year
    
    if not member_id or not amount:
        return jsonify({'success': False, 'errors': ['필수 정보가 누락되었습니다']}), 400
    
    # 데이터 수집
    payment_data = collector.collect_payment_data(
        member_id, amount, payment_date, month, year
    )
    
    # 데이터 처리 및 검증
    is_valid, processed_data, errors = processor.process_payment_data(payment_data)
    
    if not is_valid:
        return jsonify({'success': False, 'errors': errors}), 400
    
    # 데이터 저장
    try:
        payment_id = db.save_payment(
            processed_data['member_id'],
            processed_data['amount'],
            processed_data['payment_date'],
            processed_data['month'],
            processed_data['year'],
            processed_data['status']
        )
        return jsonify({'success': True, 'payment_id': payment_id})
    except Exception as e:
        return jsonify({'success': False, 'errors': [str(e)]}), 500

@app.route('/analysis')
def analysis():
    """분석 페이지"""
    year = request.args.get('year', type=int) or datetime.now().year
    
    # 연간 분석
    yearly_summary = analyzer.analyze_yearly_summary(year)
    yearly_chart = visualizer.prepare_yearly_summary_chart(yearly_summary)
    
    # 상위 납부자
    top_payers = analyzer.get_top_payers(10)
    top_payers_chart = visualizer.prepare_top_payers_chart(top_payers)
    
    # 납부 추이
    trend_data = analyzer.get_payment_trend(12)
    trend_chart = visualizer.prepare_monthly_trend_chart(trend_data)
    
    return render_template('analysis.html',
                         yearly_summary=yearly_summary,
                         yearly_chart=yearly_chart,
                         top_payers=top_payers,
                         top_payers_chart=top_payers_chart,
                         trend_chart=trend_chart,
                         selected_year=year)

@app.route('/api/member/<int:member_id>/history')
def member_history(member_id):
    """회원 납부 이력 API"""
    history = analyzer.analyze_member_payment_history(member_id)
    if history:
        return jsonify(history)
    else:
        return jsonify({'error': '회원을 찾을 수 없습니다'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

