import uuid
from django.db import models
from django.conf import settings
from apps.catalog.models import Component


class Build(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='builds')
    name       = models.CharField(max_length=255)
    slug       = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    components = models.ManyToManyField(Component, through='BuildComponent', related_name='builds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.user.username})'

    def get_total_price(self):
        return sum(bc.component.price for bc in self.build_components.select_related('component'))

    def get_share_url(self):
        return f'/builds/{self.slug}/'

    def check_compatibility(self):
        """Повертає список помилок сумісності. Порожній список = все ОК."""
        errors = []
        components = {bc.component for bc in self.build_components.select_related('component')}
        by_type = {}
        for c in components:
            by_type.setdefault(c.type, []).append(c)

        cpu_list         = by_type.get('cpu', [])
        motherboard_list = by_type.get('motherboard', [])
        ram_list         = by_type.get('ram', [])
        psu_list         = by_type.get('psu', [])

        # CPU ↔ Motherboard — сокет
        if cpu_list and motherboard_list:
            cpu = cpu_list[0]
            mb  = motherboard_list[0]
            if cpu.socket and mb.socket and cpu.socket != mb.socket:
                errors.append(
                    f'Несумісний сокет: CPU {cpu.name} ({cpu.socket}) '
                    f'і Motherboard {mb.name} ({mb.socket})'
                )

        # RAM ↔ Motherboard — тип пам'яті
        if ram_list and motherboard_list:
            mb = motherboard_list[0]
            for ram in ram_list:
                if ram.ram_type and mb.ram_type and ram.ram_type != mb.ram_type:
                    errors.append(
                        f'Несумісний тип RAM: {ram.name} ({ram.ram_type.upper()}) '
                        f'і Motherboard {mb.name} ({mb.ram_type.upper()})'
                    )

        # PSU — перевірка потужності
        if psu_list:
            psu = psu_list[0]
            total_draw = sum(c.wattage for c in components if c.type != 'psu')
            if total_draw > psu.wattage:
                errors.append(
                    f'Недостатня потужність PSU: потрібно ~{total_draw}W, '
                    f'PSU {psu.name} забезпечує {psu.wattage}W'
                )

        return errors



class BuildLike(models.Model):
    """Збережені / лайкнуті збірки."""
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liked_builds')
    build = models.ForeignKey('Build', on_delete=models.CASCADE, related_name='likes')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'build')

    def __str__(self):
        return f'{self.user.username} ♥ {self.build.name}'


class BuildComponent(models.Model):
    """Проміжна таблиця M:N між Build і Component."""
    build     = models.ForeignKey(Build, on_delete=models.CASCADE, related_name='build_components')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='build_components')
    added_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('build', 'component')

    def __str__(self):
        return f'{self.build.name} → {self.component.name}'
