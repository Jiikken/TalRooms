function getQueryParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    firstName: params.get('firstName') || 'Иван',
    lastName: params.get('lastName') || 'Петров',
    email: params.get('email') || 'ivan@company.ru'
  };
}

function displayAccountInfo() {
  const data = getQueryParams();

  document.getElementById('bookingCount').textContent = Math.floor(Math.random() * 20) + 5;
  document.getElementById('meetingHours').textContent = Math.floor(Math.random() * 80) + 20;
  document.getElementById('roomCount').textContent = Math.floor(Math.random() * 6) + 2;
  document.getElementById('notificationCount').textContent = Math.floor(Math.random() * 5) + 1;
}

async function handleLogout() {
  if (!confirm('Вы уверены?')) return;

  try {
    const response = await fetch('/auth/logout', {
      method: 'POST'
    });

    if (response.ok) {
      window.location.href = '/auth/login';
    }
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

displayAccountInfo();

setInterval(() => {
  const statusBadge = document.querySelector('.badge-online');
  if (statusBadge) {
    statusBadge.style.opacity = '0.7';
    setTimeout(() => {
      statusBadge.style.opacity = '1';
    }, 300);
  }
}, 3000);

console.log('✅ Страница успешной авторизации загружена');
console.log('👤 Пользователь:', document.getElementById('displayName').textContent);