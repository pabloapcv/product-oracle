// Winner Engine Web Interface JavaScript

// API Base URL
const API_BASE = '';

// State
let currentWeek = null;
let reports = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadReports();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('refresh-btn').addEventListener('click', () => {
        loadStats();
        loadReports();
        if (currentWeek) {
            loadOpportunities(currentWeek);
        }
    });
    
    document.getElementById('week-select').addEventListener('change', (e) => {
        if (e.target.value) {
            loadOpportunities(e.target.value);
        }
    });
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        
        document.getElementById('entity-count').textContent = data.entities || 0;
        document.getElementById('amazon-count').textContent = data.amazon_listings || 0;
        document.getElementById('tiktok-count').textContent = data.tiktok_metrics || 0;
        document.getElementById('latest-report').textContent = data.latest_report || 'None';
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadReports() {
    try {
        const response = await fetch(`${API_BASE}/api/reports`);
        const reportsData = await response.json();
        reports = reportsData;
        
        const reportsList = document.getElementById('reports-list');
        const weekSelect = document.getElementById('week-select');
        
        // Clear existing
        reportsList.innerHTML = '';
        weekSelect.innerHTML = '<option value="">Select Week...</option>';
        
        if (reportsData.length === 0) {
            reportsList.innerHTML = '<div class="empty-state">No reports available</div>';
            return;
        }
        
        // Populate reports list
        reportsData.forEach((report, index) => {
            // Sidebar list
            const reportItem = document.createElement('div');
            reportItem.className = 'report-item';
            if (index === 0) {
                reportItem.classList.add('active');
                currentWeek = report.week_start;
                loadOpportunities(report.week_start);
            }
            reportItem.innerHTML = `
                <div class="week">Week of ${report.week_start}</div>
                <div class="count">${report.opportunity_count} opportunities</div>
            `;
            reportItem.addEventListener('click', () => {
                document.querySelectorAll('.report-item').forEach(item => {
                    item.classList.remove('active');
                });
                reportItem.classList.add('active');
                loadOpportunities(report.week_start);
            });
            reportsList.appendChild(reportItem);
            
            // Dropdown select
            const option = document.createElement('option');
            option.value = report.week_start;
            option.textContent = `Week of ${report.week_start} (${report.opportunity_count} opportunities)`;
            weekSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading reports:', error);
        document.getElementById('reports-list').innerHTML = 
            '<div class="empty-state">Error loading reports</div>';
    }
}

async function loadOpportunities(weekStart) {
    currentWeek = weekStart;
    document.getElementById('content-title').textContent = `Opportunities - Week of ${weekStart}`;
    
    const container = document.getElementById('opportunities-container');
    container.innerHTML = '<div class="loading">Loading opportunities...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/opportunities/${weekStart}`);
        const data = await response.json();
        
        if (data.opportunities.length === 0) {
            container.innerHTML = '<div class="empty-state">No opportunities found for this week</div>';
            return;
        }
        
        container.innerHTML = '';
        
        data.opportunities.forEach((opp, index) => {
            const card = createOpportunityCard(opp, index + 1);
            container.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading opportunities:', error);
        container.innerHTML = '<div class="empty-state">Error loading opportunities</div>';
    }
}

function createOpportunityCard(opp, rank) {
    const card = document.createElement('div');
    card.className = 'opportunity-card';
    
    const probPercent = (opp.score_winner_prob * 100).toFixed(1);
    const probColor = opp.score_winner_prob > 0.5 ? '#28a745' : 
                     opp.score_winner_prob > 0.3 ? '#ffc107' : '#dc3545';
    
    card.innerHTML = `
        <div class="opportunity-header">
            <div>
                <div class="opportunity-title">${opp.canonical_name}</div>
                <div class="category-badge">${opp.category_primary || 'General'}</div>
            </div>
            <div class="opportunity-rank">#${rank}</div>
        </div>
        
        <div class="winner-probability" style="color: ${probColor}">
            ${probPercent}% Winner Probability
        </div>
        
        <div class="score-grid">
            <div class="score-item">
                <div class="score-label">Demand</div>
                <div class="score-value">${opp.score_demand.toFixed(1)}</div>
            </div>
            <div class="score-item">
                <div class="score-label">Competition</div>
                <div class="score-value">${opp.score_competition.toFixed(1)}</div>
            </div>
            <div class="score-item">
                <div class="score-label">Margin</div>
                <div class="score-value">${opp.score_margin.toFixed(1)}</div>
            </div>
            <div class="score-item">
                <div class="score-label">Risk</div>
                <div class="score-value">${opp.score_risk.toFixed(1)}</div>
            </div>
        </div>
        
        ${opp.innovation_angles && opp.innovation_angles.length > 0 ? `
        <div class="innovation-section">
            <h4>Innovation Angles</h4>
            <ul class="innovation-list">
                ${opp.innovation_angles.map(angle => `<li>${angle}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
        
        ${opp.experiment_plan ? `
        <div class="experiment-plan">
            <strong>Experiment Plan:</strong> ${opp.experiment_plan}
        </div>
        ` : ''}
    `;
    
    return card;
}

