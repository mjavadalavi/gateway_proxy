from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.website import Website
from typing import Optional

class WebsiteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_api_key(self, api_key: str) -> Optional[Website]:
        result = await self.db.execute(
            select(Website).where(Website.api_key == api_key, Website.is_active == True)
        )
        return result.scalars().first()
    
    async def create(self, domain: str, name: str) -> Website:
        import secrets
        api_key = secrets.token_urlsafe(32)
        
        website = Website(
            domain=domain,
            name=name,
            api_key=api_key
        )
        self.db.add(website)
        await self.db.commit()
        await self.db.refresh(website)
        return website 