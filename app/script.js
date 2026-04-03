document.addEventListener('DOMContentLoaded', () => {
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD', maximumFractionDigits: 0
    });

    // ====== Tab Navigation ======
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            const tab = link.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
            document.getElementById(`tab-${tab}`).classList.add('active');
            if (tab === 'saved') renderSaved();
        });
    });

    // ====== Local Storage for Saved Properties ======
    function getSaved() {
        try { return JSON.parse(localStorage.getItem('savedProperties') || '[]'); }
        catch { return []; }
    }
    function saveProp(prop) {
        const saved = getSaved();
        if (saved.find(p => p.id === prop.id)) return false;
        saved.push(prop);
        localStorage.setItem('savedProperties', JSON.stringify(saved));
        return true;
    }
    function removeProp(id) {
        const saved = getSaved().filter(p => p.id !== id);
        localStorage.setItem('savedProperties', JSON.stringify(saved));
        renderSaved();
    }

    // ====== Render a Property Card ======
    function createCard(prop, isSaved) {
        const card = document.createElement('div');
        card.className = 'property-card glass-panel';

        const price = prop.price ? formatter.format(prop.price) :
                      prop.lastSalePrice ? formatter.format(prop.lastSalePrice) : 'N/A';

        card.innerHTML = `
            <div class="card-header">
                <div class="card-address">${prop.address || 'Unknown Address'}</div>
                <div class="card-price glow-text">${price}</div>
                <div style="font-size:10px; color:var(--neon-cyan); letter-spacing:1px; margin-top:5px; text-transform:uppercase;">⚡ AI Predicted Valuation</div>
            </div>
            <div class="card-stats">
                ${prop.bedrooms ? `<div class="card-stat"><span class="stat-val">${prop.bedrooms}</span><span class="stat-label">Beds</span></div>` : ''}
                ${prop.bathrooms ? `<div class="card-stat"><span class="stat-val">${prop.bathrooms}</span><span class="stat-label">Baths</span></div>` : ''}
                ${prop.squareFootage ? `<div class="card-stat"><span class="stat-val">${prop.squareFootage.toLocaleString()}</span><span class="stat-label">Sqft</span></div>` : ''}
                ${prop.yearBuilt ? `<div class="card-stat"><span class="stat-val">${prop.yearBuilt}</span><span class="stat-label">Built</span></div>` : ''}
                ${prop.lotSize ? `<div class="card-stat"><span class="stat-val">${prop.lotSize.toLocaleString()}</span><span class="stat-label">Lot Sqft</span></div>` : ''}
            </div>
            ${prop.propertyType ? `<div class="card-type">${prop.propertyType}</div>` : ''}
            <div class="card-actions">
                ${isSaved
                    ? `<button class="card-btn remove-btn" data-id="${prop.id}">✕ Remove</button>`
                    : `<button class="card-btn save-btn" data-id="${prop.id}">📌 Save Property</button>`
                }
            </div>
        `;

        if (isSaved) {
            card.querySelector('.remove-btn').addEventListener('click', () => removeProp(prop.id));
        } else {
            card.querySelector('.save-btn').addEventListener('click', (e) => {
                if (saveProp(prop)) {
                    e.target.innerText = '✓ Saved!';
                    e.target.disabled = true;
                    e.target.classList.add('saved');
                } else {
                    e.target.innerText = 'Already Saved';
                    e.target.disabled = true;
                }
            });
        }
        return card;
    }

    // ====== Render Saved Tab ======
    function renderSaved() {
        const container = document.getElementById('savedList');
        const saved = getSaved();
        if (saved.length === 0) {
            container.innerHTML = `
                <div class="empty-state glass-panel">
                    <div class="empty-icon">📌</div>
                    <h3>No Saved Properties Yet</h3>
                    <p>Search for properties and click "Save" to bookmark them here.</p>
                </div>`;
            return;
        }
        container.innerHTML = '';
        saved.forEach(prop => container.appendChild(createCard(prop, true)));
    }

    // ====== Market Search ======
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const searchStatus = document.getElementById('searchStatus');

    async function doSearch() {
        const query = searchInput.value.trim();
        if (!query) { searchStatus.innerHTML = '<p class="status-warn">Please enter an address to search.</p>'; return; }

        searchStatus.innerHTML = '<p class="status-loading">🔍 Searching RentCast API...</p>';
        searchResults.innerHTML = '';

        try {
            const res = await fetch('/api/lookup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ address: query })
            });
            const data = await res.json();

            if (data.error) {
                searchStatus.innerHTML = '';
                searchResults.innerHTML = `
                    <div class="glass-panel api-notice">
                        <h3>⚠️ API Key Required</h3>
                        <p>${data.error}</p>
                        <a href="https://www.rentcast.io/api" target="_blank" class="api-link">Get your free RentCast API key →</a>
                        <div class="api-help">
                            <p>Once you have a key, set it as an environment variable:</p>
                            <code>export RENTCAST_API_KEY=your_key_here</code>
                        </div>
                    </div>`;
                return;
            }

            const items = Array.isArray(data) ? data : [data];
            if (items.length === 0) {
                searchStatus.innerHTML = '<p class="status-warn">No results found for that address.</p>';
                return;
            }

            searchStatus.innerHTML = `<p class="status-success">Found ${items.length} result${items.length > 1 ? 's' : ''}</p>`;
            items.forEach((item, i) => {
                const prop = {
                    id: `${query}-${i}-${Date.now()}`,
                    address: item.formattedAddress || item.addressLine1 || query,
                    price: item.ai_predicted_price || item.price || item.estimatedValue || null,
                    lastSalePrice: item.lastSalePrice || null,
                    bedrooms: item.bedrooms || null,
                    bathrooms: item.bathrooms || null,
                    squareFootage: item.squareFootage || null,
                    yearBuilt: item.yearBuilt || null,
                    lotSize: item.lotSize || null,
                    propertyType: item.propertyType || null
                };
                searchResults.appendChild(createCard(prop, false));
            });
        } catch (err) {
            searchStatus.innerHTML = '<p class="status-error">Network error. Is app_server.py running?</p>';
            console.error(err);
        }
    }

    searchBtn.addEventListener('click', doSearch);
    searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });

    // Initial render of saved
    renderSaved();

    // ====== Native Telemetry Chart.js Initialization ======
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    const telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'CPU Usage (%)', borderColor: '#00e5ff', backgroundColor: 'rgba(0, 229, 255, 0.1)', data: [], fill: true, tension: 0.4 },
                { label: 'Memory (MB)', borderColor: '#0b6bf2', backgroundColor: 'rgba(11, 107, 242, 0.05)', data: [], fill: true, yAxisID: 'y1', tension: 0.4 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#8b9bb4' } } },
            scales: {
                x: { ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { min: 0, max: 100, ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y1: { position: 'right', ticks: { color: '#8b9bb4' }, grid: { drawOnChartArea: false } }
            }
        }
    });

    // Stream realtime metrics from the Python Server
    setInterval(async () => {
        try {
            const res = await fetch('/api/stats');
            const stats = await res.json();
            
            // Update Number Cards
            document.getElementById('stat-cpu').innerText = stats.cpu_percent + '%';
            document.getElementById('stat-mem').innerText = stats.memory_mb + ' MB';
            document.getElementById('stat-req').innerText = stats.total_lookups;
            
            // Format uptime
            const hrs = Math.floor(stats.uptime_seconds / 3600);
            const mins = Math.floor((stats.uptime_seconds % 3600) / 60);
            const secs = stats.uptime_seconds % 60;
            document.getElementById('stat-uptime').innerText = 
                (hrs > 0 ? hrs + 'h ' : '') + (mins > 0 ? mins + 'm ' : '') + secs + 's';

            // Push to Chart
            const timeLabel = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
            if(telemetryChart.data.labels.length > 20) {
                telemetryChart.data.labels.shift();
                telemetryChart.data.datasets.forEach(d => d.data.shift());
            }
            telemetryChart.data.labels.push(timeLabel);
            telemetryChart.data.datasets[0].data.push(stats.cpu_percent);
            telemetryChart.data.datasets[1].data.push(stats.memory_mb);
            telemetryChart.update();
        } catch(e) { }
    }, 2000);
});
