from __future__ import annotations

import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.builds.models import Build, BuildComponent
from apps.catalog.models import Component, ComponentSpec


TYPE_ORDER = [
    Component.Type.CPU,
    Component.Type.MOTHERBOARD,
    Component.Type.RAM,
    Component.Type.GPU,
    Component.Type.PSU,
    Component.Type.STORAGE,
    Component.Type.CASE,
    Component.Type.COOLER,
]

BRANDS = {
    Component.Type.CPU: ["AMD", "Intel"],
    Component.Type.MOTHERBOARD: ["ASUS", "MSI", "Gigabyte", "ASRock"],
    Component.Type.RAM: ["Corsair", "G.Skill", "Kingston", "Crucial"],
    Component.Type.GPU: ["MSI", "ASUS", "Gigabyte", "Sapphire"],
    Component.Type.PSU: ["Seasonic", "Corsair", "MSI", "be quiet!"],
    Component.Type.STORAGE: ["Samsung", "WD", "Kingston", "Crucial"],
    Component.Type.CASE: ["NZXT", "DeepCool", "Fractal", "Lian Li"],
    Component.Type.COOLER: ["Noctua", "DeepCool", "be quiet!", "Cooler Master"],
}

NAME_TEMPLATES = {
    Component.Type.MOTHERBOARD: ["{chip} {s}", "{chip}M {s}"],
    Component.Type.RAM: ["{cap}GB DDR{gen} {s}", "{cap}GB DDR{gen} Kit {s}"],
    Component.Type.PSU: ["{w}W Gold", "{w}W Bronze"],
    Component.Type.STORAGE: ["{cap}TB NVMe", "{cap}TB SSD"],
    Component.Type.CASE: ["{s} ATX", "{s} mATX"],
    Component.Type.COOLER: ["{s} Tower", "{s} Air"],
}

SOCKETS = ["AM4", "AM5", "LGA1700"]
RAM_TYPES = [Component.RamType.DDR4, Component.RamType.DDR5]


def make_price(low: int, high: int) -> Decimal:
    return Decimal(random.randint(low, high))


def build_component_payload(component_type: str) -> dict:
    brand = random.choice(BRANDS[component_type])
    template = NAME_TEMPLATES.get(component_type)

    if component_type == Component.Type.CPU:
        if brand == "AMD":
            series = random.choice(["Ryzen 5", "Ryzen 7", "Ryzen 9"])
            model = random.choice(["5600", "5700X", "7600", "7700", "7800X3D", "7900"])
            name = f"{series} {model}"
            socket = "AM4" if model.startswith("5") else "AM5"
        else:
            series = random.choice(["Core i5", "Core i7", "Core i9"])
            model = random.choice(["12400F", "12600K", "13400F", "13600K", "13700K", "13900K"])
            name = f"{series}-{model}"
            socket = "LGA1700"
        ram_type = ""
        wattage = random.choice([65, 95, 105, 125])
        price = make_price(4500, 16000)
    elif component_type == Component.Type.MOTHERBOARD:
        chip = random.choice(["B650", "X670", "B760", "Z790"])
        name = random.choice(template).format(chip=chip, s=random.choice(["A", "PRO", "PLUS", "M"])).strip()
        socket = "AM5" if chip in {"B650", "X670"} else "LGA1700"
        ram_type = random.choice(RAM_TYPES)
        wattage = random.choice([40, 50, 60])
        price = make_price(3500, 12000)
    elif component_type == Component.Type.RAM:
        gen = random.choice([4, 5])
        name = random.choice(template).format(cap=random.choice([16, 32, 64]), gen=gen, s=random.choice(["CL36", "CL32", "RGB"]))
        socket = ""
        ram_type = Component.RamType.DDR4 if gen == 4 else Component.RamType.DDR5
        wattage = random.choice([8, 10, 12])
        price = make_price(1800, 9000)
    elif component_type == Component.Type.GPU:
        if brand == "Sapphire":
            name = f"Radeon RX {random.choice([6600, 7600, 7800])} {random.choice(['XT', 'OC'])}"
        else:
            if random.random() < 0.65:
                name = f"GeForce RTX {random.choice([3060, 4060, 4070, 4080])} {random.choice(['OC', 'Gaming'])}"
            else:
                name = f"Radeon RX {random.choice([6600, 7600, 7800])} {random.choice(['XT', 'OC'])}"
        socket = ""
        ram_type = ""
        wattage = random.choice([115, 160, 220, 300])
        price = make_price(9000, 32000)
    elif component_type == Component.Type.PSU:
        name = random.choice(template).format(w=random.choice([550, 650, 750, 850]))
        socket = ""
        ram_type = ""
        wattage = int(name.split("W")[0])
        price = make_price(2000, 6000)
    elif component_type == Component.Type.STORAGE:
        name = random.choice(template).format(cap=random.choice([1, 2, 4]))
        socket = ""
        ram_type = ""
        wattage = random.choice([5, 7, 9])
        price = make_price(1800, 9000)
    elif component_type == Component.Type.CASE:
        name = random.choice(template).format(s=random.choice(["Flow", "Mesh", "Air", "Silent"]))
        socket = ""
        ram_type = ""
        wattage = random.choice([5, 7, 9])
        price = make_price(2000, 7000)
    else:
        name = random.choice(template).format(s=random.choice(["Pro", "V2", "Elite", "Edge"]))
        socket = random.choice(SOCKETS)
        ram_type = ""
        wattage = random.choice([5, 7, 10])
        price = make_price(900, 3500)

    return {
        "name": name,
        "brand": brand,
        "type": component_type,
        "price": price,
        "socket": socket,
        "ram_type": ram_type,
        "wattage": wattage,
        "description": f"{brand} {name} — тестовий компонент для каталогу.",
    }


