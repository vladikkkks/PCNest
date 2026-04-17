from __future__ import annotations

from pathlib import Path
import random
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import Component


WIKIMEDIA_FILES_BY_TYPE = {
    "cpu": [
        {"file": "Cpu_1.jpg", "alt": "Фото процесора"},
        {"file": "Cpu.jpg", "alt": "Фото процесора"},
    ],
    "cpu_amd": [
        {"file": "AMD_CPU_(49325505733).jpg", "alt": "Фото процесора AMD"},
        {"file": "AMD_Ryzen_5_2600_(39851733273).jpg", "alt": "Фото процесора AMD Ryzen"},
    ],
    "cpu_intel": [
        {"file": "IMG3186_-_Intel_CPU.jpg", "alt": "Фото процесора Intel"},
        {"file": "CPU-INTEL-CORE.jpg", "alt": "Фото процесора Intel Core"},
        {"file": "Cpu.jpg", "alt": "Фото процесора Intel"},
    ],
    "motherboard": [
        {"file": "Computer-motherboard.jpg", "alt": "Фото материнської плати"},
    ],
    "ram": [
        {"file": "DDR5_SDRAM_IMGP6295_smial_wp.jpg", "alt": "Фото модуля оперативної пам'яті DDR5"},
        {"file": "RAM_Module_(SDRAM-DDR4).jpg", "alt": "Фото модуля оперативної пам'яті DDR4"},
    ],
    "gpu": [
        {"file": "Graphic_card.jpg", "alt": "Фото відеокарти"},
        {"file": "Graphics_Card_(25600081191).jpg", "alt": "Фото дискретної відеокарти"},
    ],
    "psu": [
        {"file": "Power_supply.JPG", "alt": "Фото блока живлення"},
        {"file": "ATX_Computer_power_supply_unit.jpg", "alt": "Фото ATX блока живлення"},
    ],
    "storage": [
        {"file": "WesterDigital-Black-NVMe-SSD.jpg", "alt": "Фото NVMe SSD накопичувача"},
    ],
    "case": [
        {"file": "Computer_case_-_Full_Tower.jpg", "alt": "Фото корпуса ПК"},
        {"file": "Computer_Case_(CM).jpg", "alt": "Фото комп'ютерного корпуса"},
        {"file": "Computer_case_with_power_supply.JPG", "alt": "Фото корпуса з блоком живлення"},
    ],
    "cooler": [
        {"file": "Fan_cooler_CPU.jpg", "alt": "Фото кулера для процесора"},
        {"file": "CPU_fan_and_heatsink.jpg", "alt": "Фото кулера з радіатором"},
        {"file": "CPU_Heat_Sink_(5066575382).jpg", "alt": "Фото процесорного радіатора"},
        {"file": "CPU_Heat_Sink_(5066574708).jpg", "alt": "Фото процесорного радіатора"},
        {"file": "CPU_copper_heat_sink.jpg", "alt": "Фото мідного радіатора процесора"},
    ],
}


class Command(BaseCommand):
    help = "Download real component photos from Wikimedia Commons and attach them to components."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace image even if component already has one.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        updated = 0
        skipped = 0
        failed = 0

        for component in Component.objects.all():
            if component.image and not force:
                skipped += 1
                continue

            if component.type == "cpu":
                if component.brand.lower().startswith("amd"):
                    pool = WIKIMEDIA_FILES_BY_TYPE["cpu_amd"]
                elif component.brand.lower().startswith("intel"):
                    pool = WIKIMEDIA_FILES_BY_TYPE["cpu_intel"]
                else:
                    pool = WIKIMEDIA_FILES_BY_TYPE["cpu"]
            else:
                pool = WIKIMEDIA_FILES_BY_TYPE.get(component.type)

            if not pool:
                skipped += 1
                continue
            photo = random.choice(pool)
            file_name = photo["file"]

            source_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(file_name)}"
            target_name = f"{component.type}_{component.pk}{Path(file_name).suffix.lower()}"

            try:
                request = Request(
                    source_url,
                    headers={
                        "User-Agent": "PC-NEST/1.0 (+https://localhost)",
                    },
                )
                with urlopen(request, timeout=30) as response:
                    image_bytes = response.read()

                component.image.save(target_name, ContentFile(image_bytes), save=False)
                component.image_source = source_url
                component.image_alt = component.image_alt or f'{component.brand} {component.name} - {photo["alt"]}'
                component.has_real_photo = True
                component.image_updated_at = timezone.now()
                component.save(update_fields=[
                    "image",
                    "image_source",
                    "image_alt",
                    "has_real_photo",
                    "image_updated_at",
                ])
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"[OK] {component} -> {target_name}"))
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.WARNING(f"[FAIL] {component}: {exc}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Updated: {updated}"))
        self.stdout.write(f"Skipped: {skipped}")
        self.stdout.write(f"Failed: {failed}")
