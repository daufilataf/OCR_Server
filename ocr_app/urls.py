from django.urls import path
from .views import highlight_view, ocr_to_json_view

urlpatterns = [
    path('highlight/', highlight_view, name='highlight'),
    path('ocr-to-json/', ocr_to_json_view, name='ocr_to_json'),
]
