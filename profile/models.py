from datetime import datetime
import sqlalchemy as _sql
from database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'auth'

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    username = _sql.Column(_sql.String(length=255), unique=True)
    password = _sql.Column(_sql.String)
    email = _sql.Column(_sql.String, unique=True, nullable=True)
    first_name = _sql.Column(_sql.String(length=255), nullable=True)
    last_name = _sql.Column(_sql.String(length=255), nullable=True)
    phone = _sql.Column(_sql.String(length=20), nullable=True)
    is_active = _sql.Column(_sql.Boolean, default=True)
    created = _sql.Column(_sql.DateTime, default=datetime.now)
    updated = _sql.Column(_sql.DateTime, default=datetime.now, onupdate=datetime.now)

    listings = relationship('Listing', backref='user', lazy='joined', cascade='all, delete')
    favorites = relationship('Favorite', backref='user', lazy='joined', cascade='all, delete')

    def __repr__(self) -> str:
        return f'<User: {self.username}>'
