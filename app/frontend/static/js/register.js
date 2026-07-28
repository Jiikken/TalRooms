const form = document.getElementById('registerForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirmInput = document.getElementById('confirmPassword');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');
const termsCheckbox = document.getElementById('terms');

const str1 = document.getElementById('str1');
const str2 = document.getElementById('str2');
const str3 = document.getElementById('str3');
const strengthText = document.getElementById('strengthText');

function checkPasswordStrength(password) {
  let score = 0;
  if (password.length >= 8) score++;
  if (password.match(/[a-z]/) && password.match(/[A-Z]/)) score++;
  if (password.match(/[0-9]/) && password.match(/[^a-zA-Z0-9]/)) score++;
  return score;
}

async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

function updateStrengthIndicator(password) {
  const score = checkPasswordStrength(password);

[str1, str2, str3].forEach(el => {
  el.className = 'segment';
});

if (password.length === 0) {
  strengthText.textContent = 'Слабый';
  return;
}

if (score === 0) {
  str1.classList.add('active', 'weak');
  strengthText.textContent = 'Слабый';
} else if (score === 1) {
  str1.classList.add('active', 'weak');
  str2.classList.add('active', 'medium');
  strengthText.textContent = 'Средний';
} else if (score === 2) {
  str1.classList.add('active', 'weak');
  str2.classList.add('active', 'medium');
  str3.classList.add('active', 'strong');
  strengthText.textContent = 'Сильный';
} else {
  str1.classList.add('active', 'weak');
  str2.classList.add('active', 'medium');
  str3.classList.add('active', 'strong');
  strengthText.textContent = 'Отличный';
    }
}

passwordInput.addEventListener('input', function() {
  updateStrengthIndicator(this.value);
});

emailInput.addEventListener('blur', function() {
  const email = this.value;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (email && !emailRegex.test(email)) {
    this.classList.add('error');
    emailError.classList.add('show');
  } else {
    this.classList.remove('error');
    emailError.classList.remove('show');
  }
});

function checkPasswordsMatch() {
  const password = passwordInput.value;
  const confirm = confirmInput.value;

  if (confirm && password !== confirm) {
    confirmInput.classList.add('error');
    passwordError.classList.add('show');
    return false;
  } else {
    confirmInput.classList.remove('error');
    passwordError.classList.remove('show');
    return true;
  }
}

confirmInput.addEventListener('input', checkPasswordsMatch);
passwordInput.addEventListener('input', function() {
  if (confirmInput.value) {
    checkPasswordsMatch();
  }
});

form.addEventListener('submit', async function(e) {
  e.preventDefault();

  const firstName = document.getElementById('firstName').value;
  const lastName = document.getElementById('lastName').value;
  const email = emailInput.value;
  const password = passwordInput.value;
  const confirm = confirmInput.value;

  if (!firstName || !lastName || !email || !password || !confirm) {
    flashMessage.warning('⚠️ Пожалуйста, заполните все поля');
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    emailInput.classList.add('error');
    emailError.classList.add('show');
    flashMessage.warning('⚠️ Введите корректный email');
    return;
  }

  if (password.length < 8) {
    flashMessage.warning('⚠️ Пароль должен содержать минимум 8 символов');
    return;
  }

  if (password !== confirm) {
    confirmInput.classList.add('error');
    passwordError.classList.add('show');
    flashMessage.warning('⚠️ Пароли не совпадают');
    return;
  }

  if (!termsCheckbox.checked) {
    flashMessage.warning('⚠️ Пожалуйста, примите условия использования');
    return;
  }

  try {
    const _responseCheckUser = await fetch('/user/check-user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email
      })
    });

    const _resultCheckUser = await _responseCheckUser.json();

    if (!_resultCheckUser.exists) {
        const _form = document.createElement('form');
        _form.method = 'POST';
        _form.action = '/auth/register-user';

        const fields = { firstName, lastName, email, password };
        for (const [key, value] of Object.entries(fields)) {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = key;
          input.value = value;
          _form.appendChild(input);
        }

        document.body.appendChild(_form);
        _form.submit();
    } else {
      flashMessage.error('❌ Пользователь с таким email уже существует');
    }
  } catch (error) {
    console.error('Ошибка:', error);
    flashMessage.error('⚠️ Ошибка сервера. Попробуйте позже');
  }
});

document.querySelectorAll('.social-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const provider = this.classList.contains('google') ? 'Google' : 'GitHub';
    flashMessage.info(`🔐 Регистрация через ${provider} (демо-режим)`);
  });
});