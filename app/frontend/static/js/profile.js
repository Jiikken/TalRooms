async function handleLogout() {
  if (!confirm('Вы уверены?')) return;

  try {
    const response = await fetch('/auth/logout', {
      method: 'POST'
    });

    if (response.ok) {
      window.location.href = '/';
    }
  } catch (error) {
    console.error('Ошибка:', error);
  }
}


async function createBookButton() {
  const container = document.getElementById('bookContainer');
  const newButton = document.createElement('button');
  newButton.className = 'btn-edit';
  newButton.innerHTML = '<i class="fas fa-plus"></i>Создать новую бронь';
  newButton.addEventListener('click', function() {
    window.location.href = '/booking-rooms';
  });

  container.insertBefore(newButton, container.firstChild);
}

async function createViewAllBookedButton() {
  const container = document.getElementById('bookContainer');
  const newButton = document.createElement('button');
  newButton.className = 'btn-edit';
  newButton.innerHTML = '<i class="fas fa-calendar-plus"></i> Посмотреть все брони';
  newButton.addEventListener('click', function() {
    window.location.href = '/booking-rooms/all-booked-rooms';
  });

  container.insertBefore(newButton, container.firstChild);
}

async function createAppendEmployeeButton() {
  const container = document.getElementById('editContainer');
  const newButton = document.createElement('button');
  newButton.className = 'btn-edit';
  newButton.innerHTML = '<i class="fas fa-pen"></i> Редактировать штат'

  container.insertBefore(newButton, container.firstChild)
}

async function updateButtons() {
  const roleResponse = await fetch('/user/get/role');
  const roleData = await roleResponse.json();

  if (roleData.role >= 1){
     createBookButton();
  }
  if (roleData.role === 2){
     createAppendEmployeeButton();
     createViewAllBookedButton();
  }
}

function renderBookings(bookings, userId) {
  const container = document.getElementById('bookingsList');

  if (!bookings || bookings.length === 0) {
    container.innerHTML = `
      <div style="padding: 2rem; text-align: center; color: #7b90ab;">
        <i class="fas fa-calendar-times" style="font-size: 2rem; display: block; margin-bottom: 0.5rem;"></i>
        У вас пока нет бронирований
      </div>
    `;
    return;
  }

  container.innerHTML = bookings.map(booking => {
    const date = booking.date.split('T')[0]
    return `
      <div class="booking-item">
        <div class="booking-info">
          <span class="room">${booking.room.name_room}</span>
          <span class="meta">
            <i class="far fa-calendar-alt"></i>
            ${date} | ${booking.room.start_time} – ${booking.room.end_time} UTC
          </span>
        </div>
        <div style="margin-top: 0.5rem; display: flex; justify-content: flex-end;">
          <div id="bookContainer" style="display: flex; gap: 6px; align-items: center;">
            <a href="/user/profile/${userId}/booked-room/${booking.room.id}?date=${date}&admin_id=${booking.booked_by_id}" style="text-decoration: none;">
              <button class="btn-booking-small">
                <i class="fas fa-calendar-plus"></i> Детали
              </button>
            </a>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

async function fetchBookings() {
  try {

    const userIdResponse = await fetch('/user/get/id');
    const userIdData = await userIdResponse.json();

    const response = await fetch('/booking-rooms/get-my-booked-rooms/' + userIdData.user_id, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    renderBookings(data.booking_rooms, userIdData.user_id);

  } catch (error) {
    console.error('Ошибка загрузки бронирований:', error);

    const container = document.getElementById('bookingsList');
    const errorNotice = document.createElement('div');
    errorNotice.style.cssText = `
      padding: 0.5rem 1rem;
      margin-top: 0.5rem;
      background: #fff0f0;
      border-radius: 8px;
      color: #d32f2f;
      font-size: 0.85rem;
      border: 1px solid #ffcdd2;
    `;
    errorNotice.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Не удалось загрузить данные с сервера`;
    container.prepend(errorNotice);
  }
}
  document.addEventListener('DOMContentLoaded', fetchBookings);

updateButtons();

window.updateButtons = updateButtons;