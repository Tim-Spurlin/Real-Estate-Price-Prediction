document.addEventListener('DOMContentLoaded', async () => {
    const grid = document.getElementById('propertyGrid');
    const modal = document.getElementById('modalOverlay');
    const closeBtn = document.getElementById('closeBtn');
    
    // Format currency
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
    });

    try {
        const data = propertyData; // Loaded from data.js
        
        grid.innerHTML = '';
        
        // Populate Grid
        data.forEach((prop, index) => {
            const delay = (index % 10) * 0.05;
            const price = prop.SalePrice ? formatter.format(prop.SalePrice) : 'Unknown';
            
            const card = document.createElement('div');
            card.className = 'prop-card glass-panel';
            card.style.animationDelay = `${delay}s`;
            
            // Generate some card HTML based on test dataset features
            // Common features: Neighborhood, YearBuilt, GrLivArea
            card.innerHTML = `
                <div class="prop-id">ID: ${prop.Id}</div>
                <div class="prop-title">${prop.Neighborhood || 'Unknown Area'}</div>
                <div class="prop-mini-stats">
                    <span>🏠 ${prop.GrLivArea || 0} sqft</span>
                    <span>🏗️ Built ${prop.YearBuilt || 'N/A'}</span>
                </div>
                <div class="prop-price">${price}</div>
            `;
            
            card.addEventListener('click', () => openModal(prop));
            grid.appendChild(card);
        });
        
    } catch (e) {
        grid.innerHTML = `<div style="color:red">Error loading data. Make sure data.json exists.</div>`;
        console.error(e);
    }

    function openModal(prop) {
        document.getElementById('modalPropId').innerText = `ID: ${prop.Id}`;
        
        // Fill Stats Box (GrLivArea, YearBuilt, OverallQual, FullBath, GarageArea)
        const statsHtml = `
            <div class="stat-item">
                <span class="label">Living Area</span>
                <span class="val">${prop.GrLivArea || 0} sqft</span>
            </div>
            <div class="stat-item">
                <span class="label">Year Built</span>
                <span class="val">${prop.YearBuilt || 'N/A'}</span>
            </div>
            <div class="stat-item">
                <span class="label">Overall Quality</span>
                <span class="val">${prop.OverallQual || 'N/A'} / 10</span>
            </div>
            <div class="stat-item">
                <span class="label">Total Rooms</span>
                <span class="val">${prop.TotRmsAbvGrd || 'N/A'}</span>
            </div>
            <div class="stat-item">
                <span class="label">Lot Area</span>
                <span class="val">${prop.LotArea || 0} sqft</span>
            </div>
            <div class="stat-item">
                <span class="label">Garage</span>
                <span class="val">${prop.GarageCars || 0} Cars</span>
            </div>
        `;
        document.getElementById('modalStats').innerHTML = statsHtml;
        
        // Animate counter for price
        const targetPrice = prop.SalePrice || 0;
        const priceEl = document.getElementById('modalPrice');
        priceEl.innerText = '$0';
        
        modal.classList.add('active');
        
        // Counter animation
        let startTimestamp = null;
        const duration = 1000;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            
            // easeOutExpo
            const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            const currentVal = targetPrice * easeProgress;
            
            priceEl.innerText = formatter.format(currentVal);
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});
