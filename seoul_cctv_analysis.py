"""
서울시 CCTV 설치 현황 및 인구 분포 분석
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# 필요한 패키지 설치 안내
try:
    import xlrd
except ImportError:
    print("xlrd 모듈이 없습니다. 설치 중...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'xlrd'])
    import xlrd

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False

# data 출처: 서울시 공공데이터
# 1. 데이터 로드
print("데이터 로딩 중...")

# CCTV 파일 읽기
cctv_df = pd.read_csv(r'C:\Users\User\data\01. CCTV_in_Seoul.csv', encoding='utf-8')

# 인구 파일 읽기
population_df = pd.read_excel(r'C:\Users\User\data\01.population_in_Seoul.xls')

# 데이터 확인
print("\n=== CCTV 데이터 ===")
print(cctv_df.head())
print(f"\n컬럼명: {cctv_df.columns.tolist()}")

print("\n=== 인구 데이터 ===")
print(population_df.head())
print(f"\n컬럼명: {population_df.columns.tolist()}")

# 2. 데이터 전처리
# CCTV 데이터에서 구별 CCTV 수 집계
# (컬럼명은 실제 파일에 맞게 수정 필요)
if '구별' in cctv_df.columns:
    cctv_by_district = cctv_df.groupby('구별')['소계'].sum().reset_index()
    cctv_by_district.columns = ['구', 'CCTV수']
elif '자치구' in cctv_df.columns:
    cctv_by_district = cctv_df.groupby('자치구')['소계'].sum().reset_index()
    cctv_by_district.columns = ['구', 'CCTV수']
else:
    # 첫 번째 컬럼이 구명, 마지막 컬럼이 합계라고 가정
    cctv_by_district = cctv_df.iloc[:, [0, -1]].copy()
    cctv_by_district.columns = ['구', 'CCTV수']
    cctv_by_district = cctv_by_district.groupby('구')['CCTV수'].sum().reset_index()

# 인구 데이터 전처리
# (컬럼명은 실제 파일에 맞게 수정 필요)
if '구별' in population_df.columns:
    population_clean = population_df[['구별', '인구수', '고령자', '외국인']].copy()
    population_clean.columns = ['구', '인구수', '고령자', '외국인']
elif '자치구' in population_df.columns:
    population_clean = population_df[['자치구', '인구수', '고령자', '외국인']].copy()
    population_clean.columns = ['구', '인구수', '고령자', '외국인']
else:
    # 첫 번째 컬럼이 구명이라고 가정
    population_clean = population_df.iloc[:, [0]].copy()
    population_clean.columns = ['구']
    # 인구수, 고령자, 외국인 컬럼 찾기
    for col in population_df.columns:
        if '인구' in str(col) and '수' in str(col):
            population_clean['인구수'] = population_df[col]
        elif '고령' in str(col):
            population_clean['고령자'] = population_df[col]
        elif '외국' in str(col):
            population_clean['외국인'] = population_df[col]

# 숫자형 변환
population_clean['인구수'] = pd.to_numeric(population_clean['인구수'], errors='coerce')
population_clean['고령자'] = pd.to_numeric(population_clean['고령자'], errors='coerce')
population_clean['외국인'] = pd.to_numeric(population_clean['외국인'], errors='coerce')

# 3. 데이터 병합
merged_df = pd.merge(cctv_by_district, population_clean, on='구', how='outer')
merged_df = merged_df.dropna(subset=['CCTV수', '인구수'])

# 4. 분석 지표 계산
merged_df['인구대비CCTV비율'] = (merged_df['CCTV수'] / merged_df['인구수']) * 1000  # 1000명당 CCTV 수
merged_df['고령자대비CCTV비율'] = (merged_df['CCTV수'] / merged_df['고령자']) * 100  # 고령자 100명당 CCTV 수
merged_df['외국인대비CCTV비율'] = (merged_df['CCTV수'] / merged_df['외국인']) * 100  # 외국인 100명당 CCTV 수

# 순위 추가
merged_df['인구대비CCTV순위'] = merged_df['인구대비CCTV비율'].rank(ascending=False, method='min').astype(int)

# 평균 계산
avg_cctv_per_1000 = merged_df['인구대비CCTV비율'].mean()
merged_df['평균대비차이'] = merged_df['인구대비CCTV비율'] - avg_cctv_per_1000

print("\n=== 분석 결과 ===")
print(f"\n인구 1000명당 CCTV 평균: {avg_cctv_per_1000:.2f}대")

# 5. 시각화
fig = plt.figure(figsize=(20, 15))

# 5-1. 구별 CCTV 수
ax1 = plt.subplot(3, 3, 1)
sorted_cctv = merged_df.sort_values('CCTV수', ascending=True)
ax1.barh(sorted_cctv['구'], sorted_cctv['CCTV수'], color='steelblue')
ax1.set_xlabel('CCTV 수')
ax1.set_title('구별 CCTV 설치 수', fontsize=12, fontweight='bold')
plt.tight_layout()

# 5-2. 인구대비 CCTV 비율 (순위)
ax2 = plt.subplot(3, 3, 2)
sorted_ratio = merged_df.sort_values('인구대비CCTV비율', ascending=True)
ax2.barh(sorted_ratio['구'], sorted_ratio['인구대비CCTV비율'], color='coral')
ax2.axvline(avg_cctv_per_1000, color='red', linestyle='--', linewidth=2, label=f'평균: {avg_cctv_per_1000:.2f}')
ax2.set_xlabel('1000명당 CCTV 수')
ax2.set_title('인구대비 CCTV 비율', fontsize=12, fontweight='bold')
ax2.legend()
plt.tight_layout()

# 5-3. 인구대비 CCTV 순위
ax3 = plt.subplot(3, 3, 3)
top10 = merged_df.nlargest(10, '인구대비CCTV비율')
ax3.barh(range(len(top10)), top10['인구대비CCTV비율'], color='green')
ax3.set_yticks(range(len(top10)))
ax3.set_yticklabels(top10['구'])
ax3.set_xlabel('1000명당 CCTV 수')
ax3.set_title('인구대비 CCTV 비율 TOP 10', fontsize=12, fontweight='bold')
plt.tight_layout()

# 5-4. 평균 대비 차이 (부족한 구 확인)
ax4 = plt.subplot(3, 3, 4)
deficit = merged_df[merged_df['평균대비차이'] < 0].sort_values('평균대비차이')
ax4.barh(deficit['구'], deficit['평균대비차이'], color='red')
ax4.set_xlabel('평균 대비 차이')
ax4.set_title('CCTV 부족 구 (평균 이하)', fontsize=12, fontweight='bold')
plt.tight_layout()

# 5-5. 고령자 대비 CCTV 비율
ax5 = plt.subplot(3, 3, 5)
sorted_elderly = merged_df.sort_values('고령자대비CCTV비율', ascending=True)
ax5.barh(sorted_elderly['구'], sorted_elderly['고령자대비CCTV비율'], color='orange')
ax5.set_xlabel('고령자 100명당 CCTV 수')
ax5.set_title('고령자 대비 CCTV 비율', fontsize=12, fontweight='bold')
plt.tight_layout()

# 5-6. 외국인 대비 CCTV 비율
ax6 = plt.subplot(3, 3, 6)
sorted_foreign = merged_df.sort_values('외국인대비CCTV비율', ascending=True)
ax6.barh(sorted_foreign['구'], sorted_foreign['외국인대비CCTV비율'], color='purple')
ax6.set_xlabel('외국인 100명당 CCTV 수')
ax6.set_title('외국인 대비 CCTV 비율', fontsize=12, fontweight='bold')
plt.tight_layout()

# 5-7. 인구수 vs CCTV 수 산점도
ax7 = plt.subplot(3, 3, 7)
ax7.scatter(merged_df['인구수'], merged_df['CCTV수'], alpha=0.6, s=100, color='blue')
ax7.set_xlabel('인구수')
ax7.set_ylabel('CCTV 수')
ax7.set_title('인구수 vs CCTV 수', fontsize=12, fontweight='bold')
ax7.grid(True, alpha=0.3)
plt.tight_layout()

# 5-8. 종합 순위표
ax8 = plt.subplot(3, 3, 8)
ax8.axis('tight')
ax8.axis('off')
top_rank = merged_df.nlargest(10, '인구대비CCTV비율')[['구', '인구대비CCTV비율', '인구대비CCTV순위']]
table = ax8.table(cellText=top_rank.values, 
                  colLabels=['구', '1000명당 CCTV', '순위'],
                  cellLoc='center',
                  loc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)
ax8.set_title('인구대비 CCTV 비율 TOP 10', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()

# 5-9. 부족 구 상세 정보
ax9 = plt.subplot(3, 3, 9)
ax9.axis('tight')
ax9.axis('off')
deficit_info = merged_df[merged_df['평균대비차이'] < 0].nsmallest(10, '평균대비차이')[['구', '인구대비CCTV비율', '평균대비차이']]
deficit_info['평균대비차이'] = deficit_info['평균대비차이'].round(2)
table2 = ax9.table(cellText=deficit_info.values,
                   colLabels=['구', '1000명당 CCTV', '평균 대비 차이'],
                   cellLoc='center',
                   loc='center')
table2.auto_set_font_size(False)
table2.set_fontsize(9)
table2.scale(1, 2)
ax9.set_title('CCTV 부족 구 상세', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()

plt.tight_layout()
plt.savefig('seoul_cctv_analysis.png', dpi=300, bbox_inches='tight')
print("\n그래프 저장 완료: seoul_cctv_analysis.png")

# 6. 결과 요약 출력
print("\n" + "="*60)
print("분석 결과 요약")
print("="*60)
print(f"\n1. 인구 1000명당 CCTV 평균: {avg_cctv_per_1000:.2f}대")
print(f"\n2. 인구대비 CCTV 비율 TOP 5:")
top5 = merged_df.nlargest(5, '인구대비CCTV비율')
for idx, row in top5.iterrows():
    print(f"   {row['인구대비CCTV순위']}위: {row['구']} - {row['인구대비CCTV비율']:.2f}대/1000명")

print(f"\n3. CCTV 부족 구 (평균 이하):")
deficit_list = merged_df[merged_df['평균대비차이'] < 0].nsmallest(5, '평균대비차이')
for idx, row in deficit_list.iterrows():
    print(f"   {row['구']} - 평균 대비 {abs(row['평균대비차이']):.2f}대 부족")

print(f"\n4. 고령자 대비 CCTV 비율 TOP 3:")
top_elderly = merged_df.nlargest(3, '고령자대비CCTV비율')
for idx, row in top_elderly.iterrows():
    print(f"   {row['구']} - {row['고령자대비CCTV비율']:.2f}대/고령자 100명")

print(f"\n5. 외국인 대비 CCTV 비율 TOP 3:")
top_foreign = merged_df.nlargest(3, '외국인대비CCTV비율')
for idx, row in top_foreign.iterrows():
    print(f"   {row['구']} - {row['외국인대비CCTV비율']:.2f}대/외국인 100명")

# 7. 결과를 CSV로 저장
merged_df.to_csv('seoul_cctv_analysis_result.csv', index=False, encoding='utf-8-sig')
print("\n분석 결과 CSV 저장 완료: seoul_cctv_analysis_result.csv")

plt.show()

