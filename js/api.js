const API_BASE_URL = 'http://localhost:8000/api';

async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || errorData.message || `HTTP Error: ${response.status} ${response.statusText}`;
            throw new Error(errorMessage);
        }

        return response.json();
    } catch (error) {
        console.error('Request failed:', error);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Не удалось подключиться к серверу. Проверьте:\n• Бэкенд запущен на localhost:8000\n• CORS настроен правильно\n• Сетевые подключения');
        }
        
        throw error;
    }
}

export const api = {

    async createCheck(checkData) {
        return request('/check', {
            method: 'POST',
            body: JSON.stringify(checkData),
        });
    },

    
    async getCheckResult(checkId) {
        return request(`/check/${checkId}`);
    },

    
    async getAgents() {
        return request('/agents');
    },

    
    async getHistory() {
        return request('/history');
    },

    
    async deleteCheck(checkId) {
        return request(`/check/${checkId}`, {
            method: 'DELETE',
        });
    },

    
    async getStats() {
        return request('/stats');
    }
};