class Command(BaseCommand):
    help = "Generate many demo components and builds."

    def add_arguments(self, parser):
        parser.add_argument("--components", type=int, default=80)
        parser.add_argument("--builds", type=int, default=20)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete previously generated demo components/builds before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        target_components = options["components"]
        target_builds = options["builds"]

        # Ensure demo users exist
        admin_user, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@pcnest.local", "role": User.Role.ADMIN, "is_staff": True, "is_superuser": True})
        if not admin_user.check_password("admin12345"):
            admin_user.set_password("admin12345")
            admin_user.save()

        demo_user, _ = User.objects.get_or_create(username="demo", defaults={"email": "demo@pcnest.local", "role": User.Role.USER})
        if not demo_user.check_password("demo12345"):
            demo_user.set_password("demo12345")
            demo_user.save()

        users = list(User.objects.all())

        if options["reset"]:
            BuildComponent.objects.filter(build__name__startswith="Demo Build ").delete()
            Build.objects.filter(name__startswith="Demo Build ").delete()
            Component.objects.filter(description__icontains="тестовий компонент для каталогу").delete()
            Component.objects.filter(description="Демо-компонент для каталогу.").delete()

        created_components = 0
        type_index = 0
        for _ in range(target_components):
            component_type = TYPE_ORDER[type_index % len(TYPE_ORDER)]
            payload = build_component_payload(component_type)
            component, created = Component.objects.get_or_create(
                name=payload["name"],
                brand=payload["brand"],
                defaults=payload,
            )
            if created:
                ComponentSpec.objects.get_or_create(component=component, defaults={"manufacturer": payload["brand"]})
                created_components += 1
            type_index += 1

        components = list(Component.objects.all())
        created_builds = 0
        for i in range(target_builds):
            owner = random.choice(users)
            build_name = f"Demo Build {Build.objects.count() + i + 1}"
            build, created = Build.objects.get_or_create(user=owner, name=build_name)
            if not created:
                continue

            picks = random.sample(components, k=min(len(components), random.randint(5, 8)))
            for comp in picks:
                BuildComponent.objects.get_or_create(build=build, component=comp)
            created_builds += 1

        self.stdout.write(self.style.SUCCESS(f"Added components: {created_components}"))
        self.stdout.write(self.style.SUCCESS(f"Added builds: {created_builds}"))
