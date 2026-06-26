from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.base import Base

class PartnerStores(Base):
    __tablename__ = "partner_stores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    logo_url = Column(String(255), nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    delivery = Column(Boolean, default=False)
    official_website = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    delivery_slots = relationship(
        "DeliverySlot",
        back_populates="partner_store",
        cascade="all, delete-orphan" # При удалении магазина удаляются и слоты
    )
    

class DeliverySlots(Base):
    __tablename__ = "delivery_slots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=False)
    delivery_start = Column(String(255), nullable=False)
    delivery_end = Column(String(255), nullable=False)
    is_holiday = Column(Boolean, default=False)
    
    partner_store = relationship(
        "PartnerStore",
        back_populates="delivery_slots"
    )