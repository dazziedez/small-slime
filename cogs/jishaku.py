import discord
from discord.ext import commands

from jishaku.cog import STANDARD_FEATURES
from jishaku.cog import OPTIONAL_FEATURES
from jishaku.features.baseclass import Feature

import asyncpg
import tabulate

from utils.ui import pager

class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    @Feature.Command(parent="jsk", name="sql")
    async def jsk_sql(self, ctx: commands.Context, *, query: str):
        """
        Executes SQL queries and displays the result in a paginated embed.
        The query can be any valid SQL statement.
        """
        pages, positive = await self.run_query(query)
        if positive:
            await ctx.message.add_reaction("▶️")
            await pager.page(ctx, pages, True)
        else:
            await ctx.message.add_reaction("‼")
            await ctx.reply(embed=pages[0])

    async def run_query(self, query: str):
        db_config = self.bot.config.db_config
        conn = await asyncpg.connect(user=db_config.user, password=db_config.password, database=db_config.database, host='localhost')
        pages = []
        pos = False
        max_length = 50
        try:
            if query.strip().lower().startswith("select"):
                results = await conn.fetch(query)
                if results:
                    headers = results[0].keys()
                    rows = [[(str(value)[:max_length] + '...') if len(str(value)) > max_length else str(value) for value in list(r.values())] for r in results]
                    table = tabulate.tabulate(rows, headers=headers, tablefmt="grid")
                    if len(table) > 1994:
                        table_chunks = [table[i:i + 1994] for i in range(0, len(table), 1994)]
                        for chunk in table_chunks:
                            embed = f"```{chunk}```"
                            pages.append(embed)
                    else:
                        embed = f"```{table}```"
                        pages.append(embed)
                    pos = True
                else:
                    pages.append(discord.Embed(description="No results found."))
            else:
                result = await conn.execute(query)
                pages.append(f"```{result}```")
                pos = True

        except Exception as e:
            pages.append(discord.Embed(description=e))
        finally:
            await conn.close()

        return pages, pos

async def setup(bot: commands.Bot):
    await bot.add_cog(Jishaku(bot=bot))
