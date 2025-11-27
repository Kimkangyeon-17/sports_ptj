import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from teams.models import Staff


class Command(BaseCommand):
    help = "Load staff (managers and coaches) data from CSV file"

    def handle(self, *args, **options):
        self.stdout.write("Starting to load staff data...")

        # 데이터 파일 경로
        data_dir = Path(settings.BASE_DIR) / "data"
        csv_file = data_dir / "wiki_epl_all_staff.csv"

        if not csv_file.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
            return

        # 기존 데이터 삭제 여부 확인
        if Staff.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Found {Staff.objects.count()} existing staff. "
                    "They will be updated or skipped."
                )
            )

        # CSV 파일 읽기
        created_count = 0
        updated_count = 0

        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                team_name = row.get("Team", "").strip()
                position = row.get("Position", "").strip()
                name = row.get("Name", "").strip()
                nationality = row.get("Nationality", "").strip()

                # 필수 필드 확인
                if not team_name or not name:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping row with missing data: {row}")
                    )
                    continue

                # 데이터베이스에 저장
                staff, created = Staff.objects.update_or_create(
                    team_name=team_name,
                    position=position,
                    name=name,
                    defaults={
                        "nationality": nationality,
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully loaded staff!\n"
                f"Created: {created_count}\n"
                f"Updated: {updated_count}\n"
                f"Total: {Staff.objects.count()}"
            )
        )
