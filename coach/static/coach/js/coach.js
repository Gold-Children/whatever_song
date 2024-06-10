document.addEventListener('DOMContentLoaded', function() {
    const inputFile = document.getElementById('input_file');
    const fileNameDisplay = document.getElementById('file-name');

    inputFile.addEventListener('change', function() {
        if (inputFile.files.length > 0) {
            fileNameDisplay.innerText = inputFile.files[0].name;
        } else {
            fileNameDisplay.innerText = '선택된 파일 없음';
    }});
});

document.getElementById('inputForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const csrfToken = getCsrfToken();
    const access = window.localStorage.getItem('access');
    if (!access) {
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
            'Authorization': `Bearer ${access}`
        }
    })
    .then(response => {
        const data = response.data;
        console.log("Response data:", data); // 응답 데이터를 로그로 출력하여 확인
        if (data && data.id) {
            const dataId = data.id;
            console.log("Data ID:", dataId); // dataId가 제대로 설정되어 있는지 확인
            window.location.href = `/api/coach/result/${dataId}/`;
        } else {
            console.error("Data or Data ID is missing:", data); // 데이터 또는 ID가 없는 경우 에러 로그 출력
        }
    })
    .catch(error => {
            console.error(error);        
    });
});

function fetchMessage() {
    axios.get('/api/coach/api/status/')
        .then(response => {
            const data = response.data;
            displayMessage(data.status);
        })
        .catch(error => {
            console.error('Error fetching message:', error);
        });
}

function displayMessage(message) {
    const messageContainer = document.getElementById('message-container');
    messageContainer.innerHTML = "";  // Clear previous messages
    const messageDiv = document.createElement('div');
    messageDiv.textContent = message;
    messageContainer.appendChild(messageDiv);
}

// 5초마다 새로운 메시지를 요청
setInterval(fetchMessage, 5000);
