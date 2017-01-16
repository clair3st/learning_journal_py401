from sqlalchemy import (
    Column,
    Index,
    Integer,
    Unicode,
    Date,
)

from .meta import Base


class MyModel(Base):
    """Initialize data model for db."""
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    body = Column(Unicode)
    creation_date = Column(Date)

    def to_json(self):
        """Return Json object."""
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "creation_date": self.creation_date.strftime('%b %d, %Y'),
        }
