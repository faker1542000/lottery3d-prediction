import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def scrape_lottery_data():
    """爬取福彩3D数据"""
    all_data = []
    
    try:
        # 方案1：从500彩票网获取数据
        url = "https://datachart.500.com/sd/history/newinc/history.php"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.encoding = 'gb2312'  # 500彩票网使用GB2312编码
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找数据表格
        table = soup.find('table', {'id': 'tdata'})
        if table:
            rows = table.find_all('tr', {'class': 't_tr1'})
            for row in rows[:50]:  # 获取最近50期
                cells = row.find_all('td')
                if len(cells) >= 4:
                    period = cells[0].text.strip()
                    # 提取期号中的数字
                    period_match = re.search(r'\d+', period)
                    if period_match:
                        period = period_match.group()
                        
                        numbers = []
                        for i in range(1, 4):
                            num_div = cells[i].find('div', {'class': 'ball_1'})
                            if num_div:
                                numbers.append(int(num_div.text.strip()))
                        
                        if len(numbers) == 3:
                            sum_val = sum(numbers)
                            span_val = max(numbers) - min(numbers)
                            
                            # 判断类型
                            unique_nums = len(set(numbers))
                            if unique_nums == 1:
                                type_name = '豹子'
                            elif unique_nums == 2:
                                type_name = '对子'
                            else:
                                sorted_nums = sorted(numbers)
                                if sorted_nums[1] - sorted_nums[0] == 1 and sorted_nums[2] - sorted_nums[1] == 1:
                                    type_name = '顺子'
                                else:
                                    type_name = '组六'
                            
                            all_data.append({
                                'period': period,
                                'numbers': numbers,
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'sum': sum_val,
                                'span': span_val,
                                'type': type_name
                            })
    except Exception as e:
        print(f"500彩票网爬取失败: {e}")
    
    # 如果第一个方案失败，尝试备用方案
    if not all_data:
        try:
            # 备用方案：从其他网站获取
            print("尝试备用数据源...")
            # 这里可以添加其他数据源
        except Exception as e:
            print(f"备用方案失败: {e}")
    
    return all_data

def save_data(data):
    """保存数据到JSON文件"""
    # 保存到data目录
    with open('data/lottery_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'success': True,
            'updateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"成功保存 {len(data)} 条数据")
    
    # 同时生成一个最新数据文件
    if data:
        with open('data/latest.json', 'w', encoding='utf-8') as f:
            json.dump({
                'success': True,
                'updateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'latest': data[0]
            }, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    print("开始爬取数据...")
    data = scrape_lottery_data()
    
    if data:
        # 创建data目录（如果不存在）
        import os
        os.makedirs('data', exist_ok=True)
        
        save_data(data)
        print("数据爬取完成！")
    else:
        print("未能获取到数据")
