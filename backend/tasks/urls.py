from django.urls import path
from .views import AnalyzeView, SuggestView

urlpatterns = [
    path("analyze/", AnalyzeView.as_view(), name="analyze"),
    path("suggest/", SuggestView.as_view(), name="suggest"),
]
