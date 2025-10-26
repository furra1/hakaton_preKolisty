export function showNotification(type, title, message, duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="${icons[type] || icons.info}"></i>
        </div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    const closeNotification = () => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 400);
    };
    
    notification.querySelector('.notification-close').addEventListener('click', closeNotification);
    
    if (duration > 0) {
        setTimeout(closeNotification, duration);
    }
    
    return closeNotification;
}

export function setupButtonAnimations() {
    const checkButton = document.querySelector('.check-button');
    if (!checkButton) return;
    
    checkButton.addEventListener('mouseenter', function() {
        if (!this.disabled) {
            this.style.transform = 'translateY(-2px)';
        }
    });
    
    checkButton.addEventListener('mouseleave', function() {
        if (!this.disabled) {
            this.style.transform = 'translateY(0)';
        }
    });
}

export function validateForm(target, selectedChecks) {
    if (!target || selectedChecks.length === 0) {
        showNotification('warning', 'Неполные данные', 'Пожалуйста, заполните хост и выберите хотя бы один тип проверки.');
        return false;
    }
    
    if (target.length > 255) {
        showNotification('warning', 'Слишком длинный хост', 'Максимальная длина - 255 символов.');
        return false;
    }
    
    const hostRegex = /^[a-zA-Z0-9.-]+(?::\d+)?$/;
    if (!hostRegex.test(target)) {
        showNotification('warning', 'Некорректный хост', 'Пожалуйста, введите корректный хост или IP-адрес.');
        return false;
    }
    
    return true;
}

export function setButtonState(button, isDisabled, text = 'проверить') {
    if (!button) return;
    
    button.disabled = isDisabled;
    button.textContent = text;
}

export function formatUptime(uptime) {
    if (!uptime) return 'Неизвестно';
    
    if (typeof uptime === 'string') {
        return uptime;
    }
    
    const days = Math.floor(uptime / 86400);
    const hours = Math.floor((uptime % 86400) / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    
    if (days > 0) {
        return `${days}д ${hours}ч ${minutes}м`;
    } else if (hours > 0) {
        return `${hours}ч ${minutes}м`;
    } else {
        return `${minutes}м`;
    }
}

export function animateCounter(element, target, duration = 2000) {
    if (!element) return;
    
    const start = parseInt(element.textContent) || 0;
    const increment = target > start ? 1 : -1;
    const steps = Math.abs(target - start);
    const stepTime = Math.abs(Math.floor(duration / steps));
    
    let current = start;
    const timer = setInterval(() => {
        current += increment;
        element.textContent = current;
        
        if (current === target) {
            clearInterval(timer);
        }
    }, stepTime);
}

export function getStatusClass(status) {
    switch (status) {
        case 'online':
        case 'active':
        case 'completed':
        case 'success':
            return 'status-online';
        case 'offline':
        case 'inactive':
        case 'error':
            return 'status-offline';
        case 'warning':
            return 'status-warning';
        default:
            return 'status-offline';
    }
}

export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

export function generateId(prefix = '') {
    return prefix + Math.random().toString(36).substr(2, 9);
}

export function checkBrowserSupport() {
    const supports = {
        fetch: typeof fetch === 'function',
        promise: typeof Promise === 'function',
        localStorage: typeof localStorage !== 'undefined',
        history: typeof history !== 'undefined'
    };
    
    return supports;
}