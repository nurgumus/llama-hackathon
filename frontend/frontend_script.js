// API endpoint - update this to match your backend
const API_URL = 'http://localhost:5001/api/recommend';

// Test backend connection on load
async function testBackend() {
    console.log('🔍 Testing backend connection...');
    try {
        const response = await fetch('http://localhost:5001/health');
        const data = await response.json();
        console.log('✅ Backend ONLINE:', data);
        return true;
    } catch (error) {
        console.error('❌ Backend OFFLINE:', error);
        showError('Backend sunucusuna bağlanılamıyor! Lütfen python api_endpoint_v2.py çalıştırın.');
        return false;
    }
}

// DOM elements
const form = document.getElementById('searchForm');
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const buttonText = document.getElementById('buttonText');
const buttonLoader = document.getElementById('buttonLoader');
const loadingDiv = document.getElementById('loadingDiv');
const errorDiv = document.getElementById('errorDiv');
const errorMessage = document.getElementById('errorMessage');
const resultsDiv = document.getElementById('resultsDiv');
const resultsContent = document.getElementById('resultsContent');

// Form submit event
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Lütfen bir sorgu girin');
        return;
    }
    
    await searchProperties(query);
});

// Main search function
async function searchProperties(query) {
    console.log('🔍 Searching:', query);
    
    hideAll();
    showLoading();
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Results received:', data);
        displayResults(data);
        
    } catch (error) {
        console.error('❌ Error:', error);
        showError(error.message || 'Bilinmeyen bir hata oluştu');
    } finally {
        hideLoading();
    }
}

// Display results in a beautiful format
function displayResults(data) {
    if (!data.recommendations || data.recommendations.length === 0) {
        showError('Hiç sonuç bulunamadı. Lütfen farklı kriterler deneyin.');
        return;
    }
    
    // Build HTML
    let html = `
        <div class="results-header">
            <h3>🎯 En İyi ${data.recommendations.length} Öneri</h3>
            <p class="reasoning"><strong>Analiz:</strong> ${data.reasoning}</p>
        </div>
        
        <div class="filters-applied">
            <strong>Uygulanan Filtreler:</strong>
            ${data.filters_applied.length > 0 ? 
                '<ul>' + data.filters_applied.map(f => `<li>${f}</li>`).join('') + '</ul>' :
                '<p>Filtre uygulanmadı</p>'
            }
            <p><em>${data.filtered_neighborhoods} / ${data.total_neighborhoods} mahalle kriterleri karşılıyor</em></p>
        </div>
    `;
    
    // Add each recommendation
    data.recommendations.forEach(rec => {
        const amenities = rec.details.amenities;
        const amenityText = [
            amenities.restaurants > 0 ? `${amenities.restaurants} restoran` : null,
            amenities.schools > 0 ? `${amenities.schools} okul` : null,
            amenities.parks > 0 ? `${amenities.parks} park` : null,
            amenities.cafes > 0 ? `${amenities.cafes} kafe` : null
        ].filter(Boolean).join(', ');
        
        html += `
            <div class="recommendation-card">
                <div class="card-header">
                    <h4>#${rec.rank}. ${rec.neighborhood}, ${rec.district}</h4>
                    <span class="similarity-badge">${rec.similarity_score}% Eşleşme</span>
                </div>
                
                ${rec.match_reasons.length > 0 ? `
                    <div class="match-reasons">
                        <strong>Neden öneriliyor:</strong>
                        <ul>
                            ${rec.match_reasons.map(r => `<li>✓ ${r}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${rec.financial ? `
                    <div class="financial-info">
                        <div class="info-item">
                            <span class="label">Tahmini Kira:</span>
                            <span class="value">${rec.financial.monthly_rent.toLocaleString('tr-TR')} TRY/ay</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Bütçeden Kalan:</span>
                            <span class="value ${rec.financial.budget_remaining >= 0 ? 'positive' : 'negative'}">
                                ${rec.financial.budget_remaining.toLocaleString('tr-TR')} TRY
                            </span>
                        </div>
                    </div>
                ` : ''}
                
                <div class="details-grid">
                    <div class="detail-item">
                        <span class="icon">🌳</span>
                        <div>
                            <div class="label">Yeşil Alan</div>
                            <div class="value">${(rec.details.green_index * 100).toFixed(0)}%</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <span class="icon">🏘️</span>
                        <div>
                            <div class="label">Refah Seviyesi</div>
                            <div class="value">${(rec.details.welfare_index * 100).toFixed(0)}%</div>
                        </div>
                    </div>
                    
                    ${rec.details.population ? `
                        <div class="detail-item">
                            <span class="icon">👥</span>
                            <div>
                                <div class="label">Nüfus</div>
                                <div class="value">${rec.details.population.toLocaleString('tr-TR')}</div>
                            </div>
                        </div>
                    ` : ''}
                    
                    ${amenityText ? `
                        <div class="detail-item full-width">
                            <span class="icon">🏪</span>
                            <div>
                                <div class="label">Olanaklar</div>
                                <div class="value">${amenityText}</div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    resultsContent.innerHTML = html;
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// UI helper functions
function showLoading() {
    loadingDiv.style.display = 'block';
    submitBtn.disabled = true;
    buttonText.style.display = 'none';
    buttonLoader.style.display = 'inline';
}

function hideLoading() {
    loadingDiv.style.display = 'none';
    submitBtn.disabled = false;
    buttonText.style.display = 'inline';
    buttonLoader.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 8000);
}

function hideAll() {
    loadingDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'none';
}

// Set example query
function setExample(text) {
    queryInput.value = text;
    queryInput.focus();
}

// Copy results
function copyResults() {
    const text = resultsContent.innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert('Sonuçlar kopyalandı! 📋');
    }).catch(err => {
        console.error('Kopyalama hatası:', err);
        alert('Kopyalama başarısız');
    });
}

// Test backend on page load
window.addEventListener('load', testBackend);
