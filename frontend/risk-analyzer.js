// AI Risk Analyzer — ported from the Bolt "Wallet Analyzer" feature into
// SmartCoin2's vanilla JS frontend. Deterministic mock analysis (seeded by
// address) so results are stable for a given address, matching the
// original generateMockAnalysis() behaviour.

let raCurrentAddress = '';

const RA_CATEGORIES = [
    { key: 'amlScore', label: 'AML Risk Score', icon: '🛡️', description: 'Anti-money laundering risk assessment' },
    { key: 'fraudScore', label: 'Fraud Probability', icon: '⚠️', description: 'Likelihood of fraudulent activity' },
    { key: 'whaleScore', label: 'Whale Activity', icon: '📈', description: 'Large holder transaction patterns' },
    { key: 'sanctionExposure', label: 'Sanction Exposure', icon: '🌐', description: 'Connection to sanctioned entities' },
    { key: 'mixerUsage', label: 'Mixer Interaction', icon: '🔀', description: 'Privacy mixer service usage' },
    { key: 'botActivity', label: 'Bot Activity', icon: '🤖', description: 'Automated transaction patterns' },
];

function raSetExample(address) {
    document.getElementById('raAddressInput').value = address;
}

function raFormatAddress(address, chars = 10) {
    if (!address) return '';
    if (address.length <= chars * 2) return address;
    return `${address.slice(0, chars)}...${address.slice(-chars)}`;
}

function raGenerateMockAnalysis(address) {
    let hash = 0;
    for (let i = 0; i < address.length; i++) {
        hash = ((hash << 5) - hash) + address.charCodeAt(i);
        hash |= 0;
    }
    const seed = Math.abs(hash) / 2147483647;

    return {
        amlScore: 15 + (seed * 45),
        fraudScore: 8 + (seed * 60),
        whaleScore: seed > 0.5 ? 60 + (seed * 35) : 10 + (seed * 30),
        sanctionExposure: seed > 0.7 ? 25 + (seed * 60) : seed * 20,
        mixerUsage: seed > 0.6 ? 30 + (seed * 50) : seed * 15,
        botActivity: 5 + (seed * 40),
        overallRisk: 20 + (seed * 65),
        aiConfidence: 85 + (seed * 14),
    };
}

function raGetRiskLevel(value) {
    if (value >= 70) return 'critical';
    if (value >= 50) return 'high';
    if (value >= 30) return 'medium';
    return 'low';
}

function raAnalyze() {
    const input = document.getElementById('raAddressInput');
    const address = input.value.trim();
    if (!address) return;

    raCurrentAddress = address;

    document.getElementById('raEmpty').style.display = 'none';
    document.getElementById('raResults').style.display = 'none';
    document.getElementById('raLoading').style.display = 'block';

    const btn = document.getElementById('raAnalyzeBtn');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';

    setTimeout(() => {
        const analysis = raGenerateMockAnalysis(address);
        raRenderResults(address, analysis);

        document.getElementById('raLoading').style.display = 'none';
        document.getElementById('raResults').style.display = 'block';
        btn.disabled = false;
        btn.innerHTML = '⚡ Analyze';
    }, 1800);
}

function raRefresh() {
    if (!raCurrentAddress) return;
    document.getElementById('raResults').style.display = 'none';
    document.getElementById('raLoading').style.display = 'block';

    setTimeout(() => {
        const analysis = raGenerateMockAnalysis(raCurrentAddress + Date.now());
        raRenderResults(raCurrentAddress, analysis);
        document.getElementById('raLoading').style.display = 'none';
        document.getElementById('raResults').style.display = 'block';
    }, 1200);
}

function raGenerateReport() {
    showNotification && showNotification('Full report generation is coming soon.', 'info');
    if (typeof showNotification !== 'function') {
        alert('Full report generation is coming soon.');
    }
}

