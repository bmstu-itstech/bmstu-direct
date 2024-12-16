from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, Text, Boolean, Enum, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from core import domain
from services.db.base import Base


class BaseModel(Base):
    __abstract__ = True

    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel):
    __tablename__ = "users"

    chat_id = Column(BigInteger,        primary_key=True)
    role    = Column(Enum(domain.Role), nullable=False)

    @classmethod
    def from_domain(cls, user: domain.User) -> "User":
        return User(chat_id=user.chat_id, role=user.role)

    def to_domain(self) -> domain.User:
        return domain.User(chat_id=self.chat_id, role=self.role)


class Ticket(BaseModel):
    __tablename__ = 'tickets'

    id = Column(BigInteger, Sequence("id", start=1, increment=1), primary_key=True)

    owner_chat_id     = Column(BigInteger,            nullable=False)
    source_message_id = Column(BigInteger,            nullable=False)
    text              = Column(Text,                  nullable=False)
    issue             = Column(Enum(domain.Issue),    nullable=False)
    category          = Column(Enum(domain.Category), nullable=False)
    anonym            = Column(Boolean,               nullable=False)
    full_name         = Column(Text,                  nullable=True)
    study_group       = Column(Text,                  nullable=True)
    status            = Column(Enum(domain.Status),   nullable=False)

    @classmethod
    def from_domain(cls, ticket: domain.Ticket) -> "Ticket":
        return Ticket(
            owner_chat_id     = ticket.owner_chat_id,
            source_message_id = ticket.source_message_id,
            text              = ticket.text,
            issue             = ticket.issue,
            category          = ticket.category,
            anonym            = ticket.owner is None,
            full_name         = ticket.owner.full_name if ticket.owner is not None else None,
            study_group       = ticket.owner.study_group if ticket.owner is not None else None,
            status            = ticket.status,
        )

    def to_domain(self) -> domain.TicketRecord:
        owner = None
        if not self.anonym:
            owner = domain.Student(
                self.full_name,
                self.study_group,
            )
        return domain.TicketRecord(
            id                = self.id,
            owner_chat_id     = self.owner_chat_id,
            source_message_id = self.source_message_id,
            text              = self.text,
            issue             = domain.Issue(self.issue),
            category          = domain.Category(self.category),
            owner             = owner,
            status            = domain.Status(self.status),
        )


class MessagePair(Base):
    __tablename__ = "message_pairs"

    source_chat_id    = Column(BigInteger, primary_key=True)
    source_message_id = Column(BigInteger, primary_key=True)
    copy_chat_id      = Column(BigInteger, nullable=False)
    copy_message_id   = Column(BigInteger, nullable=False)
    ticket_id         = Column(ForeignKey("tickets.id", ondelete="CASCADE"))

    @classmethod
    def from_domain(cls, message_pair: domain.MessagePair) -> "MessagePair":
        return MessagePair(
            source_chat_id=message_pair.source_id.chat_id,
            source_message_id=message_pair.source_id.message_id,
            copy_chat_id=message_pair.copy_id.chat_id,
            copy_message_id=message_pair.copy_id.message_id,
            ticket_id=message_pair.ticket_id,
        )

    def to_domain(self) -> domain.MessagePair:
        return domain.MessagePair(
            source_id=domain.MessageID(
                chat_id=self.source_chat_id,
                message_id=self.source_message_id,
            ),
            copy_id=domain.MessageID(
                chat_id=self.copy_chat_id,
                message_id=self.copy_message_id,
            ),
            ticket_id=self.ticket_id,
        )
