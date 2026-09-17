from neo4j import AsyncGraphDatabase
from app.core.config import settings

class Neo4jClient:
    def __init__(self):
        self._driver = None

    def connect(self):
        self._driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    async def close(self):
        if self._driver:
            await self._driver.close()

    async def query(self, cypher: str, parameters: dict = None):
        if not self._driver:
            raise RuntimeError("Neo4j driver is not initialized.")
        async with self._driver.session(database=settings.NEO4J_DATABASE) as session:
            result = await session.run(cypher, parameters or {})
            return [record.data() async for record in result]

neo4j_client = Neo4jClient()