// Initialize Socket.IO connection
const socket = io();

// Format bytes to human-readable format
function formatBytes(bytes) {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let value = bytes;
    let unitIndex = 0;
    
    while (value >= 1024 && unitIndex < units.length - 1) {
        value /= 1024;
        unitIndex++;
    }
    
    return `${value.toFixed(2)} ${units[unitIndex]}`;
}

// Update metrics cards
function updateMetrics(metrics) {
    document.querySelector('#active-users .metric-value').textContent = metrics.active_users;
    document.querySelector('#total-download .metric-value').textContent = formatBytes(metrics.bandwidth_usage.download);
    document.querySelector('#total-upload .metric-value').textContent = formatBytes(metrics.bandwidth_usage.upload);
}

// Create and update network usage graph
function updateUsageGraph(data) {
    const trace1 = {
        x: data.map(d => d.timestamp),
        y: data.map(d => d.bytes_received),
        name: 'Download',
        type: 'scatter',
        fill: 'tozeroy',
        line: {color: '#00ff00'}
    };

    const trace2 = {
        x: data.map(d => d.timestamp),
        y: data.map(d => d.bytes_sent),
        name: 'Upload',
        type: 'scatter',
        fill: 'tozeroy',
        line: {color: '#ff4b4b'}
    };

    const layout = {
        template: 'plotly_dark',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {l: 50, r: 20, t: 40, b: 50},
        title: 'Network Usage Over Time',
        xaxis: {title: 'Time'},
        yaxis: {title: 'Bytes'}
    };

    Plotly.newPlot('usage-graph', [trace1, trace2], layout);
}

// Update active sessions table
function updateActiveSessions(sessions) {
    const tbody = document.querySelector('#active-sessions tbody');
    tbody.innerHTML = '';
    
    sessions.forEach(session => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${session.user}</td>
            <td>${new Date(session.timestamp).toLocaleString()}</td>
            <td>${formatBytes(session.bytes_received)}</td>
            <td>${formatBytes(session.bytes_sent)}</td>
        `;
        tbody.appendChild(row);
    });
}

// Socket.IO event handlers
socket.on('metrics_update', (data) => {
    updateMetrics(data);
});

// Initial data load
async function loadInitialData() {
    const [metricsResponse, sessionsResponse, historyResponse] = await Promise.all([
        fetch('/api/metrics'),
        fetch('/api/active_sessions'),
        fetch('/api/usage_history')
    ]);

    const metrics = await metricsResponse.json();
    const sessions = await sessionsResponse.json();
    const history = await historyResponse.json();

    updateMetrics(metrics);
    updateUsageGraph(history);
    updateActiveSessions(sessions);
}

// Load initial data when page loads
document.addEventListener('DOMContentLoaded', loadInitialData);
