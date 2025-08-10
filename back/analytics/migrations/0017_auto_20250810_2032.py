# back/analytics/migrations/0016_auto_...py  (your new file)

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0015_alter_newssentimentdata_timestamp'),
    ]

    operations = [
        # First, add the new 'id' field that will become the primary key, but without making it a PK yet.
        # We also need to remove the primary key constraint from the existing 'article_id'.
        # Django AlterField handles this if we specify primary_key=False.
        migrations.AlterField(
            model_name='newssentimentdata',
            name='article_id',
            field=models.CharField(max_length=100), # Ensure primary_key=False (or is not present)
        ),
        
        # Now, add the 'id' field which will be the new primary key.
        # We need to make it AutoField to ensure it's an auto-incrementing primary key.
        migrations.AddField(
            model_name='newssentimentdata',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
