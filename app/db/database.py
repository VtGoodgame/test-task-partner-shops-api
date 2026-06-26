# db/database.py
import aiosqlite
from datetime import datetime, time
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from typing import Any, AsyncGenerator, Optional, List, Dict

class Database:
    """
    Асинхронный класс для работы с SQLite
    
    Особенности:
    - Использует aiosqlite для асинхронной работы
    - Поддерживает сырые SQL запросы
    - Встроенные методы CRUD
    - Безопасная работа с таблицами
    """
    
    def __init__(self, db_path: str):
        """
        Инициализация базы данных
        
        Args:
            db_path: Путь к файлу БД (например, "./app.db")
        """
        self.db_path = str(db_path)
    
    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Контекстный менеджер для работы с SQLite"""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await conn.close()
    
    async def create_tables(self, base: type[DeclarativeBase]) -> None:
        """
        Создаёт все таблицы из SQLAlchemy моделей
        
        Args:
            base: SQLAlchemy Base класс
        """
        engine = create_async_engine(f"sqlite+aiosqlite:///{self.db_path}")
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all, checkfirst=True)
        await engine.dispose()
    
    async def fetch(
        self,
        query: str,
        params: tuple[Any, ...] = (),
        table: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Выполняет SQL запрос и возвращает все строки (SELECT)
        
        Args:
            query: SQL запрос
            params: Параметры для подстановки
            table: Имя таблицы для проверки безопасности (опционально)
        
        Returns:
            List[Dict[str, Any]]: Список словарей с данными
        """
        # Проверка безопасности защита от SQL инъекций
        if table:
            allowed = {"partner_stores", "delivery_slots"}
            if table not in allowed:
                raise ValueError(f"Таблица '{table}' не разрешена")
        
        async with self.connect() as conn:
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        
        
    async def get_stores_with_nearest_delivery_by_hour(
        self,
        current_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Получает все магазины с ближайшим интервалом доставки по часу
        
        Args:
            current_time: Текущее время пользователя
        
        Returns:
            List[Dict[str, Any]]: Список магазинов с информацией о доставке
        """
        if current_time is None:
            current_time = datetime.now()
        
        current_hour = current_time.hour
        
        query = """
        WITH nearest_slots AS (
            SELECT 
                ds.shop_id,
                ds.delivery_start,
                ds.delivery_end,
                CAST(substr(ds.delivery_start, 1, 2) AS INTEGER) as start_hour,
                ABS(CAST(substr(ds.delivery_start, 1, 2) AS INTEGER) - ?) as hour_diff,
                ROW_NUMBER() OVER (
                    PARTITION BY ds.shop_id 
                    ORDER BY 
                        CASE 
                            WHEN CAST(substr(ds.delivery_start, 1, 2) AS INTEGER) = ? 
                            THEN 0 
                            ELSE 1 
                        END,
                        ABS(CAST(substr(ds.delivery_start, 1, 2) AS INTEGER) - ?) ASC
                ) as rn
            FROM delivery_slots ds
            WHERE ds.is_holiday = 0
        )
        SELECT 
            ps.id,
            ps.logo_url,
            ps.name,
            ps.delivery,
            ps.official_website,
            ps.is_active,
            ns.delivery_start as nearest_delivery_start,
            ns.delivery_end as nearest_delivery_end,
            ns.hour_diff as hour_difference,
            CASE 
                WHEN ns.delivery_start IS NOT NULL AND ns.delivery_end IS NOT NULL 
                THEN 1 
                ELSE 0 
            END as has_delivery
        FROM partner_stores ps
        LEFT JOIN nearest_slots ns ON ps.id = ns.shop_id AND ns.rn = 1
        WHERE ps.is_active = 1
        ORDER BY 
            CASE 
                WHEN ns.delivery_start IS NOT NULL AND ns.delivery_end IS NOT NULL 
                THEN 1 
                ELSE 0 
            END DESC,
            ns.hour_diff ASC
        """
        
        return await self.fetch(query, (current_hour, current_hour, current_hour))