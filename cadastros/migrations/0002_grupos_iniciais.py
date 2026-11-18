from django.db import migrations

GRUPOS = ["Administrador", "Professor", "Aluno"]


def criar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for nome in GRUPOS:
        Group.objects.get_or_create(name=nome)


class Migration(migrations.Migration):

    dependencies = [
        ("cadastros", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        # Sem reverse: remover grupos apagaria o vínculo com os usuários.
        migrations.RunPython(criar_grupos, migrations.RunPython.noop),
    ]
