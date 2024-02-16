from tortoise import fields, models

class Guilds(models.Model):
    guild_id: int = fields.BigIntField(pk=True)
    prefix: str   = fields.CharField(max_length=5, null=True)

    class Meta:
        table = "guilds"

class Users(models.Model):
    user_id: int = fields.BigIntField(pk=True)

    class Meta:
        table = "users"

class GuildNicks(models.Model):
    guildnicks_uid = fields.UUIDField(auto_generate=True, pk=True)
    user: int   = fields.ForeignKeyField(model_name="models.Users", related_name="guild_nicks", on_delete=fields.CASCADE)
    guild: int  = fields.ForeignKeyField(model_name="models.Guilds", related_name="user_nicks", on_delete=fields.CASCADE)
    nickname: int  = fields.TextField()

    class Meta:
        unique_together = ('user', 'guild')
