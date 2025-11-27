import csv
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from players.models import Player


class Command(BaseCommand):
    help = "Load players data from CSV and JSON files"

    def handle(self, *args, **options):
        self.stdout.write("Starting to load players data...")

        # 데이터 디렉토리 경로
        data_dir = Path(settings.BASE_DIR) / "data"
        club_dir = data_dir / "club"
        profiles_dir = data_dir / "player_profiles"

        # 기존 데이터 삭제 여부 확인
        if Player.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Found {Player.objects.count()} existing players. "
                    "They will be updated or skipped."
                )
            )

        # CSV 파일들 로드
        csv_files = list(club_dir.glob("*/squad_*.csv"))
        self.stdout.write(f"Found {len(csv_files)} CSV files")

        players_data = {}

        # CSV 데이터 읽기
        for csv_file in csv_files:
            self.stdout.write(f"Reading {csv_file.name}...")
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    player_id = row["player_id"]
                    players_data[player_id] = row

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(players_data)} players from CSV")
        )

        # JSON 프로필 데이터 읽기
        json_files = list(profiles_dir.glob("*_profiles.json"))
        self.stdout.write(f"Found {len(json_files)} JSON profile files")

        profiles_data = {}
        for json_file in json_files:
            self.stdout.write(f"Reading {json_file.name}...")
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for player in data.get("players", []):
                    player_id = player["player_id"]
                    profiles_data[player_id] = player

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(profiles_data)} player profiles")
        )

        # 데이터베이스에 저장
        created_count = 0
        updated_count = 0

        for player_id, csv_data in players_data.items():
            profile_data = profiles_data.get(player_id, {})

            # birth_date 처리
            birth_date = csv_data.get("birth_date")
            if birth_date and birth_date.strip():
                # ISO 형식 그대로 사용
                pass
            else:
                birth_date = None

            player_defaults = {
                "name": csv_data.get("name", ""),
                "full_name": csv_data.get("full_name", ""),
                "first_name": csv_data.get("first_name", ""),
                "last_name": csv_data.get("last_name", ""),
                "wiki_name": csv_data.get("wiki_name", ""),
                "position": csv_data.get("position", ""),
                "position_abbr": csv_data.get("position_abbr", ""),
                "jersey_number": csv_data.get("jersey_number", ""),
                "age": int(csv_data["age"]) if csv_data.get("age") else None,
                "height": csv_data.get("height", ""),
                "weight": csv_data.get("weight", ""),
                "birth_place": csv_data.get("birth_place", ""),
                "birth_date": birth_date,
                "nationality": csv_data.get("nationality", ""),
                "team_id": csv_data.get("team_id", ""),
                "team_name": csv_data.get("team_name", ""),
                "wiki_url": profile_data.get("wiki_url") or "",
                "wiki_found": profile_data.get("wiki_found", False),
                "introduction": profile_data.get("introduction") or "",
                "playing_style": profile_data.get("playing_style") or "",
                "career_summary": profile_data.get("career_summary") or "",
            }

            player, created = Player.objects.update_or_create(
                player_id=player_id, defaults=player_defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully loaded players!\n"
                f"Created: {created_count}\n"
                f"Updated: {updated_count}\n"
                f"Total: {Player.objects.count()}"
            )
        )
