from app import db
from app.models import User

def make_admin(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"User {email} is now an admin.")
    else:
        print(f"User with email {email} not found.")

if __name__ == "__main__":
    email = input("Enter your email to become admin: ")
    make_admin(email)
