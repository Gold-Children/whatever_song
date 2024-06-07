import coach.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube_title', models.TextField()),
                ('high_pitch_score', models.FloatField()),
                ('low_pitch_score', models.FloatField()),
                ('pitch_score', models.FloatField()),
                ('message', models.TextField()),
                ('graph', models.ImageField(upload_to=coach.models.upload_to_graph)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
