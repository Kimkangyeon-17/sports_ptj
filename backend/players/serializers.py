from rest_framework import serializers
from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "id",
            "player_id",
            "name",
            "full_name",
            "position",
            "position_abbr",
            "jersey_number",
            "age",
            "height",
            "weight",
            "nationality",
            "team_id",
            "team_name",
            "wiki_url",
        ]


class PlayerDetailSerializer(serializers.ModelSerializer):
    """선수 상세 정보용 시리얼라이저"""

    class Meta:
        model = Player
        fields = "__all__"
