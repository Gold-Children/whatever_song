document.addEventListener('DOMContentLoaded', function() {
    const profileuserId = window.location.pathname.split('/').slice(-2, -1)[0];
    function loadProfile() {
        const token = window.localStorage.getItem('access');  // 저장된 토큰 가져오기
        if (!token) {
            console.error('No access token found');
            return;
        }
        axios.get(`/api/accounts/api/profile/${profileuserId}/`,{
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
                loadEditProfileButton()
            })
            .catch(error => {
                console.error('Failed to load profile:', error);
            });
        };
            function loadEditProfileButton() {
                const userId = window.localStorage.getItem('user_id');
                const editProfileButton = document.getElementById("edit-profile-button");
                if (userId === profileuserId) {
                    editProfileButton.href = `/api/accounts/profile/${profileuserId}/edit/`;
                    editProfileButton.style.display = "block";
                } else {
                    editProfileButton.style.display = "none";
                    }
                };
        
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



// user_profile_playlist
function displayPlaylist(playlists) {
    const container = document.getElementById('zzim-playlist-container');
    container.innerHTML = ''; 

    playlists.forEach(playlist => {
        const item = document.createElement('div');
        item.className = 'playlist-item';
        
        // 이미지 URL이 존재하는지 확인하고 설정
        const imageUrl = playlist.image_url || 'https://via.placeholder.com/150';

        // 콘솔에 playlist 데이터 전체 출력
        console.log(`Playlist Data: ${JSON.stringify(playlist)}`);
        
        // playlist.id를 고유 식별자로 사용
        const playlistId = playlist.id;
        item.innerHTML = `
            <a href="${playlist.link}" target="_blank">
                <img src="${imageUrl}" alt="${playlist.name}">
                <div class="playlist-info">
                    <h2>${playlist.name}</h2>
                </div> 
            </a>
            <button class="zzim-button" data-id="${playlistId}">🙂</button>
        `;
        container.appendChild(item);
    });

    // 찜 버튼
    const zzimButtons = document.querySelectorAll('.zzim-button');
        zzimButtons.forEach(button => {
            button.addEventListener('click', function(event) {
            event.preventDefault();
            const playlistId = this.getAttribute('data-id');
            console.log(`Clicked Playlist ID: ${playlistId}`); // 콘솔에 클릭된 playlistId 값 출력
            toggleZzim(playlistId, this);
        });
    });
}

// 로그인 여부를 확인하고, 로그인 된 상태라면 해당 user의 찜한 playlist.id를 가져와 일치하는 찜 버튼의 설정을 바꿈
function checkUserZzimPlaylists() {
    const csrfToken = getCsrfToken();
    const accessToken = window.localStorage.getItem('access');
    axios.get('/api/playlist/user-zzim/', {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        const zzimPlaylists = response.data;
        const zzimPlaylistIds = zzimPlaylists.map(aaa => aaa.playlist_id); // 모든 값을 문자열로 변환
        const zzimButtons = document.querySelectorAll('.zzim-button');
        zzimButtons.forEach(button => {
            const playlistId = button.getAttribute('data-id');
            if (zzimPlaylistIds.includes(playlistId)) {
                button.textContent = '🥰'; // 이미 찜한 버튼 변경
            }
        });
    })
    .catch(error => {
        console.error('Error fetching user zzim playlists:', error);
    });
}

// 찜하기 상태 변경. 
function toggleZzim(playlistId, button) {
    if (!playlistId) {
        console.error('Playlist ID is undefined');
        return;
    }
    const csrfToken = getCsrfToken();
    const accessToken = window.localStorage.getItem('access');
    axios.post(`/api/playlist/zzim/${playlistId}/`, playlistId, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}` 
        }
    })
    .then(response => {
        console.log(response.data.message);
        if (response.data.message.includes('추가')) {
            button.textContent = '🥰';
        } else {
            button.textContent = '🙂';
        }
    })
    .catch(error => {
        if (error.response && error.response.status === 401) {
            alert('로그인이 필요합니다.');
            window.location.href = '/api/accounts/login/';
        } else {
            console.error('Error toggling zzim:', error);
        }
    });
}

function UserPlaylists() {
    const csrfToken = getCsrfToken();
    const accessToken = window.localStorage.getItem('access');
    const userId = window.localStorage.getItem('user_id');
    axios.get(`/api/playlist/profile-zzim/${userId}/`, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}`
        }
    })    
        .then(response => {
            console.log(response.data);
            displayPlaylist(response.data);
            checkUserZzimPlaylists();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

const zzimPlaylist = document.getElementById('zzim-playlist-link')
    zzimPlaylist.addEventListener('click', function(event) {
    event.preventDefault();
    UserPlaylists();
    document.getElementById('post-container').style.display = 'none';
    document.getElementById('liked-post-container').style.display = 'none';
    document.getElementById('coach-container').style.display = 'none';
    document.getElementById('zzim-playlist-container').style.display = 'block';
});


//훈수 목록
const coachList = document.getElementById('coach-list-link')
    coachList.addEventListener('click', function(event) {
    event.preventDefault();
    coachLists();
    document.getElementById('post-container').style.display = 'none';
    document.getElementById('liked-post-container').style.display = 'none';
    document.getElementById('coach-container').style.display = 'block';
    document.getElementById('zzim-playlist-container').style.display = 'none';
});

function coachLists() {
    const csrfToken = getCsrfToken();
    const accessToken = window.localStorage.getItem('access');
    axios.get(`/api/coach/api/user/`, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}`
        }
    })
        .then(response => {
            console.log(response.data)
            const data = response.data
            displayCoach(data)
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    }

function displayCoach(coachlist) {
    const container = document.getElementById('coach-container');
    container.innerHTML = ''; 

    coachlist.forEach(coach => {
        const item = document.createElement('div');
        item.className = 'coach-item';
        item.innerHTML = `
        <img src="${coach.graph}" >
        <p>${coach.pitch_score}</p>
        <p>${coach.message}</p>
        `;
        container.appendChild(item);
    });
}


//내가 작성한 post 목록
const myPostList = document.getElementById('posts-link')
    myPostList.addEventListener('click', function(event) {
    event.preventDefault();
    userPosts();
    document.getElementById('post-container').style.display = 'block';
    document.getElementById('liked-post-container').style.display = 'none';
    document.getElementById('coach-container').style.display = 'none';
    document.getElementById('zzim-playlist-container').style.display = 'none';
});

function userPosts() {
    const csrfToken = getCsrfToken();
    const accessToken = window.localStorage.getItem('access');
    const profileuserId = window.location.pathname.split('/').slice(-2, -1)[0];
    axios.get(`/api/posts/api/user/${profileuserId}/`, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}`
        }
    })
        .then(response => {
            console.log(response.data)
            const posts = response.data
            displayPosts(posts)
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    }

function displayPosts(posts) {
    const postList = document.getElementById('post-container');
    postList.innerHTML = ''; 

    posts.forEach(post => {
        const postElement = document.createElement('div');
        const postId = post.id
        postElement.classList.add('post');
        postElement.innerHTML = `
            <a href = "/api/posts/${postId}/">
            <h2>${post.title}</h2>
            <p>${post.content}</p>
            </a>
            <p>Likes: ${post.like_count}</p>
            <p>Category: ${post.category}</p>
        `;
        postList.appendChild(postElement);
    });
}

//좋아요한게시글들

const likedPostList = document.getElementById('liked-posts-link')
    likedPostList.addEventListener('click', function(event) {
    event.preventDefault();
    likedPosts();
    document.getElementById('post-container').style.display = 'none';
    document.getElementById('liked-post-container').style.display = 'block';
    document.getElementById('coach-container').style.display = 'none';
    document.getElementById('zzim-playlist-container').style.display = 'none';
});

function likedPosts() {
    const csrfToken = getCsrfToken();
    const accessToken = window.localStorage.getItem('access');
    const profileuserId = window.location.pathname.split('/').slice(-2, -1)[0];
    axios.get(`/api/posts/api/user/${profileuserId}/like/`, {
        headers: {
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}`
        }
    })
        .then(response => {
            console.log(response.data)
            const posts = response.data
            displayLikedPosts(posts)
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    }

function displayLikedPosts(posts) {
    const likedPosts = document.getElementById('liked-post-container');
    likedPosts.innerHTML = ''; 

    posts.forEach(post => {
        const postElement = document.createElement('div');
        const postId = post.id
        postElement.classList.add('post');
        postElement.innerHTML = `
            <a href = "/api/posts/${postId}/">
            <h2>${post.title}</h2>
            <p>${post.content}</p>
            </a>
            <p>By: ${post.author_nickname}</p>
            <p>Likes: ${post.like_count}</p>
            <p>Category: ${post.category}</p>
            <p>Posted on: ${new Date(post.created_at).toLocaleString()}</p>
        `;
        likedPosts.appendChild(postElement);
    });
}