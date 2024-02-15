from tortoise import fields, models

class Guilds(models.Model):
    id: int = fields.BigIntField(pk=True)
    prefix: str = fields.CharField(max_length=5, null=True)

    class Meta:
        table = "Guilds"
