from typing import List

from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500),
                        offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts for the current user.
        The limit and offset parameters are used to paginate the results.
    
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify the minimum value that can be passed to the limit parameter
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Skip the first n records
    :param ge: Specify the minimum value for a parameter
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the auth_service
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts

@router.get('/all', response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_contacts(limit: int = Query(10, ge=10, le=500),
                    offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):
    """
    The get_all_contacts function returns a list of contacts.
        The limit and offset parameters are used to paginate the results.
    
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of contacts returned
    :param offset: int: Set the offset for pagination
    :param ge: Specify a minimum value for the parameter
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user from the auth_service
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1),
                   db: AsyncSession = Depends(get_db),
                   user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by id.
        Args:
            contact_id (int): The id of the contact to return.
            db (AsyncSession): A database connection object.
            user (User): The current logged in user, if any.
    
    :param contact_id: int: Get the contact id from the path
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail=f"User not found")
    return contact

@router.get("/contacts/{search}", response_model=List[ContactResponse])
async def search_contacts(contact_data: str,
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The search_contacts function searches for contacts in the database.
        Args:
            contact_data (str): The search string to be used to find contacts.
            db (AsyncSession): The database session object.
            user (User): The current user object, which is passed from the auth_service dependency function get_current_user().
    
    :param contact_data: str: Search for a contact in the database
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user id of the current logged in user
    :return: A list of contacts, but the function returns a list of dictionaries
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.search_contacts(contact_data, db, user)
    if contacts is None:
        raise HTTPException(
            status_code=404,
            detail=f"Users not found")
    return contacts

@router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts_with_birthday_in_period(count_of_days: int = Query(1, ge=1, le=7), 
                                            limit: int = Query(10, ge=10, le=500),
                                            offset: int = Query(0, ge=0),
                                            db: AsyncSession = Depends(get_db),
                                            user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_with_birthday_in_period function returns a list of contacts with birthday in period.
        The function takes the following parameters:
            count_of_days - number of days from today to search for birthdays (default 1)
            limit - maximum number of contacts to return (default 10, max 500)
            offset - how many records to skip before returning results (default 0)
    
    :param count_of_days: int: Determine the period of time in which you want to get contacts with a birthday
    :param ge: Specify the minimum value that can be passed to the parameter
    :param le: Set the upper limit of the number of days
    :param limit: int: Limit the number of results returned
    :param ge: Check if the value is greater than or equal to the specified value
    :param le: Set the maximum value of a parameter
    :param offset: int: Skip the first n records
    :param ge: Specify the minimum value of the parameter
    :param db: AsyncSession: Get the database connection
    :param user: User: Get the user id from the token
    :return: A list of contactswithbirthdayinperiod objects
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts_with_birthday_in_period(count_of_days, limit, offset, db, user)
    if contacts is None:
        raise HTTPException(
            status_code=404,
            detail=f"Users not found")
    return contacts
    
    

@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(body: ContactSchema,
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes in a ContactSchema object, which is validated by pydantic.
        If the validation fails, an error will be thrown and no contact will be created.
        If the validation succeeds, then we create a new contact using our repository layer.
    
    :param body: ContactSchema: Validate the body of the request
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact

@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema,
                      contact_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        Args:
            body (ContactUpdateSchema): The schema for updating a contact.
            contact_id (int): The id of the user to update.
            db (AsyncSession): A connection to the database, provided by FastAPI's dependency injection system.
            user (User): The current logged-in user, provided by FastAPI's dependency injection system and our custom auth_service module.&lt;/code&gt;
    
    :param body: ContactUpdateSchema: Validate the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the current user
    :return: A contact object, which is a pydantic model
    :doc-author: Trelent
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail=f"User not found")
    return contact

@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession): The database session object.
            user (User): The current logged in user, as returned by auth_service's get_current_user function.
    
    :param contact_id: int: Specify the contact_id of the contact to be deleted
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="User not found")
    return contact
