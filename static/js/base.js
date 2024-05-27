document.addEventListener('DOMContentLoaded', function () {
    const accessToken = localStorage.getItem('access');
    const refreshToken = localStorage.getItem('refresh');

    axios.defaults.baseURL = 'http://127.0.0.1:8000/';
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

    const refreshTokenFunction = async () => {
        try {
            const response = await axios.post('/api/accounts/api/token/refresh/', {
                refresh: refreshToken
            });
            const newAccessToken = response.data.access;
            axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
            localStorage.setItem('access', newAccessToken);
            return newAccessToken;
        } catch (error) {
            console.error('토큰을 새로고침할 수 없습니다.', error);
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            if (window.location.pathname !== '/api/accounts/login/') {
                window.location.href = '/api/accounts/login/';
            }
        }
    };

    axios.interceptors.response.use(
        response => response,
        async error => {
            const originalRequest = error.config;
            if (error.response.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;
                const newAccessToken = await refreshTokenFunction();
                axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                return axios(originalRequest);
            }
            return Promise.reject(error);
        }
    );

});

        // CSRF 토큰을 가져오는 전역 함수
function getCsrfToken() {
    return document.getElementById('csrf-token').value;
}

function checkLoginStatus() {
    const accessToken = localStorage.getItem('access');
    const loginLogoutLink = document.getElementById('login-logout-link');
    const signupProfileLink = document.getElementById('signup-profile-link');
    if (accessToken) {
        loginLogoutLink.textContent = 'Logout';
        loginLogoutLink.style.cursor = 'pointer';
        loginLogoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
        const userId = localStorage.getItem('user_id')
        signupProfileLink.textContent ='Profile';
        signupProfileLink.href = `/api/accounts/profile/${userId}/`;
}
    else {
        loginLogoutLink.textContent = 'Login';
        loginLogoutLink.href = '/api/accounts/login/';
        signupProfileLink.textContent = 'Signup';
        signupProfileLink.href = 'api/accounts/signup/';
}}

function logout() {
    const refreshToken = localStorage.getItem('refresh');
    const csrfToken = getCsrfToken();
    axios.post('/api/accounts/logout/', { refresh: refreshToken }, {
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        window.location.href = '/api/accounts/login/';
        alert('로그아웃 성공!');
    })
    .catch(error => {
        console.error('로그아웃 실패.', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
});
