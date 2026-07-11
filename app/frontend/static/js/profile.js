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
  const roleResponse = await fetch('/user/get-role');
  const roleData = await roleResponse.json();

  if (roleData.role >= 1){
     createBookButton();
  }
  if (roleData.role === 2){
     createAppendEmployeeButton();
  }
}

function renderBookings(bookings) {
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
    let statusClass = 'upcoming';
    let statusIcon = 'fa-clock';
    let statusText = 'Предстоит';

    switch(booking.status) {
      case 'completed':
        statusClass = 'past';
        statusIcon = 'fa-check';
        statusText = 'Завершено';
        break;
      case 'cancelled':
        statusClass = 'cancelled';
        statusIcon = 'fa-times';
        statusText = 'Отменено';
        break;
      case 'upcoming':
      default:
        statusClass = 'upcoming';
        statusIcon = 'fa-clock';
        statusText = 'Предстоит';
        break;
    }

    return `
      <div class="booking-item">
        <div class="booking-info">
          <span class="room">${booking.room}</span>
          <span class="meta">
            <i class="far fa-calendar-alt"></i>
            ${booking.date} · ${booking.timeStart} – ${booking.timeEnd}
          </span>
        </div>
        <span class="booking-status ${statusClass}">
          <i class="fas ${statusIcon}"></i> ${statusText}
        </span>
      </div>
    `;
  }).join('');
}

async function fetchBookings() {
  try {

    const userIdResponse = await fetch('/user/get-id');
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

    renderBookings(data.booking_rooms);

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
    errorNotice.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Не удалось загрузить данные с сервера. Показаны примеры.`;
    container.prepend(errorNotice);
  }
}
  document.addEventListener('DOMContentLoaded', fetchBookings);

updateButtons();

window.updateButtons = updateButtons;