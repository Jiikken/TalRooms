async function loadRooms() {
  const roomList = document.getElementById('roomList');

  try {
    const response = await fetch('/booking-rooms/get-all-rooms');
    const rooms = await response.json();
    const _roomId = document.getElementById('roomId').value;
    let _roomName = '';
    for (let room of rooms.rooms) {
      if (room.id == _roomId) {
        _roomName = room.name_room;
      }
    }
    renderRooms(rooms.rooms);
    const firstAvailable = rooms.rooms.find(r => !r.isOccupied) || rooms[0];
    if (firstAvailable) {
      const firstElement = document.querySelector(`.room-item[data-room-id="${firstAvailable.id}"]`);
      if (firstElement) {
        selectRoom(firstElement, _roomId, _roomName);
      }
    }

  } catch (error) {
    console.error('Ошибка загрузки комнат:', error);
    roomList.innerHTML = `
      <div style="text-align:center; padding:2rem; color:#b13e30;">
        <i class="fas fa-exclamation-triangle" style="font-size:2rem;"></i>
        <p style="margin-top:8px;">Не удалось загрузить комнаты. Попробуйте позже.</p>
      </div>
    `;
  }
}

function renderRooms(rooms) {
  const roomList = document.getElementById('roomList');

  if (!rooms || rooms.length === 0) {
    roomList.innerHTML = `
      <div style="text-align:center; padding:2rem; color:#5b6f89;">
        <i class="fas fa-door-closed" style="font-size:2rem;"></i>
        <p style="margin-top:8px;">Нет доступных комнат</p>
      </div>
    `;
    return;
  }
  roomList.innerHTML = rooms.map(room => {
        const statusClass = room.isOccupied ? 'occupied' : '';
        const statusText = room.isOccupied
          ? (room.occupiedUntil ? `занята до ${room.occupiedUntil}` : 'занята')
          : 'свободна';
        const iconMap = {
          12: 'users',
          6: 'user-tie',
          20: 'chalkboard',
          8: 'microphone'
        };
        const icon = iconMap[room.capacity] || 'door-open';

        return `
          <div class="room-item" data-room-id="${room.id}" data-room-name="${room.name_room}" onclick="selectRoom(this, '${room.id}', '${room.name_room}')">
            <div class="room-info">
              <div class="room-icon-sm"><i class="fas fa-${icon}"></i></div>
              <div class="room-info-text">
                <div class="name">${room.name_room}</div>
                <div class="meta">
                  <span><i class="fas fa-user"></i> до ${room.capacity} чел</span>
                </div>
              </div>
            </div>
            <div class="status-badge ${statusClass}"><i class="fas fa-circle"></i> ${statusText}</div>
          </div>
        `;
      }).join('');
    }

function selectRoom(element, roomId, roomName) {
  document.querySelectorAll('.room-item').forEach(item => {
    item.classList.remove('selected');
  });
  element.classList.add('selected');

  document.getElementById('roomId').value = roomId;
  document.getElementById('roomNameDisplay').textContent = roomName;

  const nameDisplay = document.getElementById('roomNameDisplay');
  nameDisplay.style.transition = '0.15s';
  nameDisplay.style.color = '#2a7de1';
  setTimeout(() => { nameDisplay.style.color = ''; }, 300);
}

async function handleBooking(event) {
  event.preventDefault();

  const idEmployeeResponse = await fetch('/user/get/id');
  const idEmployeeData = await idEmployeeResponse.json();

  const employeeId = idEmployeeData.user_id;
  const clientId = document.getElementById('userId').value.trim();
  const roomId = document.getElementById('roomId').value.trim();
  const roomName = document.getElementById('roomNameDisplay').textContent;
  const date = document.getElementById('bookingDate').value;
  const todayDateResponse = await fetch('/get/today');
  const todayDateData = await todayDateResponse.json();

  if (date < todayDateData.today_date){
    alert('Дата должна быть не раньше сегодняшней');
    return;
  }

  if (!clientId || !roomId || !date) {
    alert('⚠️ Пожалуйста, заполните все поля.');
    return;
  }

  const userExistsResponse = await fetch('/user/get/user-by-id/' + clientId);
  const userExistsData = await userExistsResponse.json();

  if (!userExistsData){
    alert('Пользователя нет или он неактивен');
    return;
  }

  const bookingData = { employeeId, clientId, roomId, date };
  const response = await fetch('/booking-rooms/book-room', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookingData)
  });
  const dataResponse = await response.json();

  if (dataResponse.booking == 'null'){
    alert('Комната уже забронирована на это время');
    return;
  }

  const message = `✅ Бронирование успешно!\n\n` +
    `👤 Сотрудник ID: ${employeeId}\n` +
    `👤 Арендатор ID: ${clientId}\n` +
    `🚪 Комната: ${roomName} (ID: ${roomId})\n` +
    `📅 Дата: ${date}\n` +
    `Статус: подтверждено`;

  alert(message);
}

document.addEventListener('DOMContentLoaded', function() {
  loadRooms();
});

updateAuthButton();