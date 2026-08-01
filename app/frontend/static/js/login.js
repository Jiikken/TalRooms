document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  if (!email || !password) {
    flashManager.error('Пожалуйста, заполните все поля');
    return;
  }

  try {
    const responseCheckUser = await fetch('/user/check-user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({email})
    });

    const resultCheckUser = await responseCheckUser.json();

    if (resultCheckUser.exists) {
      const responsePasswordCheck = await fetch('/user/check/password', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email, password })
      });

      const resultPasswordCheck = await responsePasswordCheck.json();

      if (resultPasswordCheck) {
        const response = await fetch('/auth/login-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({email})
        });

        const responseData = await response.json();
        const userId = responseData.id;

        flashManager.success("Авторизация успешна!");

        setTimeout(() => {
          window.location.href = `/auth/success-login`;
        }, 1500);

      } else {
        flashManager.error("Неверный пароль");
      }
    } else {
      flashManager.error('Пользователь не зарегистрирован');
    }
  } catch (error) {
    console.error('Ошибка:', error);
    flashManager.error('Ошибка сервера. Попробуйте позже');
  }
});

document.querySelectorAll('.social-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const provider = this.classList.contains('google') ? 'Google' : 'GitHub';
    flashManager.info(`Вход через ${provider} (демо-режим)`);
  });
});