from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.transaction import Transaction
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import func


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self, 
        amount: Decimal,
        website_id: int,
        user_phone: str,
        callback_url: str,
        gateway_token: str,
        gateway_url: str
    ) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(
            amount=amount,
            website_id=website_id,
            user_phone=user_phone,
            callback_url=callback_url,
            status="pending",
            gateway_token=gateway_token,
            gateway_url=gateway_url
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_by_token(self, token: str) -> Optional[Transaction]:
        """Get transaction by token"""
        result = await self.db.execute(
            select(Transaction).where(Transaction.token == token)
        )
        return result.scalars().first()

    async def get_by_order_id(self, order_id: str, website_id: int) -> Optional[Transaction]:
        """Get transaction by order_id and website_id"""
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.order_id == order_id,
                Transaction.website_id == website_id
            )
        )
        return result.scalars().first()

    async def update_status(self, token: str, status: str, ref_id: Optional[str] = None) -> Optional[Transaction]:
        """Update transaction status and ref_id"""
        query = update(Transaction).where(
            Transaction.gateway_token == token
        ).values(
            status=status,
            ref_id=ref_id
        ).returning(Transaction)
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalars().first()

    async def get_website_transactions(
        self,
        website_id: int,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get all transactions for a website with optional status filter"""
        query = select(Transaction).where(
            Transaction.website_id == website_id
        ).order_by(
            Transaction.created_at.desc()
        ).limit(limit).offset(offset)
        
        if status:
            query = query.where(Transaction.status == status)
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_transaction_stats(self, website_id: int):
        """Get transaction statistics for a website"""
        
        # Total amount of successful transactions
        total_amount_query = select(func.sum(Transaction.amount)).where(
            Transaction.website_id == website_id,
            Transaction.status == "completed"
        )
        
        # Count of transactions by status
        status_count_query = select(
            Transaction.status,
            func.count(Transaction.id)
        ).where(
            Transaction.website_id == website_id
        ).group_by(Transaction.status)
        
        total_amount = await self.db.execute(total_amount_query)
        status_counts = await self.db.execute(status_count_query)
        
        return {
            "total_amount": total_amount.scalar() or 0,
            "status_counts": dict(status_counts.all())
        }

    async def update_gateway_token(self, token: str, gateway_token: str) -> Optional[Transaction]:
        """Update transaction's gateway token"""
        query = update(Transaction).where(
            Transaction.token == token
        ).values(
            gateway_token=gateway_token
        ).returning(Transaction)
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalars().first()

    async def get_by_gateway_token(self, gateway_token: str) -> Optional[Transaction]:
        """Get transaction by gateway token"""
        result = await self.db.execute(
            select(Transaction).where(Transaction.gateway_token == gateway_token)
        )
        return result.scalars().first() 