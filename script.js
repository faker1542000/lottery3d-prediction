// 模拟历史数据
let historyData = [];
let displayedCount = 10;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeData();
    loadLatestDraw();
    loadHistory();
    generatePrediction();
    analyzeNumbers();
    createFrequencyChart();
});

// 初始化数据
function initializeData() {
    // 生成模拟历史数据
    const today = new Date();
    for (let i = 0; i < 100; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        
        const period = `2024${String(100 - i).padStart(3, '0')}`;
        const numbers = [
            Math.floor(Math.random() * 10),
            Math.floor(Math.random() * 10),
            Math.floor(Math.random() * 10)
        ];
        
        historyData.push({
            period: period,
            date: formatDate(date),
            numbers: numbers,
            sum: numbers.reduce((a, b) => a + b, 0),
            span: Math.max(...numbers) - Math.min(...numbers),
            type: getNumberType(numbers)
        });
    }
}

// 格式化日期
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 判断号码类型
function getNumberType(numbers) {
    const uniqueNums = [...new Set(numbers)];
    
    if (uniqueNums.length === 1) {
        return '豹子';
    } else if (uniqueNums.length === 2) {
        return '对子';
    } else {
        const sorted = [...numbers].sort((a, b) => a - b);
        if (sorted[1] - sorted[0] === 1 && sorted[2] - sorted[1] === 1) {
            return '顺子';
        }
        return '组六';
    }
}

// 加载最新开奖
function loadLatestDraw() {
    if (historyData.length > 0) {
        const latest = historyData[0];
        document.getElementById('latestPeriod').textContent = latest.period;
        document.getElementById('latestDate').textContent = latest.date;
        document.getElementById('sumValue').textContent = latest.sum;
        document.getElementById('spanValue').textContent = latest.span;
        document.getElementById('typeValue').textContent = latest.type;
        
        const numbersHtml = latest.numbers.map(n => 
            `<span class="ball">${n}</span>`
        ).join('');
        document.getElementById('latestNumbers').innerHTML = numbersHtml;
    }
}

// 生成预测
function generatePrediction() {
    // 3D预测
    const predict3D = predictNumbers(3);
    const predict3DElement = document.getElementById('predict3D');
    predict3DElement.innerHTML = predict3D.map(n => 
        `<span class="predict-ball">${n}</span>`
    ).join('');
    
    // 5码预测
    const predict5Code = predictNumbers(5);
    const predict5CodeElement = document.getElementById('predict5Code');
    predict5CodeElement.innerHTML = predict5Code.map(n => 
        `<span class="predict-ball-small">${n}</span>`
    ).join('');
    
    // 置信度动画
    animateConfidence('confidence3D', 'confidence3DValue', 65, 85);
    animateConfidence('confidence5Code', 'confidence5CodeValue', 75, 90);
    
    // 显示动画效果
    const balls = document.querySelectorAll('.predict-ball, .predict-ball-small');
    balls.forEach((ball, index) => {
        ball.style.animation = 'none';
        setTimeout(() => {
            ball.style.animation = 'pulse 2s infinite';
        }, index * 100);
    });
}

// 预测号码算法
function predictNumbers(count) {
    const frequency = Array(10).fill(0);
    const recentData = historyData.slice(0, 30);
    
    // 频率分析
    recentData.forEach(item => {
        item.numbers.forEach(num => {
            frequency[num]++;
        });
    });
    
    // 加权随机选择
    const weights = frequency.map((freq, num) => ({
        number: num,
        weight: freq + Math.random() * 5
    }));
    
    weights.sort((a, b) => b.weight - a.weight);
    
    // 返回前count个号码
    return weights.slice(0, count).map(w => w.number).sort((a, b) => a - b);
}

