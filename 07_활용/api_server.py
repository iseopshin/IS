"""
회비 관리 API 서버
모바일 앱을 위한 RESTful API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
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
CORS(app)  # 모바일 앱에서 접근 가능하도록 CORS 허용
app.config['SECRET_KEY'] = 'membership-management-api-secret-key'

# 모듈 초기화
db_path = os.path.join(parent_dir, 'membership.db')
db = DatabaseManager(db_path)
collector = DataCollector()
processor = DataProcessor()
analyzer = DataAnalyzer(db)
visualizer = DataVisualizer()

# API 라우트

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'ok',
        'message': '회비 관리 API 서버가 정상 작동 중입니다.',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/members', methods=['GET'])
def get_members():
    """모든 회원 조회"""
    try:
        members = db.get_all_members()
        return jsonify({
            'success': True,
            'data': [dict(m) for m in members],
            'count': len(members)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members', methods=['POST'])
def create_member():
    """회원 추가"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        join_date = data.get('join_date', '')
        
        if not name or not phone:
            return jsonify({'success': False, 'error': '이름과 연락처는 필수입니다.'}), 400
        
        member_data = collector.collect_member_data(name, phone, join_date)
        is_valid, processed_data, errors = processor.process_member_data(member_data)
        
        if not is_valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        member_id = db.save_member(
            processed_data['name'],
            processed_data['phone'],
            processed_data['join_date']
        )
        
        return jsonify({
            'success': True,
            'message': '회원이 추가되었습니다.',
            'data': {'id': member_id}
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    """특정 회원 조회"""
    try:
        member = db.get_member(member_id)
        if member:
            return jsonify({'success': True, 'data': dict(member)})
        else:
            return jsonify({'success': False, 'error': '회원을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """회원 삭제"""
    try:
        success = db.delete_member(member_id)
        if success:
            return jsonify({'success': True, 'message': '회원이 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '회원을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/payments', methods=['GET'])
def get_payments():
    """회비 납부 기록 조회"""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        payments = db.get_all_payments(year=year, month=month)
        return jsonify({
            'success': True,
            'data': [dict(p) for p in payments],
            'count': len(payments)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/payments', methods=['POST'])
def create_payment():
    """회비 납부 추가"""
    try:
        data = request.get_json()
        member_id = data.get('member_id')
        amount = data.get('amount')
        payment_date = data.get('payment_date', '')
        month = data.get('month') or datetime.now().month
        year = data.get('year') or datetime.now().year
        
        if not member_id or not amount:
            return jsonify({'success': False, 'error': '회원 ID와 금액은 필수입니다.'}), 400
        
        payment_data = collector.collect_payment_data(
            member_id, amount, payment_date, month, year
        )
        is_valid, processed_data, errors = processor.process_payment_data(payment_data)
        
        if not is_valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        payment_id = db.save_payment(
            processed_data['member_id'],
            processed_data['amount'],
            processed_data['payment_date'],
            processed_data['month'],
            processed_data['year'],
            processed_data['status']
        )
        
        return jsonify({
            'success': True,
            'message': '회비 납부가 등록되었습니다.',
            'data': {'id': payment_id}
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """전체 통계"""
    try:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analysis/monthly', methods=['GET'])
def get_monthly_analysis():
    """월별 분석"""
    try:
        year = request.args.get('year', type=int) or datetime.now().year
        month = request.args.get('month', type=int) or datetime.now().month
        
        analysis = analyzer.analyze_monthly_payment_rate(year, month)
        unpaid_members = analyzer.get_unpaid_members(year, month)
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis,
                'unpaid_members': [dict(m) for m in unpaid_members]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analysis/yearly', methods=['GET'])
def get_yearly_analysis():
    """연간 분석"""
    try:
        year = request.args.get('year', type=int) or datetime.now().year
        yearly_summary = analyzer.analyze_yearly_summary(year)
        top_payers = analyzer.get_top_payers(10)
        
        return jsonify({
            'success': True,
            'data': {
                'yearly_summary': yearly_summary,
                'top_payers': top_payers
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>/history', methods=['GET'])
def get_member_history(member_id):
    """회원 납부 이력"""
    try:
        history = analyzer.analyze_member_payment_history(member_id)
        if history:
            return jsonify({'success': True, 'data': history})
        else:
            return jsonify({'success': False, 'error': '회원을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 프로덕션 환경에서는 gunicorn이나 uwsgi 사용 권장
    app.run(debug=True, host='0.0.0.0', port=5000)

