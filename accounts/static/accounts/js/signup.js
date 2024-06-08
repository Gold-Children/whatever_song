document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');
    const signupForm = document.getElementById('signup-form');
    const emailVerificationBtn = document.getElementById('email-verification-btn');

    imageInput.addEventListener('change', function() {
        if (imageInput.files.length > 0) {
            fileNameDisplay.innerText = imageInput.files[0].name;
        } else {
            fileNameDisplay.innerText = '선택된 파일 없음';
        }
    });

    if (!signupForm) {
        console.error('signup-form이 존재하지 않습니다.');
        return;
    }

    emailVerificationBtn.addEventListener('click', function() {
        sendVerificationEmail();
    });

    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmit();
    });

    function handleFormSubmit() {
        const formData = new FormData(signupForm);
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }

        const csrfToken = getCsrfToken();

        axios.post('/api/accounts/api/signup/', formData, {
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'multipart/form-data'
            }
        })
        .then(response => {
            window.location.href = '/api/accounts/login/';
        })
        .catch(error => {
            console.log(error);
            console.error('회원가입에 실패했습니다.', error);
        });
    }

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

    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return csrfToken;
    }
});
