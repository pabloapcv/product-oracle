// Winner Engine Web Interface - Enhanced JavaScript
// Modern, smooth, and feature-rich

// ============================================
// Configuration & State
// ============================================

const API_BASE = '';
let currentWeek = null;
let reports = [];
let allOpportunities = [];
let filteredOpportunities = [];

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    // Load theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Initialize tooltips and animations
    setupAnimations();
}

function setupAnimations() {
    // Intersection Observer for fade-in animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });
    
    // Observe opportunity cards
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.opportunity-card').forEach(card => {
            observer.observe(card);
        });
    });
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    const refreshBtnHeader = document.getElementById('refresh-btn-header');
    
    [refreshBtn, refreshBtnHeader].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', handleRefresh);
        }
    });
    
    // Week select
    const weekSelect = document.getElementById('week-select');
    if (weekSelect) {
        weekSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                loadOpportunities(e.target.value);
            }
        });
    }
    
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Search reports
    const searchInput = document.getElementById('search-reports');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearchReports);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + R to refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        handleRefresh();
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('search-reports');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            handleSearchReports({ target: searchInput });
        }
    }
}

// ============================================
// Theme Management
// ============================================

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
    
    showToast(`Switched to ${newTheme} theme`, 'success');
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

// ============================================
// Data Loading
// ============================================

async function loadInitialData() {
    showLoading();
    try {
        await Promise.all([
            loadStats(),
            loadReports()
        ]);
    } catch (error) {
        console.error('Error loading initial data:', error);
        showToast('Error loading data. Please refresh.', 'error');
    } finally {
        hideLoading();
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        
        const data = await response.json();
        
        // Animate stat values
        animateValue('entity-count', 0, data.entities || 0, 1000);
        animateValue('amazon-count', 0, data.amazon_listings || 0, 1000);
        animateValue('tiktok-count', 0, data.tiktok_metrics || 0, 1000);
        
        const latestReportEl = document.getElementById('latest-report');
        if (latestReportEl) {
            latestReportEl.innerHTML = data.latest_report || '<span class="skeleton-text">None</span>';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showToast('Error loading statistics', 'error');
    }
}

function animateValue(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.innerHTML = formatNumber(end);
            clearInterval(timer);
        } else {
            element.innerHTML = formatNumber(Math.floor(current));
        }
    }, 16);
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

async function loadReports() {
    try {
        const response = await fetch(`${API_BASE}/api/reports`);
        if (!response.ok) throw new Error('Failed to fetch reports');
        
        const reportsData = await response.json();
        reports = reportsData;
        
        const reportsList = document.getElementById('reports-list');
        const weekSelect = document.getElementById('week-select');
        
        // Clear existing
        if (reportsList) reportsList.innerHTML = '';
        if (weekSelect) {
            weekSelect.innerHTML = '<option value="">Select Week...</option>';
        }
        
        if (reportsData.length === 0) {
            if (reportsList) {
                reportsList.innerHTML = '<div class="empty-state"><p>No reports available</p></div>';
            }
            return;
        }
        
        // Populate reports list
        reportsData.forEach((report, index) => {
            // Sidebar list
            if (reportsList) {
                const reportItem = createReportItem(report, index === 0);
                reportsList.appendChild(reportItem);
            }
            
            // Dropdown select
            if (weekSelect) {
                const option = document.createElement('option');
                option.value = report.week_start;
                option.textContent = `Week of ${report.week_start} (${report.opportunity_count} opportunities)`;
                weekSelect.appendChild(option);
            }
        });
        
        // Load first report automatically
        if (reportsData.length > 0 && !currentWeek) {
            currentWeek = reportsData[0].week_start;
            loadOpportunities(currentWeek);
        }
        
    } catch (error) {
        console.error('Error loading reports:', error);
        const reportsList = document.getElementById('reports-list');
        if (reportsList) {
            reportsList.innerHTML = '<div class="empty-state"><p>Error loading reports</p></div>';
        }
        showToast('Error loading reports', 'error');
    }
}

