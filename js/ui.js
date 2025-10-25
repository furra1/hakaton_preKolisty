import { api } from './api.js';

export function showResultsSection(checkId, checkIdSpan, resultsSection, resultsContainer) {
    if (!checkIdSpan || !resultsSection || !resultsContainer) return;
    
    checkIdSpan.textContent = `ID проверки: ${checkId}`;
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = '<div class="agent-result"><h4><i class="fas fa-spinner fa-spin"></i> Проверка запущена, ожидаем результаты...</h4></div>';
    
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

export function renderResults(data, resultsContainer) {
    if (!resultsContainer) return;
    
    if (!data.results || data.results.length === 0) {
        resultsContainer.innerHTML = '<div class="agent-result"><h4>Результаты пока не доступны...</h4></div>';
        return;
    }

    let html = '';

    data.results.forEach(agentResult => {
        const statusClass = getStatusClass(agentResult.status);
        const statusText = getStatusText(agentResult.status);
        const icon = getStatusIcon(agentResult.status);

        html += `
            <div class="agent-result">
                <h4>
                    <i class="${icon}"></i> Агент: ${agentResult.agent_id || 'Unknown'} 
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </h4>
                ${agentResult.log ? `<div class="log-entry">${escapeHtml(agentResult.log)}</div>` : ''}
                ${agentResult.result ? `<div class="log-entry">${escapeHtml(JSON.stringify(agentResult.result, null, 2))}</div>` : ''}
            </div>
        `;
    });

    resultsContainer.innerHTML = html;
}

export async function pollCheckResults(checkId, resultsContainer) {
    if (!resultsContainer) return;
    
    const maxAttempts = 60;
    const interval = 2000;
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
            const result = await api.getCheckResult(checkId);
            renderResults(result, resultsContainer);
            
            if (isCheckComplete(result)) {
                console.log('Проверка завершена');
                break;
            }
            
            await new Promise(resolve => setTimeout(resolve, interval));
            
        } catch (error) {
            console.error('Ошибка при получении результатов:', error);
            resultsContainer.innerHTML = `<div class="agent-result"><h4 class="status-error">Ошибка: ${error.message}</h4></div>`;
            break;
        }
    }
}

function isCheckComplete(result) {
    if (!result.results) return false;
    return result.results.every(agentResult => 
        agentResult.status === 'completed' || agentResult.status === 'error'
    );
}

function getStatusClass(status) {
    switch (status) {
        case 'completed': return 'status-success';
        case 'error': return 'status-error';
        case 'pending': 
        default: return 'status-pending';
    }
}

function getStatusText(status) {
    switch (status) {
        case 'completed': return 'Завершено';
        case 'error': return 'Ошибка';
        case 'pending': 
        default: return 'В процессе';
    }
}

function getStatusIcon(status) {
    switch (status) {
        case 'completed': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'pending': 
        default: return 'fas fa-spinner fa-spin';
    }
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}