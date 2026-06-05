document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('scroll-to-top-btn');

    if (!button) {
        return;
    }

    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            button.classList.add('show');
        } else {
            button.classList.remove('show');
        }
    });

    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});