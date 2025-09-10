import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import os
import time

def get_current_period():
    """计算当前期号（2025年第242期）"""
    # 福彩3D从2025年1月1日开始，每天一期
    year = 2025
    start_date = datetime(2025, 1, 1)
    today = datetime.now()
    days_passed = (today - start_date).days
    current_period = f"{year}{str(days_passed + 1).zfill(3)}"
    return current_period

def scrape_from_official():
    """从中国福利彩票官方数据接口获取"""
    all_data = []
    
    try:
        print("尝试从官方接口获取数据...")
        
        # 获取最近的期号
        current_year = 2025
        current_day = datetime.now().timetuple().tm_yday  # 今年的第几天
        
        # 尝试获取最近50期数据
        for i in range(50):
            period_day = current_day - i
            if period_day <= 0:
                break
                
            period = f"{current_year}{str(period_day).zfill(3)}"
            
            # 这里使用多个备选API
            # API 1: 彩经网
            try:
                url = f"https://www.cjcp.com.cn/ajax/lottery/draw-lottery-result.html?lotteryId=10&issue={period}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data and 'winNumber' in data:
                        numbers = [int(n) for n in data['winNumber'].split(',')]
                        if len(numbers) == 3:
                            date = datetime.now() - timedelta(days=i)
                            all_data.append(process_lottery_item(period, numbers, date.strftime('%Y-%m-%d')))
                            continue
            except:
                pass
            
            # API 2: 备用接口
            try:
                time.sleep(0.5)  # 避免请求过快
            except:
                pass
                
        print(f"从官方接口获取了 {len(all_data)} 条数据")
        
    except Exception as e:
        print(f"官方接口获取失败: {e}")
    
    return all_data

def scrape_from_500com():
    """从500彩票网获取数据（改进版）"""
    all_data = []
    
    try:
        print("尝试从500彩票网获取数据...")
        
        # 使用直接的数据API
        url = "https://datachart.500.com/sd/history/newinc/history.php"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            response.encoding = 'gb2312'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找数据表格 - 使用更精确的选择器
            table = soup.find('table', {'id': 'tdata'})
            if not table:
                # 备用选择器
                table = soup.find('table', class_='t_tr1')
            
            if table:
                # 获取所有数据行
                rows = table.find_all('tr')
                print(f"找到 {len(rows)} 行原始数据")
                
                for row in rows:
                    # 跳过表头
                    if 'class' in row.attrs and 't_title' in row.attrs['class']:
                        continue
                    
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            # 第一列：期号
                            period_text = cells[0].get_text(strip=True)
                            # 提取数字期号
                            period_match = re.search(r'(\d{7})', period_text)
                            if not period_match:
                                continue
                            period = period_match.group(1)
                            
                            # 第2-4列：开奖号码
                            numbers = []
                            for i in range(1, 4):
                                cell_text = cells[i].get_text(strip=True)
                                # 提取数字
                                num_match = re.search(r'(\d)', cell_text)
                                if num_match:
                                    numbers.append(int(num_match.group(1)))
                            
                            if len(numbers) == 3:
                                # 根据期号计算日期
                                year = int(period[:4])
                                day_of_year = int(period[4:])
                                date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                                date_str = date.strftime('%Y-%m-%d')
                                
                                all_data.append(process_lottery_item(period, numbers, date_str))
                                
                        except Exception as e:
                            continue
                
                print(f"成功解析 {len(all_data)} 条数据")
                
    except Exception as e:
        print(f"500彩票网获取失败: {e}")
    
    return all_data

