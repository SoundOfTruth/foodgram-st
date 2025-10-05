import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image = data.split(';base64,')
            ext = format.split('/')[-1]
            id = str(uuid.uuid4())
            filename = f'{id}.{ext}'
            data = ContentFile(base64.b64decode(image), name=filename)
        return super().to_internal_value(data)
