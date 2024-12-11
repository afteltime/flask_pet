const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;

if (currentTheme) {
    document.body.classList.remove('light-theme', 'dark-theme');
    document.body.classList.add(currentTheme);

    if (currentTheme === 'dark-theme') {
        toggleSwitch.checked = true;
    }
}

function switchTheme(e) {
    if (e.target.checked) {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        localStorage.setItem('theme', 'light-theme');
    }
}

toggleSwitch.addEventListener('change', switchTheme, false);

document.addEventListener('DOMContentLoaded', () => {
    const closeButtons = document.querySelectorAll('.flash-message .close-btn');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = e.target.closest('.flash-message');
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        });
    });
});
