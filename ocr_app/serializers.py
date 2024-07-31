from rest_framework import serializers

class OcrToJsonRequestSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(required=False)
    pdf_path = serializers.CharField(required=False)
    output_dir = serializers.CharField()

class HighlightRequestSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(required=False)
    pdf_path = serializers.CharField(required=False)
    words_to_highlight = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )
    output_dir = serializers.CharField()
