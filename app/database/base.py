from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=True,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
