from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.subscription.subscription import Subscription
from src.schemas.subscription.subscription_schema import SubscriptionOutput, SubscriptionEndpoint, SubscriptionInput


class SubscriptionRepository:
    """
    Repository for handling operations related to the Subscription model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        :param session: The AsyncSession to interact with the database
        """
        self.session = session

    async def create(self, data: SubscriptionInput) -> SubscriptionOutput:
        """
        Creates a new subscription and stores it in the database.

        :param data: The input data to create the subscription
        :return: The created subscription as SubscriptionOutput
        """
        subscription = Subscription(
            access=data.access,
            end_at=data.end_at,
            user_id=data.user_id
        )
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return SubscriptionOutput(
            id=subscription.id,
            access=subscription.access,
            created_at=subscription.created_at,
            end_at=subscription.end_at,
            user_id=subscription.user_id
        )

    async def get_all(self) -> List[Optional[SubscriptionOutput]]:
        """
        Retrieves all subscriptions from the database, ordered by creation date.

        :return: A list of SubscriptionOutput objects representing all subscriptions
        """
        stmt = select(Subscription).order_by(Subscription.created_at)
        result = await self.session.execute(stmt)
        subscriptions = result.scalars().all()
        return [SubscriptionOutput(**subscription.__dict__) for subscription in subscriptions]

    async def get_subscription(self, _id: UUID) -> SubscriptionOutput:
        """
        Retrieves a specific subscription by its ID.

        :param _id: The ID of the subscription to retrieve
        :return: The subscription as SubscriptionOutput if found, otherwise None
        """
        subscription = await self.session.get(Subscription, _id)
        if subscription:
            return SubscriptionOutput(
                id=subscription.id,
                access=subscription.access,
                created_at=subscription.created_at,
                end_at=subscription.end_at,
                user_id=subscription.user_id
            )
        return None

    async def update(self, subscription: Subscription, data: SubscriptionEndpoint) -> SubscriptionOutput:
        """
        Updates an existing subscription with the given data.

        :param subscription: The subscription instance to update
        :param data: The new data for updating the subscription
        :return: The updated subscription as SubscriptionOutput
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(subscription, key, value)
        await self.session.commit()
        await self.session.refresh(subscription)
        return SubscriptionOutput(
            id=subscription.id,
            access=subscription.access,
            created_at=subscription.created_at,
            end_at=subscription.end_at,
            user_id=subscription.user_id
        )

    async def delete(self, subscription: Subscription) -> bool:
        """
        Deletes a subscription from the database.

        :param subscription: The subscription to delete
        :return: True if the subscription was successfully deleted, otherwise False
        """
        await self.session.delete(subscription)
        await self.session.commit()
        return True

    async def subscription_exists_by_id(self, _id: UUID) -> bool:
        """
        Checks if a subscription exists by its ID.

        :param _id: The ID of the subscription
        :return: True if the subscription exists, otherwise False
        """
        subscription = await self.session.get(Subscription, _id)
        return subscription is not None
