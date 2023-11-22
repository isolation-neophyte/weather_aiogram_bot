#import os
#import aiomysql
#
#from loader import loop
#from dotenv import load_dotenv, find_dotenv
#
#
#async def connect():
#    load_dotenv(find_dotenv())
#
#    return await aiomysql.create_pool(
#        host=os.getenv("host"),
#        user=os.getenv("user"),
#        password=os.getenv("password"),
#        db=os.getenv("database"),
#        autocommit=True,
#        loop=loop
#    )
#
#db_connect = loop.run_until_complete(connect())
