// 기본 플레이리스트 가져오기
function fetchPlaylists() {
    axios.get('/api/playlist/data/')
        .then(response => {
            console.log(response.data); // API 응답 데이터 구조 확인
            displayPlaylist(response.data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// 검색 결과 가져오기
function searchPlaylist(query) {
    axios.get(`/api/playlist/search/?query=${query}`)
        .then(response => {
            console.log(response.data); // API 응답 데이터 구조 확인
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
            <a href="${playlist.link}" target="_blank">
                <img src="${imageUrl}" alt="${playlist.name}">
                // 🥰찜기능 🫥찜안함
                <div class="playlist-info">
                    <h2>${playlist.name}</h2>
                </div>
            </a>
            <button onclick="zzim('{playlist.playlist_id}')">
                ${playlist.is_zzim ? '🥰' : '🫥'}
            </button>
        `;
        container.appendChild(item);
    });
}

// 페이지 로드 시 기본 플레이리스트를 가져옴
document.addEventListener('DOMContentLoaded', function() {
    fetchPlaylists();

    // 검색 
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            const query = searchInput.value;
            if (query) {
                searchPlaylist(query);
            } else {
                fetchPlaylists(); // 검색어가 없으면 기본 플레이리스트를 다시 가져옴
            }
        }
    });
});
