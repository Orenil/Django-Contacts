const btn = document.getElementById('button');
const menu = document.getElementById('menu-btn');
const loginButton = document.getElementById('login');

btn.addEventListener('click', () => {
    btn.classList.toggle('clicked')
    menu.classList.toggle('hidden')
    menu.classList.toggle('flex')
    loginButton.classList.toggle('hidden');
})