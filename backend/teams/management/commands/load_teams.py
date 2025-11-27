import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from teams.models import Team


class Command(BaseCommand):
    help = "Load teams data from CSV files"

    def handle(self, *args, **options):
        self.stdout.write("Starting to load teams data...")

        # 데이터 디렉토리 경로
        data_dir = Path(settings.BASE_DIR) / "data" / "club"

        # CSV 파일들에서 팀 정보 추출
        csv_files = list(data_dir.glob("*/squad_*.csv"))
        self.stdout.write(f"Found {len(csv_files)} CSV files")

        teams_data = {}

        for csv_file in csv_files:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    team_id = row.get("team_id")
                    team_name = row.get("team_name")

                    if team_id and team_id not in teams_data:
                        teams_data[team_id] = {
                            "team_id": team_id,
                            "team_name": team_name,
                        }

        self.stdout.write(f"Found {len(teams_data)} unique teams")

        # 데이터베이스에 저장
        created_count = 0
        updated_count = 0

        for team_id, team_data in teams_data.items():
            team, created = Team.objects.update_or_create(
                team_id=team_id,
                defaults={
                    "team_name": team_data["team_name"],
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully loaded teams!\n"
                f"Created: {created_count}\n"
                f"Updated: {updated_count}\n"
                f"Total: {Team.objects.count()}"
            )
        )
