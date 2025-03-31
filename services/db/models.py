from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, Text, Boolean, Enum, Sequence, ForeignKey

from core import domain
from services.db.base import Base


class BaseModel(Base):
    __abstract__ = True

    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BannedUser(BaseModel):
    __tablename__ = "banned_users"

    chat_id = Column(BigInteger, primary_key=True)

    @classmethod
    def from_domain(cls, user: domain.BannedUser) -> "BannedUser":
        return BannedUser(chat_id=user.chat_id)

    def to_domain(self) -> domain.BannedUser:
        return domain.BannedUser(chat_id=self.chat_id)


class Ticket(BaseModel):
    __tablename__ = 'tickets'

    id = Column(BigInteger, Sequence("id", start=1, increment=1), primary_key=True)

    owner_chat_id               = Column(BigInteger,            nullable=False)
    channel_content_message_id  = Column(BigInteger,            nullable=True)
    channel_meta_message_id     = Column(BigInteger,            nullable=True)
    group_message_id            = Column(BigInteger,            nullable=True)
    text                        = Column(Text,                  nullable=False)
    issue                       = Column(Enum(domain.Issue),    nullable=False)
    category                    = Column(Enum(domain.Category), nullable=False)
    anonym                      = Column(Boolean,               nullable=False)
    full_name                   = Column(Text,                  nullable=True)
    study_group                 = Column(Text,                  nullable=True)
    status                      = Column(Enum(domain.Status),   nullable=False)

    @classmethod
    def from_domain(cls, ticket: domain.Ticket) -> "Ticket":
        return Ticket(
            owner_chat_id               = ticket.owner_chat_id,
            channel_content_message_id  = None,
            channel_meta_message_id     = None,
            group_message_id            = None,
            text                        = ticket.text,
            issue                       = ticket.issue,
            category                    = ticket.category,
            anonym                      = ticket.owner is None,
            full_name                   = ticket.owner.full_name if ticket.owner is not None else None,
            study_group                 = ticket.owner.study_group if ticket.owner is not None else None,
            status                      = ticket.status,
        )

    def to_domain(self) -> domain.TicketRecord:
        owner = None
        if not self.anonym:
            owner = domain.Student(
                self.full_name,
                self.study_group,
            )
        return domain.TicketRecord(
            id                          = self.id,
            owner_chat_id               = self.owner_chat_id,
            channel_content_message_id  = self.channel_content_message_id,
            channel_meta_message_id     = self.channel_meta_message_id,
            group_message_id            = self.group_message_id,
            text                        = self.text,
            issue                       = domain.Issue(self.issue),
            category                    = domain.Category(self.category),
            owner                       = owner,
            status                      = domain.Status(self.status),
            opened_at                   = self.created_on,
        )


class GroupMessage(BaseModel):
    __tablename__ = "group_messages"

    id = Column(BigInteger, Sequence("id", start=1, increment=1), primary_key=True)

    chat_id             = Column(BigInteger, nullable=True)
    message_id          = Column(BigInteger, nullable=True)
    owner_message_id    = Column(BigInteger, nullable=False)
    reply_to_message_id = Column(BigInteger, nullable=True)
    ticket_id           = Column(ForeignKey("tickets.id", ondelete="CASCADE"))

    @classmethod
    def from_domain(cls, message: domain.Message) -> "GroupMessage":
        return GroupMessage(
            chat_id=message.chat_id,
            message_id=message.message_id,
            owner_message_id=message.owner_message_id,
            reply_to_message_id=message.reply_to_message_id,
            ticket_id=message.ticket_id,
        )

    def to_domain(self) -> domain.Message:
        return domain.Message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            owner_message_id=self.owner_message_id,
            reply_to_message_id=self.reply_to_message_id,
            ticket_id=self.ticket_id,
        )
