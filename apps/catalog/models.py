from django.db import models


class Component(models.Model):
    class Type(models.TextChoices):
        CPU         = 'cpu',         'Процесор'
        MOTHERBOARD = 'motherboard', 'Материнська плата'
        RAM         = 'ram',         "Оперативна пам'ять"
        GPU         = 'gpu',         'Відеокарта'
        PSU         = 'psu',         'Блок живлення'
        STORAGE     = 'storage',     'Накопичувач'
        CASE        = 'case',        'Корпус'
        COOLER      = 'cooler',      'Кулер'

    class RamType(models.TextChoices):
        DDR4 = 'ddr4', 'DDR4'
        DDR5 = 'ddr5', 'DDR5'

    name    = models.CharField(max_length=255)
    type    = models.CharField(max_length=20, choices=Type.choices)
    brand   = models.CharField(max_length=100)
    price   = models.DecimalField(max_digits=10, decimal_places=2)
    image   = models.ImageField(upload_to='components/', blank=True, null=True)

    # Поля для перевірки сумісності
    socket   = models.CharField(max_length=50, blank=True)   # для CPU і Motherboard
    ram_type = models.CharField(max_length=10, choices=RamType.choices, blank=True)  # для RAM і Motherboard
    wattage  = models.PositiveIntegerField(default=0)         # TDP для компонентів, потужність для PSU

    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['type', 'brand', 'name']

    def __str__(self):
        return f'{self.brand} {self.name}'


class ComponentSpec(models.Model):
    """1:1 — розширені технічні характеристики компонента."""
    component    = models.OneToOneField(Component, on_delete=models.CASCADE, related_name='spec')
    manufacturer = models.CharField(max_length=100, blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)
    warranty     = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Гарантія в місяцях')
    extra        = models.JSONField(default=dict, blank=True, help_text='Довільні характеристики у форматі JSON')

    def __str__(self):
        return f'Spec: {self.component}'
