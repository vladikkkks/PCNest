from __future__ import annotations

from pathlib import Path
import random
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Component


WIKIMEDIA_FILES_BY_TYPE = {
    "cpu": [
        "Cpu_1.jpg",
        "Cpu.jpg",
    ],
    "cpu_amd": [
        "AMD_CPU_(49325505733).jpg",
        "AMD_Ryzen_5_2600_(39851733273).jpg",
    ],
    "cpu_intel": [
        "IMG3186_-_Intel_CPU.jpg",
        "CPU-INTEL-CORE.jpg",
        "Cpu.jpg",
    ],
    "motherboard": [
        "Computer-motherboard.jpg",
    ],
    "ram": [
        "DDR5_SDRAM_IMGP6295_smial_wp.jpg",
        "RAM_Module_(SDRAM-DDR4).jpg",
    ],
    "gpu": [
        "Graphic_card.jpg",
        "Graphics_Card_(25600081191).jpg",
    ],
    "psu": [
        "Power_supply.JPG",
        "ATX_Computer_power_supply_unit.jpg",
    ],
    "storage": [
        "WesterDigital-Black-NVMe-SSD.jpg",
    ],
    "case": [
        "Computer_case_-_Full_Tower.jpg",
        "Computer_Case_(CM).jpg",
        "Computer_case_with_power_supply.JPG",
    ],
    "cooler": [
        "Fan_cooler_CPU.jpg",
        "CPU_fan_and_heatsink.jpg",
        "CPU_Heat_Sink_(5066575382).jpg",
        "CPU_Heat_Sink_(5066574708).jpg",
        "CPU_copper_heat_sink.jpg",
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
            file_name = random.choice(pool)

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

                component.image.save(target_name, ContentFile(image_bytes), save=True)
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"[OK] {component} -> {target_name}"))
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.WARNING(f"[FAIL] {component}: {exc}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Updated: {updated}"))
        self.stdout.write(f"Skipped: {skipped}")
        self.stdout.write(f"Failed: {failed}")
