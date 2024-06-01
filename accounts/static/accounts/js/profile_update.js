document.addEventListener('DOMContentLoaded', function() {
    const userId = window.localStorage.getItem('user_id');
    const csrfToken = "{{ csrf_token }}"; // Django 템플릿에서 제공한 CSRF 토큰
    const token = localStorage.getItem('access');  // 저장된 토큰 가져오기

    // 프로필 정보 로드
    function loadProfile() {
        if (!token) {
            console.error('No access token found');
            return;
        }
        axios.get(`/api/accounts/api/profile/${userId}/`, {
            headers: {
                'Authorization': `Bearer ${token}`  // 인증 토큰을 헤더에 추가
            }
        })
        .then(response => {
            const data = response.data;
            document.getElementById('username').value = data.username;
            document.getElementById('email').value = data.email;
            document.getElementById('nickname').value = data.nickname;
            if (data.image) {
                document.getElementById('image-preview').src = data.image;
                document.getElementById('image-preview').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Failed to load profile:', error);
        });
    }

    loadProfile();

    document.getElementById('image').addEventListener('change', function(event) {
        const input = event.target;
        const reader = new FileReader();
        
        reader.onload = function() {
            const preview = document.getElementById('image-preview');
            preview.src = reader.result; // 파일의 내용을 미리보기 이미지로 설정
            preview.style.display = 'block'; // 미리보기 이미지를 보이도록 설정
        }
        
        reader.readAsDataURL(input.files[0]); // 파일을 읽어오기
    });

    document.getElementById('update-profile-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData();
        formData.append('username', document.getElementById('username').value);
        formData.append('nickname', document.getElementById('nickname').value);
        formData.append('email', document.getElementById('email').value);
        const imageFile = document.getElementById('image').files[0];
        if (imageFile) {
            formData.append('image', imageFile);
        }

        axios.put(`/api/accounts/api/profile/${userId}/update/`, formData, {
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'multipart/form-data',
                'Authorization': `Bearer ${token}`
            }
        })
        .then(function(response) {
            alert('프로필 변경에 성공하셨습니다!');
            window.location.href = `/api/accounts/profile/${userId}/`;
            console.log(response.data);
        })
        .catch(function(error) {
            console.error('There was an error!', error);
            if (error.response) {
                alert('업데이트 실패...: ' + (error.response.data.error || error.response.data));
            } else {
                alert('업데이트 실패.');
            }
        });
    });

    document.getElementById('change-password-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const data = {
            current_password: document.getElementById('current_password').value,
            new_password: document.getElementById('new_password').value
        };

        axios.put(`/api/accounts/api/profile/${userId}/change-password/`, data, {
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        })
        .then(function(response) {
            alert('비밀번호 변경을 성공하셨습니다!');
            window.location.href = '{% url "main" %}';
            console.log(response.data);
        })
        .catch(function(error) {
            console.error('There was an error!', error);
            if (error.response) {
                alert('비밀번호를 변경할 수 없습니다: ' + (error.response.data.error || error.response.data));
            } else {
                alert('변경 불가');
            }
        });
    });
});