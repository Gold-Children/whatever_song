{% extends "base.html" %}
{% load static %}
{% block content %}
<link rel="stylesheet" href="{% static 'accounts/css/signup.css' %}">
<div class="signup-form">
    <p>Signup</p>
    <form id="signup-form" method="post" enctype="multipart/form-data" novalidate>
        {% csrf_token %}
        <div class="signup">
            <span class="signup-text">아이디</span>
            <input type="text" id="username" name="username" placeholder="아이디를 입력해주세요" required><br>
        </div>
        <div class="signup">
            <span class="signup-text">닉네임</span>
            <input type="text" id="nickname" name="nickname" placeholder="닉네임을 입력해주세요" required><br>
        </div>
        <div class="signup">
            <span class="signup-text">비밀번호</span>
            <input type="password" id="password" name="password" placeholder="비밀번호를 입력해주세요" required><br>
        </div>
        <div class="signup-image-line">
            <span class="signup-text">사진</span>
            <span id="file-name">선택된 파일 없음</span>
            <label for="file-input" class="file-choice-btn">파일 선택</label>
            <input type="file" id="file-input" name="image" style="display:none;"><br>
        </div>
        <div class="email">
            <span class="signup-text">이메일</span>
            <input type="email" id="email" name="email" placeholder="이메일을 입력해주세요" required><br>
        </div>
        <div class="email-btn">
            <button type="button" id="email-verification-btn">이메일 인증</button>
        </div>
        <div class="signup-btn-line">
            <button type="submit">Signup</button>
        </div>
    </form>
    <div class="resend-verification"></div>
</div>

<script src="{% static 'accounts/js/signup.js' %}"></script>
{% endblock content %}
