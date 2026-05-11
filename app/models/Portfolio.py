from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db

if TYPE_CHECKING:
    # imports that are used only for type checking to avoid circular dependencies
    from app.models import Investment, PortfolioAccess, Transaction, User


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    owner: Mapped[str] = mapped_column(String(30), ForeignKey('user.username'), nullable=False)

    investments: Mapped[List['Investment']] = relationship('Investment', back_populates='portfolio', lazy='selectin', cascade='all, delete-orphan')

    user: Mapped['User'] = relationship('User', foreign_keys=[owner], back_populates='portfolios', lazy='selectin')

    transactions: Mapped[List['Transaction']] = relationship('Transaction', back_populates='portfolio', lazy='selectin', cascade='all, delete-orphan')

    accesses: Mapped[List['PortfolioAccess']] = relationship('PortfolioAccess', back_populates='portfolio', lazy='selectin', cascade='all, delete-orphan')

    # this is needed because PyLance cannot infer the constructor signature from SQLAlchemy's Mapped class
    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            name: str | None = None,
            user: User | None = None,
            description: str | None = None,
            id: int | None = None,
        ) -> None: ...

    def __str__(self):
        user_str = getattr(self, 'user', None)
        username = user_str.username if user_str else 'N/A'
        investments = []
        for investment in self.investments:
            investments.append(f'{investment.ticker}:{investment.quantity}')
        return f'<Portfolio: id={self.id}; name={self.name}; description={self.description}; user={username}; investments={", ".join(investments)}>'

    def _estimate_position_values(self) -> dict[str, dict[str, float]]:
        positions: dict[str, dict[str, float]] = {}

        transactions = sorted(
            self.transactions or [],
            key=lambda transaction: getattr(transaction, 'date_time', None),
        )
        for transaction in transactions:
            ticker = getattr(transaction, 'ticker', None)
            quantity = getattr(transaction, 'quantity', 0) or 0
            price = getattr(transaction, 'price', 0.0) or 0.0
            transaction_type = getattr(transaction, 'transaction_type', '')

            if not ticker or quantity <= 0:
                continue

            position = positions.setdefault(ticker, {'quantity': 0.0, 'cost': 0.0})
            if transaction_type == 'BUY':
                position['quantity'] += quantity
                position['cost'] += price * quantity
            elif transaction_type == 'SELL' and position['quantity'] > 0:
                sell_quantity = min(quantity, position['quantity'])
                average_cost = position['cost'] / position['quantity'] if position['quantity'] else 0.0
                position['quantity'] -= sell_quantity
                position['cost'] = max(0.0, position['cost'] - (average_cost * sell_quantity))

        estimated_positions: dict[str, dict[str, float]] = {}
        for investment in self.investments or []:
            ticker = getattr(investment, 'ticker', None)
            quantity = getattr(investment, 'quantity', 0) or 0
            if not ticker or quantity <= 0:
                continue

            position = positions.get(ticker)
            if position and position['quantity'] > 0:
                average_cost = position['cost'] / position['quantity']
                estimated_total_value = average_cost * quantity
                estimated_positions[ticker] = {
                    'estimated_price': average_cost,
                    'estimated_total_value': estimated_total_value,
                }
            else:
                estimated_positions[ticker] = {
                    'estimated_price': 0.0,
                    'estimated_total_value': 0.0,
                }

        return estimated_positions

    def __to_dict__(self):
        try:
            estimated_positions = self._estimate_position_values()
            investments = []
            total_portfolio_value = 0.0
            for investment in self.investments or []:
                ticker = getattr(investment, 'ticker', None)
                estimate = estimated_positions.get(
                    ticker,
                    {'estimated_price': 0.0, 'estimated_total_value': 0.0},
                )
                total_portfolio_value += estimate['estimated_total_value']
                investments.append(
                    {
                        'ticker': ticker,
                        'quantity': getattr(investment, 'quantity', None),
                        'estimated_price': estimate['estimated_price'],
                        'estimated_total_value': estimate['estimated_total_value'],
                    }
                )
            result = {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'owner': self.owner,
                'investments_count': len(self.investments or []),
                'investments': investments,
                'total_portfolio_value': total_portfolio_value,
            }
            return result
        except Exception as ex:
            return {'id': self.id, 'error': str(ex)}
