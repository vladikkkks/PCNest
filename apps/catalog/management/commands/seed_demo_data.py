from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.builds.models import Build, BuildComponent
from apps.catalog.models import Component, ComponentSpec


class Command(BaseCommand):
    help = "Seed demo data (users, components, specs, demo build). Safe to run multiple times."

    @transaction.atomic
    def handle(self, *args, **options):
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("admin12345")
        admin_user.save()

        demo_user, _ = User.objects.get_or_create(
            username="demo",
            defaults={
                "role": User.Role.USER,
            },
        )
        demo_user.role = User.Role.USER
        demo_user.set_password("demo12345")
        demo_user.save()

        component_payloads = [
            {
                "name": "Ryzen 5 7600",
                "type": Component.Type.CPU,
                "brand": "AMD",
                "price": "8499.00",
                "socket": "AM5",
                "ram_type": "",
                "wattage": 65,
                "description": "6-ядерний процесор для ігрової та робочої збірки.",
                "spec": {"manufacturer": "AMD", "release_year": 2023, "warranty": 36, "extra": {"Cores": 6, "Threads": 12}},
            },
            {
                "name": "B650M DS3H",
                "type": Component.Type.MOTHERBOARD,
                "brand": "Gigabyte",
                "price": "5699.00",
                "socket": "AM5",
                "ram_type": Component.RamType.DDR5,
                "wattage": 40,
                "description": "Материнська плата mATX для AM5.",
                "spec": {"manufacturer": "Gigabyte", "release_year": 2023, "warranty": 36, "extra": {"Chipset": "B650"}},
            },
            {
                "name": "Vengeance 32GB DDR5",
                "type": Component.Type.RAM,
                "brand": "Corsair",
                "price": "3999.00",
                "socket": "",
                "ram_type": Component.RamType.DDR5,
                "wattage": 10,
                "description": "Комплект 2x16GB DDR5.",
                "spec": {"manufacturer": "Corsair", "release_year": 2024, "warranty": 60, "extra": {"Frequency": "6000MHz"}},
            },
            {
                "name": "GeForce RTX 4060",
                "type": Component.Type.GPU,
                "brand": "MSI",
                "price": "13999.00",
                "socket": "",
                "ram_type": "",
                "wattage": 115,
                "description": "Відеокарта для FullHD/QHD.",
                "spec": {"manufacturer": "MSI", "release_year": 2023, "warranty": 36, "extra": {"VRAM": "8GB"}},
            },
            {
                "name": "MAG A650BN",
                "type": Component.Type.PSU,
                "brand": "MSI",
                "price": "2699.00",
                "socket": "",
                "ram_type": "",
                "wattage": 650,
                "description": "Блок живлення 650W 80+ Bronze.",
                "spec": {"manufacturer": "MSI", "release_year": 2022, "warranty": 36, "extra": {"Certification": "80+ Bronze"}},
            },
            {
                "name": "SN770 1TB",
                "type": Component.Type.STORAGE,
                "brand": "WD",
                "price": "2899.00",
                "socket": "",
                "ram_type": "",
                "wattage": 7,
                "description": "NVMe SSD 1TB.",
                "spec": {"manufacturer": "Western Digital", "release_year": 2023, "warranty": 60, "extra": {"Interface": "PCIe 4.0"}},
            },
            {
                "name": "CH370",
                "type": Component.Type.CASE,
                "brand": "DeepCool",
                "price": "2199.00",
                "socket": "",
                "ram_type": "",
                "wattage": 5,
                "description": "Компактний корпус з хорошою вентиляцією.",
                "spec": {"manufacturer": "DeepCool", "release_year": 2022, "warranty": 24, "extra": {"Form Factor": "mATX"}},
            },
            {
                "name": "AG400",
                "type": Component.Type.COOLER,
                "brand": "DeepCool",
                "price": "1399.00",
                "socket": "AM5",
                "ram_type": "",
                "wattage": 5,
                "description": "Повітряний кулер баштового типу.",
                "spec": {"manufacturer": "DeepCool", "release_year": 2023, "warranty": 24, "extra": {"TDP": "220W"}},
            },
        ]

        created_components = []
        for payload in component_payloads:
            spec_payload = payload.pop("spec")
            component, _ = Component.objects.update_or_create(
                name=payload["name"],
                brand=payload["brand"],
                defaults=payload,
            )
            ComponentSpec.objects.update_or_create(
                component=component,
                defaults=spec_payload,
            )
            created_components.append(component)

        demo_build, _ = Build.objects.get_or_create(
            user=demo_user,
            name="Demo Gaming Build",
        )
        for component in created_components:
            BuildComponent.objects.get_or_create(build=demo_build, component=component)

        errors = demo_build.check_compatibility()
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("Users:")
        self.stdout.write("  admin / admin12345")
        self.stdout.write("  demo / demo12345")
        self.stdout.write(f"Components: {Component.objects.count()}")
        self.stdout.write(f"Builds: {Build.objects.count()}")
        if errors:
            self.stdout.write(self.style.WARNING("Compatibility warnings in demo build:"))
            for err in errors:
                self.stdout.write(f"  - {err}")
