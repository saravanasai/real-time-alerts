# app/models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.utils.password import hash_password
from sqlalchemy.ext.hybrid import hybrid_property


class User(Base):
    __tablename__ = "users"
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    _password = Column("password", String, nullable=False)

    # relationship Alerts
    alerts = relationship("Alerts", back_populates="user")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plain_password: str):
        """Automatically hash password when set."""
        self._password = hash_password(plain_password)
