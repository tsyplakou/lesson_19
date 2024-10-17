from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from base_models import BaseModel


class Recipe(BaseModel):
    __tablename__ = 'recipes'

    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)
    description = Column(String)
    prep_time = Column(Integer)
    instructions = Column(String)
    image_url = Column(String)

    comments = relationship('Comment', backref='recipe')


class Comment(BaseModel):
    __tablename__ = 'comments'

    recipe_id = Column(Integer, ForeignKey('recipes.id'), primary_key=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
