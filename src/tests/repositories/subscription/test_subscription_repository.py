from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.subscription.subscription_repository import SubscriptionRepository
from src.schemas.subscription.subscription_schema import SubscriptionInput, SubscriptionUpdate


@pytest.mark.anyio
class TestSubscriptionRepository:
    @pytest.fixture
    async def subscription_repo(self, session: AsyncSession):
        return SubscriptionRepository(session)

    @pytest.fixture
    async def create_subscription(self, subscription_repo: SubscriptionRepository):
        subscription_data = SubscriptionInput(
            access=1.0,
            end_at=datetime(2024, 12, 31),
            user_id=uuid4()
        )
        return await subscription_repo.create(subscription_data)

    async def test_create_subscription(self, subscription_repo: SubscriptionRepository):
        """Test creating a subscription."""
        subscription_data = SubscriptionInput(
            access=2.0,
            end_at=datetime(2025, 12, 31),
            user_id=uuid4()
        )
        subscription = await subscription_repo.create(subscription_data)

        assert subscription.id is not None
        assert subscription.access == 2.0
        assert subscription.end_at == datetime(2025, 12, 31)
        assert subscription.user_id is not None

    async def test_get_all_subscriptions(self, subscription_repo: SubscriptionRepository, create_subscription):
        """Test retrieving all subscriptions."""
        subscription = await create_subscription
        subscriptions = await subscription_repo.get_all()

        assert len(subscriptions) > 0
        assert subscriptions[0].id == subscription.id

    async def test_get_subscription_by_id(self, subscription_repo: SubscriptionRepository, create_subscription):
        """Test retrieving a subscription by its ID."""
        subscription = await create_subscription
        retrieved_subscription = await subscription_repo.get_subscription(subscription.id)

        assert retrieved_subscription.id == subscription.id
        assert retrieved_subscription.access == subscription.access

    async def test_update_subscription(self, subscription_repo: SubscriptionRepository, create_subscription):
        """Test updating a subscription."""
        subscription = await create_subscription
        updated_data = SubscriptionUpdate(access=3.0, end_at=datetime(2026, 12, 31))
        updated_subscription = await subscription_repo.update(subscription, updated_data)

        assert updated_subscription.access == 3.0
        assert updated_subscription.end_at == datetime(2026, 12, 31)

    async def test_delete_subscription(self, subscription_repo: SubscriptionRepository, create_subscription):
        """Test deleting a subscription."""
        subscription = await create_subscription
        deleted = await subscription_repo.delete(subscription)

        assert deleted is True
        assert await subscription_repo.get_subscription(subscription.id) is None

    async def test_subscription_exists_by_id(self, subscription_repo: SubscriptionRepository, create_subscription):
        """Test checking if a subscription exists by ID."""
        subscription = await create_subscription
        exists = await subscription_repo.subscription_exists_by_id(subscription.id)

        assert exists is True

    async def test_subscription_does_not_exist(self, subscription_repo: SubscriptionRepository):
        """Test checking if a subscription does not exist by an invalid ID."""
        exists = await subscription_repo.subscription_exists_by_id(uuid4())

        assert exists is False
