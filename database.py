# database.py

import logging
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
import os
from datetime import datetime

from config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name='{self.name}')>"

class DailyRecord(Base):
    __tablename__ = "daily_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    date = Column(DateTime, index=True, nullable=False)
    summa = Column(Integer, nullable=False)
    
    # Основные поля
    s_fz = Column(Boolean, default=False)
    krh = Column(Boolean, default=False)
    omp = Column(Boolean, default=False)
    sms = Column(Boolean, default=False)
    vis_dbo = Column(Boolean, default=False)
    viv_krh = Column(Boolean, default=False)
    krh_vydacha = Column(Boolean, default=False)
    krh_start = Column(Boolean, default=False)
    krh_oborot_sum = Column(Integer, default=0)
    podpiska_god = Column(Boolean, default=False)
    komp = Column(Boolean, default=False)
    vse_vezde = Column(Boolean, default=False)
    sticker = Column(Boolean, default=False)
    ref_sum = Column(Integer, default=0)
    dk_sum = Column(Integer, default=0)
    dk_type = Column(String(50), default=None)
    multipolis_sum = Column(Integer, default=0)
    debet_type = Column(String(20), default=None)
    debet_sum = Column(Integer, default=0)
    halvyenok = Column(Boolean, default=False)
    
    # Новые поля для финансовых продуктов
    vklad_type = Column(String(50), default=None)
    kd_type = Column(String(50), default=None)
    
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<DailyRecord(id={self.id}, user_id={self.user_id}, date={self.date}, total={self.total})>"

def ensure_schema():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы БД созданы/проверены успешно")
        
        if DATABASE_URL.startswith("sqlite"):
            db_path = DATABASE_URL.replace("sqlite:///", "")
            
            conn = sqlite3.connect(db_path)
            try:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_records';")
                if cur.fetchone() is None:
                    return
                
                cur.execute("PRAGMA table_info(daily_records);")
                cols = [row[1] for row in cur.fetchall()]
                
                # Добавляем недостающие колонки только если их нет
                missing_columns = {
                    "vis_dbo": "ALTER TABLE daily_records ADD COLUMN vis_dbo BOOLEAN DEFAULT FALSE;",
                    "viv_krh": "ALTER TABLE daily_records ADD COLUMN viv_krh BOOLEAN DEFAULT FALSE;",
                    "vklad_type": "ALTER TABLE daily_records ADD COLUMN vklad_type TEXT DEFAULT NULL;",
                    "kd_type": "ALTER TABLE daily_records ADD COLUMN kd_type TEXT DEFAULT NULL;",
                }
                
                for col_name, sql in missing_columns.items():
                    if col_name not in cols:
                        try:
                            cur.execute(sql)
                            logger.info(f"Добавлена колонка {col_name}")
                        except sqlite3.OperationalError as e:
                            if "duplicate column name" not in str(e):
                                raise e
                            logger.warning(f"Колонка {col_name} уже существует")
                
                # Если есть старая колонка vis и нет vis_dbo, переименовываем
                if "vis" in cols and "vis_dbo" not in cols:
                    try:
                        cur.execute("ALTER TABLE daily_records RENAME COLUMN vis TO vis_dbo;")
                        logger.info("Колонка vis переименована в vis_dbo")
                    except sqlite3.OperationalError as e:
                        logger.warning(f"Не удалось переименовать колонку: {e}")
                
                conn.commit()
                    
            finally:
                conn.close()
                
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")

ensure_schema()

# Функции для работы с БД
def get_db_session():
    return SessionLocal()

def close_db_session(session):
    if session:
        session.close()

async def db_get_user(telegram_id: int):
    def _get():
        session = get_db_session()
        try:
            return session.query(User).filter(User.telegram_id == telegram_id).first()
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_get)

async def db_create_user(telegram_id: int, name: str):
    def _create():
        session = get_db_session()
        try:
            user = User(telegram_id=telegram_id, name=name.strip())
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_create)

async def db_save_record(record_data: dict):
    def _save():
        session = get_db_session()
        try:
            rec = DailyRecord(**record_data)
            session.add(rec)
            session.commit()
            session.refresh(rec)
            return rec
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_save)

async def db_get_user_records(telegram_id: int, limit: int = 10):
    def _get():
        session = get_db_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                return []
            return session.query(DailyRecord)\
                .filter(DailyRecord.user_id == user.id)\
                .order_by(DailyRecord.date.desc())\
                .limit(limit)\
                .all()
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_get)

async def db_get_records_by_date_range(telegram_id: int, start_date, end_date):
    def _get():
        session = get_db_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                return []
            return session.query(DailyRecord)\
                .filter(DailyRecord.user_id == user.id)\
                .filter(DailyRecord.date >= start_date)\
                .filter(DailyRecord.date <= end_date)\
                .order_by(DailyRecord.date)\
                .all()
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_get)

async def db_delete_record(record_id: int):
    def _delete():
        session = get_db_session()
        try:
            record = session.query(DailyRecord).filter(DailyRecord.id == record_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_delete)

async def db_get_record_by_id(record_id: int):
    def _get():
        session = get_db_session()
        try:
            return session.query(DailyRecord).filter(DailyRecord.id == record_id).first()
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_get)

async def db_update_record(record_id: int, update_data: dict):
    def _update():
        session = get_db_session()
        try:
            record = session.query(DailyRecord).filter(DailyRecord.id == record_id).first()
            if record:
                for key, value in update_data.items():
                    setattr(record, key, value)
                session.commit()
                session.refresh(record)
                return record
            return None
        finally:
            close_db_session(session)
    
    return await asyncio.to_thread(_update)

# Экспортируем все функции для импорта
__all__ = [
    'get_db_session',
    'close_db_session',
    'db_get_user',
    'db_create_user',
    'db_save_record',
    'db_get_user_records',
    'db_get_records_by_date_range',
    'db_delete_record',
    'db_get_record_by_id',
    'db_update_record',
    'User',
    'DailyRecord',
    'ensure_schema'
]