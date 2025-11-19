"""
데이터 시각화 모듈
차트 및 그래프 생성 기능
"""

from typing import Dict, List
import json

class DataVisualizer:
    """데이터 시각화 클래스"""
    
    @staticmethod
    def prepare_payment_rate_chart(analysis_data: Dict) -> Dict:
        """
        납부율 차트 데이터 준비
        
        Returns:
            Chart.js 형식의 데이터
        """
        return {
            'type': 'doughnut',
            'data': {
                'labels': ['납부', '미납'],
                'datasets': [{
                    'data': [
                        analysis_data['paid_members'],
                        analysis_data['unpaid_members']
                    ],
                    'backgroundColor': ['#4CAF50', '#F44336'],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'bottom'
                    },
                    'title': {
                        'display': True,
                        'text': f"{analysis_data['year']}년 {analysis_data['month']}월 납부 현황"
                    }
                }
            }
        }
    
    @staticmethod
    def prepare_monthly_trend_chart(trend_data: List[Dict]) -> Dict:
        """
        월별 추이 차트 데이터 준비
        
        Returns:
            Chart.js 형식의 데이터
        """
        labels = [item['label'] for item in trend_data]
        amounts = [item['amount'] for item in trend_data]
        counts = [item['count'] for item in trend_data]
        
        return {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [
                    {
                        'label': '납부 금액',
                        'data': amounts,
                        'borderColor': '#2196F3',
                        'backgroundColor': 'rgba(33, 150, 243, 0.1)',
                        'yAxisID': 'y',
                        'tension': 0.4
                    },
                    {
                        'label': '납부 건수',
                        'data': counts,
                        'borderColor': '#FF9800',
                        'backgroundColor': 'rgba(255, 152, 0, 0.1)',
                        'yAxisID': 'y1',
                        'tension': 0.4
                    }
                ]
            },
            'options': {
                'responsive': True,
                'interaction': {
                    'mode': 'index',
                    'intersect': False
                },
                'scales': {
                    'y': {
                        'type': 'linear',
                        'display': True,
                        'position': 'left',
                        'title': {
                            'display': True,
                            'text': '금액 (원)'
                        }
                    },
                    'y1': {
                        'type': 'linear',
                        'display': True,
                        'position': 'right',
                        'title': {
                            'display': True,
                            'text': '건수'
                        },
                        'grid': {
                            'drawOnChartArea': False
                        }
                    }
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': '월별 납부 추이'
                    }
                }
            }
        }
    
    @staticmethod
    def prepare_yearly_summary_chart(yearly_data: Dict) -> Dict:
        """
        연간 요약 차트 데이터 준비
        
        Returns:
            Chart.js 형식의 데이터
        """
        monthly_summary = yearly_data['monthly_summary']
        labels = [f"{item['month']}월" for item in monthly_summary]
        amounts = [item['amount'] for item in monthly_summary]
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': '월별 납부 금액',
                    'data': amounts,
                    'backgroundColor': 'rgba(76, 175, 80, 0.6)',
                    'borderColor': 'rgba(76, 175, 80, 1)',
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': '금액 (원)'
                        }
                    }
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f"{yearly_data['year']}년 연간 납부 현황"
                    }
                }
            }
        }
    
    @staticmethod
    def prepare_top_payers_chart(top_payers: List[Dict], limit: int = 10) -> Dict:
        """
        상위 납부자 차트 데이터 준비
        
        Returns:
            Chart.js 형식의 데이터
        """
        top_payers = top_payers[:limit]
        labels = [item['member']['name'] for item in top_payers]
        amounts = [item['total_amount'] for item in top_payers]
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': '총 납부 금액',
                    'data': amounts,
                    'backgroundColor': 'rgba(33, 150, 243, 0.6)',
                    'borderColor': 'rgba(33, 150, 243, 1)',
                    'borderWidth': 1
                }]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'layout': {
                    'padding': 10
                },
                'scales': {
                    'x': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': '금액 (원)'
                        }
                    }
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': '상위 납부자'
                    }
                }
            }
        }
    
    @staticmethod
    def format_chart_data_for_html(chart_config: Dict) -> str:
        """
        차트 데이터를 HTML에서 사용할 수 있는 JSON 문자열로 변환
        
        Returns:
            JSON 문자열
        """
        return json.dumps(chart_config, ensure_ascii=False, indent=2)