function createReportItem(report, isActive) {
    const reportItem = document.createElement('div');
    reportItem.className = 'report-item';
    if (isActive) {
        reportItem.classList.add('active');
    }
    
    reportItem.innerHTML = `
        <div class="week">Week of ${report.week_start}</div>
        <div class="count">${report.opportunity_count} opportunities</div>
    `;
    
    reportItem.addEventListener('click', () => {
        // Remove active class from all items
        document.querySelectorAll('.report-item').forEach(item => {
            item.classList.remove('active');
        });
        reportItem.classList.add('active');
        loadOpportunities(report.week_start);
    });
    
    return reportItem;
}

async function loadOpportunities(weekStart) {
    if (!weekStart) return;
    
    currentWeek = weekStart;
    const container = document.getElementById('opportunities-container');
    const titleEl = document.getElementById('content-title');
    const subtitleEl = document.getElementById('content-subtitle');
    
    if (titleEl) {
        titleEl.textContent = `Opportunities - Week of ${weekStart}`;
    }
    if (subtitleEl) {
        subtitleEl.textContent = `Analyzing product opportunities for this week`;
    }
    
    if (container) {
        container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Loading opportunities...</p></div>';
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/opportunities/${weekStart}`);
        if (!response.ok) throw new Error('Failed to fetch opportunities');
        
        const data = await response.json();
        allOpportunities = data.opportunities || [];
        filteredOpportunities = allOpportunities;
        
        if (allOpportunities.length === 0) {
            if (container) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fas fa-inbox"></i></div>
                        <h3>No Opportunities Found</h3>
                        <p>No opportunities found for this week</p>
                    </div>
                `;
            }
            return;
        }
        
        if (container) {
            container.innerHTML = '';
            
            // Render with stagger animation
            allOpportunities.forEach((opp, index) => {
                setTimeout(() => {
                    const card = createOpportunityCard(opp, index + 1);
                    container.appendChild(card);
                }, index * 50);
            });
        }
        
        showToast(`Loaded ${allOpportunities.length} opportunities`, 'success');
        
    } catch (error) {
        console.error('Error loading opportunities:', error);
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Error Loading Opportunities</h3>
                    <p>Please try refreshing the page</p>
                </div>
            `;
        }
        showToast('Error loading opportunities', 'error');
    }
}

// ============================================
// Card Creation
// ============================================

function createOpportunityCard(opp, rank) {
    const card = document.createElement('div');
    card.className = 'opportunity-card slide-up';
    card.dataset.entityId = opp.entity_id;
    
    const probPercent = (opp.score_winner_prob * 100).toFixed(1);
    const probColor = getProbabilityColor(opp.score_winner_prob);
    
    // Determine risk level
    const riskLevel = opp.score_risk > 80 ? 'high' : opp.score_risk > 50 ? 'medium' : 'low';
    const riskIcon = riskLevel === 'high' ? '⚠️' : riskLevel === 'medium' ? '⚡' : '✅';
    
    // Get top signals
    const topSignals = opp.explanations?.top_signals || [];
    
    card.innerHTML = `
        <div class="opportunity-header">
            <div>
                <div class="opportunity-title">${escapeHtml(opp.canonical_name)}</div>
                <div class="category-badge">${escapeHtml(opp.category_primary || 'General')}</div>
            </div>
            <div class="opportunity-rank">#${rank}</div>
        </div>
        
        <div class="winner-probability" style="color: ${probColor}">
            ${probPercent}% Winner Probability
        </div>
        <div class="probability-bar">
            <div class="probability-fill" style="width: ${probPercent}%; background: linear-gradient(90deg, ${probColor}, ${adjustColor(probColor, 20)});"></div>
        </div>
        
        ${topSignals.length > 0 ? `
        <div class="signals-section">
            <div class="signals-label">
                <i class="fas fa-bolt"></i>
                Key Signals
            </div>
            <div class="signals-list">
                ${topSignals.map(signal => `<span class="signal-badge">${escapeHtml(signal)}</span>`).join('')}
            </div>
        </div>
        ` : ''}
        
        <div class="score-grid">
            ${createScoreItem('Demand', opp.score_demand, getScoreColor(opp.score_demand), 'Measures market demand and growth potential')}
            ${createScoreItem('Competition', opp.score_competition, getScoreColor(opp.score_competition, true), 'Lower is better - indicates less competition')}
            ${createScoreItem('Margin', opp.score_margin, getScoreColor(opp.score_margin), 'Estimated profit margin potential')}
            ${createScoreItem('Risk', opp.score_risk, getScoreColor(opp.score_risk, true), 'Lower is better - indicates lower business risk')}
        </div>
        
        <div class="risk-indicator risk-${riskLevel}">
            <i class="fas fa-${riskLevel === 'high' ? 'exclamation-triangle' : riskLevel === 'medium' ? 'info-circle' : 'check-circle'}"></i>
            <span>Risk Level: ${riskLevel.toUpperCase()}</span>
        </div>
        
        ${opp.innovation_angles && opp.innovation_angles.length > 0 ? `
        <div class="innovation-section">
            <h4>
                <i class="fas fa-lightbulb"></i>
                Innovation Angles
            </h4>
            <ul class="innovation-list">
                ${opp.innovation_angles.map(angle => `<li>${escapeHtml(angle)}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
        
        ${opp.experiment_plan ? `
        <div class="experiment-plan">
            <div class="experiment-header">
                <i class="fas fa-flask"></i>
                <strong>Experiment Plan</strong>
            </div>
            <p>${escapeHtml(opp.experiment_plan)}</p>
        </div>
        ` : ''}
        
        <div class="card-actions">
            <button class="btn-details" onclick="showEntityDetails('${opp.entity_id}')">
                <i class="fas fa-info-circle"></i>
                View Details
            </button>
            <button class="btn-expand" onclick="toggleCardDetails(this)">
                <i class="fas fa-chevron-down"></i>
                <span>More Info</span>
            </button>
        </div>
        
        <div class="card-details" style="display: none;">
            <div class="details-loading">
                <div class="spinner"></div>
                <p>Loading detailed information...</p>
            </div>
        </div>
    `;
    
    return card;
}

function createScoreItem(label, value, color, tooltip = '') {
    const percentage = Math.min(100, Math.max(0, value));
    const tooltipAttr = tooltip ? `title="${tooltip}" data-tooltip="${tooltip}"` : '';
    return `
        <div class="score-item" ${tooltipAttr}>
            <div class="score-label">
                ${label}
                ${tooltip ? '<i class="fas fa-question-circle tooltip-icon"></i>' : ''}
            </div>
            <div class="score-value" style="color: ${color}">${value.toFixed(1)}</div>
            <div class="score-progress">
                <div class="score-progress-fill" style="width: ${percentage}%; background: ${color};"></div>
            </div>
        </div>
    `;
}

function getProbabilityColor(probability) {
    if (probability > 0.5) return '#10b981'; // success
    if (probability > 0.3) return '#f59e0b'; // warning
    return '#ef4444'; // danger
}

function getScoreColor(score, inverted = false) {
    const normalized = Math.min(100, Math.max(0, score));
    const effectiveScore = inverted ? 100 - normalized : normalized;
    
    if (effectiveScore >= 70) return '#10b981'; // success
    if (effectiveScore >= 40) return '#f59e0b'; // warning
    return '#ef4444'; // danger
}

function adjustColor(color, amount) {
    // Simple color adjustment for gradients
    return color;
}

// ============================================
// Search & Filter
// ============================================

function handleSearchReports(e) {
    const searchTerm = e.target.value.toLowerCase();
    const reportItems = document.querySelectorAll('.report-item');
    
    reportItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// ============================================
// Refresh Handler
// ============================================

async function handleRefresh() {
    showLoading();
    showToast('Refreshing data...', 'info');
    
    try {
        await Promise.all([
            loadStats(),
            loadReports()
        ]);
        
        if (currentWeek) {
            await loadOpportunities(currentWeek);
        }
        
        showToast('Data refreshed successfully', 'success');
    } catch (error) {
        console.error('Error refreshing:', error);
        showToast('Error refreshing data', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================
// Loading Overlay
// ============================================

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// ============================================
// Toast Notifications
// ============================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// ============================================
// Entity Details & Expandable Cards
// ============================================

async function showEntityDetails(entityId) {
    if (!entityId) {
        console.error('No entity ID provided');
        showToast('Error: No entity ID provided', 'error');
        return;
    }
    
    showLoading();
    try {
        const [detailsResponse, statsResponse] = await Promise.all([
            fetch(`${API_BASE}/api/entity/${entityId}`),
            fetch(`${API_BASE}/api/entity/${entityId}/stats`)
        ]);
        
        if (!detailsResponse.ok) {
            throw new Error(`Failed to fetch entity details: ${detailsResponse.status}`);
        }
        if (!statsResponse.ok) {
            throw new Error(`Failed to fetch entity stats: ${statsResponse.status}`);
        }
        
        const [details, stats] = await Promise.all([
            detailsResponse.json(),
            statsResponse.json()
        ]);
        
        // Check for errors in response
        if (details.error) {
            throw new Error(details.error);
        }
        if (stats.error) {
            console.warn('Stats error:', stats.error);
        }
        
        // Create and show modal
        showDetailsModal(details, stats);
    } catch (error) {
        console.error('Error loading entity details:', error);
        showToast(`Error loading entity details: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function showDetailsModal(details, stats) {
    // Remove existing modal
    const existingModal = document.getElementById('entity-details-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    if (!details || !details.canonical_name) {
        console.error('Invalid details object:', details);
        showToast('Error: Invalid entity data', 'error');
        return;
    }
    
    const modal = document.createElement('div');
    modal.id = 'entity-details-modal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>${escapeHtml(details.canonical_name || 'Unknown Entity')}</h2>
                <button class="modal-close" onclick="closeDetailsModal()" aria-label="Close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                ${createDetailsContent(details, stats)}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Trigger animation
    setTimeout(() => {
        modal.classList.add('active');
    }, 10);
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeDetailsModal();
        }
    });
    
    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            closeDetailsModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
}

