from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema



async def get_contacts(limit: int, offset: int,
                       db:AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the user.
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db:AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    query = select(Contact).filter_by(user=user).limit(limit).offset(offset)
    contacts = await db.execute(query)
    return contacts.scalars().all()

async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_contacts function returns a list of all contacts in the database.
        
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first n rows, and limit: int is used to limit the number of returned rows
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact(contact_id: int, db:AsyncSession, user: User):
    """
    The get_contact function returns a contact object from the database.
    
    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db:AsyncSession: Pass in the database session
    :param user: User: Filter the query to only return contacts that belong to the user
    :return: A contact object
    :doc-author: Trelent
    """
    query = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(query)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db:AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactSchema: Validate the body of the request
    :param db:AsyncSession: Pass the database session object to the function
    :param user: User: Get the user object from the request
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

async def update_contact(contact_id: int,
                      body: ContactUpdateSchema, 
                      db:AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactUpdateSchema): A schema containing all fields that can be updated for a Contact object.
            db (AsyncSession): An async session with an open connection to the database.
            user (User): The user who is making this request, used for authorization purposes only.
    
    :param contact_id: int: Identify the contact to be updated
    :param body: ContactUpdateSchema: Validate the request body
    :param db:AsyncSession: Pass the database session to the function
    :param user: User: Check if the contact belongs to the user
    :return: A contact object
    :doc-author: Trelent
    """
    query = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_data = body.additional_data
        await db.commit()
        await db.refresh(contact)
        return contact


async def delete_contact(contact_id: int, db:AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession): An async session object for interacting with the database.
            user (User): The user who is deleting this contact, used to ensure that only contacts belonging to this user are deleted.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db:AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is deleting their own contact
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    query = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact



async def search_contacts(query: str, db: AsyncSession, user: User):
    """
    The search_contacts function searches the database for contacts that match a given query.
        The function takes in a string, which is the search query, and returns all contacts that match
        the search criteria.
    
    :param query: str: Search for a contact by first name, last name or email
    :param db: AsyncSession: Pass in the database connection
    :param user: User: Filter the results to only show contacts that belong to the user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).where(
        or_(
            Contact.first_name.ilike(f'%{query}%'),
            Contact.last_name.ilike(f'%{query}%'),
            Contact.email.ilike(f'%{query}%')
        )
    ).filter_by(user=user)
    result = await db.execute(stmt)
    result = result.scalars().all()
    return result


async def get_contacts_with_birthday_in_period(count_of_days: int, limit: int, offset: int,
                                               db: AsyncSession, user: User):
    """
    The get_contacts_with_birthday_in_period function returns a list of contacts with birthdays in the specified period.
    
    :param count_of_days: int: Specify the number of days from today to search for contacts with birthdays
    :param limit: int: Limit the number of results returned by the query
    :param offset: int: Specify the number of records to skip before starting to return the records
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts, but the function is called in a loop
    :doc-author: Trelent
    """
    today = datetime.today().date()
    end_date = today + timedelta(days=count_of_days)
    today_str = today.strftime("%m-%d")
    end_date_str = end_date.strftime("%m-%d")

    if today.month <= end_date.month:
        query = select(Contact).where(
            func.to_char(Contact.birthday, "MM-DD").between(today_str, end_date_str)
        ).filter_by(user=user).limit(limit).offset(offset)
    else:
        query = select(Contact).where(
            or_(
                func.to_char(Contact.birthday, "MM-DD") >= today_str,
                func.to_char(Contact.birthday, "MM-DD") <= end_date_str
            )
        ).filter_by(user=user).limit(limit).offset(offset)
        
    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts