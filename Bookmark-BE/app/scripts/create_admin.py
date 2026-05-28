import asyncio
import getpass
from sqlalchemy.future import select
from passlib.context import CryptContext

# Import models to register them on SQLAlchemy Base
import app.api.auth.domain.models
import app.api.bookmark.domain.models
import app.api.tag.domain.models

from app.api.auth.domain.models import User
from app.config.db_connection import AsyncSessionLocal
from app.utils.enums import RoleType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin():
    print("\n--- Create Admin User ---")
    name = input("Enter Full Name: ").strip()
    email = input("Enter Email: ").strip()
    password = getpass.getpass("Enter Password: ").strip()

    if not all([name, email, password]):
        print("\nError: All fields are required.")
        return

    async with AsyncSessionLocal() as session:
        # Check if user already exists
        query = select(User).where(User.email == email.lower())
        result = await session.execute(query)
        existing_user = result.scalars().first()

        if existing_user:
            print(f"\nError: A user with the email '{email}' already exists.")
            return

        # Create admin user
        try:
            password_hash = pwd_context.hash(password)
            new_admin = User(
                name=name,
                email=email.lower(),
                password_hash=password_hash,
                role=RoleType.ADMIN.value,
                is_active=True,
            )

            session.add(new_admin)
            await session.commit()
            print(f"\nSuccessfully created Admin user: {email}")
        except Exception as e:
            await session.rollback()
            print(f"\nFailed to create admin user: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(create_admin())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")


# For running the script command: python -m app.scripts.create_admin
