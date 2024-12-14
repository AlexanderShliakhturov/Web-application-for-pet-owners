from sqlalchemy import text
import asyncio
import os, sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
from src.database import async_session_factory

sql_file_path = 'db_init.sql'

async def add_ttrigger():
    try:
        async with async_session_factory() as session:
                async with session.begin():
                    
                    sql_commands = [
                    """
                    ALTER TABLE users
                    ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                    """,
                    """
                    CREATE OR REPLACE FUNCTION update_last_updated()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.last_updated = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                    """,
                    """
                    CREATE TRIGGER trigger_update_last_updated
                    BEFORE UPDATE ON users
                    FOR EACH ROW
                    EXECUTE FUNCTION update_last_updated();
                    """
                ]

                    for command in sql_commands:
                        command = command.strip()
                        if command: 
                            await session.execute(text(command))
                        print("SQL выполнен:", command[:50])
    except Exception as e:
        print(f"Ошибка создания триггера {e}")
        
if __name__ == "__main__":
    asyncio.run(add_ttrigger())        