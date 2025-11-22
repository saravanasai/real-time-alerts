from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Alerts(Base):

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_price = Column(Integer, nullable=False)
    metal_type = Column(String, nullable=False)
    user = relationship("User", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "alert_price": self.alert_price,
            "user_id": self.user_id,
            "metal_type": self.metal_type
        }
