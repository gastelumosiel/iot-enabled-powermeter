from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pahomqtt", "0008_alter_usercfesettings_rate"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="messages",
            index=models.Index(fields=["esp_id", "date"], name="messages_esp_date_idx"),
        ),
        migrations.AddIndex(
            model_name="messages",
            index=models.Index(fields=["date"], name="messages_date_idx"),
        ),
    ]