function raRenderResults(address, analysis) {
    const overallLevel = raGetRiskLevel(analysis.overallRisk);

    document.getElementById('raResultAddress').textContent = raFormatAddress(address, 10);

    const badge = document.getElementById('raOverallBadge');
    badge.className = `ra-badge ${overallLevel}`;
    badge.textContent = overallLevel.charAt(0).toUpperCase() + overallLevel.slice(1) + ' Risk';

    // Gauge (circle circumference = 2 * PI * 70 ≈ 440)
    const circumference = 440;
    const offset = circumference - (analysis.overallRisk / 100) * circumference;
    const gaugeCircle = document.getElementById('raGaugeCircle');
    gaugeCircle.style.stroke = raColorForLevel(overallLevel);
    gaugeCircle.setAttribute('stroke-dashoffset', offset);
    document.getElementById('raGaugeValue').textContent = analysis.overallRisk.toFixed(1) + '%';

    document.getElementById('raConfidence').textContent = analysis.aiConfidence.toFixed(1) + '%';

    const etherscanLink = document.getElementById('raEtherscanLink');
    etherscanLink.href = `https://etherscan.io/address/${encodeURIComponent(address)}`;

    // Metric grid
    const grid = document.getElementById('raMetricGrid');
    grid.innerHTML = RA_CATEGORIES.map(cat => {
        const value = analysis[cat.key];
        const level = raGetRiskLevel(value);
        return `
            <div class="ra-metric-card">
                <div class="ra-metric-top">
                    <div class="ra-metric-info">
                        <div class="ra-metric-icon">${cat.icon}</div>
                        <div>
                            <div class="ra-metric-label">${cat.label}</div>
                            <div class="ra-metric-desc">${cat.description}</div>
                        </div>
                    </div>
                    <div class="ra-metric-value color-${level}">${value.toFixed(1)}%</div>
                </div>
                <div class="ra-metric-bar"><div class="ra-metric-bar-fill fill-${level}" style="width:${Math.min(100, value)}%"></div></div>
            </div>
        `;
    }).join('');

    // AI summary text
    const txCount = Math.floor(Math.random() * 500 + 200);
    const counterparties = Math.floor(Math.random() * 50 + 10);
    let summaryHtml = `<p>Based on comprehensive blockchain analysis, this wallet shows
        <span class="${analysis.overallRisk >= 50 ? 'warn' : 'ok'}" style="font-weight:600;">
        ${analysis.overallRisk >= 70 ? 'critical' : analysis.overallRisk >= 50 ? 'elevated' : 'acceptable'}</span>
        risk indicators. The AI has analyzed ${txCount} transactions across ${counterparties} counterparties.</p><p>`;

    if (analysis.mixerUsage > 30) {
        summaryHtml += `<span class="warn">Significant mixer interaction detected. This wallet has received funds from privacy mixer services, which increases AML risk exposure. </span>`;
    }
    if (analysis.sanctionExposure > 25) {
        summaryHtml += `<span class="caution">Connections to potentially sanctioned entities identified. Enhanced due diligence recommended. </span>`;
    }
    if (analysis.fraudScore < 30) {
        summaryHtml += `<span class="ok">No significant fraud indicators detected. Transaction patterns appear normal for this wallet type. </span>`;
    }
    if (analysis.whaleScore > 60) {
        summaryHtml += `<span class="info">Large volume transaction patterns detected. Consider enhanced monitoring for market impact analysis. </span>`;
    }
    summaryHtml += `</p>`;
    document.getElementById('raSummaryText').innerHTML = summaryHtml;

    // Recommendations
    const recs = [];
    if (analysis.overallRisk >= 50) {
        recs.push({ icon: '⚠️', text: 'Enhanced due diligence recommended before accepting transactions from this address' });
    }
    if (analysis.mixerUsage > 30) {
        recs.push({ icon: '⚠️', text: 'Request source of funds documentation for compliance' });
    }
    recs.push({ icon: '✅', text: 'Continue monitoring for changes in transaction patterns' });
    recs.push({ icon: '✅', text: 'Add to watchlist for automated risk alerts' });

    document.getElementById('raRecommendations').innerHTML = recs.map(r =>
        `<li><span>${r.icon}</span><span>${r.text}</span></li>`
    ).join('');
}

function raColorForLevel(level) {
    switch (level) {
        case 'critical': return '#eb3941';
        case 'high': return '#f2994a';
        case 'medium': return '#667eea';
        default: return '#11998e';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('raAddressInput');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') raAnalyze();
        });
    }
});
