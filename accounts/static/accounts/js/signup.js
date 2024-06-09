document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');

    imageInput.addEventListener('change', function() {
        if (imageInput.files.length > 0) {
            fileNameDisplay.innerText = imageInput.files[0].name;
        } else {
            fileNameDisplay.innerText = '선택된 파일 없음';
    }});

    const signupForm = document.getElementById('signup-form');
    if (!signupForm) {
        console.error('signup-form이 존재하지 않습니다.');
        return;
    }

        // CSRF 토큰을 가져옵니다.
        const csrfToken = getCsrfToken();
        
        const emailVerificationBtn = document.getElementById('email-verification-btn'); // 이메일 인증 버튼 선택
        // 이메일 인증 버튼 클릭 시 이메일 인증 요청
        emailVerificationBtn.addEventListener('click', function() {
            sendVerificationEmail();
        });
        // 이메일 인증 요청을 서버로 보내는 함수
        function sendVerificationEmail() {
            const email = document.getElementById('email').value;
            const csrfToken = getCsrfToken();
        
            fetch("/api/accounts/send-verification-email/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ 'email': email })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || response.statusText);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('이메일 인증 요청에 실패했습니다. 다시 시도해주세요.');
            });
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
