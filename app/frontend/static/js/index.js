(function() {
      function renderRooms(rooms) {
        const grid = document.getElementById('roomGrid');
        const badge = document.getElementById('roomCountBadge');

        if (!rooms || rooms.length === 0) {
          grid.innerHTML = `<div class="error-msg"><i class="fas fa-exclamation-circle"></i> Нет доступных комнат. Попробуйте позже.</div>`;
          badge.innerHTML = `<i class="fas fa-building"></i> 0 комнат`;
          return;
        }

        badge.innerHTML = `<i class="fas fa-building"></i> Доступно ${rooms.length} комнат`;

        let html = '';
        rooms.forEach(room => {
          const statusClass = room.status === 1 ? '' : 'occupied';
          const statusIcon = room.status === 1 ? 'fa-circle' : 'fa-circle';
          const statusColor = room.status === 1 ? '#2a9d8f' : '#e76f51';
          const statusText = room.status === 1 ? 'свободна' : 'занята';
          console.log(room.start_time);

          html += `
            <div class="room-card" data-id="${room.id}">
              <div class="room-icon"><i class="fas ${room.icon || 'fa-door-open'}"></i></div>
              <div class="room-name">${room.name_room}</div>
              <div class="room-desc">до ${room.capacity} чел</div>
              <div class="room-meta">
                <span><i class="fas fa-clock"></i> ${room.start_time} — ${room.end_time} UTC</span>
              </div>
              <button class="book-btn" onclick="removeToBookingPage(${room.id})">
                <i class="fas fa-calendar-plus"></i> Забронировать
              </button>
              <span class="status-badge ${statusClass}">
                <i class="fas ${statusIcon}" style="color: ${statusColor};"></i> ${statusText}
              </span>
            </div>
          `;
        });

        grid.innerHTML = html;
      }

      async function fetchRoomsFromBackend() {
        const roomsResponse = await fetch('/booking-rooms/get-all-rooms');
        const roomsData = await roomsResponse.json();
        return roomsData.rooms;
      }

      const grid = document.getElementById('roomGrid');
      grid.innerHTML = `<div class="loader"><i class="fas fa-spinner fa-pulse"></i> Загрузка комнат...</div>`;

      fetchRoomsFromBackend()
        .then(rooms => {
          renderRooms(rooms);
        })
        .catch(error => {
          grid.innerHTML = `<div class="error-msg"><i class="fas fa-exclamation-triangle"></i> Ошибка загрузки: ${error.message}</div>`;
          document.getElementById('roomCountBadge').innerHTML = `<i class="fas fa-building"></i> Ошибка`;
        });
    })();

async function removeToBookingPage(roomId) {
  try {
        const userIsAuthResponse = await fetch('/user/check-auth');
        const userIsAuthData = await userIsAuthResponse.json();
        if (!userIsAuthData.authenticated){
            alert('Для начала нужно авторизоваться');
            return;
        }

        const userRoleResponse = await fetch('/user/get/role');
        const userRoleData = await userRoleResponse.json();
        if (userRoleData.role < 1){
            alert('Для аренды комнаты обратитесь к сотрудникам компании');
            return;
        }

        const response = await fetch('/booking-rooms/room-id', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ room_id: roomId })
        });

        if (response.ok) {
            window.location.href = '/booking-rooms';
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при выборе комнаты');
    }
}

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