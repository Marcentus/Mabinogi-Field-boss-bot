import discord
import aiosqlite
import settings
from unix_conversions import convert_boss_window_string_to_unix
from datetime import datetime, timedelta

async def field_boss_update_send_message(ctx: discord.ApplicationContext, id: int):
    async with aiosqlite.connect('timers_db.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT name, respawn_time, respawn_window, last_killed_time, role_id, image_link FROM field_bosses WHERE id = ?', (id,))
        row = await cursor.fetchone()
        if row:
            name = row['name']
            respawn_time = row['respawn_time']
            respawn_window = row['respawn_window']
            last_killed_time = row['last_killed_time']
            role_id = row['role_id']
            image_link = row['image_link']
            
        next_spawn_window_start = last_killed_time + respawn_time
        next_spawn_window_end = last_killed_time + respawn_window
            
    embed = discord.Embed(title=name, description=f"Next spawn window: <t:{next_spawn_window_start}:t> - <t:{next_spawn_window_end}:t>")
    try:
        role = ctx.guild.get_role(role_id)
        embed.color = role.color
    except:
        print(f"No role found to mention for {name}")
        
    if image_link is not None:
        embed.set_thumbnail(url=image_link)
    else:
        print(f"No image link to set as thumbnail for {name}")

    await ctx.interaction.response.send_message(embed=embed)
    
    return

async def field_boss_window_up_message(channel: discord.TextChannel, name, description, next_spawn_window_start, next_spawn_window_end, role_id, image_link):
    embed = discord.Embed(title=f'{name}\t<t:{next_spawn_window_start}:t> - <t:{next_spawn_window_end}:t>', description=description)
    try:
        role = channel.guild.get_role(role_id)
        content = role.mention
        embed.color = role.color
    except Exception as e:
        print(f"No role found to mention for {name} {role_id}")
        content = None
        
    if image_link is not None:
        embed.set_thumbnail(url=image_link)
    else:
        print(f"No image link to set as thumbnail for {name} {image_link}")

    await channel.send(embed=embed, content=content)
    return

async def raid_boss_window_up_message(channel: discord.TextChannel, role_id: discord.Role, bosses_in_boss_window: list):
    # If you set the url for each embed to the same thing, they will link when sending them with embeds
    embed = discord.Embed(title="", description="", url='https://www.google.com/')
    embed_list = [embed]
    try:
        role = channel.guild.get_role(role_id)
        content = role.mention
        embed.color = role.color
    except Exception as e:
        print(f"No role found to mention for id:{role_id}")
        content = None
    
    for boss in bosses_in_boss_window:
        name = boss[0]
        description = boss[1]
        window1 = boss[2]
        window2 = boss[3]
        image_link = boss[4]
        embed.add_field(name=f'{name}\t<t:{window1}:t> - <t:{window2}:t>', value='', inline=False)
        embed_list.append(discord.Embed(url='https://www.google.com/').set_image(url=image_link))
    
    # Use embeds to send multiple embeds for the images
    await channel.send(embeds=embed_list, content=content)
    return

async def ancient_create_message(ctx: discord.ApplicationContext, area, last_killed_time):
    next_spawn_time = last_killed_time + settings.ancient_respawn_time
    name = f'{area}-ancient-tracker'
    embed = discord.Embed(title=name, description=f"Created new respawn at: <t:{next_spawn_time}:t>")
    try:
        embed.color = ctx.guild.get_role(settings.ancienttracker_roleid).color
    except:
        pass
    
    await ctx.interaction.response.send_message(embed=embed)
    return

async def ancient_respawn_message(channel: discord.TextChannel, name, description, role_id, image_link):
    embed = discord.Embed(title=name, description=f"{description}")
    try:
        role = channel.guild.get_role(role_id)
        content = role.mention
        embed.color = role.color
    except:
        print(f"No role found to mention for {name}")
        content = None
        
    if image_link is not None:
        embed.set_thumbnail(url=image_link)
    else:
        print(f"No image link to set as thumbnail for {name}")

    await channel.send(embed=embed, content=content)
    return

async def list_timers_message(ctx: discord.ApplicationContext, timers, type="Timers"):
    embed = discord.Embed(title=type, description="")
    if timers is None or timers == []:
        embed.add_field(name='There are no timers currently set', 
                        value="", 
                        inline=False)
    elif type == "Ancients":
        for timer in timers:
            respawn_time = timer[4] + timer[3]
            embed.add_field(name=f'{timer[1]}\tRespawn time: <t:{respawn_time}:t>', 
                            value=f'Description: {timer[2]}', 
                            inline=False,)
            embed.add_field(name=f'--------------------------------------------------------',
                            value=f'',
                            inline=False)
            embed.color = discord.Color.green()
    elif type == "Field-Bosses":
        for timer in timers:
            window = f'{timer[3]/3600} - {timer[4]/3600} Hours'
            try:
                spawn_window_start = timer[5] + timer[3] # add last killed to respawn_time
                spawn_window_end = timer[5] + timer[4] # add last killed to respawn_window
                current_window = f'<t:{spawn_window_start}:t> - <t:{spawn_window_end}:t>'
            except:
                current_window = None
            embed.add_field(name=f'{timer[1]}\nCurrent Window: {current_window}\nWindow: {window}',  
                            value=f'Description: {timer[2]}', 
                            inline=False)
            embed.add_field(name=f'--------------------------------------------------------',
                            value=f'',
                            inline=False)
            embed.color = discord.Color.gold()
    elif type == "Field-Raids":
        for timer in timers:
            if timer[1] == 'White Dragon':
                continue
            try:
                week_day_window1 = await convert_boss_window_string_to_unix(timer[3])
                window1 = f'<t:{week_day_window1[0]}:t> - <t:{week_day_window1[1]}:t>'
            except:
                window1 = ""
            try:
                week_day_window2 = await convert_boss_window_string_to_unix(timer[4])
                window2 = f'<t:{week_day_window2[0]}:t> - <t:{week_day_window2[1]}:t>'
            except:
                window2 = ""
            try:
                week_end_window1 = await convert_boss_window_string_to_unix(timer[5])
                window3 = f'<t:{week_end_window1[0]}:t> - <t:{week_end_window1[1]}:t>'
            except:
                window3 = ""
            try:
                week_end_window2 = await convert_boss_window_string_to_unix(timer[6])
                window4 = f'<t:{week_end_window2[0]}:t> - <t:{week_end_window2[1]}:t>'
            except:
                window4 = ""
            try:
                week_end_window3 = await convert_boss_window_string_to_unix(timer[7])
                window5 = f'<t:{week_end_window3[0]}:t> - <t:{week_end_window3[1]}:t>'
            except:
                window5 = ""
            
            weekday_windows = f'{window1}\n{window2}'
            weekend_windows = f'{window3}\n{window4}\n{window5}'
            if timer[1] == 'Black Dragon':
                name = 'Black Dragon and White Dragon'
            else:
                name = timer[1]
            embed.add_field(name=f'{name}', 
                            value= '',
                            inline=False)
            embed.add_field(name=f'Weekday Times',  
                            value=f'{weekday_windows}', 
                            inline=True)
            embed.add_field(name=f'Weekend Times',  
                            value = f'{weekend_windows}', 
                            inline=True)
            embed.add_field(name=f'--------------------------------------------------------', 
                            value='', 
                            inline=False)
            embed.color = discord.Color.red()
            
    await ctx.interaction.response.send_message(embed=embed, delete_after=60)
    return