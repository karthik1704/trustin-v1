import click
from app.database import SessionLocal

from app.models.users import User  # Import your User model

@click.command()
@click.option('--email', prompt='Enter email', help='Superuser email')
@click.option('--password', prompt=True, hide_input=True, help='Superuser password')
def create_super_user(email, password):

    db = SessionLocal()

    # Check if the superuser already exists
    existing_superuser = db.query(User).filter(User.email == email).first()

    if not existing_superuser:
        # Create a new superuser
        superuser = User(
            email=email,
            password=password,
            is_active=True,
            is_superuser=True
        )
        
        # Add the superuser to the database
        db.add(superuser)
        db.commit()
        db.refresh(superuser)

        print("Superuser created successfully.")
    else:
        print("Superuser already exists.")

if __name__ == "__main__":
    create_super_user()