// 置信度动画
function animateConfidence(barId, valueId, min, max) {
    const confidence = Math.floor(Math.random() * (max - min + 1)) + min;
    const bar = document.getElementById(barId);
    const value = document.getElementById(valueId);
    
    setTimeout(() => {
        bar.style.width = confidence + '%';
        value.textContent = confidence + '%';
    }, 300);
}

// 加载历史记录
function loadHistory() {
    const historyList = document.getElementById('historyList');
    const displayData = historyData.slice(0, displayedCount);
    
    historyList.innerHTML = displayData.map(item => {
        const typeClass = item.type === '豹子' ? 'baozi' : 
                         item.type === '对子' ? 'duizi' : 
                         item.type === '顺子' ? 'shunzi' : '';
        
        return `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-period">第 ${item.period} 期</span>
                    <span class="history-date">${item.date}</span>
                </div>
                <div class="history-numbers">
                    ${item.numbers.map(n => `<span class="history-ball">${n}</span>`).join('')}
                </div>
                <div class="history-tags">
                    <span class="tag">和值: ${item.sum}</span>
                    <span class="tag">跨度: ${item.span}</span>
                    <span class="tag ${typeClass}">${item.type}</span>
                </div>
            </div>
        `;
    }).join('');
}

// 搜索历史
function searchHistory() {
    const searchInput = document.getElementById('searchInput').value;
    const historyList = document.getElementById('historyList');
    
    if (!searchInput) {
        loadHistory();
        return;
    }
    
    const filtered = historyData.filter(item => 
        item.period.includes(searchInput)
    );
    
    historyList.innerHTML = filtered.map(item => {
        const typeClass = item.type === '豹子' ? 'baozi' : 
                         item.type === '对子' ? 'duizi' : 
                         item.type === '顺子' ? 'shunzi' : '';
        
        return `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-period">第 ${item.period} 期</span>
                    <span class="history-date">${item.date}</span>
                </div>
                <div class="history-numbers">
                    ${item.numbers.map(n => `<span class="history-ball">${n}</span>`).join('')}
                </div>
                <div class="history-tags">
                    <span class="tag">和值: ${item.sum}</span>
                    <span class="tag">跨度: ${item.span}</span>
                    <span class="tag ${typeClass}">${item.type}</span>
                </div>
            </div>
        `;
    }).join('');
}

// 加载更多
function loadMore() {
    displayedCount += 10;
    loadHistory();
}

// 分析热号冷号
function analyzeNumbers() {
    const frequency = Array(10).fill(0);
    const recentData = historyData.slice(0, 30);
    
    recentData.forEach(item => {
        item.numbers.forEach(num => {
            frequency[num]++;
        });
    });
    
    const sorted = frequency.map((freq, num) => ({num, freq}))
        .sort((a, b) => b.freq - a.freq);
    
    // 热号
    const hotNumbers = sorted.slice(0, 3);
    document.getElementById('hotNumbers').innerHTML = hotNumbers.map(item => 
        `<span class="number-tag hot">${item.num}</span>`
    ).join('');
    
    // 冷号
    const coldNumbers = sorted.slice(-3);
    document.getElementById('coldNumbers').innerHTML = coldNumbers.map(item => 
        `<span class="number-tag cold">${item.num}</span>`
    ).join('');
}

// 创建频率图表
function createFrequencyChart() {
    const frequency = Array(10).fill(0);
    const recentData = historyData.slice(0, 50);
    
    recentData.forEach(item => {
        item.numbers.forEach(num => {
            frequency[num]++;
        });
    });
    
    const maxFreq = Math.max(...frequency);
    const chartHtml = frequency.map((freq, num) => {
        const height = (freq / maxFreq) * 100;
        return `
            <div class="freq-bar" 
                 style="height: ${height}%"
                 data-num="${num}"
                 data-count="${freq}">
            </div>
        `;
    }).join('');
    
    document.getElementById('frequencyChart').innerHTML = chartHtml;
}

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
        
        // 更新活动链接
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        this.classList.add('active');
    });
});
