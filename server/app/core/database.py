"""
Database configuration and initialization.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional

from app.core.config import settings
from app.models.workflow import Workflow
from app.models.execution import WorkflowExecution
from app.models.agent import Agent


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = Database()


async def connect_to_mongo():
    """Create database connection."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()


async def init_database():
    """Initialize the database and Beanie ODM."""
    await connect_to_mongo()
    
    # Initialize Beanie with document models
    await init_beanie(
        database=db.database,
        document_models=[
            Workflow,
            WorkflowExecution,
            Agent,
        ]
    )


def get_database():
    """Get database instance."""
    return db.database