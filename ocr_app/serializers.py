from rest_framework import serializers

class HighlightRequestSerializer(serializers.Serializer):
    pdf_file = serializers.FileField()
    words_to_highlight = serializers.ListField(child=serializers.CharField())
    output_dir = serializers.CharField()

class OcrToJsonRequestSerializer(serializers.Serializer):
    pdf_file = serializers.FileField()
    output_dir = serializers.CharField()
