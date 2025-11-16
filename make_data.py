# make_data.py
import csv

with open('large_file.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'value_a', 'value_b'])
    for i in range(5000000):
        writer.writerow([i, f'value_{i}', i * 10])
print(">>> 'large_file.csv' 파일 생성 완료! (500만 줄)")