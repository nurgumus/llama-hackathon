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
        
        // Debug: Log the full response to console
        console.log('📊 Full API Response:', JSON.stringify(data, null, 2));
        
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
    
    // Check if reasoning is empty or has error message
    const hasValidReasoning = data.reasoning && 
                               data.reasoning !== 'Unable to extract preferences' &&
                               data.reasoning.trim().length > 0;
    
    // Build HTML
    let html = `
        <div class="results-header">
            <h3>
                <i data-lucide="target" style="width: 28px; height: 28px;"></i>
                En İyi ${data.recommendations.length} Öneri
            </h3>
            ${hasValidReasoning ? `
                <p class="reasoning"><strong>Analiz:</strong> ${data.reasoning}</p>
            ` : `
                <p class="reasoning warning">
                    <strong>⚠️ Not:</strong> Backend sorgunuzu tam olarak anlayamadı. 
                    Lütfen daha spesifik kriterler belirtin (örn: "bütçe 30000 TL, yeşil alan, 2 park").
                </p>
                <details style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    <summary style="cursor: pointer; font-weight: 600;">🔍 Teknik Detaylar</summary>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin-top: 10px; overflow-x: auto;">Backend Response: ${data.reasoning || 'No reasoning provided'}</pre>
                </details>
            `}
        </div>
        
        <div class="filters-applied">
            <strong>Uygulanan Filtreler:</strong>
            ${data.filters_applied && data.filters_applied.length > 0 ? 
                '<ul>' + data.filters_applied.map(f => `<li>${f}</li>`).join('') + '</ul>' :
                '<p>Filtre uygulanmadı - Genel öneriler gösteriliyor</p>'
            }
            <p><em>${data.filtered_neighborhoods || 0} / ${data.total_neighborhoods || 0} mahalle kriterleri karşılıyor</em></p>
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
                
                ${rec.match_reasons && rec.match_reasons.length > 0 ? `
                    <div class="match-reasons">
                        <strong>Neden öneriliyor:</strong>
                        <ul>
                            ${rec.match_reasons.map(r => `<li>${r}</li>`).join('')}
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
                        <i data-lucide="tree-deciduous" class="icon" style="width: 32px; height: 32px; color: #16a34a;"></i>
                        <div>
                            <div class="label">Yeşil Alan</div>
                            <div class="value">${(rec.details.green_index * 100).toFixed(0)}%</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <i data-lucide="trending-up" class="icon" style="width: 32px; height: 32px; color: #667eea;"></i>
                        <div>
                            <div class="label">Refah Seviyesi</div>
                            <div class="value">${(rec.details.welfare_index * 100).toFixed(0)}%</div>
                        </div>
                    </div>
                    
                    ${rec.details.population ? `
                        <div class="detail-item">
                            <i data-lucide="users" class="icon" style="width: 32px; height: 32px; color: #f59e0b;"></i>
                            <div>
                                <div class="label">Nüfus</div>
                                <div class="value">${rec.details.population.toLocaleString('tr-TR')}</div>
                            </div>
                        </div>
                    ` : ''}
                    
                    ${amenityText ? `
                        <div class="detail-item full-width">
                            <i data-lucide="map-pin" class="icon" style="width: 32px; height: 32px; color: #dc2626;"></i>
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
    
    // Initialize Lucide icons for the new content
    lucide.createIcons();
    
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