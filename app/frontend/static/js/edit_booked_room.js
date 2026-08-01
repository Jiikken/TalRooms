let currentBooking = null;

async function populateRooms(selectedId) {
  const select = document.getElementById('roomSelect');
  select.innerHTML = '<option value="">Выберите комнату...</option>';
  const availableRooms = await getAvailableRooms();

  availableRooms.forEach(room => {
    const option = document.createElement('option');
    option.value = room.id;
    option.textContent = `${room.name_room} (до ${room.capacity} чел.)`;
    if (room.id === selectedId) {
      option.selected = true;
    }
    select.appendChild(option);
  });
}

async function getAvailableRooms() {
    const roomsResponse = await fetch(`/booking-rooms/get-all-rooms`);
    const rooms = await roomsResponse.json();

    return rooms.rooms;
}

async function renderForm(booking) {
  currentBooking = booking;
  const room = booking.booked_room;
  const fullDate = room.date;
  const date = fullDate.split('T')[0];

  await populateRooms(room.room_id);

  document.getElementById('dateInput').value = date;

  document.getElementById('skeletonLoader').style.display = 'none';
  document.getElementById('editForm').style.display = 'block';
}

async function fetchBookingData(bookingId) {
  try {

    const urlParams = new URLSearchParams(window.location.search);
    const date = urlParams.get('date');
    const response = await fetch(`/booking-rooms/get/booked-room/${bookingId}?date=${date}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    await renderForm(data);

  } catch (error) {
    console.error('Ошибка загрузки данных для редактирования:', error);

    flashManager.error('Не удалось загрузить данные с сервера');
  }
}

function getBookingIdFromUrl() {
  const url = window.location.pathname;

  const parts = url.split('/');

  const bookedRoomIndex = parts.indexOf('edit-booked-room');
  if (bookedRoomIndex !== -1 && bookedRoomIndex + 1 < parts.length) {
    return parts[bookedRoomIndex + 1];
  }

  return null;
}

async function handleSubmit(event, roomId, date) {
  event.preventDefault();

  const saveButton = document.getElementById('saveButton');
  saveButton.disabled = true;
  saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';

  const newRoomId = parseInt(document.getElementById('roomSelect').value);
  const newDate = document.getElementById('dateInput').value;

  const formData = {
    newRoomId: newRoomId,
    newDate: newDate
  };

  if (!formData.newRoomId) {
    flashManager.error('Пожалуйста, выберите комнату');
    saveButton.disabled = false;
    saveButton.innerHTML = '<i class="fas fa-save"></i> Сохранить изменения';
    return;
  }

  const todayDateResponse = await fetch('/get/today');
  const todayDateData = await todayDateResponse.json();

  if (newDate < todayDateData.today_date){
    flashManager.error('Дата должна быть не раньше сегодняшней');
    saveButton.disabled = false;
    saveButton.innerHTML = '<i class="fas fa-save"></i> Сохранить изменения';
    return;
  }

  try {
    const bookingId = getBookingIdFromUrl();
    const response = await fetch(`/booking-rooms/change-booked-room/${roomId}?date=${date}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    flashManager.success('Бронирование успешно обновлено!');

    const bookedRoomResponse = await fetch(`/booking-rooms/get/booked-room/${newRoomId}?date=${newDate}`);
    const bookedRoomData = await bookedRoomResponse.json();
    const adminId = bookedRoomData.booked_room.booked_by_id;

    const userIdResponse = await fetch(`/user/get/id`);
    const userIdData = await userIdResponse.json();
    const userId = userIdData.user_id;

    setTimeout(() => {
      window.location.href = `/booking-rooms/booked-room/${newRoomId}?date=${newDate}&admin_id=${adminId}`;
    }, 1500);

  } catch (error) {
    console.error('Ошибка сохранения:', error);
    flashManager.error('Ошибка при сохранении. Попробуйте снова.');
    saveButton.disabled = false;
    saveButton.innerHTML = '<i class="fas fa-save"></i> Сохранить изменения';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const bookingId = getBookingIdFromUrl();
  fetchBookingData(bookingId);
});

updateAuthButton();