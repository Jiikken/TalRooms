class FlashManager {
  constructor(containerId = 'flashContainer') {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.warn('Flash container not found');
      return;
    }
    this.messages = [];
    this.autoCloseDelay = 5000; // 5 секунд
  }

  show(message, type = 'info', title = '', duration = null) {
     const id = Date.now() + Math.random();
     const autoClose = duration !== false;
     const closeDelay = duration || this.autoCloseDelay;

     const flashEl = document.createElement('div');
     flashEl.className = `flash-message ${type}`;
     flashEl.dataset.id = id;

     const icons = {
       success: 'fas fa-check-circle',
       error: 'fas fa-exclamation-circle',
       warning: 'fas fa-exclamation-triangle',
       info: 'fas fa-info-circle'
     };

     // Заголовки по умолчанию
     const defaultTitles = {
       success: 'Успешно!',
       error: 'Ошибка!',
       warning: 'Внимание!',
       info: 'Информация'
     };

     const iconClass = icons[type] || icons.info;
     const titleText = title || defaultTitles[type] || '';

     flashEl.innerHTML = `
       <div class="flash-icon">
         <i class="${iconClass}"></i>
       </div>
       <div class="flash-content">
         ${titleText ? `<div class="flash-title">${titleText}</div>` : ''}
         <div class="flash-text">${message}</div>
       </div>
       <button class="flash-close" onclick="flashManager.close(${id})">
         <i class="fas fa-times"></i>
       </button>
     `;

     this.container.appendChild(flashEl);
     this.messages.push(id);

     // Автоматическое закрытие
     if (autoClose) {
       setTimeout(() => {
         this.close(id);
       }, closeDelay);
     }

     return id;
  }

  close(id) {
    const flashEl = this.container.querySelector(`[data-id="${id}"]`);
    if (flashEl) {
      flashEl.classList.add('hiding');
      setTimeout(() => {
        flashEl.remove();
        this.messages = this.messages.filter(msgId => msgId !== id);
      }, 300);
    }
  }

  closeAll() {
    this.messages.forEach(id => this.close(id));
  }

  clear() {
    this.container.innerHTML = '';
    this.messages = [];
  }

  success(message, title = '', duration = null) {
    return this.show(message, 'success', title, duration);
  }

  error(message, title = '', duration = null) {
    return this.show(message, 'error', title, duration);
  }

  warning(message, title = '', duration = null) {
    return this.show(message, 'warning', title, duration);
  }

  info(message, title = '', duration = null) {
    return this.show(message, 'info', title, duration);
  }
}

const flashManager = new FlashManager();

window.flashManager = flashManager;