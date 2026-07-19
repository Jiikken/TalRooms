async function renderBookingDetail(booking, roomId) {
  const container = document.getElementById('bookingContent');
  const skeletonLoader = document.getElementById('skeletonLoader');
  const date = skeletonLoader.dataset.bookingDate || '—';
  const dateService = skeletonLoader.dataset.bookingDateService || '—';
  const adminId = skeletonLoader.dataset.bookedById || '—';
  const userResponse = await fetch('/user/get/user-by-id/' + adminId);
  const userData = await userResponse.json();

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
        <span class="value">${date}</span>
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
        <span class="label"><i class="fas fa-calendar-check"></i> Забронировал</span>
        <span class="value">${userData.first_name} ${userData.last_name}</span>
      </div>
    </div>

    <div class="action-buttons">
      <button class="btn-action primary" onclick="window.location.href = '/user/profile/${adminId}/edit-booked-room/${roomId}?date=${dateService}'">
        <i class="fas fa-edit"></i> Редактировать
      </button>
      <button class="btn-action danger" onclick="handlerDeleteBookedRoom(${booking.id}, '${dateService}')">
        <i class="fas fa-times"></i> Отменить
      </button>
    </div>
  `;

  skeletonLoader.style.display = 'none';
  container.style.display = 'block';
}

async function handlerDeleteBookedRoom(roomId, date) {
  if (confirm('Отменить бронирование?')) {
    const deleteRoomResponse = await fetch(`/booking-rooms/delete?room_id=${roomId}&date=${date}`);
    const deleteRoomData = await deleteRoomResponse.json();
    if (deleteRoomData.status){
        alert('Бронирование отменено');
        const userIdResponse = await fetch('/user/get/id');
        const userId = await userIdResponse.json();

        window.location.href = `/user/profile/${userId.user_id}`;
        return;
    }
    alert('Что-то пошло не по плану');
  }
}

async function fetchBookingDetail(bookingId) {
  try {
    const response = await fetch(`/booking-rooms/get/room/` + bookingId, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    renderBookingDetail(data.room[0], bookingId);

  } catch (error) {
    console.error('Ошибка загрузки деталей бронирования:', error);
  }
}

function getBookingIdFromUrl() {
  const url = window.location.pathname;

  const parts = url.split('/');

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
