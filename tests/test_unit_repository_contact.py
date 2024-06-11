from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository.contacts import (create_contact,
                                     update_contact,
                                     delete_contact,
                                     get_contact,
                                     get_contacts,
                                     get_all_contacts,
                                     search_contacts,
                                     get_contacts_with_birthday_in_period,) 


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, 
                         username='test_user', 
                         password='Test_password8',
                         confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)
        
    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, first_name='test_title1', 
                    last_name='test_description1', 
                    email="some1@gmail.com",
                    phone="1234567890",
                    birthday="2020-01-01",
                    additional_data="test_additional_data1",
                    user=self.user),
            Contact(id=1, first_name='test_title2', 
                    last_name='test_description2', 
                    email="some2@gmail.com",
                    phone="1234567890",
                    birthday="2020-01-01",
                    additional_data="test_additional_data2",),
                    ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, first_name='test_title1', 
                    last_name='test_description1', 
                    email="some1@gmail.com",
                    phone="1234567890",
                    birthday="2020-01-01",
                    additional_data="test_additional_data1",
                    user=self.user),
            Contact(id=2, first_name='test_title2', 
                    last_name='test_description2', 
                    email="some2@gmail.com",
                    phone="1234567890",
                    birthday="2020-01-01",
                    additional_data="test_additional_data2",
                    user=self.user),
                    ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='test_title1', 
                    last_name='test_description', 
                    email="some1@gmail.com",
                    phone="1234567890",
                    birthday="2020-01-01",
                    additional_data="test_additional_data1",
                    user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await get_contact(1, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, 'test_title1')
        self.assertEqual(result.last_name, 'test_description')
        self.assertEqual(result.email, 'some1@gmail.com')
        self.assertEqual(result.phone, '1234567890')

    async def test_create_contact(self):
        body = ContactSchema(first_name='test_title1', 
                             last_name='test_description', 
                             email="some1@gmail.com",
                             phone="1234567890",
                             birthday="2020-01-01",
                             additional_data="test_additional_data1",
                             user=self.user)
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, 'test_title1')
        self.assertEqual(result.last_name, 'test_description')
        self.assertEqual(result.email, 'some1@gmail.com')
        self.assertEqual(result.phone, '1234567890')
    
    async def test_update_contact(self):
        body = ContactUpdateSchema(first_name='test_title1', 
                                   last_name='test_description', 
                                   email="some1@gmail.com",
                                   phone="1234567890",
                                   birthday="2020-01-01",
                                   additional_data="test_additional_data1",
                                   user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='test_title1', last_name='test_description',
                                                 user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, 'test_title1')
        self.assertEqual(result.last_name, 'test_description')
        self.assertEqual(result.email, 'some1@gmail.com')
        self.assertEqual(result.phone, '1234567890')

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='test_title1', last_name='test_description',
                                                 user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.assertIsInstance(result, Contact)

    async def test_search_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, first_name='test_title1', 
                    last_name='test_description1', 
                    email="some1@gmail.com",
                    phone="1234567890",
                    birthday="2020-01-01",
                    additional_data="test_additional_data1",
                    user=self.user),
            Contact(id=2, first_name='test_title2', 
                    last_name='test_description2', 
                    email="some2@gmail.com",
                    phone="1234567890",
                    birthday="2020-01-01",
                    additional_data="test_additional_data2",
                    user=self.user),
                    ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts("st", self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contacts_with_birthday_in_period(self):
        limit = 10
        offset = 0
        today = datetime.today().date()
        user = User(id=1)
        contacts = [
            Contact(birthday=today + timedelta(days=i), user_id=user.id) for i in range(5)
        ]

        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts_with_birthday_in_period(5, limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)