# -*- coding: utf-8 -*-
from flask import g
from contextlib import contextmanager
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import BIGINT
from .base import Base


class SequenceDual(Base):
    __tablename__ = "sequence_dual"

    sequence_name = Column(String(length=255), nullable=False)
    value = Column(BIGINT(unsigned=True), nullable=False, default=1)

    def __init__(self, sequence_name, initial_value):
        self.sequence_name = sequence_name
        self.value = initial_value

    @staticmethod
    def get_by_name(sequence_name):
        return g.db_session.query(SequenceDual).filter(
            SequenceDual.is_deleted == 0,
            SequenceDual.sequence_name == sequence_name
        ).first()

    @staticmethod
    @contextmanager
    def select_for_update(sequence_name):
        sequence = g.db_session.query(SequenceDual).filter(
            SequenceDual.is_deleted == 0,
            SequenceDual.sequence_name == sequence_name
        ).with_for_update().first()
        try:
            yield sequence
        finally:
            sequence.value += 1
