document.addEventListener("DOMContentLoaded", function() {
    const pk = window.location.pathname.split('/').slice(-2, -1)[0];
    function loadResult() {
        const csrfToken = getCsrfToken();
        const access = localStorage.getItem('access');
        if (!access) {
            console.error('No access token found');
            return;
        }
        axios.get(`https://whateversong.com/api/coach/api/result/${pk}/`, {
            headers: {
                'X-CSRFToken': csrfToken,
                'Authorization': `Bearer ${access}`
            }
        })
        .then(response => {
            const data = response.data;
            document.getElementById('title').innerText = data.youtube_title;
            document.getElementById('high_pitch_score').innerText = data.high_pitch_score;
            document.getElementById('low_pitch_score').innerText = data.low_pitch_score;
            document.getElementById('pitch_score').innerText = data.pitch_score;
            document.getElementById('message').innerText = data.message;
            if (data.graph) {
                document.getElementById('graph').src = data.graph;
            }
            setupSocialShare(data);
        })
        .catch(error => console.error('Error:', error));
    }
    function setupSocialShare(data) {
        const baseUrl = 'https://whateversong.com'; // Base URL
        const url = `${baseUrl}${window.location.pathname}`; // 현재 페이지 UR
        const title = data.youtube_title;
        const text = data.message;

        document.getElementById('share-facebook').addEventListener('click', function() {
            const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
            window.open(facebookUrl, '_blank');
        });

        document.getElementById('share-twitter').addEventListener('click', function() {
            const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
            window.open(twitterUrl, '_blank');
        });
        document.getElementById('share-kakao').addEventListener('click', function() {
            // Ensure Kakao SDK is initialized
            if (!Kakao.isInitialized()) {
                Kakao.init('여기다가 넣어줘야함'); // Replace with your actual JavaScript key
            }
            Kakao.Link.sendDefault({
                objectType: 'feed',
                content: {
                    title: title,
                    description: text,
                    imageUrl: data.graph, // 그래프 이미지 URL 사용
                    link: {
                        mobileWebUrl: url,
                        webUrl: url
                    }
                }
            });
        });
    }

    loadResult();
});