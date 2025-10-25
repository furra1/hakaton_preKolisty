import { api } from './api.js';

// Хранилище для истории проверок (кеш на клиенте)
let checkHistory = JSON.parse(localStorage.getItem('checkHistory')) || [];

// Инициализация истории с загрузкой данных с сервера
export async function initHistory(historyList, onHistoryItemClick) {
    historyList.innerHTML = '<div class="loading">Загрузка истории...</div>';
    
    try {
        // Загружаем историю с сервера
        const serverHistory = await api.getHistory();
        
        // Объединяем с локальной историей (если есть)
        const mergedHistory = mergeHistories(serverHistory, checkHistory);
        
        // Сохраняем объединенную историю
        checkHistory = mergedHistory.slice(0, 50); // Ограничиваем размер
        localStorage.setItem('checkHistory', JSON.stringify(checkHistory));
        
        // Отображаем историю
        renderHistoryList(mergedHistory, historyList, onHistoryItemClick);
        
    } catch (error) {
        console.error('Ошибка загрузки истории с сервера:', error);
        
        // Если сервер недоступен, используем локальную историю
        historyList.innerHTML = '<div class="error-message">Не удалось загрузить историю с сервера. Используется локальная история.</div>';
        renderHistoryList(checkHistory, historyList, onHistoryItemClick);
    }
}

// Добавление в историю (сохраняем и локально, и на сервере)
export async function addToHistory(target, checks, checkId, historyList, onHistoryItemClick) {
    const historyItem = {
        id: checkId,
        target: target,
        checks: checks,
        status: 'pending',
        created_at: new Date().toISOString(),
        timestamp: Date.now()
    };
    
    // Добавляем в локальную историю
    checkHistory.unshift(historyItem);
    if (checkHistory.length > 50) checkHistory = checkHistory.slice(0, 50);
    localStorage.setItem('checkHistory', JSON.stringify(checkHistory));
    
    // Обновляем отображение
    if (historyList) {
        renderHistoryList(checkHistory, historyList, onHistoryItemClick);
    }
    
    // Пытаемся синхронизировать с сервером (в фоне)
    syncWithServer(historyItem).catch(error => {
        console.error('Ошибка синхронизации с сервером:', error);
    });
    
    return historyItem;
}

// Обновление статуса проверки в истории
export function updateCheckStatus(checkId, status, results = null) {
    const itemIndex = checkHistory.findIndex(item => item.id === checkId);
    if (itemIndex !== -1) {
        checkHistory[itemIndex].status = status;
        if (results) {
            checkHistory[itemIndex].results = results;
        }
        checkHistory[itemIndex].updated_at = new Date().toISOString();
        localStorage.setItem('checkHistory', JSON.stringify(checkHistory));
    }
}

// Получение элемента истории по ID
export function getHistoryItem(checkId) {
    return checkHistory.find(item => item.id === checkId);
}

// Очистка истории
export async function clearHistory(historyList, onHistoryItemClick) {
    if (confirm('Вы уверены, что хотите очистить всю историю проверок?')) {
        checkHistory = [];
        localStorage.removeItem('checkHistory');
        
        try {
            // Пытаемся очистить историю на сервере
            await api.clearHistory();
        } catch (error) {
            console.error('Ошибка очистки истории на сервере:', error);
        }
        
        if (historyList) {
            historyList.innerHTML = '<div class="empty-history">История проверок пуста</div>';
        }
    }
}

// Удаление конкретной проверки из истории
export async function deleteHistoryItem(checkId, historyList, onHistoryItemClick) {
    checkHistory = checkHistory.filter(item => item.id !== checkId);
    localStorage.setItem('checkHistory', JSON.stringify(checkHistory));
    
    try {
        // Пытаемся удалить с сервера
        await api.deleteCheck(checkId);
    } catch (error) {
        console.error('Ошибка удаления проверки с сервера:', error);
    }
    
    // Обновляем отображение
    if (historyList) {
        renderHistoryList(checkHistory, historyList, onHistoryItemClick);
    }
}

// Вспомогательные функции

// Объединение истории с сервера и локальной истории
function mergeHistories(serverHistory, localHistory) {
    const merged = [...serverHistory];
    
    // Добавляем элементы из локальной истории, которых нет на сервере
    localHistory.forEach(localItem => {
        const exists = merged.some(serverItem => serverItem.id === localItem.id);
        if (!exists) {
            merged.push(localItem);
        }
    });
    
    // Сортируем по дате (новые сверху)
    return merged.sort((a, b) => {
        const dateA = new Date(a.created_at || a.timestamp);
        const dateB = new Date(b.created_at || b.timestamp);
        return dateB - dateA;
    });
}

// Синхронизация с сервером
async function syncWithServer(historyItem) {
    try {
        // Отправляем данные на сервер
        await api.syncHistory(historyItem);
    } catch (error) {
        console.error('Ошибка синхронизации с сервером:', error);
        throw error;
    }
}

// Рендер списка истории
function renderHistoryList(history, historyList, onHistoryItemClick) {
    historyList.innerHTML = '';
    
    if (history.length === 0) {
        historyList.innerHTML = '<div class="empty-history">История проверок пуста</div>';
        return;
    }
    
    history.forEach(item => {
        const historyItem = createHistoryElement(item, onHistoryItemClick);
        historyList.appendChild(historyItem);
    });
}

// Создание элемента истории
function createHistoryElement(item, onHistoryItemClick) {
    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';
    historyItem.setAttribute('data-id', item.id);
    
    const statusClass = `status-${item.status}`;
    const statusText = getStatusText(item.status);
    const checksText = Array.isArray(item.checks) ? item.checks.join(', ') : 'не указаны';
    const dateText = formatDate(item.created_at || item.timestamp);
    
    historyItem.innerHTML = `
        <div class="history-target">${escapeHtml(item.target)}</div>
        <div class="history-date">${dateText}</div>
        <div class="history-checks">${checksText}</div>
        <div class="history-status">
            <span class="status-badge ${statusClass}">${statusText}</span>
        </div>
        <div class="history-actions">
            <button class="action-btn view-btn" data-id="${item.id}">просмотр</button>
            <button class="action-btn repeat-btn" data-id="${item.id}">повторить</button>
            <button class="action-btn delete-btn" data-id="${item.id}">удалить</button>
        </div>
    `;
    
    // Обработчики событий
    historyItem.addEventListener('click', (e) => {
        if (!e.target.closest('.history-actions')) {
            onHistoryItemClick(item.id);
        }
    });
    
    const viewBtn = historyItem.querySelector('.view-btn');
    const repeatBtn = historyItem.querySelector('.repeat-btn');
    const deleteBtn = historyItem.querySelector('.delete-btn');
    
    viewBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        onHistoryItemClick(item.id);
    });
    
    repeatBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        // Здесь можно вызвать функцию для повторения проверки
        console.log('Повтор проверки:', item.id);
    });
    
    deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        // Здесь можно вызвать функцию для удаления
        console.log('Удаление проверки:', item.id);
    });
    
    return historyItem;
}

// Получение текста статуса
function getStatusText(status) {
    switch (status) {
        case 'completed': return 'Завершено';
        case 'error': return 'Ошибка';
        case 'pending': return 'Ожидание';
        case 'running': return 'Выполняется';
        default: return status || 'Неизвестно';
    }
}

// Форматирование даты
function formatDate(dateString) {
    if (!dateString) return 'Неизвестно';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('ru-RU');
    } catch (e) {
        return dateString;
    }
}

// Экранирование HTML
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}