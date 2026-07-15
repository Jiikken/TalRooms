function renderBookingDetail(booking) {
  const container = document.getElementById('bookingContent');
  console.log(booking)

  container.innerHTML = `
    <div class="detail-header">
      <div class="detail-title">
        <div class="room-icon"><i class="${'fas fa-door-open'}"></i></div>
        <div>
          <h1>${booking.name_room}</h1>
          <div class="room-location">
            <i class="fas fa-map-pin"></i> ${booking.location || 'Этаж не указан'}
          </div>
        </div>
      </div>
    </div>

    <div class="detail-grid">
      <div class="detail-item">
        <span class="label"><i class="far fa-calendar-alt"></i> Дата</span>
        <span class="value">${booking.date}</span>
      </div>
      <div class="detail-item">
        <span class="label"><i class="far fa-clock"></i> Время</span>
        <span class="value">${booking.start_time} – ${booking.end_time}</span>
      </div>
      <div class="detail-item">
        <span class="label"><i class="fas fa-users"></i> Вместимость</span>
        <span class="value">${booking.capacity || '—'} чел.</span>
      </div>
      <div class="detail-item">
        <span class="label"><i class="fas fa-calendar-check"></i> Забронировано</span>
        <span class="value">${booking.bookedBy || '—'}</span>
      </div>
    </div>

    ${booking.participants && booking.participants.length > 0 ? `
      <div class="participants-section">
        <h3><i class="fas fa-user-friends"></i> Участники</h3>
        <div class="participants-list">
          ${booking.participants.map(p => `
            <span class="participant-chip">
              <i class="fas fa-user"></i> ${p.name}
              ${p.role ? `<span class="role">${p.role}</span>` : ''}
            </span>
          `).join('')}
        </div>
      </div>
    ` : ''}

    ${booking.description ? `
      <div class="description-section">
        <p><i class="fas fa-info-circle" style="color: #2a7de1; margin-right: 8px;"></i> ${booking.description}</p>
      </div>
    ` : ''}

    <div class="action-buttons">
      <button class="btn-action primary" onclick="alert('Редактирование бронирования')">
        <i class="fas fa-edit"></i> Редактировать
      </button>
      <button class="btn-action secondary" onclick="alert('Экспорт в календарь')">
        <i class="fas fa-calendar-plus"></i> В календарь
      </button>
      ${booking.status !== 'cancelled' ? `
        <button class="btn-action danger" onclick="if(confirm('Отменить бронирование?')) alert('Бронирование отменено')">
          <i class="fas fa-times"></i> Отменить
        </button>
      ` : ''}
    </div>
  `;

  document.getElementById('skeletonLoader').style.display = 'none';
  container.style.display = 'block';
}

// Функция загрузки данных с бекенда
async function fetchBookingDetail(bookingId) {
  try {
    const response = await fetch(`/booking-rooms/get/booked-room/` + bookingId, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    renderBookingDetail(data.room[0]);

  } catch (error) {
    console.error('Ошибка загрузки деталей бронирования:', error);
  }
}

function getBookingIdFromUrl() {
  // Получаем текущий URL
  const url = window.location.pathname;

  // Разбиваем URL на части
  const parts = url.split('/');

  // Ищем индекс "booked-room" и берём следующий элемент
  const bookedRoomIndex = parts.indexOf('booked-room');
  if (bookedRoomIndex !== -1 && bookedRoomIndex + 1 < parts.length) {
    return parts[bookedRoomIndex + 1];
  }

  return null;
}

document.addEventListener('DOMContentLoaded', () => {
  const bookingId = getBookingIdFromUrl();
  fetchBookingDetail(bookingId);
});

async function createAuthButton(type) {
  authContainer.innerHTML = '';

  if (type === 'login') {
    const link = document.createElement('a');
    link.href = '/auth/login';
    link.style.textDecoration = 'none';

    const button = document.createElement('button');
    button.id = 'authButton';
    button.className = 'btn-primary';
    button.innerHTML = '<i class="fas fa-sign-in-alt"></i> Вход';

    link.appendChild(button);
    authContainer.appendChild(link);
  } else if (type === 'profile') {
    const link = document.createElement('a');

    const userId = await fetch('/user/get/id');
    const dataUser = await userId.json();

    link.href = '/user/profile/' + dataUser.user_id;
    link.style.textDecoration = 'none';

    const button = document.createElement('button');
    button.id = 'authButton';
    button.className = 'btn-primary';
    button.innerHTML = '<i class="fas fa-user-circle"></i> Личный кабинет';

    link.appendChild(button);
    authContainer.appendChild(link);
  }
}

const authButton = document.getElementById('authButton');
const authButtonText = document.getElementById('authButtonText');

async function updateAuthButton() {
  const response = await fetch('/user/check-auth');
  const data = await response.json();

  if (data.authenticated) {
    createAuthButton('profile');
  } else {
    createAuthButton('login');
  }
}

updateAuthButton();

window.updateAuthButton = updateAuthButton;
