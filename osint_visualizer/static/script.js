// DOM Elements
let usernameInput, startBtn, dashboard, logContainer, dataSummary, phishingEmailDiv;
let progressBar, riskFill, riskDetails;

// Attack state
let isRunning = false;
let currentPhase = 0;
const phases = ['phase1', 'phase2', 'phase3', 'phase4', 'phase5', 'phase6'];

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // Get elements
    usernameInput = document.getElementById('username');
    startBtn = document.getElementById('startAttack');
    dashboard = document.getElementById('dashboard');
    logContainer = document.getElementById('logContainer');
    dataSummary = document.getElementById('dataSummary');
    phishingEmailDiv = document.getElementById('phishingEmail');
    progressBar = document.getElementById('progressBar');
    riskFill = document.getElementById('riskFill');
    riskDetails = document.getElementById('riskDetails');
    
    // Add event listener
    startBtn.addEventListener('click', startAttack);
});

function addLog(message, type = 'info') {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    
    // Extract timestamp and message
    const timeMatch = message.match(/^(\d{2}:\d{2}:\d{2})/);
    if (timeMatch) {
        logEntry.innerHTML = `<span style="color: #888;">[${timeMatch[0]}]</span> ${message.substring(9)}`;
    } else {
        logEntry.textContent = message;
    }
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function updatePhase(phaseIndex) {
    // Reset all phases
    phases.forEach((phase, idx) => {
        const element = document.getElementById(phase);
        if (element) {
            if (idx < phaseIndex) {
                element.classList.add('completed');
                element.classList.remove('active');
            } else if (idx === phaseIndex) {
                element.classList.add('active');
                element.classList.remove('completed');
            } else {
                element.classList.remove('active', 'completed');
            }
        }
    });
    
    // Update progress bar
    const progress = (phaseIndex / phases.length) * 100;
    progressBar.style.width = `${progress}%`;
}

function updateDataSummary(data) {
    if (!data) return;
    
    let html = '';
    
    // Identity
    if (data.identity && Object.keys(data.identity).length > 0) {
        html += `<div class="data-item">
                    <div class="data-label">🎯 TARGET IDENTITY</div>
                    <div class="data-value">
                        Username: @${data.identity.username || 'Unknown'}<br>
                        Name: ${data.identity.full_name || 'Unknown'}<br>
                        Location: ${data.identity.location || 'Unknown'}
                    </div>
                 </div>`;
    }
    
    // Social Media
    if (data.social_media && data.social_media.length > 0) {
        html += `<div class="data-item">
                    <div class="data-label">📱 SOCIAL MEDIA PROFILES</div>
                    <div class="data-value">`;
        data.social_media.forEach(platform => {
            html += `• ${platform.platform}: ${platform.details}<br>`;
        });
        html += `</div></div>`;
    }
    
    // Emails
    if (data.email_addresses && data.email_addresses.length > 0) {
        html += `<div class="data-item">
                    <div class="data-label">📧 EMAIL ADDRESSES</div>
                    <div class="data-value">`;
        data.email_addresses.forEach(email => {
            html += `• ${email.email} (${email.source})<br>`;
        });
        html += `</div></div>`;
    }
    
    // Breach Data
    if (data.breach_data && data.breach_data.length > 0) {
        html += `<div class="data-item">
                    <div class="data-label">💀 BREACH DATABASE MATCHES</div>
                    <div class="data-value">`;
        data.breach_data.forEach(breach => {
            html += `• ${breach.name}<br>`;
            html += `  <span style="font-size: 11px; color: #888;">${breach.data}</span><br>`;
        });
        html += `</div></div>`;
    }
    
    // Relationships
    if (data.relationships && data.relationships.length > 0) {
        html += `<div class="data-item">
                    <div class="data-label">👥 MAPPED RELATIONSHIPS</div>
                    <div class="data-value">`;
        data.relationships.slice(0, 4).forEach(rel => {
            html += `• ${rel}<br>`;
        });
        html += `</div></div>`;
    }
    
    // Behavioral
    if (data.behavioral && Object.keys(data.behavioral).length > 0) {
        html += `<div class="data-item">
                    <div class="data-label">🧠 BEHAVIORAL PATTERNS</div>
                    <div class="data-value">
                        Active Hours: ${data.behavioral.active_hours || 'Unknown'}<br>
                        Interests: ${(data.behavioral.common_topics || []).join(', ')}<br>
                        Emotional State: ${data.behavioral.emotional_state || 'Unknown'}
                    </div>
                 </div>`;
    }
    
    dataSummary.innerHTML = html || '<div class="data-placeholder">No data collected yet</div>';
}

function updatePhishingEmail(email) {
    if (email) {
        phishingEmailDiv.innerHTML = `<pre style="margin: 0; white-space: pre-wrap;">${email}</pre>`;
    } else {
        phishingEmailDiv.innerHTML = '<div class="email-placeholder">Personalized phishing email will appear here</div>';
    }
}

function updateRiskScore(score, level) {
    // Set risk fill color based on score
    let color;
    if (score >= 70) color = '#ff6b6b';
    else if (score >= 40) color = '#ffc107';
    else color = '#4caf50';
    
    riskFill.style.width = `${score}%`;
    riskFill.style.background = `linear-gradient(90deg, ${color}, ${color}dd)`;
    
    let riskText = '';
    if (score >= 70) {
        riskText = `⚠️ CRITICAL RISK (${score}/100) - Immediate action required. Attack highly likely.`;
    } else if (score >= 40) {
        riskText = `⚠️ HIGH RISK (${score}/100) - Significant exposure detected. Reduce public data.`;
    } else {
        riskText = `✓ MEDIUM RISK (${score}/100) - Some exposure, but no immediate threat.`;
    }
    
    riskDetails.innerHTML = riskText;
}

async function startAttack() {
    const username = usernameInput.value.trim();
    
    if (!username) {
        alert('Please enter a username');
        return;
    }
    
    if (isRunning) {
        alert('Attack already in progress');
        return;
    }
    
    // Confirm ethical use
    const confirmMsg = `⚠️ ETHICAL WARNING\n\nYou are about to simulate an OSINT attack on "@${username}".\n\nOnly proceed if this is YOUR account or you have explicit permission.\n\nProceed?`;
    
    if (!confirm(confirmMsg)) {
        return;
    }
    
    // Reset UI
    isRunning = true;
    startBtn.disabled = true;
    dashboard.style.display = 'block';
    logContainer.innerHTML = '';
    currentPhase = 0;
    updatePhase(0);
    
    addLog('🚀 INITIATING OSINT ATTACK SIMULATION', 'warning');
    addLog(`🎯 Target: @${username}`, 'info');
    addLog('=' .repeat(50), 'info');
    
    // Call API
    try {
        const response = await fetch('/api/attack', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username })
        });
        
        const results = await response.json();
        
        if (results.error) {
            addLog(`ERROR: ${results.error}`, 'error');
            return;
        }
        
        // Process logs
        if (results.logs && Array.isArray(results.logs)) {
            results.logs.forEach(log => {
                addLog(`[${log.time}] ${log.message}`, log.type);
                
                // Update phase based on log content
                if (log.message.includes('PHASE 1')) {
                    updatePhase(1);
                } else if (log.message.includes('PHASE 2')) {
                    updatePhase(2);
                } else if (log.message.includes('PHASE 3')) {
                    updatePhase(3);
                } else if (log.message.includes('PHASE 4')) {
                    updatePhase(4);
                } else if (log.message.includes('PHASE 5')) {
                    updatePhase(5);
                } else if (log.message.includes('PHASE 6')) {
                    updatePhase(6);
                }
            });
        }
        
        // Update data summary
        if (results.data) {
            updateDataSummary(results.data);
            updateRiskScore(results.data.risk_score || 0, results.data.attack_readiness);
        }
        
        // Update phishing email
        if (results.phishing_email) {
            updatePhishingEmail(results.phishing_email);
        }
        
        // Show summary
        if (results.summary) {
            addLog('', 'info');
            addLog(results.summary, 'info');
        }
        
        addLog('✅ OSINT ATTACK SIMULATION COMPLETE', 'success');
        addLog('⚠️ DEMONSTRATION ONLY - No actual attack was executed', 'warning');
        
    } catch (error) {
        console.error('Error:', error);
        addLog(`ERROR: Failed to complete simulation: ${error.message}`, 'error');
    } finally {
        isRunning = false;
        startBtn.disabled = false;
    }
}
