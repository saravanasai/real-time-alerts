from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.timezone("Asia/Kolkata", func.now()),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.timezone("Asia/Kolkata", func.now()),
    )
