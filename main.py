import discord
import settings
from datetime import datetime
import db_utils
from discord_messages import *
import asyncio
from unix_conversions import parse_user_time_input_to_unix, convert_boss_window_string_to_unix
import re

bot = discord.Bot(intents=discord.Intents.all())

# Bot events
@bot.event
async def on_ready():
    print("Bot has connected to Discord!")
    await check_field_bosses()

# Functions
async def check_field_bosses():
    if db_utils.bosses is None:
        db_utils.bosses = await db_utils.get_field_bosses_from_db()
    if db_utils.raid_bosses is None:
        db_utils.raid_bosses = await db_utils.get_field_raids_from_db()
    if db_utils.ancients is None:
        db_utils.ancients = await db_utils.get_ancients_from_db()
        # await raid_boss_window_up_message(bot.get_channel(settings.field_boss_timers_channelid), 688173180333981717, [["test", "desc", "time1", "time2", db_utils.raid_bosses[0][9]], ["test", "desc", "time1", "time2", db_utils.raid_bosses[1][9]], ["test", "desc", "time1", "time2", db_utils.raid_bosses[3][9]], ["test", "desc", "time1", "time2", db_utils.raid_bosses[2][9]]])
        
    channel = bot.get_channel(settings.field_boss_timers_channelid)
        
    while True:
        now = int(datetime.now().timestamp())
        day_of_week = datetime.now().weekday()
        
        # Check field bosses
        for boss in db_utils.bosses:
            id = boss[0]
            name = boss[1]
            description = boss[2]
            respawn_time = boss[3]
            respawn_window = boss[4]
            last_killed_time = boss[5]
            role_id = boss[6]
            image_link = boss[7]
            
            if last_killed_time is None:
                continue
            else:
                next_spawn_window_start = last_killed_time + respawn_time
                next_spawn_window_end = last_killed_time + respawn_window
            
            if now > next_spawn_window_start:
                await field_boss_window_up_message(channel, name, description, next_spawn_window_start, next_spawn_window_end, role_id, image_link)
                await db_utils.update_last_killed_time_to_null(id)
        
        # Check raid bosses
        raid_bosses_in_window = []
        for boss in db_utils.raid_bosses:
            id = boss[0]
            name = boss[1]
            description = boss[2]
            weekday_spawn_window1 = boss[3]
            if weekday_spawn_window1 != None: 
                weekday_spawn_window1 = await convert_boss_window_string_to_unix(weekday_spawn_window1)
            weekday_spawn_window2 = boss[4]
            if weekday_spawn_window2 != None: 
                weekday_spawn_window2 = await convert_boss_window_string_to_unix(weekday_spawn_window2)
            weekend_spawn_window1 = boss[5]
            if weekend_spawn_window1 != None: 
                weekend_spawn_window1 = await convert_boss_window_string_to_unix(weekend_spawn_window1)
            weekend_spawn_window2 = boss[6]
            if weekend_spawn_window2 != None: 
                weekend_spawn_window2 = await convert_boss_window_string_to_unix(weekend_spawn_window2)
            weekend_spawn_window3 = boss[7]
            if weekend_spawn_window3 != None: 
                weekend_spawn_window3 = await convert_boss_window_string_to_unix(weekend_spawn_window3)
                
            weekday_spawn_windows = [weekday_spawn_window1, weekday_spawn_window2]
            weekend_spawn_windows = [weekend_spawn_window1, weekend_spawn_window2, weekend_spawn_window3]
            role_id = boss[8]
            image_link = boss[9]
           
            if day_of_week < 5:
                for window in weekday_spawn_windows:
                    if window is None:
                        continue
                    elif 0 <= now - window[0] <= 60:
                        raid_bosses_in_window.append([name, description, window[0], window[1], image_link])
                        break
            else: 
                for window in weekend_spawn_windows:
                    if window is None:
                        continue
                    elif 0 <= now - window[0] <= 60:
                        raid_bosses_in_window.append([name, description, window[0], window[1], image_link])
                        break
                    
        if len(raid_bosses_in_window) > 0:
            print("Sending message up window to discord server")
            await raid_boss_window_up_message(channel, settings.fieldboss_roleid, raid_bosses_in_window)
        
        
        # Check Ancients
        if db_utils.ancients:
            for ancient in db_utils.ancients:
                id = ancient[0]
                name = ancient[1]
                description = ancient[2]
                respawn_time = ancient[3]
                last_killed_time = ancient[4]
                role_id = ancient[5]
                image_link = ancient[6]
                
                if now > last_killed_time + respawn_time:
                    await ancient_respawn_message(channel, name, description, role_id, image_link)
                    await db_utils.delete_ancient_time(id)
                    
        await asyncio.sleep(60)

# Bot command groups
gnucommands_group_list = discord.SlashCommandGroup("list", "Lists timers!")
gnucommands_group_start = discord.SlashCommandGroup("start", "Start timers!")
gnucommands_group_clear = discord.SlashCommandGroup("clear", "Clear a set timer!")

# Bot start commands
@gnucommands_group_start.command(name="gnu-tracker", description="Giant Big-horned Gnu")
async def gnutracker_command(
    ctx: discord.ApplicationContext,
    last_killed_time: discord.Option(
        str,
        "Specify the time the gnu was killed",
        autocomplete=discord.utils.basic_autocomplete(["now"]),
    ),
):
    boss_id = 1 # Boss ID from field_bosses table
    
    last_killed_time = await parse_user_time_input_to_unix(last_killed_time)
    if last_killed_time is None:
        await ctx.interaction.response.send_message("Custom time not supported yet!")
        return
        
    await db_utils.update_last_killed_time(boss_id, last_killed_time)
    await field_boss_update_send_message(ctx, boss_id)
    
