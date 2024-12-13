// Показать форму для нового поста
document.getElementById('new-post-btn').onclick = function() {
    document.getElementById('new-post-form').style.display = 'block';
};
// Скрыть форму для нового поста
document.getElementById('cancel-btn').onclick = function() {
    document.getElementById('new-post-form').style.display = 'none';
};

document.querySelectorAll('.rating-btn').forEach(button => {
    button.onclick = function() {
        const postId = this.getAttribute('data-post-id');
        const action = this.classList.contains('upvote') ? 'upvote' : 'downvote';
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');  // Получение CSRF токена
        const currentVoteType = this.parentNode.getAttribute('data-vote-type');

        fetch(`/rate-post/${postId}/${action}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,  // Добавление CSRF токена
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                const ratingScore = this.parentNode.querySelector('.rating-score');
                ratingScore.textContent = `Rating: ${data.rating}`;

                if (currentVoteType === action) {
                    // Если пользователь нажимает ту же кнопку, отменить голос
                    this.parentNode.setAttribute('data-vote-type', '');
                    this.classList.remove('voted');
                } else {
                    // Иначе изменить голос и обновить индикатор
                    this.parentNode.setAttribute('data-vote-type', action);
                    document.querySelectorAll(`button[data-post-id="${postId}"]`).forEach(btn => {
                        btn.classList.remove('voted');
                    });
                    this.classList.add('voted');
                }
            } else {
                alert('Something went wrong!');
            }
        })
        .catch(error => console.error('Error:', error));
    };
});
