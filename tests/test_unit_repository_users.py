import unittest
from unittest.mock import MagicMock, AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserSchema
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar_url,
)

@pytest.mark.asyncio
class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        email="some1@gmail.com"
        user = User(id=1, username='test_user', email=email, password='12345678', confirmed=True)
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email, self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserSchema(username='test_user', email='some1@gmail.com', password='12345678')
        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, 'test_user')
        self.assertEqual(result.email, 'some1@gmail.com')

    async def test_update_token(self):
        token = "test_token"
        user = User(id=1, username='test_user', email='some1@gmail.com', password='12345678', confirmed=True)
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        await update_token(user, token, self.session)
        self.assertEqual(user.refresh_token, token)
    
    async def test_confirmed_email(self):
        email = "some1@gmail.com"
        user = User(id=1, username='test_user', email=email, password='12345678', confirmed=False)
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        await confirmed_email(email, self.session)
        self.assertEqual(user.confirmed, True)
    
    async def test_update_avatar_url(self):
        email = "some1@gmail.com"
        url = "test_url"
        user = User(id=1, username='test_user', email=email, password='12345678', confirmed=True)
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await update_avatar_url(email, url, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.avatar, url)