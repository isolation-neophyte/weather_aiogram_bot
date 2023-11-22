import os
import aiomysql

from dotenv import load_dotenv, find_dotenv


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        load_dotenv(find_dotenv())
        self.pool = await aiomysql.create_pool(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            db=os.getenv("database"),
            autocommit=True,
        )

    async def disconnect(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def get_users(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users_info")
                result = await cur.fetchall()
                return result

    async def get_timezone(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT timezone FROM users_info WHERE user_id = %s", (user_id,))
                result = await cur.fetchone()
                return result[0]

    async def get_forecast_msg_id(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT forecast_msg_id FROM users_info WHERE user_id = %s", (user_id,))
                result = await cur.fetchone()
                return result[0]

    async def get_last_city_data(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT last_city_data FROM users_info WHERE user_id = %s", (user_id,))
                result = await cur.fetchone()
                city_data = result[0]
                if city_data[0].isdigit():
                    return city_data.split(", ")
                else:
                    return city_data

    async def get_sub_city_data(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT sub_city_data FROM users_info WHERE user_id = %s", (user_id,))
                result = await cur.fetchone()
                city_data = result[0]
                if city_data[0].isdigit():
                    return city_data.split(", ")
                else:
                    return city_data

    async def get_sub_forecast_time(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT sub_forecast_time FROM users_info WHERE user_id = %s", (user_id,))
                result = await cur.fetchone()
                return result[0]

    async def create_user(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                return await cur.execute("INSERT INTO users_info (user_id) VALUES (%s)", (user_id,))

    async def is_user_exists(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users_info WHERE user_id = %s", (user_id,))
                result = await cur.fetchmany(1)
                return bool(len(result))

    async def is_user_subscribed(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users_info WHERE user_id = %s AND sub_city_data IS NOT NULL", (user_id,))
                result = await cur.fetchmany(1)
                return bool(len(result))

    async def is_user_has_timezone(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users_info WHERE user_id = %s AND timezone IS NOT NULL", (user_id,))
                result = await cur.fetchmany(1)
                return bool(len(result))

    async def create_subscription(self, sub_city_data, sub_forecast_time, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                return await cur.execute("""
                UPDATE users_info
                SET sub_city_data = %s,
                sub_forecast_time = %s
                WHERE user_id = %s""", (sub_city_data, sub_forecast_time, user_id))

    async def set_timezone(self, user_id, timezone):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                return await cur.execute("UPDATE users_info SET timezone = %s WHERE user_id = %s", (timezone, user_id,))

    async def set_last_city_data(self, user_id, city_data):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if isinstance(city_data, list):
                    city_data = f"{city_data[0]}, {city_data[1]}"
                await cur.execute("UPDATE users_info SET last_city_data = %s WHERE user_id = %s", (city_data, user_id,))

    async def set_sub_city_data(self, user_id, city_data):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE users_info SET sub_city_data = %s WHERE user_id = %s", (city_data, user_id,))

    async def set_sub_forecast_time(self, user_id, time):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE users_info SET sub_forecast_time = %s WHERE user_id = %s", (time, user_id,))

    async def set_forecast_msg_id(self, user_id, msg_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE users_info SET forecast_msg_id = %s WHERE user_id = %s", (msg_id, user_id,))

    async def cancel_subscription(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                UPDATE users_info 
                SET sub_city_data = NULL,
                sub_forecast_time = NULL
                WHERE user_id = %s""", (user_id,))


db = Database()
