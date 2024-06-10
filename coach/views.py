from django.urls import path
from . import views
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Coach
from .serializers import CoachSerializer
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.conf import settings
import uuid

import os
import subprocess
import librosa
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from spleeter.separator import Separator
import tempfile
import shutil
from dtaidistance import dtw
from django.core.cache import cache
from scipy.signal import correlate
import random

class CoachPageView(TemplateView):
    template_name = "coach/coach.html"

class InputView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        youtube_url = request.data.get('youtube_url')
        input_file = request.FILES.get('input_file')
        
        if not input_file:
            return Response({"error": "파일을 입력하세요"}, status=status.HTTP_400_BAD_REQUEST)
        
        def update_progress(user, progress):
            cache.set(f'progress_{user.id}', progress, timeout=300)
        
        def download_audio_from_youtube(youtube_url, output_path):
            print("Downloading audio from YouTube...")
            title_command = [
                'yt-dlp',
                '--get-title',
                youtube_url
            ]
            title_result = subprocess.run(title_command, capture_output=True, text=True, check=True)
            title = title_result.stdout.strip()

            audio_command = [
                'yt-dlp',
                '-x',
                '--audio-format', 'mp3',
                '--playlist-items', '1',
                '-o', output_path,
                youtube_url
            ]
            subprocess.run(audio_command, check=True)
            return title, output_path

        def separate_vocals(audio_path, output_path):
            print(f"Separating vocals from {audio_path}...")
            separator = Separator('spleeter:2stems', stft_backend='librosa')
            separator.separate_to_file(audio_path, output_path)
            vocal_path = os.path.join(output_path, os.path.splitext(os.path.basename(audio_path))[0], 'vocals.wav')
            return vocal_path

        def calculate_highest_dB_freqs(vocal_path):
            print(f"Calculating highest dB frequencies for {vocal_path}...")
            y, sr = librosa.load(vocal_path)
            hop_length = 512
            D = librosa.stft(y, n_fft=1024, hop_length=hop_length)
            magnitude, phase = librosa.magphase(D)
            db_magnitude = librosa.amplitude_to_db(magnitude, ref=np.max)
            freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)
            times = librosa.frames_to_time(np.arange(db_magnitude.shape[1]), sr=sr, hop_length=hop_length)

            new_magnitude = np.full_like(db_magnitude, -80)
            for i in range(db_magnitude.shape[1]):
                valid_indices = np.where((freqs >= 82) & (freqs <= 1046.5) & (db_magnitude[:, i] > -80))[0]
                if len(valid_indices) > 0:
                    top_indices = valid_indices[:10] if len(valid_indices) > 10 else valid_indices
                    for idx in top_indices:
                        new_magnitude[idx, i] = db_magnitude[idx, i]

            highest_dB_freqs = []
            time_range = 0.1
            for t in np.arange(0, times[-1], time_range):
                start_idx = np.searchsorted(times, t)
                end_idx = np.searchsorted(times, t + time_range)
                if (start_idx < end_idx) and (end_idx < new_magnitude.shape[1]):
                    max_dB_idx = np.argmax(new_magnitude[:, start_idx:end_idx], axis=None)
                    max_freq_idx = np.unravel_index(max_dB_idx, new_magnitude[:, start_idx:end_idx].shape)
                    if new_magnitude[max_freq_idx[0], start_idx + max_freq_idx[1]] > -80:
                        highest_dB_freqs.append((times[start_idx + max_freq_idx[1]], freqs[max_freq_idx[0]]))

            return highest_dB_freqs

        def classify_vocal_ranges(highest_dB_freqs):
            male_range = (82, 587.33) 
            female_range = (175, 1046.5)
            male_count = sum(1 for time, freq in highest_dB_freqs if male_range[0] <= freq <= male_range[1])
            female_count = sum(1 for time, freq in highest_dB_freqs if female_range[0] <= freq <= female_range[1])
            return 'male' if male_count > female_count else 'female'

        def split_freq_ranges(highest_dB_freqs, classification):
            if classification == 'male':
                low_range = (82, 175)  
                high_range = (175, 350) 
            else:
                low_range = (175, 350) 
                high_range = (350, 1046.5)
            
            low_freqs = [(time, freq) for time, freq in highest_dB_freqs if low_range[0] <= freq <= low_range[1]]
            high_freqs = [(time, freq) for time, freq in highest_dB_freqs if high_range[0] <= freq <= high_range[1]]
            return low_freqs, high_freqs

        def calculate_scores(youtube_freqs, file_freqs):
            scores = []
            for yt_freq, file_freq in zip(youtube_freqs, file_freqs):
                if yt_freq == file_freq:
                    scores.append(100)
                else:
                    diff = abs(yt_freq - file_freq)
                    if diff < 12:
                        score = max(0, 100 - (diff * 25))  
                        scores.append(score)
                    else:
                        scores.append(0)
            return scores

        def calculate_signal_similarity(signal1, signal2):
            signal1, signal2 = pad_sequences(signal1, signal2)
            return np.sum(np.minimum(signal1, signal2)) / np.sum(np.maximum(signal1, signal2))

        def pad_sequences(seq1, seq2):
            max_len = max(len(seq1), len(seq2))
            if len(seq1) < max_len:
                seq1 = np.pad(seq1, (0, max_len - len(seq1)), 'constant')
            if len(seq2) < max_len:
                seq2 = np.pad(seq2, (0, max_len - len(seq2)), 'constant')
            return seq1, seq2

        def sync_signals_optimized(youtube_freqs, file_freqs):
            youtube_freqs, file_freqs = pad_sequences(youtube_freqs, file_freqs)
            path = dtw.warping_path(youtube_freqs, file_freqs)
            aligned_file_freqs = [file_freqs[j] for i, j in path]

            aligned_file_freqs = np.array(aligned_file_freqs)
            youtube_freqs = np.array(youtube_freqs)
            
            cross_corr = correlate(youtube_freqs, aligned_file_freqs)
            shift = np.argmax(cross_corr) - (len(aligned_file_freqs) - 1)
            
            if shift > 0:
                aligned_file_freqs = np.pad(aligned_file_freqs, (shift, 0), mode='constant')[:-shift]
            elif shift < 0:
                aligned_file_freqs = np.pad(aligned_file_freqs, (0, -shift), mode='constant')[-shift:]
            
            best_shift = 0
            best_similarity = -1

            for test_shift in range(-len(aligned_file_freqs) + 1, len(aligned_file_freqs)):
                if test_shift > 0:
                    test_aligned_file_freqs = np.pad(aligned_file_freqs, (test_shift, 0), mode='constant')[:-test_shift]
                elif test_shift < 0:
                    test_aligned_file_freqs = np.pad(aligned_file_freqs, (0, -test_shift), mode='constant')[-test_shift:]
                else:
                    test_aligned_file_freqs = aligned_file_freqs
                
                similarity = calculate_signal_similarity(youtube_freqs, test_aligned_file_freqs)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_shift = test_shift

            if best_shift > 0:
                aligned_file_freqs = np.pad(aligned_file_freqs, (best_shift, 0), mode='constant')[:-best_shift]
            elif best_shift < 0:
                aligned_file_freqs = np.pad(aligned_file_freqs, (0, -best_shift), mode='constant')[-best_shift:]
            
            return aligned_file_freqs.tolist()

        def extract_pitch_changes(highest_dB_freqs):
            pitch_changes = []
            prev_freq = highest_dB_freqs[0][1]
            for time, freq in highest_dB_freqs[1:]:
                pitch_changes.append(freq - prev_freq)
                prev_freq = freq
            return pitch_changes

        def save_and_get_graph_path(highest_dB_freqs_youtube, highest_dB_freqs_file, output_path):
            note_freqs = [82.41, 87.31, 98.00, 110.00, 123.47, 130.81, 146.83, 
                        164.81, 174.61, 196.00, 220.00, 246.94, 261.63, 293.66,
                        329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 587.33,
                        659.25, 698.46, 783.99, 880.00, 987.77, 1046.50]
            note_labels = ['E', 'F', 'G', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'D',
                        'E', 'F', 'G', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

            def map_freq_to_note_index(freq):
                index = np.argmin(np.abs(np.array(note_freqs) - freq))
                return index

            highest_dB_freqs_youtube_mapped = [(time, map_freq_to_note_index(freq)) for time, freq in highest_dB_freqs_youtube]
            highest_dB_freqs_file_mapped = [(time, map_freq_to_note_index(freq)) for time, freq in highest_dB_freqs_file]

            fig = plt.figure(figsize=(15, 9))
            ax = fig.add_subplot(111)

            ax.plot([x[0] for x in highest_dB_freqs_youtube_mapped], [x[1] for x in highest_dB_freqs_youtube_mapped], drawstyle='steps-post', linewidth=1, label='YouTube', color='white')
            ax.plot([x[0] for x in highest_dB_freqs_file_mapped], [x[1] for x in highest_dB_freqs_file_mapped], drawstyle='steps-post', linewidth=1, label='File', color='orange')

            ax.set_xlabel('시간', color='white')
            ax.set_ylabel('음정', color='white')
            ax.legend(loc='lower right')

            note_ticks = np.arange(len(note_labels))

            ax.set_yticks(note_ticks)
            ax.set_yticklabels(note_labels)
            ax.set_ylim([note_ticks[0], note_ticks[-1]])

            def format_time(x, pos):
                minutes = int(x // 60)
                seconds = int(x % 60)
                return f'{minutes}:{seconds:02}' if minutes > 0 else f'{seconds}'

            ax.xaxis.set_major_locator(plt.MultipleLocator(10))
            ax.xaxis.set_major_formatter(plt.FuncFormatter(format_time))

            ax.set_facecolor('none')

            for spine in ax.spines.values():
                spine.set_edgecolor('white')

            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')

            graph_id = str(uuid.uuid4())
            graph_path = os.path.join(output_path, f'{graph_id}.png')
            plt.savefig(graph_path, transparent=True)

            return graph_path

        def main(youtube_url, input_file):
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            progress = "작업을 시작합니다"
            update_progress(user, progress)
            
            audio_path_youtube = os.path.join(output_dir, f'{uuid.uuid4()}_audio.mp3')
            progress = "YouTube에서 오디오 다운로드 중"
            update_progress(user, progress)
            title, _ = download_audio_from_youtube(youtube_url, audio_path_youtube)
            
            progress = "YouTube 오디오에서 보컬 분리 중"
            update_progress(user, progress)
            vocal_output_path_youtube = os.path.join(output_dir, 'vocals_youtube')
            os.makedirs(vocal_output_path_youtube, exist_ok=True)
            vocal_path_youtube = separate_vocals(audio_path_youtube, vocal_output_path_youtube)
            
            progress = "업로드된 파일에서 보컬 분리 중"
            update_progress(user, progress)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in input_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            vocal_output_path_file = os.path.join(output_dir, 'vocals_file')
            os.makedirs(vocal_output_path_file, exist_ok=True)
            vocal_path_file = separate_vocals(temp_file_path, vocal_output_path_file)
            
            progress = "YouTube 보컬의 주파수 계산 중"
            update_progress(user, progress)
            highest_dB_freqs_youtube = calculate_highest_dB_freqs(vocal_path_youtube)
            
            progress = "업로드된 보컬의 주파수 계산 중"
            update_progress(user, progress)
            highest_dB_freqs_file = calculate_highest_dB_freqs(vocal_path_file)
            
            progress = "보컬 범위 분류 중"
            update_progress(user, progress)
            classification = classify_vocal_ranges(highest_dB_freqs_youtube)
            
            progress = "주파수 범위 나누는 중"
            update_progress(user, progress)
            low_freqs_youtube, high_freqs_youtube = split_freq_ranges(highest_dB_freqs_youtube, classification)
            low_freqs_file, high_freqs_file = split_freq_ranges(highest_dB_freqs_file, classification)
            
            progress = "DTW와 크로스 코릴레이션을 사용하여 신호 싱크 맞추기 중"
            update_progress(user, progress)
            aligned_low_freqs_file = sync_signals_optimized([freq for _, freq in low_freqs_youtube], [freq for _, freq in low_freqs_file])
            aligned_high_freqs_file = sync_signals_optimized([freq for _, freq in high_freqs_youtube], [freq for _, freq in high_freqs_file])
            
            progress = "점수 계산 중"
            update_progress(user, progress)
            full_scores = calculate_scores([freq for _, freq in highest_dB_freqs_youtube], [freq for _, freq in highest_dB_freqs_file])
            low_scores = 100, calculate_scores([freq for _, freq in low_freqs_youtube], aligned_low_freqs_file)
            high_scores = 100, calculate_scores([freq for _, freq in high_freqs_youtube], aligned_high_freqs_file)
            
            full_score_avg = min(100, round(np.mean(full_scores), 2) *6)
            low_score_avg = min(100, round(np.mean(low_scores), 2) *6)
            high_score_avg = min(100, round(np.mean(high_scores), 2) *6)
            
            progress = "음정 변화 배열 추출 및 신호 싱크 맞추기 중"
            update_progress(user, progress)
            pitch_changes_youtube = extract_pitch_changes(highest_dB_freqs_youtube)
            pitch_changes_file = extract_pitch_changes(highest_dB_freqs_file)
            
            pitch_changes_youtube, pitch_changes_file = pad_sequences(pitch_changes_youtube, pitch_changes_file)
            
            aligned_pitch_changes_file = sync_signals_optimized(pitch_changes_youtube, pitch_changes_file)
            
            progress = "그래프 저장 중"
            update_progress(user, progress)
            graph_output_path = os.path.join(settings.MEDIA_ROOT, 'graph')
            os.makedirs(graph_output_path, exist_ok=True)
            graph_path = save_and_get_graph_path(highest_dB_freqs_youtube, highest_dB_freqs_file, graph_output_path)
            
            graph_rel_path = os.path.relpath(graph_path, settings.MEDIA_ROOT)
            
            progress = "임시 파일 정리 중"
            update_progress(user, progress)
            os.remove(audio_path_youtube)
            os.remove(temp_file_path)
            shutil.rmtree(vocal_output_path_youtube)
            shutil.rmtree(vocal_output_path_file)
            
            return title, graph_rel_path, high_score_avg, low_score_avg, full_score_avg

        title, graph, high_pitch_score, low_pitch_score, pitch_score = main(youtube_url, input_file)
        
        def generate_message(score):
            messages = {
                (0, 10): ["ㅋ", "뭐하세요?", "공기가 노래 부르나용?"],
                (11, 20): ["부른고 있는건 맞냐?", "뭐해????????????", "아는 노래가 맞나요?"],
                (21, 30): [
                    "오 이게 그거죠? 당신 억장 무너지는 소리", 
                    "걍… 하지마…", 
                    "소불고기 레시피: [• **1.**소고기 등심에 설탕 40컵, 물엿 2병을 넣어요. • ***2.***거기에 매실, 다진마늘 3접, 간장 12병 후추 약간을 넣고 주물러 양념이 배게 해줍니다. • ***3.***여기에 기름 1L를 넣고 주물러 30초 기다려줘요.](https://m.10000recipe.com/recipe/6879215)"
                ],
                (31, 40): ["성대에 기름칠 못하셨어요?", "당신의 노래는 마치 반 고흐가 받았던 평가만큼 150년 후에야 칭찬 받을 만한 노래 실력이라고 말할 수 있겠는데요."],
                (41, 50): ["우와! 절반 아래로 나오기 힘든데 그걸 하셨군요! 대단해요!", "베토벤이 말합니다 : 넌 노래하지 마라;"],
                (51, 60): ["그… 내가 받아쓰기해도 이것보단 잘나오겠는데?", "어…음….그래 노력해봐"],
                (61, 70): ["넌 그냥 흥얼거리기만 하자", "이걸 잘 불렀다고 해야 해 못 불렀다고 해야 해…?"],
                (71, 80): ["이 정도면 노력 하면 될거 같기도한데?", "화이팅!"],
                (81, 90): ["아쉽네유", "조금만 더 하지 그거 하나 못해서 100점을 못받네 아이고난", "오?"],
                (91, 100): ["찢었따", "ㅇㅇ 들어줄만함", "크으", "조금 많이 부를줄 아네?"]
            }
            for range_, msgs in messages.items():
                if range_[0] <= score <= range_[1]:
                    return random.choice(msgs)
            return "평가 점수 범위를 벗어났습니다."

        message = generate_message(pitch_score)
        
        coach = Coach.objects.create(
            user=user,
            youtube_title=title,
            high_pitch_score=high_pitch_score,
            low_pitch_score=low_pitch_score,
            pitch_score=pitch_score,
            message=message,
            graph=graph
        )
        
        serializer = CoachSerializer(coach)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
class ResultPageView(TemplateView):
    template_name = "coach/coach_result.html"

class ResultView(APIView):
    def get(self, request, pk):
        coach = get_object_or_404(Coach, pk=pk)
        serializer = CoachSerializer(coach)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCoachedVocalView(APIView):
    def get(self, request):
        user_coached_vocals = Coach.objects.filter(user=request.user)
        serializer = CoachSerializer(user_coached_vocals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CheckStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        progress = cache.get(f'progress_{user.id}', '진행중인 프로세스가 없습니다')
        return Response({"status": progress}, status=status.HTTP_200_OK)
