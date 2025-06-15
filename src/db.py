from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from os import environ
from dotenv import load_dotenv
load_dotenv()
# ASYNC_DB_URL = "mysql+aiomysql://root@db:3306/demo?charset=utf8mb4"
ASYNC_DB_URL = URL.create(
    drivername="mysql+aiomysql",
    username=environ.get('DB_USER'),
    password=environ.get('DB_PASSWORD'),
    host="db",
    database=environ.get('DB_NAME'),
    query={"charset":"utf8mb4"}
)

async_engine = create_async_engine(ASYNC_DB_URL, connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
    },echo=True)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session