function createDetailsContent(details, stats) {
    const amazon = stats.amazon || {};
    const tiktok = stats.tiktok || {};
    const latestScore = stats.latest_score || {};
    
    return `
        <div class="details-grid">
            <div class="details-section">
                <h3><i class="fas fa-chart-line"></i> Performance Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">Winner Probability</div>
                        <div class="metric-value">${((latestScore.score_winner_prob || 0) * 100).toFixed(1)}%</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Overall Rank</div>
                        <div class="metric-value">#${(latestScore.score_rank || 0).toFixed(0)}</div>
                    </div>
                </div>
            </div>
            
            <div class="details-section">
                <h3><i class="fab fa-amazon"></i> Amazon Data</h3>
                ${amazon.count > 0 ? `
                <div class="data-stats">
                    <div class="data-stat">
                        <span class="stat-label">Listings Tracked:</span>
                        <span class="stat-value">${amazon.count || 0}</span>
                    </div>
                    ${amazon.avg_price ? `
                    <div class="data-stat">
                        <span class="stat-label">Avg Price:</span>
                        <span class="stat-value">$${parseFloat(amazon.avg_price || 0).toFixed(2)}</span>
                    </div>
                    ` : ''}
                    ${amazon.best_bsr ? `
                    <div class="data-stat">
                        <span class="stat-label">Best BSR:</span>
                        <span class="stat-value">#${amazon.best_bsr || 'N/A'}</span>
                    </div>
                    ` : ''}
                    ${amazon.avg_rating ? `
                    <div class="data-stat">
                        <span class="stat-label">Avg Rating:</span>
                        <span class="stat-value">${parseFloat(amazon.avg_rating || 0).toFixed(1)} ⭐</span>
                    </div>
                    ` : ''}
                    ${amazon.total_reviews ? `
                    <div class="data-stat">
                        <span class="stat-label">Total Reviews:</span>
                        <span class="stat-value">${parseInt(amazon.total_reviews || 0).toLocaleString()}</span>
                    </div>
                    ` : ''}
                </div>
                ` : '<p class="no-data">No Amazon data available</p>'}
            </div>
            
            <div class="details-section">
                <h3><i class="fab fa-tiktok"></i> TikTok Data</h3>
                ${tiktok.count > 0 ? `
                <div class="data-stats">
                    <div class="data-stat">
                        <span class="stat-label">Hashtags Tracked:</span>
                        <span class="stat-value">${tiktok.count || 0}</span>
                    </div>
                    ${tiktok.max_views ? `
                    <div class="data-stat">
                        <span class="stat-label">Max Views:</span>
                        <span class="stat-value">${parseInt(tiktok.max_views || 0).toLocaleString()}</span>
                    </div>
                    ` : ''}
                    ${tiktok.max_videos ? `
                    <div class="data-stat">
                        <span class="stat-label">Max Videos:</span>
                        <span class="stat-value">${parseInt(tiktok.max_videos || 0).toLocaleString()}</span>
                    </div>
                    ` : ''}
                    ${tiktok.max_creators ? `
                    <div class="data-stat">
                        <span class="stat-label">Max Creators:</span>
                        <span class="stat-value">${parseInt(tiktok.max_creators || 0).toLocaleString()}</span>
                    </div>
                    ` : ''}
                </div>
                ` : '<p class="no-data">No TikTok data available</p>'}
            </div>
            
            ${details.aliases && details.aliases.length > 0 ? `
            <div class="details-section">
                <h3><i class="fas fa-tags"></i> Aliases & Sources</h3>
                <div class="aliases-list">
                    ${details.aliases.map(alias => `
                        <span class="alias-badge source-${alias.source}">
                            <i class="fas fa-${alias.source === 'amazon' ? 'amazon' : alias.source === 'tiktok' ? 'tiktok' : 'tag'}"></i>
                            ${escapeHtml(alias.alias_text)}
                        </span>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

function closeDetailsModal() {
    const modal = document.getElementById('entity-details-modal');
    if (modal) {
        modal.classList.remove('active');
        // Wait for animation to complete before removing
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }
}

function toggleCardDetails(button) {
    if (!button) {
        console.error('No button provided to toggleCardDetails');
        return;
    }
    
    const card = button.closest('.opportunity-card');
    if (!card) {
        console.error('Could not find opportunity card');
        return;
    }
    
    const details = card.querySelector('.card-details');
    if (!details) {
        console.error('Could not find card-details element');
        return;
    }
    
    const icon = button.querySelector('i');
    const span = button.querySelector('span');
    
    const isHidden = details.style.display === 'none' || !details.style.display;
    
    if (isHidden) {
        // Show details
        details.style.display = 'block';
        if (icon) icon.className = 'fas fa-chevron-up';
        if (span) span.textContent = 'Less Info';
        
        // Load details if not loaded
        const detailsContent = details.querySelector('.details-content');
        const detailsLoading = details.querySelector('.details-loading');
        
        if (!detailsContent && detailsLoading) {
            // Still loading or not loaded yet
            const entityId = card.dataset.entityId;
            if (entityId) {
                loadCardDetails(entityId, details);
            } else {
                console.error('No entity ID found on card');
                details.innerHTML = '<div class="error-state">Error: No entity ID</div>';
            }
        }
    } else {
        // Hide details
        details.style.display = 'none';
        if (icon) icon.className = 'fas fa-chevron-down';
        if (span) span.textContent = 'More Info';
    }
}

async function loadCardDetails(entityId, container) {
    if (!entityId) {
        container.innerHTML = '<div class="error-state">Error: No entity ID</div>';
        return;
    }
    
    if (!container) {
        console.error('No container provided to loadCardDetails');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/entity/${entityId}/stats`);
        
        // Handle both 200 and 404 responses gracefully
        const stats = await response.json();
        
        // Check for error in response (even if status is 200)
        if (stats.error && response.status === 404) {
            container.innerHTML = `
                <div class="details-content fade-in">
                    <div class="no-data">
                        <i class="fas fa-info-circle"></i>
                        <p>Entity not found or no data available</p>
                    </div>
                </div>
            `;
            return;
        }
        
        const amazon = stats.amazon || {};
        const tiktok = stats.tiktok || {};
        const latestScore = stats.latest_score || {};
        
        // Build quick stats HTML
        let quickStatsHtml = '<div class="quick-stats">';
        let hasData = false;
        
        if (amazon.count > 0) {
            hasData = true;
            quickStatsHtml += `
                <div class="quick-stat">
                    <i class="fab fa-amazon"></i>
                    <div>
                        <div class="quick-stat-value">${amazon.count} listings</div>
                        <div class="quick-stat-label">Amazon</div>
                        ${amazon.avg_price ? `<div class="quick-stat-extra">Avg: $${parseFloat(amazon.avg_price).toFixed(2)}</div>` : ''}
                    </div>
                </div>
            `;
        }
        
        if (tiktok.count > 0) {
            hasData = true;
            quickStatsHtml += `
                <div class="quick-stat">
                    <i class="fab fa-tiktok"></i>
                    <div>
                        <div class="quick-stat-value">${tiktok.count} hashtags</div>
                        <div class="quick-stat-label">TikTok</div>
                        ${tiktok.max_views ? `<div class="quick-stat-extra">Max views: ${parseInt(tiktok.max_views).toLocaleString()}</div>` : ''}
                    </div>
                </div>
            `;
        }
        
        if (latestScore && latestScore.score_winner_prob !== undefined && latestScore.score_winner_prob !== null) {
            hasData = true;
            quickStatsHtml += `
                <div class="quick-stat">
                    <i class="fas fa-chart-line"></i>
                    <div>
                        <div class="quick-stat-value">${(latestScore.score_winner_prob * 100).toFixed(1)}%</div>
                        <div class="quick-stat-label">Winner Probability</div>
                        ${latestScore.week_start ? `<div class="quick-stat-extra">Week of ${latestScore.week_start}</div>` : ''}
                    </div>
                </div>
            `;
        }
        
        if (!hasData) {
            quickStatsHtml += `
                <div class="no-data">
                    <i class="fas fa-info-circle"></i>
                    <p>No additional data available for this entity</p>
                </div>
            `;
        }
        
        quickStatsHtml += '</div>';
        
        container.innerHTML = `
            <div class="details-content fade-in">
                ${quickStatsHtml}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading card details:', error);
        container.innerHTML = `
            <div class="details-content fade-in">
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load details. Please try again.</p>
                </div>
            </div>
        `;
    }
}

// Make functions globally available
window.showEntityDetails = showEntityDetails;
window.closeDetailsModal = closeDetailsModal;
window.toggleCardDetails = toggleCardDetails;

// Debug: Log when functions are available
console.log('✅ Entity detail functions loaded:', {
    showEntityDetails: typeof window.showEntityDetails,
    toggleCardDetails: typeof window.toggleCardDetails,
    closeDetailsModal: typeof window.closeDetailsModal
});

// ============================================
// Utility Functions
// ============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Performance Optimization
// ============================================

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to search
const searchInput = document.getElementById('search-reports');
if (searchInput) {
    searchInput.addEventListener('input', debounce(handleSearchReports, 300));
}