def scrape_from_cwl():
    """从中国福彩网获取数据"""
    all_data = []
    
    try:
        print("尝试从中国福彩网获取数据...")
        
        # 中国福彩网的API
        base_url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://www.cwl.gov.cn/ygkj/wqkjgg/fc3d/',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        }
        
        # 获取最近的数据
        params = {
            'name': '3D',
            'issueCount': 50,  # 获取50期
            'issueStart': '',
            'issueEnd': '',
            'dayStart': '',
            'dayEnd': ''
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and data['result']:
                for item in data['result']:
                    if 'code' in item and 'red' in item:
                        period = item['code']
                        # 将红球字符串转换为数字列表
                        numbers = [int(n) for n in item['red'].split(',')]
                        date = item.get('date', datetime.now().strftime('%Y-%m-%d'))
                        
                        if len(numbers) == 3:
                            all_data.append(process_lottery_item(period, numbers, date))
                
                print(f"从中国福彩网获取了 {len(all_data)} 条数据")
                
    except Exception as e:
        print(f"中国福彩网获取失败: {e}")
    
    return all_data

def scrape_from_78500():
    """从78500彩票网获取数据"""
    all_data = []
    
    try:
        print("尝试从78500彩票网获取数据...")
        
        url = "https://www.78500.cn/fc3d/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找历史开奖表格
            table = soup.find('table', class_='history-table')
            if not table:
                table = soup.find('table', id='history')
            
            if table:
                rows = table.find_all('tr')[1:]  # 跳过表头
                
                for row in rows[:50]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        period = cells[0].get_text(strip=True)
                        numbers_text = cells[1].get_text(strip=True)
                        
                        # 提取数字
                        numbers = re.findall(r'\d', numbers_text)
                        if len(numbers) >= 3:
                            numbers = [int(n) for n in numbers[:3]]
                            
                            # 计算日期
                            year = int(period[:4]) if len(period) >= 4 else 2025
                            day_of_year = int(period[4:]) if len(period) >= 7 else 1
                            date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                            date_str = date.strftime('%Y-%m-%d')
                            
                            all_data.append(process_lottery_item(period, numbers, date_str))
                
                print(f"从78500获取了 {len(all_data)} 条数据")
                
    except Exception as e:
        print(f"78500彩票网获取失败: {e}")
    
    return all_data

def process_lottery_item(period, numbers, date=None):
    """处理单条彩票数据"""
    sum_val = sum(numbers)
    span_val = max(numbers) - min(numbers)
    
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
    
    return {
        'period': period,
        'numbers': numbers,
        'date': date or datetime.now().strftime('%Y-%m-%d'),
        'sum': sum_val,
        'span': span_val,
        'type': type_name
    }

def merge_and_sort_data(all_sources_data):
    """合并多个数据源的数据并去重排序"""
    merged = {}
    
    for data_list in all_sources_data:
        for item in data_list:
            period = item['period']
            if period not in merged:
                merged[period] = item
    
    # 按期号降序排序（最新的在前）
    sorted_data = sorted(merged.values(), key=lambda x: x['period'], reverse=True)
    
    return sorted_data[:50]  # 返回最近50期

def save_data(data):
    """保存数据到JSON文件"""
    os.makedirs('data', exist_ok=True)
    
    # 保存完整数据
    file_path = 'data/lottery_data.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'success': True,
            'updateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到 {file_path}")
    
    # 保存最新一期
    if data:
        latest_path = 'data/latest.json'
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump({
                'success': True,
                'updateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'latest': data[0]
            }, f, ensure_ascii=False, indent=2)
        print(f"最新数据已保存到 {latest_path}")

def main():
    """主函数 - 从多个源获取数据"""
    print("=" * 60)
    print(f"开始执行爬虫程序 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_sources_data = []
    
    # 尝试多个数据源
    sources = [
        ('500彩票网', scrape_from_500com),
        ('中国福彩网', scrape_from_cwl),
        ('78500彩票网', scrape_from_78500),
        ('官方接口', scrape_from_official),
    ]
    
    for source_name, scraper_func in sources:
        print(f"\n正在尝试 {source_name}...")
        try:
            data = scraper_func()
            if data:
                all_sources_data.append(data)
                print(f"✅ {source_name} 获取成功: {len(data)} 条")
            else:
                print(f"❌ {source_name} 未获取到数据")
        except Exception as e:
            print(f"❌ {source_name} 出错: {e}")
    
    # 合并所有数据
    if all_sources_data:
        final_data = merge_and_sort_data(all_sources_data)
        if final_data:
            save_data(final_data)
            print(f"\n✅ 最终获取 {len(final_data)} 条有效数据")
            print(f"最新期号: {final_data[0]['period']}")
            print(f"最新开奖: {final_data[0]['numbers']}")
            return True
    
    print("\n❌ 所有数据源都失败了")
    
    # 如果全部失败，创建一个包含当前期号的基础数据
    current_period = get_current_period()
    basic_data = [{
        'period': current_period,
        'numbers': [0, 0, 0],
        'date': datetime.now().strftime('%Y-%m-%d'),
        'sum': 0,
        'span': 0,
        'type': '豹子',
        'note': '数据获取失败，请稍后重试'
    }]
    save_data(basic_data)
    
    return False

if __name__ == '__main__':
    success = main()
    print("=" * 60)
    print("程序执行完成")
    exit(0 if success else 1)
