from sqlalchemy import text
import asyncio
import os, sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from src.database import async_session_factory

sql_file_path = 'db_delete.sql'

async def delete():
    try:
        async with async_session_factory() as session:
            async with session.begin():
                with open(sql_file_path, 'r') as file:
                    sql_script = file.read()
                sql_commands = sql_script.split(';')

                for command in sql_commands:
                    command = command.strip()
                    if command: 
                        await session.execute(text(command))    
                        
                print("Таблицы успешно удалены из базы данных.")
    except Exception as e:
        print(f"Ошибка удаления таблиц из базы данных: {e}")

if __name__ == "__main__":
    asyncio.run(delete())