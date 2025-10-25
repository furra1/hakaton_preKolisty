import { api } from './api.js';
import { initHistory, addToHistory } from './history.js';
import { showResultsSection, pollCheckResults, renderResults } from './ui.js';
import { setupButtonAnimations, validateForm, setButtonState } from './utils.js';

const checkForm = document.getElementById('checkForm');
const targetInput = document.getElementById('target');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const checkIdSpan = document.getElementById('checkId');
const historyList = document.getElementById('historyList');

const checkTypes = [
    { id: 'ping', name: 'Ping', icon: 'fas fa-broadcast-tower', description: 'ICMP проверка доступности' },
    { id: 'http', name: 'HTTP', icon: 'fas fa-globe-americas', description: 'HTTP сервер' },
    { id: 'https', name: 'HTTPS', icon: 'fas fa-lock', description: 'HTTPS сервер' },
    { id: 'tcp', name: 'TCP Port', icon: 'fas fa-plug', description: 'TCP порт' },
    { id: 'traceroute', name: 'Traceroute', icon: 'fas fa-route', description: 'Трассировка маршрута' },
    { id: 'dns', name: 'DNS Lookup', icon: 'fas fa-search-location', description: 'DNS запрос' }
];

function initCheckTypes() {
    const container = document.getElementById('checkTypesContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    checkTypes.forEach(type => {
        const card = document.createElement('div');
        card.className = 'check-type-card';
        card.innerHTML = `
            <div class="check-icon">
                <i class="${type.icon}"></i>
            </div>
            <div class="check-name">${type.name}</div>
        `;
        
        card.addEventListener('click', function() {
            this.classList.toggle('selected');
            const checkbox = document.querySelector(`input[value="${type.id}"]`);
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
            }
        });
        
        container.appendChild(card);
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = 'checks';
        checkbox.value = type.id;
        checkbox.style.display = 'none';
        document.getElementById('checkForm').appendChild(checkbox);
    });
}

async function loadRealTimeData() {
    try {
        const agents = await api.getAgents();
        updateAgentsList(agents);
        updateStats(agents);
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
    }
}

function updateAgentsList(agents) {
    const agentsList = document.getElementById('agentsList');
    if (!agentsList) return;

    agentsList.innerHTML = '';
    
    agents.forEach(agent => {
        const agentItem = document.createElement('div');
        agentItem.className = 'agent-item';
        agentItem.innerHTML = `
            <div class="agent-status ${agent.status}"></div>
            <div class="agent-name">${agent.name}</div>
            <div style="margin-left: auto; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                ${agent.location}
            </div>
        `;
        agentsList.appendChild(agentItem);
    });
}

function updateStats(agents) {
    const totalAgents = agents.length;
    const onlineAgents = agents.filter(agent => agent.status === 'online').length;
    const activeChecks = agents.reduce((sum, agent) => sum + (agent.active_checks || 0), 0);
    
    const onlineAgentsEl = document.getElementById('onlineAgents');
    const activeChecksEl = document.getElementById('activeChecks');
    const successRateEl = document.getElementById('successRate');
    const avgResponseEl = document.getElementById('avgResponse');
    
    if (onlineAgentsEl) onlineAgentsEl.textContent = onlineAgents;
    if (activeChecksEl) activeChecksEl.textContent = activeChecks;
    if (successRateEl) successRateEl.textContent = '98%';
    if (avgResponseEl) avgResponseEl.textContent = '24мс';
}

function onHistoryItemClick(checkId) {
    showResultsSection(checkId, checkIdSpan, resultsSection, resultsContainer);
    pollCheckResults(checkId, resultsContainer);
}

document.addEventListener('DOMContentLoaded', async function() {
    initCheckTypes();
    
    if (historyList) {
        initHistory(historyList, onHistoryItemClick);
    }
    
    setupButtonAnimations();
    
    await loadRealTimeData();
    
    setInterval(loadRealTimeData, 10000);
});

if (checkForm) {
    checkForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const target = targetInput.value.trim();
        const checkboxes = document.querySelectorAll('input[name="checks"]:checked');
        const selectedChecks = Array.from(checkboxes).map(cb => cb.value);

        if (!validateForm(target, selectedChecks)) {
            return;
        }

        setButtonState(submitBtn, true, 'проверка...');

        try {
            const checkData = { target, checks: selectedChecks };
            const result = await api.createCheck(checkData);
            
            if (historyList) {
                addToHistory(target, selectedChecks, result.checkId, historyList, onHistoryItemClick);
            }
            
            showResultsSection(result.checkId, checkIdSpan, resultsSection, resultsContainer);
            
            pollCheckResults(result.checkId, resultsContainer);

        } catch (error) {
            console.error('Ошибка при создании проверки:', error);
            alert(`Ошибка: ${error.message}`);
        } finally {
            setButtonState(submitBtn, false, 'проверить');
        }
    });
}