@gnucommands_group_start.command(name="golem-tracker", description="Golem (Black)")
async def golemtracker_command(
    ctx: discord.ApplicationContext,
    last_killed_time: discord.Option(
        str,
        "Specify the time the golem was killed",
        autocomplete=discord.utils.basic_autocomplete(["now"]),
    ),
):
    boss_id = 2 # Boss ID from field_bosses table
    
    last_killed_time = await parse_user_time_input_to_unix(last_killed_time)
    if last_killed_time is None:
        await ctx.interaction.response.send_message("Custom time not supported yet!")
        return
        
    await db_utils.update_last_killed_time(boss_id, last_killed_time)
    await field_boss_update_send_message(ctx, boss_id)
    
@gnucommands_group_start.command(name="warrior-tracker", description="Black Warrior")
async def warriortracker_command(
    ctx: discord.ApplicationContext,
    last_killed_time: discord.Option(
        str,
        "Specify the time the black warrior was killed",
        autocomplete=discord.utils.basic_autocomplete(["now"]),
    ),
):
    boss_id = 3 # Boss ID from field_bosses table
    
    last_killed_time = await parse_user_time_input_to_unix(last_killed_time)
    if last_killed_time is None:
        await ctx.interaction.response.send_message("Custom time not supported yet!")
        return
        
    await db_utils.update_last_killed_time(boss_id, last_killed_time)
    await field_boss_update_send_message(ctx, boss_id)
    
@gnucommands_group_start.command(name="goblin-tracker", description="Goblin Bandit")
async def goblintracker_command(
    ctx: discord.ApplicationContext,
    last_killed_time: discord.Option(
        str,
        "Specify the time the goblin bandits were killed",
        autocomplete=discord.utils.basic_autocomplete(["now"]),
    ),
):
    boss_id = 4 # Boss ID from field_bosses table
    
    last_killed_time = await parse_user_time_input_to_unix(last_killed_time)
    if last_killed_time is None:
        await ctx.interaction.response.send_message("Custom time not supported yet!")
        return
        
    await db_utils.update_last_killed_time(boss_id, last_killed_time)
    await field_boss_update_send_message(ctx, boss_id)
    
@gnucommands_group_start.command(name="spider-tracker", description="Wolf-striped Desert Spider")
async def spidertracker_command(
    ctx: discord.ApplicationContext,
    last_killed_time: discord.Option(
        str,
        "Specify the time the gnu was killed",
        autocomplete=discord.utils.basic_autocomplete(["now"]),
    ),
):
    boss_id = 5 # Boss ID from field_bosses table
    
    last_killed_time = await parse_user_time_input_to_unix(last_killed_time)
    if last_killed_time is None:
        await ctx.interaction.response.send_message("Custom time not supported yet!")
        return
    
    await db_utils.update_last_killed_time(boss_id, last_killed_time)
    await field_boss_update_send_message(ctx, boss_id)

@gnucommands_group_start.command(name="ancient-tracker", description="Ancients")
async def ancientracker_command(
    ctx: discord.ApplicationContext,
    area: discord.Option(
        str,
        "Specify the area of the ancients killed",
        autocomplete=discord.utils.basic_autocomplete(
            ["Qilla", "Muyu", "Karu", "Filia", "Physis", "Cor", "Raspa", "Uladh"]),
    ),
    last_killed_time: discord.Option(
        str,
        "Specify the time that the ancients were killed",
        autocomplete=discord.utils.basic_autocomplete(["now"]),
    ),
):
    last_killed_time = await parse_user_time_input_to_unix(last_killed_time)
    if last_killed_time is None:
        await ctx.interaction.response.send_message("Custom time not supported yet!")
        return
    
    await db_utils.create_new_ancient_time(area, last_killed_time)
    await ancient_create_message(ctx, area, last_killed_time)
    
@gnucommands_group_list.command(name="ancients", description="Lists all currently active ancient timers")
async def ancient_list_command(
    ctx: discord.ApplicationContext,
):
    await list_timers_message(ctx, db_utils.ancients, 'Ancients')

@gnucommands_group_list.command(name="field-bosses", description="Lists all field bosses")
async def ancient_list_command(
    ctx: discord.ApplicationContext,
):
    await list_timers_message(ctx, db_utils.bosses, 'Field-Bosses')
    
@gnucommands_group_list.command(name="raid-bosses", description="Lists all field bosses")
async def ancient_list_command(
    ctx: discord.ApplicationContext,
):
    await list_timers_message(ctx, db_utils.raid_bosses, 'Field-Raids')
    
@gnucommands_group_list.command(name="todays-raids", description="Lists all todays raids")
async def todays_raids_list_command(
    ctx: discord.ApplicationContext,
):
    pass
    
@gnucommands_group_clear.command(name="ancient", description="Clears a ancient spawn timer")
async def ancient_clear_command(
    ctx: discord.ApplicationContext,
    ancient: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(db_utils.get_ancient_options)),
):
    id = int(re.search(r"\d+", ancient).group())
    await db_utils.delete_ancient_time(id)
    await ctx.interaction.response.send_message(f"Ancient {id} cleared!")

@gnucommands_group_clear.command(name="field-boss", description="Clears a field-boss spawn timer")
async def ancient_clear_command(
    ctx: discord.ApplicationContext,
    boss: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(db_utils.get_field_boss_options)),
):
    id = int(re.search(r"\d+", boss).group())
    await db_utils.update_last_killed_time_to_null(id)
    await ctx.interaction.response.send_message(f"Field-boss {id} cleared!")

# Bot timer commands
bot.add_application_command(gnucommands_group_start)
bot.add_application_command(gnucommands_group_list)
bot.add_application_command(gnucommands_group_clear)

# Start the bot
bot.run(settings.token)
