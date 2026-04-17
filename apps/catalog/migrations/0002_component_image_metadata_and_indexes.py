# Generated manually for catalog component metadata and indexes.

from django.db import migrations, models


def populate_component_image_metadata(apps, schema_editor):
    Component = apps.get_model('catalog', 'Component')
    for component in Component.objects.all():
        updates = []
        if not component.image_alt:
            component.image_alt = f'{component.brand} {component.name}'
            updates.append('image_alt')
        if component.image and not component.image_source:
            component.has_real_photo = True
            updates.append('has_real_photo')
        if updates:
            component.save(update_fields=updates)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='has_real_photo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='component',
            name='image_alt',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='component',
            name='image_source',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='component',
            name='image_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='component',
            index=models.Index(fields=['type'], name='catalog_com_type_62ac7d_idx'),
        ),
        migrations.AddIndex(
            model_name='component',
            index=models.Index(fields=['brand'], name='catalog_com_brand_69b337_idx'),
        ),
        migrations.AddIndex(
            model_name='component',
            index=models.Index(fields=['price'], name='catalog_com_price_57f754_idx'),
        ),
        migrations.AddConstraint(
            model_name='component',
            constraint=models.UniqueConstraint(
                fields=('type', 'brand', 'name'),
                name='catalog_component_unique_type_brand_name',
            ),
        ),
        migrations.RunPython(populate_component_image_metadata, noop_reverse),
    ]
