document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');

    imageInput.addEventListener('change', function() {
        if (imageInput.files.length > 0) {
            fileNameDisplay.innerText = imageInput.files[0].name;
        } else {
            fileNameDisplay.innerText = '선택된 파일 없음';
    }});
});

document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.getElementById('signup-form');
    if (!signupForm) {
        console.error('signup-form이 존재하지 않습니다.');
        return;
    }

    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append('username', document.getElementById('username').value);
        formData.append('email', document.getElementById('email').value);
        formData.append('password', document.getElementById('password').value);
        formData.append('nickname', document.getElementById('nickname').value);
        const imageInput = document.getElementById('file-input');
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }

        sendVerificationEmail();
        
        // CSRF 토큰을 가져옵니다.
        const csrfToken = getCsrfToken();

        function sendVerificationEmail() {
            const email = document.getElementById('email').value;
        
            fetch("/api/accounts/send-verification-email/", {  // 전체 경로 확인
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json().then(data => {
                if (!response.ok) {
                    throw new Error(data.error || response.statusText);
                }
                return data;
            }))
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (error.message === 'No user with this email exists.') {
                    alert('입력하신 이메일 주소로 가입된 사용자가 없습니다.');
                } else {
                    alert(  error.message);
                }
            });
        }

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