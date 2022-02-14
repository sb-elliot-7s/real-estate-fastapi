from datetime import datetime
import sqlalchemy as _sql
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.postgresql import ENUM


class Listing(Base):
    __tablename__ = 'listings'

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    category_type = _sql.Column(ENUM('SELL', 'RENT', 'DAILY_RENT', name='categories', ), nullable=False, default='SELL')
    number_of_rooms = _sql.Column(_sql.Integer, default=1)
    total_area = _sql.Column(_sql.Float)
    price = _sql.Column(_sql.Numeric(12, 2))
    title = _sql.Column(_sql.String(length=255), nullable=False)
    slug = _sql.Column(_sql.String, nullable=True)
    description = _sql.Column(_sql.String, nullable=True)
    created = _sql.Column(_sql.DateTime, default=datetime.now)
    updated = _sql.Column(_sql.DateTime, default=datetime.now, onupdate=datetime.now)
    is_published = _sql.Column(_sql.Boolean, default=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey('auth.id'))
    number_of_views = _sql.Column(_sql.Integer, nullable=True)

    country = _sql.Column(_sql.String(length=100))
    city = _sql.Column(_sql.String(length=255))
    street = _sql.Column(_sql.String(length=255), nullable=True)
    house_number = _sql.Column(_sql.String(length=10), nullable=True)
    region = _sql.Column(_sql.String, nullable=True)
    district = _sql.Column(_sql.String, nullable=True)
    longitude = _sql.Column(_sql.Float, nullable=True)
    latitude = _sql.Column(_sql.Float, nullable=True)
    full_address = _sql.Column(_sql.String, nullable=True)
    house_type = _sql.Column(ENUM('NEW_BUILDING', 'SECONDARY_HOUSING', name='houses', ), nullable=True, default='NEW_BUILDING')
    wall_type = _sql.Column(ENUM('BRICK', 'WOOD', 'PANEL', name='walls', ), nullable=True, default='BRICK')
    number_of_floors = _sql.Column(_sql.Integer, default=1)
    elevator = _sql.Column(_sql.Boolean, default=True)
    year_built = _sql.Column(_sql.Integer)

    favorites = relationship('Favorite', backref='listing', lazy='joined', cascade='all, delete')
    images = relationship('Image', backref='article', cascade='all, delete', lazy='joined')

    def __repr__(self) -> str:
        return f'<Listing: {self.title}>'


class Image(Base):
    __tablename__ = 'images'

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    photo = _sql.Column(_sql.String, nullable=False)
    listing_id = _sql.Column(_sql.Integer, _sql.ForeignKey('listings.id'))

    def __repr__(self) -> str:
        return f'<Image: {self.photo}>'


class Favorite(Base):
    __tablename__ = 'favorites'

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    listing_id = _sql.Column(_sql.Integer, _sql.ForeignKey('listings.id'))
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey('auth.id'))
    is_favorite = _sql.Column(_sql.Boolean, default=False)

    def __repr__(self) -> str:
        return f'<Favorite: listing: {self.listing_id} user: {self.user_id}>'
