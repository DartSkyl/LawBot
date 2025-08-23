from typing import List

import asyncpg as apg
from asyncpg import Record


class BotBase:
    """Через данный класс реализованы конект с базой данных и методы взаимодействия с БД"""

    def __init__(self, _db_user, _db_pass, _db_name, _db_host):
        self.db_name = _db_name
        self.db_user = _db_user
        self.db_pass = _db_pass
        self.db_host = _db_host
        self.pool = None

    async def connect(self):
        """Для использования БД будем использовать пул соединений.
        Иначе рискуем поймать asyncpg.exceptions._base.InterfaceError: cannot perform operation:
        another operation is in progress. А нам это не надо"""
        self.pool = await apg.create_pool(
            database=self.db_name,
            user=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            max_inactive_connection_lifetime=10,
            min_size=1,
            max_size=100
        )

    async def check_db_structure(self):
        async with self.pool.acquire() as connection:
            # Таблица со всеми ссылками
            await connection.execute("CREATE TABLE IF NOT EXISTS consumer_card ("
                                     "id SERIAL PRIMARY KEY,"
                                     "card_name TEXT UNIQUE,"
                                     "card_id VARCHAR(155) UNIQUE,"
                                     "card_content TEXT NOT NULL"
                                     ");")

            await connection.execute("CREATE TABLE IF NOT EXISTS consumer_card_content ("
                                     "id SERIAL PRIMARY KEY,"
                                     "item_name TEXT,"
                                     "item_id VARCHAR(155) UNIQUE,"
                                     "item_content TEXT,"
                                     "card_id VARCHAR(155) REFERENCES consumer_card(card_id) ON DELETE CASCADE"
                                     ");")

            await connection.execute("CREATE TABLE IF NOT EXISTS laws ("
                                     "id SERIAL PRIMARY KEY,"
                                     "law_name TEXT,"
                                     "law_id VARCHAR(155) UNIQUE,"
                                     "law_description TEXT,"
                                     "law_content TEXT"
                                     ");")

    # ====================
    # Карты потребителей
    # ====================

    async def add_new_card(self, card_name, card_id, card_content):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO consumer_card (card_name, card_id, card_content)
                VALUES ($1, $2, $3)
                """,
                card_name, card_id, card_content
            )

    async def get_all_cards(self) -> List[Record]:
        async with self.pool.acquire() as connection:
            result = await connection.fetch("SELECT * FROM consumer_card ORDER BY id")
            return result

    async def get_card_by_id(self, card_id) -> Record:
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM consumer_card WHERE card_id = '{card_id}'")
            return result[0]

    async def remove_card(self, card_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM consumer_card WHERE card_id = '{card_id}'")

    # ====================
    # Пункты карт потребителей
    # ====================

    async def add_new_item(self, item_name, item_id, item_content, card_id):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO consumer_card_content (item_name, item_id, item_content, card_id)
                VALUES ($1, $2, $3, $4)
                """,
                item_name, item_id, item_content, card_id
            )

    async def get_all_items_by_card(self, card_id) -> List[Record]:
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM consumer_card_content WHERE card_id = '{card_id}' "
                                            f"ORDER BY id")
            return result

    async def get_item_by_id(self, item_id) -> Record:
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM consumer_card_content WHERE item_id = '{item_id}'")
            return result[0]

    async def remove_item(self, item_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM consumer_card_content WHERE item_id = '{item_id}'")

    # ====================
    # Законы и права
    # ====================

    async def add_new_law(self, law_name, law_id, law_description, law_content):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO laws (law_name, law_id, law_description, law_content)
                VALUES ($1, $2, $3, $4)
                """,
                law_name, law_id, law_description, law_content
            )

    async def get_all_laws(self) -> List[Record]:
        async with self.pool.acquire() as connection:
            result = await connection.fetch("SELECT * FROM laws ORDER BY id")
            return result

    async def get_law_by_id(self, law_id) -> Record:
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM laws WHERE law_id = '{law_id}'")
            return result[0]

    async def remove_law(self, law_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM laws WHERE law_id = '{law_id}'")
