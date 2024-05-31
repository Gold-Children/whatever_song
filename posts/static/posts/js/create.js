document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('create-form').addEventListener('submit', function(e) {
        e.preventDefault();

        const userId = window.localStorage.getItem('user_id')
        const userNickname = window.localStorage.getItem('user_nickname')
        const formData = new FormData();
        formData.append('title', document.getElementById('post-title').value);
        formData.append('author', userId);
        formData.append('author_nickname', userNickname);
        formData.append('content', document.getElementById('post-content').value);
        formData.append('category', document.getElementById('post-category').value);
        formData.append('link', document.getElementById('post-url').value);

        const imageInput = document.getElementById('file-input');
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }

    
        // CSRF 토큰을 가져옵니다.
        const csrfToken = getCsrfToken();
    
        axios.post('/api/posts/api/create/', formData, {
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {

            window.location.href = '/api/posts/list/'

        })
        .catch(error => {
            console.log("error: ", error);
            console.error('게시 실패.', error);
        });
    });
});