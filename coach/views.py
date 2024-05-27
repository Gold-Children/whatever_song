from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class CoachAPIView(TemplateView):
    template_name = "coach/coach.html"


class CoachResultAPIView(TemplateView):
    template_name = 'coach/coach_result.html'