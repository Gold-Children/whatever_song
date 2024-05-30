document.addEventListener('DOMContentLoaded', function() {
    const userId = window.localStorage.getItem('user_id');  // 템플릿 태그를 사용해 현재 로그인한 유저의 ID를 가져옴
    function loadProfile() {
        const token = localStorage.getItem('access');  // 저장된 토큰 가져오기
        if (!token) {
            console.error('No access token found');
            return;
        }
        axios.get(`/api/accounts/api/profile/${userId}/`,{
            headers: {
                'Authorization': `Bearer ${token}`  // 인증 토큰을 헤더에 추가
            }
        })
            .then(response => {
                const data = response.data;
                document.getElementById('username').textContent = data.username;
                document.getElementById('email').textContent = data.email;
                document.getElementById('nickname').textContent = data.nickname;
                if (data.image) {
                    document.getElementById('profile-picture').src = data.image;
                }
            })
            .catch(error => {
                console.error('Failed to load profile:', error);
            });
    }

    loadProfile();
    
    const menuLinks = document.querySelectorAll('.menu a');

    menuLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            menuLinks.forEach(link => link.classList.remove('active'));
            this.classList.add('active');
        });
    });
    document.getElementById('home-button').addEventListener('click', function() {
        window.location.href = '/api/accounts/api/main/';  // 메인 페이지로 이동
    });
});

