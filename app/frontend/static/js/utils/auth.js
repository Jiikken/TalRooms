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
  }

  else if (type === 'profile') {
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
