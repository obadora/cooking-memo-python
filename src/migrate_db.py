from sqlalchemy import create_engine
from src.models.task import Base as TaskBase
from src.models.recipe import Base as RecipeBase
from sqlalchemy.engine.url import URL
from os import environ
from dotenv import load_dotenv
load_dotenv()

DB_URL = URL.create(
    drivername="mysql+aiomysql",
    username=environ.get('DB_USER'),
    password=environ.get('DB_PASSWORD'),
    host="db",
    database=environ.get('DB_NAME'),
    query={"charset":"utf8mb4"}
)
engine = create_engine(DB_URL, connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
    }, echo=True)


def reset_database():
    TaskBase.metadata.drop_all(bind=engine)
    TaskBase.metadata.create_all(bind=engine)
    RecipeBase.metadata.drop_all(bind=engine)
    RecipeBase.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()