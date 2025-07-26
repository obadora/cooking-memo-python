from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from os import environ
from dotenv import load_dotenv
load_dotenv()

# DATABASE_URLから設定を取得するか、個別の環境変数を使用
if environ.get('DATABASE_URL'):
    ASYNC_DB_URL = environ.get('DATABASE_URL')
else:
    ASYNC_DB_URL = URL.create(
        drivername="mysql+aiomysql",
        username=environ.get('DB_USER'),
        password=environ.get('DB_PASSWORD'),
        host=environ.get('DB_HOST', "db"),  # 環境変数化
        database=environ.get('DB_NAME'),
        query={"charset":"utf8mb4"}
    )

async_engine = create_async_engine(
    ASYNC_DB_URL,
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
    },
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True
)

async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session
