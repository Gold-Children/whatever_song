document.getElementById('inputForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const csrfToken = getCsrfToken();
    const accessToken = window.localStorage.getItem('access');
    if (!accessToken) {
        alert('로그인이 필요합니다.');
        window.location.href = '/api/accounts/login/';
        return;
    }

    const youtubeUrl = document.getElementById('youtube_url').value;
    const inputFile = document.getElementById('input_file').files[0];

    const formData = new FormData();
    formData.append('youtube_url', youtubeUrl);
    formData.append('input_file', inputFile);

    axios.post('/api/coach/api/input/', formData,{ 
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        const data = response.data;
        const dataId = data.id;
        window.location.href = `/api/coach/result/${dataId}/`;
    })
    .catch(error => {
            console.error(error);        
    });
});