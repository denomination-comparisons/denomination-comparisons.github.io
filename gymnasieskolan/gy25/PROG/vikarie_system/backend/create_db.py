from app.utils.database import engine, Base
from app.models.substitute import Substitute
from app.models.user import User
from app.models.assignment import Assignment
from app.models.attendance import Attendance

Base.metadata.create_all(bind=engine)
print("Database created successfully!")
