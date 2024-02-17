## SCHEMA
```sql
guilds (
    guild_id bigint NOT NULL,
    prefix varchar(5),
    PRIMARY KEY(guild_id)
);

users (
    user_id bigint NOT NULL,
    donor boolean DEFAULT false,
    PRIMARY KEY(user_id)
);

guildnicks (
    guildnicks_uid uuid NOT NULL DEFAULT uuid_generate_v4(),
    user_id bigint,
    guild_id bigint,
    nickname text,
    PRIMARY KEY(guildnicks_uid),
    CONSTRAINT user_fk FOREIGN key(user_id) REFERENCES users(user_id),
    CONSTRAINT guild_fk FOREIGN key(guild_id) REFERENCES guilds(guild_id)
);
```

## TODO
- copy adonis
