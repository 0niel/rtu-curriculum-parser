import sqlalchemy as db
from sqlalchemy.orm import relationship

from db import db_session
from models.base import BaseModel


class DisciplineName(BaseModel):
    __tablename__ = "discipline_names"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.UnicodeText, nullable=False, index=True, unique=True)
    disciplines = relationship("Discipline", back_populates="name")

    def create(self):
        with db_session() as session:
            session.add(self)
            session.commit()
            session.refresh(self)

    @staticmethod
    def get_or_create(text):
        with db_session() as session:
            discipline_name = (
                session.query(DisciplineName)
                .filter(
                    DisciplineName.text == text,
                )
                .first()
            )

            if discipline_name is None:
                discipline_name = DisciplineName(
                    text=text,
                )
                try:
                    session.add(discipline_name)
                except Exception as e:
                    pass

                session.commit()
                session.refresh(discipline_name)

            return discipline_name

    @staticmethod
    def get_by_text(text):
        with db_session() as session:
            return (
                session.query(DisciplineName)
                .filter(
                    DisciplineName.text == text,
                )
                .first()
            )


DisciplineName.__table__.create(checkfirst=True)
