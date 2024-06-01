document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.getElementById('signup-form');
    console.log(signupForm);
    if (!signupForm) {
        console.error('signup-form이 존재하지 않습니다.');
        return;
    }

    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();

        console.log('폼 제출 시작');  // 폼 제출 시 로그 확인

        const formData = new FormData();
        formData.append('username', document.getElementById('username').value);
        formData.append('email', document.getElementById('email').value);
        formData.append('password', document.getElementById('password').value);
        formData.append('nickname', document.getElementById('nickname').value);
        
        const imageInput = document.getElementById('file-input');
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }

        // CSRF 토큰을 가져옵니다.
        const csrfToken = getCsrfToken();

        console.log('CSRF Token:', csrfToken);  // CSRF 토큰 확인
        axios.post('/api/accounts/api/signup/', formData, {
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'multipart/form-data' // 필수 헤더
            }
        })
        .then(response => {

            window.location.href = '/api/accounts/login/';
        })
        .catch(error => {
            console.log(error);
            console.error('회원가입에 실패했습니다.', error);
        });
    });
});