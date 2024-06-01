document.addEventListener("DOMContentLoaded", function() {
    const postsList = document.getElementById('postsList');
    const searchInput = document.getElementById('searchInput');
    const categorySelect = document.getElementById('categorySelect');
    const sortSelect = document.getElementById('sortSelect');

    async function fetchPosts() {
        const searchQuery = encodeURIComponent(searchInput.value.trim()); // 검색어 URI 인코딩
        const category = categorySelect.value;
        const sortOption = sortSelect.value;

        try {
            const response = await axios.get('/api/posts/', {
                params: {
                    search: searchQuery,
                    category: category,
                    sort: sortOption
                }
            });

            if (response.status === 200) { // 요청이 성공했는지 확인
                const posts = response.data;
                renderPosts(posts);
            } else {
                console.error("Failed to fetch posts, status code:", response.status);
            }
        } catch (error) {
            console.error("Error fetching posts:", error);
        }
    }

    function renderPosts(posts) {
        postsList.innerHTML = '';

        posts.forEach(post => {
            const postElement = document.createElement('div');
            const postId = post.id
            postElement.classList.add('post');
            postElement.innerHTML = `
                <h2>
                <a href=/api/posts/${post.id}/>${post.title}</a>
                </h2>
                <p>${post.content}</p>
                </a>
                <p>By: ${post.author_nickname}</p>
                <p>Likes: ${post.like_count}</p>
                <p>Category: ${post.category}</p>
                <p>Posted on: ${new Date(post.created_at).toLocaleString()}</p>
            `;
            postsList.appendChild(postElement);
        });
    }

    searchInput.addEventListener('input', fetchPosts);
    categorySelect.addEventListener('change', fetchPosts);
    sortSelect.addEventListener('change', fetchPosts);

    fetchPosts(); // 페이지 로드 시 초기 게시글 목록을 가져옴
});