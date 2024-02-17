import click
from fastapi import Depends
from app.database import  sessionmanager
from app.utils import get_hashed_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User  # Import your User model
from typing import Annotated

# db_dep =
@click.command()
@click.option('--email', prompt='Enter email', help='Superuser email')
@click.option('--password', prompt=True, hide_input=True, help='Superuser password')
def create_super_user(email, password,  ):


    db = Annotated[AsyncSession, get_db()]
    # Check if the superuser already exists

    existing_superuser =  db.execute(select(User.fullname).where(User.id == 2)).scalar_one()

    if not existing_superuser:
        # Create a new superuser
        superuser = User(
            email=email,
            password=get_hashed_password(password),
            is_active=True,
            is_superuser=True
        )
        
        # Add the superuser to the database
        db.add(superuser)

        print("Superuser created successfully.")
    else:
        print("Superuser already exists.")

if __name__ == "__main__":
    create_super_user()