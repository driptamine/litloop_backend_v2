# serializers.py
from rest_framework import serializers
from .models import Query

class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ['query_text', 'suggestion', 'is_crawled']
