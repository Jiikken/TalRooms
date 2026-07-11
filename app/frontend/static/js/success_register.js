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

displayAccountInfo();

document.querySelector('.success-card').addEventListener('mouseenter', function() {
  this.style.transition = 'transform 0.3s ease';
});

console.log('✅ Страница успешной регистрации загружена');
console.log('👤 Пользователь:', document.getElementById('displayName').textContent);