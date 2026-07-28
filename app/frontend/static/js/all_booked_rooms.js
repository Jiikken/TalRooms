async function renderBookings(bookings, filter = 'all') {
  const container = document.getElementById('bookingsContent');

  const total = bookings.length;

  container.innerHTML = `
    <div class="stats-bar">
      <span class="stat-item"><i class="fas fa-calendar-check"></i> Всего: <span class="number">${total}</span></span>
      ${filter !== 'all' ? `<span class="stat-item" style="margin-left: auto;"><i class="fas fa-filter"></i> Фильтр: ${filter === 'upcoming' ? 'Предстоят' : filter === 'past' ? 'Завершены' : 'Отменены'}</span>` : ''}
    </div>
    ${bookings.map(booking => {
      const dateAndTime = booking.date;
      const date = dateAndTime.split('T')[0]
      return `
        <div class="booking-item" data-id="${booking.id}">
          <div class="booking-info">
            <span class="room"><i class="fas fa-door-open"></i> ${booking.room.name_room}</span>
            <span class="meta"><i class="far fa-calendar-alt"></i> ${date}</span>
            <span class="meta"><i class="far fa-clock"></i> ${booking.room.start_time} – ${booking.room.end_time} UTC</span>
          </div>
          <div class="booking-actions">
            <button class="btn-action-icon edit" onclick="editBooking('${booking.room_id}', '${date}')" title="Редактировать">
              <i class="fas fa-pen"></i>
            </button>
            <button class="btn-action-icon delete" onclick="deleteBooking('${booking.room_id}', '${date}')" title="Удалить">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      `;
    }).join('')}
  `;

  container.style.display = 'block';
  document.getElementById('skeletonLoader').style.display = 'none';
}

async function editBooking(roomId, date) {
  const userIdResponse = await fetch(`/user/get/id`);
  const userIdData = await userIdResponse.json();
  const userId = userIdData.user_id;

  window.location.href = `/user/profile/${userId}/edit-booked-room/${roomId}?date=${date}`;
}

async function deleteBooking(roomId, date) {
  if (confirm(`Удалить бронирование #${roomId}?`)) {
    const deleteResponse = await fetch(`/booking-rooms/delete?room_id=${roomId}&date=${date}`);
    const deleteData = await deleteResponse.json();
    const deleteStatus = deleteData.status;

    if (deleteStatus){
      alert(`Бронирование комнаты #${roomId} удалено`);
      fetchBookings();
    }
    alert(`Удаление сорвалось`);
  }
}

document.querySelectorAll('.btn-filter').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    const filter = this.dataset.filter;
    if (window.currentBookings) {
      renderBookings(window.currentBookings, filter);
    }
  });
});

async function fetchBookings() {
  try {
    const response = await fetch('/booking-rooms/get/all-booked-rooms', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    window.currentBookings = data.all_booked_rooms;

    const activeFilter = document.querySelector('.btn-filter.active');
    const filter = activeFilter ? activeFilter.dataset.filter : 'all';
    await renderBookings(data.all_booked_rooms, filter);

  } catch (error) {
    console.error('Ошибка загрузки бронирований:', error);
  }
}

document.addEventListener('DOMContentLoaded', fetchBookings);

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