import aiosqlite
import discord
import settings

bosses = None
raid_bosses = None
ancients = None
ancienttracker_image = "https://wiki.mabinogiworld.com/images/6/64/Bohemian_Set_Equipped_Female_Front.png"


async def update_last_killed_time(boss_id: int, last_killed_time: int):
    global bosses
    async with aiosqlite.connect('timers_db.db') as db:
        await db.execute('UPDATE field_bosses SET last_killed_time = ? WHERE id = ?', (last_killed_time, boss_id))
        await db.commit()
    bosses = await get_field_bosses_from_db()

async def update_description(boss_id: int, description: str):
    global bosses
    async with aiosqlite.connect('timers_db.db') as db:
        await db.execute('UPDATE field_bosses SET description = ? WHERE id = ?', (description, boss_id))
        await db.commit()
    bosses = await get_field_bosses_from_db()

async def update_last_killed_time_to_null(boss_id: int):
    global bosses
    async with aiosqlite.connect('timers_db.db') as db:
        await db.execute('UPDATE field_bosses SET last_killed_time = ? WHERE id = ?', (None, boss_id))
        await db.commit()
    bosses = await get_field_bosses_from_db()
    print(f'Cleared boss last_killed at id:{boss_id}')
    
async def create_new_ancient_time(area, last_killed_time: int):
    global ancients
    name = f'{area}-ancient-tracker'
    description = None
    respawn_time = settings.ancient_respawn_time
    role_id = settings.fieldboss_roleid
    image_link = ancienttracker_image
    async with aiosqlite.connect('timers_db.db') as db:
        await db.execute('INSERT INTO ancients (name, description, respawn_time, last_killed_time, role_id, image_link) VALUES (?, ?, ?, ?, ?, ?)', (name, description, respawn_time, last_killed_time, role_id, image_link))
        await db.commit()
    ancients = await get_ancients_from_db()
    
async def delete_ancient_time(id):
    global ancients
    async with aiosqlite.connect('timers_db.db') as db:
        await db.execute('DELETE FROM ancients WHERE id =?', (id,))
        await db.commit()
    ancients = await get_ancients_from_db()
    print(f"Deleted ancient at id:{id}")
        
async def get_field_bosses_from_db():
    async with aiosqlite.connect('timers_db.db') as db:
        async with db.execute('SELECT * FROM field_bosses') as cursor:
            result = await cursor.fetchall()
            return result
  
async def get_field_raids_from_db():
    async with aiosqlite.connect('timers_db.db') as db:
        async with db.execute('SELECT * FROM field_raids') as cursor:
            result = await cursor.fetchall()
            return result
        
async def get_ancients_from_db():
    async with aiosqlite.connect('timers_db.db') as db:
        async with db.execute('SELECT * FROM ancients') as cursor:
            result = await cursor.fetchall()
            return result
        
async def get_ancient_options(ctx: discord.ApplicationContext):
    global ancients
    options = [f'{ancient[0]} {ancient[1]}' for ancient in ancients]
    return options

async def get_field_boss_options(ctx: discord.ApplicationContext):
    global bosses
    options = [f'{boss[0]} {boss[1]}' for boss in bosses if boss[5] != None]
    return options