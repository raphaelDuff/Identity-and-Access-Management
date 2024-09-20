from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
import json


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

"""
Drink
a persistent drink entity, extends the base SQLAlchemy Model
"""


class Drink(db.Model):
    __tablename__ = "drink"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    recipe: Mapped[str] = mapped_column(String(180), nullable=False)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    # recipe = Column(String(180), nullable=False)

    def __init__(self, title, recipe):
        self.title = title
        self.recipe = recipe

    """
    short()
        short form representation of the Drink model
    """

    def short(self):
        short_recipe = [
            {"color": r["color"], "parts": r["parts"]} for r in json.loads(self.recipe)
        ]
        return {"id": self.id, "title": self.title, "recipe": short_recipe}

    """
    long()
        long form representation of the Drink model
    """

    def long(self):
        return {"id": self.id, "title": self.title, "recipe": json.loads(self.recipe)}

    def __repr__(self):
        return json.dumps(self.short())
