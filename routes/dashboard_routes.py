import logging
from quart import Blueprint, render_template_string, redirect, request, session, url_for

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)

# HTML Login Template
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAPTCHA Admin Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 450px;
            text-align: center;
        }
        .login-card h2 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .login-card p {
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #444;
            font-weight: 600;
            font-size: 0.9em;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
            outline: none;
        }
        .form-group input:focus {
            border-color: #667eea;
        }
        .error-message {
            background: #ffe3e3;
            color: #d63031;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.9em;
            font-weight: 500;
            border-left: 4px solid #d63031;
            text-align: left;
        }
        .login-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 14px;
            width: 100%;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 5px 15px rgba(118, 75, 162, 0.3);
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(118, 75, 162, 0.4);
        }
        .login-btn:active {
            transform: translateY(0);
        }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>🚀 Admin Portal</h2>
        <p>Sign in to access the CAPTCHA Dashboard</p>

        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required placeholder="Enter admin username" autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter admin password" autocomplete="current-password">
            </div>
            <button type="submit" class="login-btn">Log In</button>
        </form>
    </div>
</body>
</html>
'''

# HTML Dashboard Template
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAPTCHA API Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            padding: 15px 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar-brand {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }

        .navbar-user {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .user-info {
            color: #555;
            font-size: 0.95em;
        }

        .logout-btn {
            background: #ff7675;
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 0.9em;
            transition: background 0.2s ease, transform 0.2s;
        }

        .logout-btn:hover {
            background: #d63031;
            transform: scale(1.05);
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .section-title {
            color: white;
            font-size: 1.8em;
            margin: 30px 0 20px 0;
            font-weight: bold;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        /* Time Period Selector */
        .time-period-selector {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .period-btn {
            background: white;
            border: 2px solid #e0e0e0;
            color: #666;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .period-btn:hover {
            border-color: #667eea;
            color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }

        .period-btn.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-color: transparent;
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .stat-card.period-1h { border-left-color: #e91e63; }
        .stat-card.period-1h::before { background: linear-gradient(90deg, #e91e63, #f06292); }
        .stat-card.period-2h { border-left-color: #9c27b0; }
        .stat-card.period-2h::before { background: linear-gradient(90deg, #9c27b0, #ba68c8); }
        .stat-card.period-6h { border-left-color: #3f51b5; }
        .stat-card.period-6h::before { background: linear-gradient(90deg, #3f51b5, #7986cb); }
        .stat-card.period-12h { border-left-color: #2196f3; }
        .stat-card.period-12h::before { background: linear-gradient(90deg, #2196f3, #64b5f6); }
        .stat-card.period-24h { border-left-color: #4caf50; }
        .stat-card.period-24h::before { background: linear-gradient(90deg, #4caf50, #81c784); }
        
        .stat-label {
            color: #999;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .stat-subtext {
            color: #666;
            font-size: 0.9em;
        }

        .accuracy-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 10px;
        }

        .accuracy-high { background: #e8f5e9; color: #2e7d32; }
        .accuracy-medium { background: #fff3e0; color: #f57f17; }
        .accuracy-low { background: #ffebee; color: #c62828; }

        /* Recent CAPTCHAs */
        .recent-captchas-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
            margin-bottom: 20px;
            padding: 25px;
        }

        .captchas-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        .captchas-table th, .captchas-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            font-size: 0.95em;
        }

        .captchas-table th {
            background-color: #f8f9fa;
            color: #333;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }

        .captchas-table tbody tr:hover {
            background-color: #fcfcfc;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
            display: inline-block;
        }

        .badge.correct {
            background-color: #e2fbe8;
            color: #2e7d32;
        }

        .badge.incorrect {
            background-color: #ffebee;
            color: #c62828;
        }

        .badge.pending {
            background-color: #fff8e1;
            color: #f57f17;
        }

        /* System Stats */
        .system-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .system-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .system-card h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.2em;
        }
        
        .progress-bar {
            width: 100%;
            height: 25px;
            background: #eee;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 15px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.85em;
            font-weight: bold;
            transition: width 0.3s ease;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #eee;
        }
        
        .stat-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        
        .stat-item label {
            color: #666;
            font-weight: 500;
        }
        
        .stat-item value {
            color: #333;
            font-weight: bold;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: transform 0.2s ease;
            margin-top: 20px;
            width: 100%;
        }
        
        .refresh-btn:hover {
            transform: scale(1.02);
        }
        
        .refresh-btn:active {
            transform: scale(0.98);
        }
        
        .timestamp {
            color: #999;
            font-size: 0.85em;
            text-align: center;
            margin-top: 15px;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .stat-value {
                font-size: 2em;
            }
            
            .time-period-selector {
                padding: 15px;
            }
            
            .period-btn {
                padding: 8px 16px;
                font-size: 0.85em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sticky Modern Header/Navbar -->
        <nav class="navbar">
            <div class="navbar-brand">🚀 CAPTCHA Control Panel</div>
            <div class="navbar-user">
                <span class="user-info">Welcome, <strong>Admin</strong> 👤</span>
                <a href="/logout" class="logout-btn">Logout 🚪</a>
            </div>
        </nav>

        <div class="header">
            <h1>🚀 CAPTCHA API Dashboard</h1>
            <p>Real-time statistics and system monitoring</p>
        </div>

        <div class="section-title">📊 CAPTCHA Statistics by Time Period</div>
        
        <div class="stats-grid" id="stats-grid">
            <!-- Cards will be populated by JavaScript -->
        </div>
        
        <div class="section-title">📋 Recent CAPTCHAs Log</div>
        
        <div class="recent-captchas-card">
            <table class="captchas-table">
                <thead>
                    <tr>
                        <th>CAPTCHA ID</th>
                        <th>Generated At</th>
                        <th>Verified At</th>
                        <th>Answer</th>
                        <th>User Answer</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="recent-captchas-body">
                    <tr>
                        <td colspan="6" style="text-align: center; color: #999; padding: 20px;">Loading recent CAPTCHAs...</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="section-title">⚙️ System Resources</div>
        
        <div class="system-stats">
            <div class="system-card">
                <h3>🖥️ CPU Status</h3>
                <div class="stat-item">
                    <label>Current Usage</label>
                    <value id="cpu-percent">-</value>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 0%">
                        <span id="cpu-progress-text">0%</span>
                    </div>
                </div>
                <div class="stat-item">
                    <label>Cores</label>
                    <value id="cpu-cores">-</value>
                </div>
            </div>
            
            <div class="system-card">
                <h3>💾 Memory Status</h3>
                <div class="stat-item">
                    <label>Usage</label>
                    <value id="memory-percent">-</value>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" style="width: 0%">
                        <span id="memory-progress-text">0%</span>
                    </div>
                </div>
                <div class="stat-item">
                    <label>Used / Total</label>
                    <value id="memory-used">-</value>
                </div>
                <div class="stat-item">
                    <label>Available</label>
                    <value id="memory-available">-</value>
                </div>
            </div>
            
            <div class="system-card">
                <h3>💿 Disk Storage</h3>
                <div class="stat-item">
                    <label>Usage</label>
                    <value id="disk-percent">-</value>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress" style="width: 0%">
                        <span id="disk-progress-text">0%</span>
                    </div>
                </div>
                <div class="stat-item">
                    <label>Used / Total</label>
                    <value id="disk-used">-</value>
                </div>
                <div class="stat-item">
                    <label>Free Space</label>
                    <value id="disk-free">-</value>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        <div class="timestamp" id="last-update"></div>
    </div>
    
    <script>
        let currentPeriod = 1;
        let allTimeData = {};
        let globalStats = {};
        
        const periodColors = {
            1: { primary: '#e91e63', light: '#fce4ec' },
            2: { primary: '#9c27b0', light: '#f3e5f5' },
            6: { primary: '#3f51b5', light: '#e8eaf6' },
            12: { primary: '#2196f3', light: '#e3f2fd' },
            24: { primary: '#4caf50', light: '#e8f5e9' }
        };
        
        async function fetchData() {
            try {
                const [stats, systemStats, recentResponse, timeBasedResponse] = await Promise.all([
                    fetch('/api/stats').then(r => r.json()),
                    fetch('/api/system/stats').then(r => r.json()),
                    fetch('/api/admin/recent').then(r => r.json()).catch(() => ({ success: false })),
                    fetch('/api/stats/time-based').then(r => r.json())
                ]);
                
                globalStats = stats;
                updateSystemStats(systemStats);
                if (recentResponse && recentResponse.success) {
                    updateRecentCaptchas(recentResponse.data);
                }
                if (timeBasedResponse.success) {
                    allTimeData = timeBasedResponse.data;
                    updateTimeBasedStats();
                }
                updateTimestamp();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        function selectPeriod(hours) {
            currentPeriod = hours;
            document.querySelectorAll('.period-btn').forEach(btn => {
                btn.classList.toggle('active', parseInt(btn.dataset.period) === hours);
            });
            updateTimeBasedStats();
        }
        
        function updateTimeBasedStats() {
            const grid = document.getElementById('stats-grid');
            
            // Build overall stats cards
            let html = `
                <div class="stat-card" style="border-left-color: #607d8b;">
                    <div class="stat-label">Total Generated</div>
                    <div class="stat-value">${globalStats.total_generated?.toLocaleString() || '-'}</div>
                    <div class="stat-subtext">All time</div>
                </div>

                <div class="stat-card" style="border-left-color: #795548;">
                    <div class="stat-label">Total Verified</div>
                    <div class="stat-value">${globalStats.total_verified?.toLocaleString() || '-'}</div>
                    <div class="stat-subtext">All time</div>
                </div>

                <div class="stat-card" style="border-left-color: #ff9800;">
                    <div class="stat-label">Total Correct</div>
                    <div class="stat-value">${globalStats.total_correct?.toLocaleString() || '-'}</div>
                    <div class="stat-subtext">All time</div>
                </div>

                <div class="stat-card" style="border-left-color: #00bcd4;">
                    <div class="stat-label">Overall Accuracy</div>
                    <div class="stat-value">${globalStats.accuracy_rate?.toFixed(1) || '-'}%</div>
                    <div class="stat-subtext">Of verified challenges</div>
                </div>
            `;
            
            // Sort periods in descending order: 24h, 12h, 6h, 2h, 1h
            const desiredOrder = ["24h", "12h", "6h", "2h", "1h"];
            const sortedEntries = desiredOrder
                .filter(period => allTimeData[period])
                .map(period => [period, allTimeData[period]]);
            
            // Add period-specific cards in sorted order
            for (const [periodStr, periodData] of sortedEntries) {
                const periodHours = parseInt(periodStr);
                const accuracyClass = periodData.accuracy >= 80 ? 'accuracy-high' : (periodData.accuracy >= 50 ? 'accuracy-medium' : 'accuracy-low');
                const isActive = periodHours === currentPeriod;
                
                html += `
                    <div class="stat-card period-${periodStr} ${isActive ? 'active-period' : ''}" style="${isActive ? 'box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);' : ''}">
                        <div class="stat-label">Last ${periodStr.replace('h', '')} Hour${periodHours > 1 ? 's' : ''}</div>
                        <div class="stat-value">${periodData.verified.toLocaleString()}</div>
                        <div class="stat-subtext">Verified CAPTCHAs</div>
                        <div class="stat-subtext" style="color: #4caf50; margin-top: 8px; font-weight: 600;">
                            ✓ ${periodData.correct.toLocaleString()} Correct
                        </div>
                        <span class="accuracy-badge ${accuracyClass}">
                            ${periodData.accuracy.toFixed(1)}% Accuracy
                        </span>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
        }
        
        function updateSystemStats(stats) {
            // CPU
            document.getElementById('cpu-percent').textContent = stats.cpu_percent.toFixed(1) + '%';
            document.getElementById('cpu-cores').textContent = stats.cpu_count || 'Unknown';
            document.getElementById('cpu-progress').style.width = Math.min(stats.cpu_percent, 100) + '%';
            document.getElementById('cpu-progress-text').textContent = stats.cpu_percent.toFixed(0) + '%';
            
            // Memory
            document.getElementById('memory-percent').textContent = stats.memory_percent.toFixed(1) + '%';
            document.getElementById('memory-used').textContent = `${stats.memory_used_mb.toFixed(0)} MB / ${stats.memory_total_mb.toFixed(0)} MB`;
            document.getElementById('memory-available').textContent = stats.memory_available_mb.toFixed(0) + ' MB';
            document.getElementById('memory-progress').style.width = Math.min(stats.memory_percent, 100) + '%';
            document.getElementById('memory-progress-text').textContent = stats.memory_percent.toFixed(0) + '%';
            
            // Disk
            document.getElementById('disk-percent').textContent = stats.disk_percent.toFixed(1) + '%';
            document.getElementById('disk-used').textContent = `${stats.disk_used_gb.toFixed(1)} GB / ${stats.disk_total_gb.toFixed(1)} GB`;
            document.getElementById('disk-free').textContent = stats.disk_free_gb.toFixed(1) + ' GB';
            document.getElementById('disk-progress').style.width = Math.min(stats.disk_percent, 100) + '%';
            document.getElementById('disk-progress-text').textContent = stats.disk_percent.toFixed(0) + '%';
        }
        
        function updateRecentCaptchas(captchas) {
            const tbody = document.getElementById('recent-captchas-body');
            if (!captchas || captchas.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #999; padding: 20px;">No recent CAPTCHAs found</td></tr>`;
                return;
            }

            tbody.innerHTML = captchas.map(c => {
                const genDate = new Date(c.generated_at).toLocaleString();
                const verDate = c.verified_at ? new Date(c.verified_at).toLocaleString() : '-';
                const userAns = c.user_answer !== null && c.user_answer !== undefined ? c.user_answer : '-';

                let statusBadge = '';
                if (c.is_correct === true) {
                    statusBadge = '<span class="badge correct">Correct ✓</span>';
                } else if (c.is_correct === false) {
                    statusBadge = '<span class="badge incorrect">Incorrect ✗</span>';
                } else {
                    statusBadge = '<span class="badge pending">Pending</span>';
                }

                return `
                    <tr>
                        <td style="font-family: monospace; font-size: 0.85em; color: #555;">${c.captcha_id}</td>
                        <td>${genDate}</td>
                        <td>${verDate}</td>
                        <td style="font-weight: bold; color: #4CAF50;">${c.answer}</td>
                        <td style="font-weight: bold;">${userAns}</td>
                        <td>${statusBadge}</td>
                    </tr>
                `;
            }).join('');
        }
        
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('last-update').textContent = 'Last updated: ' + now.toLocaleString();
        }
        
        function refreshData() {
            fetchData();
        }
        
        // Auto refresh every 10 seconds
        setInterval(fetchData, 10000);
        
        // Initial load
        fetchData();
    </script>
</body>
</html>
'''

async def setup_dashboard_routes(app):
    @dashboard_bp.get("/dashboard")
    async def dashboard():
        """Serve the dashboard."""
        if not session.get("is_admin"):
            return redirect(url_for("dashboard.login"))
        return await render_template_string(DASHBOARD_HTML)

    @dashboard_bp.route("/login", methods=["GET", "POST"])
    async def login():
        """Handle admin login."""
        if session.get("is_admin"):
            return redirect(url_for("dashboard.dashboard"))

        error = None
        if request.method == "POST":
            form = await request.form
            username = form.get("username")
            password = form.get("password")

            from config.settings import ADMIN_USERNAME, ADMIN_PASSWORD
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session["is_admin"] = True
                return redirect(url_for("dashboard.dashboard"))
            else:
                error = "Invalid username or password"

        return await render_template_string(LOGIN_HTML, error=error)

    @dashboard_bp.get("/logout")
    async def logout():
        """Handle admin logout."""
        session.pop("is_admin", None)
        return redirect(url_for("dashboard.login"))
    
    app.register_blueprint(dashboard_bp)
