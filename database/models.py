from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database.connection import Base


# ==========================================================
# BRANCH
# ==========================================================

class Branch(Base):
    __tablename__ = "branch"

    branch_id = Column(Integer, primary_key=True, index=True)
    branch_name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)

    accounts = relationship("Account", back_populates="branch")


# ==========================================================
# CUSTOMER
# ==========================================================

class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(String(20))
    birth_date = Column(Date)

    segment = Column(String(50))

    country = Column(String(100))
    city = Column(String(100))

    profession = Column(String(100))

    risk_level = Column(String(30))

    date_created = Column(Date)

    status = Column(String(30))

    accounts = relationship("Account", back_populates="customer")


# ==========================================================
# ACCOUNT
# ==========================================================

class Account(Base):
    __tablename__ = "account"

    account_id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customer.customer_id"),
        nullable=False
    )

    account_number = Column(
    String(50),
    nullable=False,
    unique=True
    )

    account_type = Column(String(50))

    currency = Column(String(10))

    balance = Column(Float)

    status = Column(String(30))

    open_date = Column(Date)

    close_date = Column(Date)

    branch_id = Column(
        Integer,
        ForeignKey("branch.branch_id"),
        nullable=False
    )

    customer = relationship(
        "Customer",
        back_populates="accounts"
    )

    branch = relationship(
        "Branch",
        back_populates="accounts"
    )

    transactions = relationship(
        "Transaction",
        back_populates="account"
    )

    cards = relationship(
        "Card",
        back_populates="account"
    )

    balance_history = relationship(
        "BalanceHistory",
        back_populates="account"
    )


# ==========================================================
# TRANSACTION
# ==========================================================

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(Integer, primary_key=True, index=True)

    account_id = Column(
        Integer,
        ForeignKey("account.account_id"),
        nullable=False
    )

    transaction_date = Column(Date,nullable=False)

    amount = Column(Float)

    currency = Column(String(10))

    transaction_type = Column(String(50))

    channel = Column(String(50))

    merchant_name = Column(String(150))

    category = Column(String(100))

    status = Column(String(30))

    reference = Column(String(100))

    country = Column(String(100))

    account = relationship(
        "Account",
        back_populates="transactions"
    )


# ==========================================================
# BALANCE HISTORY
# ==========================================================

class BalanceHistory(Base):
    __tablename__ = "balance_history"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(
        Integer,
        ForeignKey("account.account_id"),
        nullable=False
    )

    date = Column(Date)

    balance = Column(Float)

    account = relationship(
        "Account",
        back_populates="balance_history"
    )


# ==========================================================
# CARD
# ==========================================================

class Card(Base):
    __tablename__ = "card"

    card_id = Column(Integer, primary_key=True, index=True)

    account_id = Column(
        Integer,
        ForeignKey("account.account_id"),
        nullable=False
    )

    card_type = Column(String(50))

    card_level = Column(String(50))

    issue_date = Column(Date)

    expiry_date = Column(Date)

    status = Column(String(30))

    limit_amount = Column(Float)

    account = relationship(
        "Account",
        back_populates="cards"
    )