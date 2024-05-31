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

import librosa
import matplotlib.pyplot as plt
from spleeter.separator import Separator
from django.core.files.temp import TemporaryFile
import numpy as np
import os
import tensorflow as tf
from pytube import YouTube

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
        
        tf.compat.v1.disable_eager_execution()

        def download_youtube_audio(youtube_url, download_folder='downloads'):
            yt = YouTube(youtube_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            output_file = audio_stream.download(output_path=download_folder)
            base, ext = os.path.splitext(output_file)
            new_file = base + '.mp4'
            os.rename(output_file, new_file)
            return new_file

        def separate_vocals(input_file_path, output_folder):
            print(f"보컬 분리 시작: {input_file_path}")
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(input_file_path, output_folder)
            print(f"보컬 분리 완료: {input_file_path}")
            vocal_path = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file_path))[0], 'vocals.wav')
            return vocal_path

        def extract_pitch(audio_path, duration=120, energy=0.7):
            y, sr = librosa.load(audio_path, sr=None, duration=duration)
            pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if magnitudes[index, t] > energy:
                    pitch_values.append(pitch)
                else:
                    pitch_values.append(0)
            return pitch_values, sr

        def freq_to_quarter_tone(pitch_values):
            A4 = 440
            notes = []
            for freq in pitch_values:
                if freq > 0:
                    note_number = 12 * np.log2(freq / A4) + 69
                    quarter_tone = round(note_number * 4) / 4
                    notes.append(quarter_tone)
            return notes

        def filter_high_pitch(pitch_values, threshold=90):
            return [p if p < threshold else 0 for p in pitch_values]

        def remove_outliers(pitch_values, m=2.):
            data = np.array(pitch_values)
            d = np.abs(data - np.nanmedian(data))
            mdev = np.nanmedian(d)
            s = d / (mdev if mdev else 1.)
            return np.where(s < m, pitch_values, 0)

        def maintain_continuity(pitch1, pitch2):
            result1 = []
            result2 = []
            prev1, prev2 = 0, 0
            for p1, p2 in zip(pitch1, pitch2):
                if p1 == 0 and p2 != 0:
                    result1.append(prev1)
                    result2.append(p2)
                elif p1 != 0 and p2 == 0:
                    result1.append(p1)
                    result2.append(prev2)
                else:
                    result1.append(p1)
                    result2.append(p2)
                prev1, prev2 = result1[-1], result2[-1]
            return result1, result2

        def pitch_to_note_label(pitch):
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = int(pitch // 12) - 1
            note_index = int(pitch % 12)
            return f'{note_names[note_index]}{octave}'

        def zero_to_nan(pitch_values):
            return [np.nan if p == 0 else p for p in pitch_values]

        def visualize_pitch(pitch1, pitch2, sr, output_image_path):
            min_length = min(len(pitch1), len(pitch2))
            pitch1 = pitch1[:min_length]
            pitch2 = pitch2[:min_length]
            time_axis = np.arange(0, min_length) / sr

            pitch1 = zero_to_nan(pitch1)
            pitch2 = zero_to_nan(pitch2)

            plt.figure(figsize=(12, 6))
            plt.plot(time_axis, pitch1, label='User Vocal Pitch')
            plt.plot(time_axis, pitch2, label='YouTube Vocal Pitch')

            yticks = np.arange(12*3, 12*8)
            ytick_labels = [pitch_to_note_label(p) for p in yticks]
            plt.yticks(yticks, ytick_labels)

            plt.xticks(np.arange(0, time_axis[-1], 10))

            plt.xlabel('Time (s)')
            plt.ylabel('Pitch')
            plt.legend()
            plt.title('Pitch Comparison Between User and YouTube Vocals')

            # 그래프를 저장할 디렉토리 생성
            os.makedirs(output_image_path, exist_ok=True)

            # UUID를 사용하여 그래프 파일 이름 생성
            graph_filename = f'graph_{uuid.uuid4()}.png'
            graph = os.path.join(output_image_path, graph_filename)
            plt.savefig(graph)
            return graph

        def calculate_similarity_score(pitch1, pitch2):
            similarity_scores = []
            for p1, p2 in zip(pitch1, pitch2):
                if p1 != 0 and p2 != 0:
                    similarity_scores.append(1 - abs(p1 - p2) / max(p1, p2))
                else:
                    similarity_scores.append(0)
            return round(np.mean(similarity_scores) * 100, 2)

        def main(youtube_url, user_audio_file, download_folder, output_path, output_image_path, energy=0.1):
            youtube_audio_path = download_youtube_audio(youtube_url, download_folder)
            
            youtube_vocal_folder = os.path.join(output_path, 'youtube')
            user_vocal_folder = os.path.join(output_path, 'user')
            os.makedirs(youtube_vocal_folder, exist_ok=True)
            os.makedirs(user_vocal_folder, exist_ok=True)
            
            youtube_vocal_path = separate_vocals(youtube_audio_path, youtube_vocal_folder)
            
            with TemporaryFile() as temp_file:
                for chunk in user_audio_file.chunks():
                    temp_file.write(chunk)
                temp_file.seek(0)  # 임시 파일 포인터를 처음으로 이동

                user_vocal_path = separate_vocals(temp_file.name, user_vocal_folder)
            
            youtube_pitch, sr = extract_pitch(youtube_vocal_path, energy=energy)
            user_pitch, sr = extract_pitch(user_vocal_path, energy=energy)
            
            youtube_quarter_tones = freq_to_quarter_tone(youtube_pitch)
            user_quarter_tones = freq_to_quarter_tone(user_pitch)
            
            youtube_filtered = filter_high_pitch(youtube_quarter_tones)
            user_filtered = filter_high_pitch(user_quarter_tones)
            
            user_filtered = remove_outliers(user_filtered)
            youtube_filtered = remove_outliers(youtube_filtered)
            
            user_filtered, youtube_filtered = maintain_continuity(user_filtered, youtube_filtered)
            
            graph = visualize_pitch(user_filtered, youtube_filtered, sr, output_image_path)

            high_pitch_threshold = np.mean(user_filtered)
            low_pitch_threshold = np.mean(youtube_filtered)

            high_pitch_score = calculate_similarity_score(
                [p for p in user_filtered if p > high_pitch_threshold],
                [p for p in youtube_filtered if p > low_pitch_threshold]
            )
            low_pitch_score = calculate_similarity_score(
                [p for p in user_filtered if p <= high_pitch_threshold],
                [p for p in youtube_filtered if p <= low_pitch_threshold]
            )
            pitch_score = calculate_similarity_score(user_filtered, youtube_filtered)

            # 파일 삭제
            os.remove(youtube_audio_path)
            os.remove(youtube_vocal_path)
            os.remove(user_vocal_path)

            return graph, high_pitch_score, low_pitch_score, pitch_score

        download_folder = 'downloads'
        output_path = 'output'
        output_image_path = os.path.join(settings.MEDIA_ROOT, 'graphs')

        graph, high_pitch_score, low_pitch_score, pitch_score = main(
            youtube_url, input_file, download_folder, output_path, output_image_path
        )

        coach = Coach.objects.create(
            user=user,
            youtube_url=youtube_url,
            input_file=input_file,
            high_pitch_score=high_pitch_score,
            low_pitch_score=low_pitch_score,
            pitch_score=pitch_score,
            message='메세지 로직을 추가해주세요',
            graph=graph
        )
        
        serializer = CoachSerializer(coach)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ResultPageView(TemplateView):
    template_name = "coach/coach_result.html"

class ResultView(APIView):
    def get(self, request, pk):
        coach = get_object_or_404(Coach, pk=pk)
        print(coach.pk)
        serializer = CoachSerializer(coach)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UserCoachedVocalView(APIView):
    def get(self, request):
        user_coached_vocals = Coach.objects.filter(user=request.user)
        serializer = CoachSerializer(user_coached_vocals, many=True)
        return Response(serializer.data)