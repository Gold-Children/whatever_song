// 기본 플레이리스트 가져오기
function fetchPlaylists() {
    axios.get('http://127.0.0.1:8000/api/playlist/')
        .then(response => {
            displayPlaylist(response.data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}


// 검색 결과 가져오기
function searchPlaylist(query) {
    axios.get(`http://127.0.0.1:8000/api/playlist/search/?query=${query}`)
        .then(response => {
            displayPlaylist(response.data);
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}


// 플레이리스트 표시
function displayPlaylist(playlists) {
    const container = document.getElementById('playlist-container');
    container.innerHTML = ''; // 기존 내용을 지움

    playlists.forEach(playlist => {
        const item = document.createElement('div');
        item.className = 'playlist-item';
        
        // 이미지 URL이 존재하는지 확인하고 설정
        const imageUrl = playlist.image_url || 'https://via.placeholder.com/150';
        
        item.innerHTML = `
            <img src="${imageUrl}" alt="${playlist.name}">
            <div class="playlist-info">
                <h2>${playlist.name}</h2>
                <a href="${playlist.link}" target="_blank">듣기</a>
            </div>
        `;
        container.appendChild(item);
    });
}


// 페이지 로드 시 기본 플레이리스트를 가져옴
document.addEventListener('DOMContentLoaded', function() {
    fetchPlaylists();

    // 검색 버튼 클릭 이벤트
    const searchButton = document.getElementById('search-btn');
    searchButton.addEventListener('click', function() {
        const query = document.getElementById('search-input').value;
        if (query) {
            searchPlaylist(query);
        } else {
            fetchPlaylists(); // 검색어가 없으면 기본 플레이리스트를 다시 가져옴
        }
    });
});
