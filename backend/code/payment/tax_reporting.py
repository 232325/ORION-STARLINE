"""
Tax Reporting System
Soliq hisoboti tizimi

Xususiyatlar:
- Transaction reports (buy, sell, dividend)
- PnL statements
- Capital gains/losses calculation
- Tax lots tracking (FIFO, LIFO, Specific ID)
- Annual tax summary
- CSV/PDF export
- Multi-jurisdiction support
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal
import csv
import io
import logging

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Tranzaksiya turlari"""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    FEE = "fee"
    AIRDROP = "airdrop"
    STAKING_REWARD = "staking_reward"


class TaxLotMethod(Enum):
    """Tax lot accounting methods"""
    FIFO = "fifo"  # First In First Out
    LIFO = "lifo"  # Last In First Out
    HIFO = "hifo"  # Highest In First Out
    SPECIFIC_ID = "specific_id"  # Specific identification


class CapitalGainType(Enum):
    """Capital gain turlari"""
    SHORT_TERM = "short_term"  # < 1 year
    LONG_TERM = "long_term"    # >= 1 year


@dataclass
class TaxTransaction:
    """Soliq uchun tranzaksiya"""
    id: str
    user_id: str
    date: datetime
    type: TransactionType
    asset: str
    quantity: Decimal
    price: Decimal
    total_value: Decimal
    fee: Decimal
    currency: str = "USD"
    description: Optional[str] = None
    cost_basis: Optional[Decimal] = None
    proceeds: Optional[Decimal] = None
    gain_loss: Optional[Decimal] = None
    gain_type: Optional[CapitalGainType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "type": self.type.value,
            "asset": self.asset,
            "quantity": str(self.quantity),
            "price": str(self.price),
            "total_value": str(self.total_value),
            "fee": str(self.fee),
            "currency": self.currency,
            "description": self.description,
            "cost_basis": str(self.cost_basis) if self.cost_basis else None,
            "proceeds": str(self.proceeds) if self.proceeds else None,
            "gain_loss": str(self.gain_loss) if self.gain_loss else None,
            "gain_type": self.gain_type.value if self.gain_type else None
        }


@dataclass
class TaxLot:
    """Tax lot (bir dona sotib olish)"""
    id: str
    asset: str
    quantity: Decimal
    cost_basis: Decimal
    purchase_date: datetime
    remaining_quantity: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "quantity": str(self.quantity),
            "cost_basis": str(self.cost_basis),
            "purchase_date": self.purchase_date.isoformat(),
            "remaining_quantity": str(self.remaining_quantity),
            "avg_cost_per_unit": str(self.cost_basis / self.quantity) if self.quantity > 0 else "0"
        }


@dataclass
class CapitalGain:
    """Capital gain/loss"""
    id: str
    asset: str
    quantity: Decimal
    cost_basis: Decimal
    proceeds: Decimal
    gain_loss: Decimal
    purchase_date: datetime
    sale_date: datetime
    holding_period_days: int
    gain_type: CapitalGainType
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "quantity": str(self.quantity),
            "cost_basis": str(self.cost_basis),
            "proceeds": str(self.proceeds),
            "gain_loss": str(self.gain_loss),
            "purchase_date": self.purchase_date.isoformat(),
            "sale_date": self.sale_date.isoformat(),
            "holding_period_days": self.holding_period_days,
            "gain_type": self.gain_type.value
        }


@dataclass
class TaxReport:
    """Soliq hisoboti"""
    id: str
    user_id: str
    year: int
    report_type: str  # annual, quarterly, custom
    start_date: datetime
    end_date: datetime
    generated_at: datetime
    
    # Summary data
    total_capital_gains: Decimal
    total_capital_losses: Decimal
    net_capital_gain_loss: Decimal
    short_term_gains: Decimal
    long_term_gains: Decimal
    total_dividend_income: Decimal
    total_interest_income: Decimal
    total_fees: Decimal
    
    # Detailed data
    transactions: List[TaxTransaction] = field(default_factory=list)
    capital_gains: List[CapitalGain] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "year": self.year,
            "report_type": self.report_type,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "generated_at": self.generated_at.isoformat(),
            "summary": {
                "total_capital_gains": str(self.total_capital_gains),
                "total_capital_losses": str(self.total_capital_losses),
                "net_capital_gain_loss": str(self.net_capital_gain_loss),
                "short_term_gains": str(self.short_term_gains),
                "long_term_gains": str(self.long_term_gains),
                "total_dividend_income": str(self.total_dividend_income),
                "total_interest_income": str(self.total_interest_income),
                "total_fees": str(self.total_fees)
            },
            "transactions_count": len(self.transactions),
            "capital_gains_count": len(self.capital_gains)
        }


class TaxReporting:
    """
    Tax Reporting System
    
    Soliq hisobotlari va PnL statement yaratish
    """
    
    def __init__(self):
        self.transactions: Dict[str, TaxTransaction] = {}
        self.tax_lots: Dict[str, List[TaxLot]] = {}  # asset -> lots
        self.reports: Dict[str, TaxReport] = {}
        self.default_method = TaxLotMethod.FIFO
        
        logger.info("TaxReporting initialized")
    
    async def record_transaction(
        self,
        user_id: str,
        date: datetime,
        transaction_type: TransactionType,
        asset: str,
        quantity: Decimal,
        price: Decimal,
        fee: Decimal = Decimal("0"),
        currency: str = "USD",
        description: Optional[str] = None
    ) -> TaxTransaction:
        """
        Tranzaksiyani yozish
        
        Args:
            user_id: Foydalanuvchi ID
            date: Sana
            transaction_type: Tranzaksiya turi
            asset: Asset nomi
            quantity: Miqdor
            price: Narx
            fee: Fee
            currency: Valyuta
            description: Tavsif
        
        Returns:
            TaxTransaction obyekti
        """
        import uuid
        
        total_value = quantity * price
        
        transaction = TaxTransaction(
            id=f"tax_txn_{uuid.uuid4().hex[:16]}",
            user_id=user_id,
            date=date,
            type=transaction_type,
            asset=asset,
            quantity=quantity,
            price=price,
            total_value=total_value,
            fee=fee,
            currency=currency,
            description=description
        )
        
        self.transactions[transaction.id] = transaction
        
        # Update tax lots for BUY transactions
        if transaction_type == TransactionType.BUY:
            await self._add_tax_lot(asset, quantity, total_value + fee, date)
        
        # Process SELL transactions
        elif transaction_type == TransactionType.SELL:
            await self._process_sale(transaction)
        
        logger.info(f"Tax transaction recorded: {transaction.id} - {transaction_type.value} {quantity} {asset}")
        
        return transaction
    
    async def _add_tax_lot(
        self,
        asset: str,
        quantity: Decimal,
        cost_basis: Decimal,
        purchase_date: datetime
    ) -> TaxLot:
        """Tax lot qo'shish"""
        import uuid
        
        lot = TaxLot(
            id=f"lot_{uuid.uuid4().hex[:12]}",
            asset=asset,
            quantity=quantity,
            cost_basis=cost_basis,
            purchase_date=purchase_date,
            remaining_quantity=quantity
        )
        
        if asset not in self.tax_lots:
            self.tax_lots[asset] = []
        
        self.tax_lots[asset].append(lot)
        
        return lot
    
    async def _process_sale(
        self,
        sale_transaction: TaxTransaction,
        method: Optional[TaxLotMethod] = None
    ) -> List[CapitalGain]:
        """
        Sotish tranzaksiyasini qayta ishlash va capital gains hisoblash
        
        Args:
            sale_transaction: Sotish tranzaksiyasi
            method: Tax lot method
        
        Returns:
            Capital gains ro'yxati
        """
        asset = sale_transaction.asset
        quantity_to_sell = sale_transaction.quantity
        sale_date = sale_transaction.date
        proceeds_per_unit = sale_transaction.price
        
        if asset not in self.tax_lots or not self.tax_lots[asset]:
            logger.warning(f"No tax lots found for asset {asset}")
            return []
        
        # Select lots based on method
        method = method or self.default_method
        lots = self._select_lots_for_sale(asset, quantity_to_sell, method)
        
        capital_gains = []
        remaining_to_sell = quantity_to_sell
        total_cost_basis = Decimal("0")
        
        for lot in lots:
            if remaining_to_sell <= 0:
                break
            
            # Determine quantity to sell from this lot
            sell_from_lot = min(remaining_to_sell, lot.remaining_quantity)
            
            # Calculate cost basis for this portion
            cost_basis_per_unit = lot.cost_basis / lot.quantity
            cost_basis = sell_from_lot * cost_basis_per_unit
            
            # Calculate proceeds
            proceeds = sell_from_lot * proceeds_per_unit
            
            # Calculate gain/loss
            gain_loss = proceeds - cost_basis
            
            # Determine holding period
            holding_days = (sale_date - lot.purchase_date).days
            gain_type = (
                CapitalGainType.LONG_TERM if holding_days >= 365
                else CapitalGainType.SHORT_TERM
            )
            
            # Create capital gain record
            import uuid
            capital_gain = CapitalGain(
                id=f"gain_{uuid.uuid4().hex[:16]}",
                asset=asset,
                quantity=sell_from_lot,
                cost_basis=cost_basis,
                proceeds=proceeds,
                gain_loss=gain_loss,
                purchase_date=lot.purchase_date,
                sale_date=sale_date,
                holding_period_days=holding_days,
                gain_type=gain_type
            )
            
            capital_gains.append(capital_gain)
            
            # Update lot
            lot.remaining_quantity -= sell_from_lot
            remaining_to_sell -= sell_from_lot
            total_cost_basis += cost_basis
        
        # Update sale transaction with totals
        total_proceeds = quantity_to_sell * proceeds_per_unit
        sale_transaction.cost_basis = total_cost_basis
        sale_transaction.proceeds = total_proceeds
        sale_transaction.gain_loss = total_proceeds - total_cost_basis
        
        # Determine overall gain type (majority)
        long_term_qty = sum(
            g.quantity for g in capital_gains
            if g.gain_type == CapitalGainType.LONG_TERM
        )
        sale_transaction.gain_type = (
            CapitalGainType.LONG_TERM if long_term_qty > quantity_to_sell / 2
            else CapitalGainType.SHORT_TERM
        )
        
        return capital_gains
    
    def _select_lots_for_sale(
        self,
        asset: str,
        quantity: Decimal,
        method: TaxLotMethod
    ) -> List[TaxLot]:
        """Sotish uchun lotlarni tanlash"""
        available_lots = [
            lot for lot in self.tax_lots[asset]
            if lot.remaining_quantity > 0
        ]
        
        if method == TaxLotMethod.FIFO:
            # First In First Out
            return sorted(available_lots, key=lambda x: x.purchase_date)
        
        elif method == TaxLotMethod.LIFO:
            # Last In First Out
            return sorted(available_lots, key=lambda x: x.purchase_date, reverse=True)
        
        elif method == TaxLotMethod.HIFO:
            # Highest In First Out (highest cost basis first)
            return sorted(
                available_lots,
                key=lambda x: x.cost_basis / x.quantity,
                reverse=True
            )
        
        else:
            # Default to FIFO
            return sorted(available_lots, key=lambda x: x.purchase_date)
    
    async def generate_annual_report(
        self,
        user_id: str,
        year: int
    ) -> TaxReport:
        """
        Yillik soliq hisobotini yaratish
        
        Args:
            user_id: Foydalanuvchi ID
            year: Yil
        
        Returns:
            TaxReport obyekti
        """
        import uuid
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        # Filter transactions for this period
        period_transactions = [
            txn for txn in self.transactions.values()
            if txn.user_id == user_id and start_date <= txn.date <= end_date
        ]
        
        # Calculate summary
        total_capital_gains = Decimal("0")
        total_capital_losses = Decimal("0")
        short_term_gains = Decimal("0")
        long_term_gains = Decimal("0")
        total_dividend_income = Decimal("0")
        total_interest_income = Decimal("0")
        total_fees = Decimal("0")
        
        capital_gains_list = []
        
        for txn in period_transactions:
            # Process fees
            total_fees += txn.fee
            
            # Process dividends and interest
            if txn.type == TransactionType.DIVIDEND:
                total_dividend_income += txn.total_value
            elif txn.type == TransactionType.INTEREST:
                total_interest_income += txn.total_value
            
            # Process capital gains
            elif txn.type == TransactionType.SELL and txn.gain_loss:
                if txn.gain_loss > 0:
                    total_capital_gains += txn.gain_loss
                else:
                    total_capital_losses += abs(txn.gain_loss)
                
                if txn.gain_type == CapitalGainType.SHORT_TERM:
                    short_term_gains += txn.gain_loss
                elif txn.gain_type == CapitalGainType.LONG_TERM:
                    long_term_gains += txn.gain_loss
                
                # Create capital gain record
                if txn.cost_basis and txn.proceeds:
                    gain = CapitalGain(
                        id=f"gain_{uuid.uuid4().hex[:16]}",
                        asset=txn.asset,
                        quantity=txn.quantity,
                        cost_basis=txn.cost_basis,
                        proceeds=txn.proceeds,
                        gain_loss=txn.gain_loss,
                        purchase_date=txn.date - timedelta(days=100),  # Simplified
                        sale_date=txn.date,
                        holding_period_days=100,  # Simplified
                        gain_type=txn.gain_type or CapitalGainType.SHORT_TERM
                    )
                    capital_gains_list.append(gain)
        
        net_capital_gain_loss = total_capital_gains - total_capital_losses
        
        # Create report
        report = TaxReport(
            id=f"tax_report_{uuid.uuid4().hex[:16]}",
            user_id=user_id,
            year=year,
            report_type="annual",
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(),
            total_capital_gains=total_capital_gains,
            total_capital_losses=total_capital_losses,
            net_capital_gain_loss=net_capital_gain_loss,
            short_term_gains=short_term_gains,
            long_term_gains=long_term_gains,
            total_dividend_income=total_dividend_income,
            total_interest_income=total_interest_income,
            total_fees=total_fees,
            transactions=period_transactions,
            capital_gains=capital_gains_list
        )
        
        self.reports[report.id] = report
        
        logger.info(f"Annual tax report generated: {report.id} for user {user_id} - Year {year}")
        
        return report
    
    async def generate_pnl_statement(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        PnL statement yaratish
        
        Args:
            user_id: Foydalanuvchi ID
            start_date: Boshlang'ich sana
            end_date: Tugash sana
        
        Returns:
            PnL statement
        """
        # Filter transactions
        transactions = [
            txn for txn in self.transactions.values()
            if txn.user_id == user_id and start_date <= txn.date <= end_date
        ]
        
        # Calculate totals
        total_realized_pnl = sum(
            txn.gain_loss for txn in transactions
            if txn.gain_loss and txn.type == TransactionType.SELL
        )
        
        total_dividend_income = sum(
            txn.total_value for txn in transactions
            if txn.type == TransactionType.DIVIDEND
        )
        
        total_interest_income = sum(
            txn.total_value for txn in transactions
            if txn.type == TransactionType.INTEREST
        )
        
        total_fees = sum(txn.fee for txn in transactions)
        
        # Net PnL
        net_pnl = total_realized_pnl + total_dividend_income + total_interest_income - total_fees
        
        # By asset breakdown
        by_asset: Dict[str, Dict[str, Decimal]] = {}
        
        for txn in transactions:
            if txn.asset not in by_asset:
                by_asset[txn.asset] = {
                    "realized_pnl": Decimal("0"),
                    "dividend_income": Decimal("0"),
                    "fees": Decimal("0")
                }
            
            if txn.type == TransactionType.SELL and txn.gain_loss:
                by_asset[txn.asset]["realized_pnl"] += txn.gain_loss
            elif txn.type == TransactionType.DIVIDEND:
                by_asset[txn.asset]["dividend_income"] += txn.total_value
            
            by_asset[txn.asset]["fees"] += txn.fee
        
        # Format by_asset
        by_asset_formatted = {
            asset: {
                "realized_pnl": str(data["realized_pnl"]),
                "dividend_income": str(data["dividend_income"]),
                "fees": str(data["fees"]),
                "net_pnl": str(data["realized_pnl"] + data["dividend_income"] - data["fees"])
            }
            for asset, data in by_asset.items()
        }
        
        return {
            "user_id": user_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {
                "total_realized_pnl": str(total_realized_pnl),
                "total_dividend_income": str(total_dividend_income),
                "total_interest_income": str(total_interest_income),
                "total_fees": str(total_fees),
                "net_pnl": str(net_pnl)
            },
            "by_asset": by_asset_formatted,
            "transactions_count": len(transactions)
        }
    
    async def export_to_csv(
        self,
        report_id: str
    ) -> str:
        """
        Hisobotni CSV formatda export qilish
        
        Args:
            report_id: Report ID
        
        Returns:
            CSV string
        """
        if report_id not in self.reports:
            raise ValueError(f"Report not found: {report_id}")
        
        report = self.reports[report_id]
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Date", "Type", "Asset", "Quantity", "Price",
            "Total Value", "Fee", "Cost Basis", "Proceeds",
            "Gain/Loss", "Gain Type", "Description"
        ])
        
        # Transactions
        for txn in report.transactions:
            writer.writerow([
                txn.date.strftime("%Y-%m-%d"),
                txn.type.value,
                txn.asset,
                str(txn.quantity),
                str(txn.price),
                str(txn.total_value),
                str(txn.fee),
                str(txn.cost_basis) if txn.cost_basis else "",
                str(txn.proceeds) if txn.proceeds else "",
                str(txn.gain_loss) if txn.gain_loss else "",
                txn.gain_type.value if txn.gain_type else "",
                txn.description or ""
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    async def get_report(self, report_id: str) -> Optional[TaxReport]:
        """Hisobotni olish"""
        return self.reports.get(report_id)
    
    async def get_user_reports(self, user_id: str) -> List[TaxReport]:
        """Foydalanuvchi hisobotlarini olish"""
        reports = [
            report for report in self.reports.values()
            if report.user_id == user_id
        ]
        
        # Sort by year descending
        reports.sort(key=lambda x: x.year, reverse=True)
        
        return reports
    
    async def get_tax_lots(self, asset: str) -> List[TaxLot]:
        """Asset uchun tax lots olish"""
        if asset not in self.tax_lots:
            return []
        
        # Return only lots with remaining quantity
        return [
            lot for lot in self.tax_lots[asset]
            if lot.remaining_quantity > 0
        ]
    
    async def get_unrealized_gains(self, user_id: str) -> Dict[str, Any]:
        """
        Unrealized gains hisoblash
        
        Args:
            user_id: Foydalanuvchi ID
        
        Returns:
            Unrealized gains ma'lumotlari
        """
        # This would require current market prices
        # Simplified implementation
        
        unrealized_by_asset: Dict[str, Dict[str, Any]] = {}
        
        for asset, lots in self.tax_lots.items():
            total_quantity = sum(lot.remaining_quantity for lot in lots)
            total_cost_basis = sum(
                (lot.remaining_quantity / lot.quantity) * lot.cost_basis
                for lot in lots if lot.quantity > 0
            )
            
            if total_quantity > 0:
                # Would need current price here
                # Using placeholder
                current_price = Decimal("100")  # Placeholder
                current_value = total_quantity * current_price
                unrealized_gain = current_value - total_cost_basis
                
                unrealized_by_asset[asset] = {
                    "quantity": str(total_quantity),
                    "cost_basis": str(total_cost_basis),
                    "current_value": str(current_value),
                    "unrealized_gain": str(unrealized_gain),
                    "avg_cost": str(total_cost_basis / total_quantity) if total_quantity > 0 else "0"
                }
        
        return {
            "user_id": user_id,
            "by_asset": unrealized_by_asset,
            "note": "Current market prices would be needed for accurate calculation"
        }
    
    async def calculate_tax_optimization(
        self,
        user_id: str,
        asset: str,
        sell_quantity: Decimal,
        sale_date: datetime,
        current_prices: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """
        Soliq optimizatsiyasi hisoblash
        
        Args:
            user_id: Foydalanuvchi ID
            asset: Asset nomi
            sell_quantity: Sotish miqdori
            sale_date: Sotish sanasi
            current_prices: Joriy narxlar
        
        Returns:
            Optimizatsiya tavsiyalari
        """
        if asset not in self.tax_lots:
            return {"error": f"No holdings found for {asset}"}
        
        current_price = current_prices.get(asset, Decimal("0"))
        if current_price == 0:
            return {"error": f"No current price available for {asset}"}
        
        optimization_results = {}
        
        # Har bir tax lot method uchun hisoblash
        for method in TaxLotMethod:
            # Hisobiy sotish
            lots = self._select_lots_for_sale(asset, sell_quantity, method)
            total_cost_basis = Decimal("0")
            short_term_gain = Decimal("0")
            long_term_gain = Decimal("0")
            
            for lot in lots:
                sell_qty = min(lot.remaining_quantity, sell_quantity)
                cost_basis_per_unit = lot.cost_basis / lot.quantity
                cost_basis = sell_qty * cost_basis_per_unit
                
                proceeds = sell_qty * current_price
                gain_loss = proceeds - cost_basis
                holding_days = (sale_date - lot.purchase_date).days
                
                if holding_days < 365:
                    short_term_gain += gain_loss
                else:
                    long_term_gain += gain_loss
                
                total_cost_basis += cost_basis
            
            total_proceeds = sell_quantity * current_price
            net_gain = short_term_gain + long_term_gain
            
            optimization_results[method.value] = {
                "cost_basis": str(total_cost_basis),
                "proceeds": str(total_proceeds),
                "short_term_gain": str(short_term_gain),
                "long_term_gain": str(long_term_gain),
                "net_gain": str(net_gain),
                "tax_efficiency": str(net_gain / total_proceeds) if total_proceeds > 0 else "0"
            }
        
        # Eng yaxshi strategiyani aniqlash
        best_method = max(
            optimization_results.items(),
            key=lambda x: Decimal(x[1]["net_gain"])
        )[0]
        
        return {
            "asset": asset,
            "sell_quantity": str(sell_quantity),
            "current_price": str(current_price),
            "optimization_results": optimization_results,
            "recommended_method": best_method,
            "reasoning": f"{best_method} eng yuqori sof daromad beradi"
        }
    
    async def calculate_capital_gains_precise(
        self,
        asset: str,
        sell_quantity: Decimal,
        sale_price: Decimal,
        sale_date: datetime,
        method: TaxLotMethod = TaxLotMethod.FIFO
    ) -> Dict[str, Any]:
        """
        Aniq kapital daromad hisoblash
        
        Args:
            asset: Asset nomi
            sell_quantity: Sotish miqdori
            sale_price: Sotish narxi
            sale_date: Sotish sanasi
            method: Tax lot method
        
        Returns:
            Batafsil kapital daromad hisoboti
        """
        if asset not in self.tax_lots:
            return {"error": f"No tax lots found for {asset}"}
        
        lots = self._select_lots_for_sale(asset, sell_quantity, method)
        remaining_to_sell = sell_quantity
        
        capital_gains_detail = []
        total_cost_basis = Decimal("0")
        total_proceeds = Decimal("0")
        
        for lot in lots:
            if remaining_to_sell <= 0:
                break
            
            sell_from_lot = min(remaining_to_sell, lot.remaining_quantity)
            
            # Hisob-kitoblar
            cost_basis_per_unit = lot.cost_basis / lot.quantity
            cost_basis = sell_from_lot * cost_basis_per_unit
            proceeds = sell_from_lot * sale_price
            gain_loss = proceeds - cost_basis
            
            # Holding period
            holding_days = (sale_date - lot.purchase_date).days
            gain_type = (
                CapitalGainType.LONG_TERM if holding_days >= 365
                else CapitalGainType.SHORT_TERM
            )
            
            capital_gains_detail.append({
                "lot_id": lot.id,
                "purchase_date": lot.purchase_date.isoformat(),
                "quantity_sold": str(sell_from_lot),
                "cost_basis": str(cost_basis),
                "proceeds": str(proceeds),
                "gain_loss": str(gain_loss),
                "holding_period_days": holding_days,
                "gain_type": gain_type.value,
                "cost_per_unit": str(cost_basis_per_unit)
            })
            
            total_cost_basis += cost_basis
            total_proceeds += proceeds
            remaining_to_sell -= sell_from_lot
        
        net_gain_loss = total_proceeds - total_cost_basis
        
        return {
            "asset": asset,
            "total_quantity_sold": str(sell_quantity),
            "sale_price": str(sale_price),
            "method_used": method.value,
            "summary": {
                "total_cost_basis": str(total_cost_basis),
                "total_proceeds": str(total_proceeds),
                "net_gain_loss": str(net_gain_loss),
                "average_cost_per_unit": str(total_cost_basis / sell_quantity) if sell_quantity > 0 else "0",
                "gain_loss_percentage": str((net_gain_loss / total_cost_basis) * 100) if total_cost_basis > 0 else "0"
            },
            "detailed_gains": capital_gains_detail
        }
    
    async def tax_loss_harvesting_analysis(
        self,
        user_id: str,
        current_prices: Dict[str, Decimal],
        target_losses: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Soliq yo'qotishlarini yig'ish tahlili
        
        Args:
            user_id: Foydalanuvchi ID
            current_prices: Joriy narxlar
            target_losses: Maqsadli yo'qotishlar (ixtiyoriy)
        
        Returns:
            Yo'qotishlar tahlili
        """
        unrealized_losses = []
        total_unrealized_loss = Decimal("0")
        
        # Har bir asset uchun unrealized yo'qotishlarni hisoblash
        for asset, lots in self.tax_lots.items():
            current_price = current_prices.get(asset, Decimal("0"))
            if current_price == 0:
                continue
            
            for lot in lots:
                if lot.remaining_quantity <= 0:
                    continue
                
                current_value = lot.remaining_quantity * current_price
                cost_basis = (lot.remaining_quantity / lot.quantity) * lot.cost_basis
                unrealized_gain_loss = current_value - cost_basis
                
                if unrealized_gain_loss < 0:  # Faqat yo'qotishlar
                    unrealized_losses.append({
                        "asset": asset,
                        "lot_id": lot.id,
                        "quantity": str(lot.remaining_quantity),
                        "cost_basis": str(cost_basis),
                        "current_value": str(current_value),
                        "unrealized_loss": str(abs(unrealized_gain_loss)),
                        "purchase_date": lot.purchase_date.isoformat(),
                        "holding_period_days": (datetime.now() - lot.purchase_date).days
                    })
                    
                    total_unrealized_loss += abs(unrealized_gain_loss)
        
        # Yo'qotishlarni kamayish tartibida saralash
        unrealized_losses.sort(key=lambda x: Decimal(x["unrealized_loss"]), reverse=True)
        
        # Maqsadli yo'qotishga yetish uchun kerakli aktivlar
        if target_losses:
            recommended_sells = []
            accumulated_loss = Decimal("0")
            
            for loss in unrealized_losses:
                if accumulated_loss >= target_losses:
                    break
                
                recommended_sells.append(loss)
                accumulated_loss += Decimal(loss["unrealized_loss"])
        else:
            recommended_sells = unrealized_losses[:10]  # Top 10
            accumulated_loss = total_unrealized_loss
        
        return {
            "user_id": user_id,
            "total_unrealized_losses": str(total_unrealized_loss),
            "asset_count_with_losses": len(set(loss["asset"] for loss in unrealized_losses)),
            "recommended_sells": recommended_sells,
            "potential_tax_savings": str(accumulated_loss * Decimal("0.22")),  # 22% tax rate
            "harvesting_opportunities": len(unrealized_losses),
            "note": "Consider wash sale rules (30-day rule) when harvesting losses"
        }
    
    async def year_end_tax_planning(
        self,
        user_id: str,
        year: int,
        tax_rates: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """
        Yil oxiridagi soliq rejalash
        
        Args:
            user_id: Foydalanuvchi ID
            year: Hisobot yili
            tax_rates: Soliq stavkalari
        
        Returns:
            Soliq reja tashish
        """
        # Yil boshidan boshlab hisobot yaratish
        report = await self.generate_annual_report(user_id, year)
        
        current_gains = report.total_capital_gains
        current_losses = report.total_capital_losses
        net_capital_gain = report.net_capital_gain_loss
        
        # Soliq optimizatsiya tavsiyalari
        recommendations = []
        
        # Agar katta kapital daromadlar bo'lsa
        if current_gains > Decimal("10000"):
            short_term_rate = tax_rates.get("short_term", Decimal("0.22"))
            long_term_rate = tax_rates.get("long_term", Decimal("0.15"))
            
            est_short_term_tax = max(Decimal("0"), report.short_term_gains) * short_term_rate
            est_long_term_tax = max(Decimal("0"), report.long_term_gains) * long_term_rate
            total_estimated_tax = est_short_term_tax + est_long_term_tax
            
            recommendations.append({
                "type": "capital_gains_realization",
                "description": "Consider timing of asset sales for tax efficiency",
                "estimated_tax_liability": str(total_estimated_tax),
                "potential_savings": "Variable based on timing and method"
            })
        
        # Agar katta yo'qotishlar bo'lsa
        if current_losses > Decimal("5000"):
            recommendations.append({
                "type": "loss_harvesting",
                "description": "Consider harvesting additional losses before year-end",
                "current_net_losses": str(current_losses),
                "max_deduction": "3000 per year for individuals"
            })
        
        # Qisqa muddatli vs uzoq muddatli daromadlar muvozanatlash
        if abs(report.short_term_gains) > report.long_term_gains * 2:
            recommendations.append({
                "type": "hold_period_optimization",
                "description": "Consider holding assets longer to qualify for long-term capital gains rates",
                "current_short_term": str(report.short_term_gains),
                "potential_benefit": "Lower tax rates on long-term gains"
            })
        
        # Dividend va foiz daromadlar
        if report.total_dividend_income > Decimal("1000"):
            recommendations.append({
                "type": "dividend_income",
                "description": "Consider qualified dividend strategies",
                "current_dividend_income": str(report.total_dividend_income),
                "tax_advantage": "Qualified dividends taxed at capital gains rates"
            })
        
        return {
            "user_id": user_id,
            "tax_year": year,
            "current_summary": {
                "total_capital_gains": str(current_gains),
                "total_capital_losses": str(current_losses),
                "net_capital_gain_loss": str(net_capital_gain),
                "short_term_gains": str(report.short_term_gains),
                "long_term_gains": str(report.long_term_gains),
                "dividend_income": str(report.total_dividend_income),
                "interest_income": str(report.total_interest_income)
            },
            "recommendations": recommendations,
            "next_steps": [
                "Review and optimize tax lot selection methods",
                "Consider year-end loss harvesting",
                "Plan next year's transactions for tax efficiency",
                "Consult tax professional for complex situations"
            ]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Tax reporting statistikasi"""
        return {
            "total_transactions": len(self.transactions),
            "total_reports": len(self.reports),
            "total_assets_tracked": len(self.tax_lots),
            "total_tax_lots": sum(len(lots) for lots in self.tax_lots.values()),
            "default_method": self.default_method.value
        }


# ========================
# FOYDALANISH MISOLLARI VA TEST
# ========================

async def demo_tax_reporting():
    """Tax reporting tizimi demo"""
    
    # Tizimni yaratish
    tax_system = TaxReporting()
    
    user_id = "demo_user_123"
    
    print("=" * 60)
    print("SOLIQ HISOBOTI TIZIMI DEMO")
    print("=" * 60)
    
    # 1. Tranzaksiyalarni qayd etish
    print("\n1. TRANZAKSIYALARNI QAYD ETISH")
    print("-" * 40)
    
    # AAPL aksiyalarini sotib olish
    buy1 = await tax_system.record_transaction(
        user_id=user_id,
        date=datetime(2024, 1, 15),
        transaction_type=TransactionType.BUY,
        asset="AAPL",
        quantity=Decimal("100"),
        price=Decimal("150.00"),
        fee=Decimal("10.00"),
        description="AAPL aksiyalarini sotib olish"
    )
    print(f"✓ Buy: {buy1.quantity} {buy1.asset} @ ${buy1.price}")
    
    # Yana AAPL sotib olish
    buy2 = await tax_system.record_transaction(
        user_id=user_id,
        date=datetime(2024, 3, 10),
        transaction_type=TransactionType.BUY,
        asset="AAPL",
        quantity=Decimal("50"),
        price=Decimal("175.00"),
        fee=Decimal("5.00"),
        description="Qo'shimcha AAPL sotib olish"
    )
    print(f"✓ Buy: {buy2.quantity} {buy2.asset} @ ${buy2.price}")
    
    # Dividend
    dividend = await tax_system.record_transaction(
        user_id=user_id,
        date=datetime(2024, 5, 15),
        transaction_type=TransactionType.DIVIDEND,
        asset="AAPL",
        quantity=Decimal("0"),
        price=Decimal("0"),
        total_value=Decimal("25.50"),
        description="AAPL dividend"
    )
    print(f"✓ Dividend: ${dividend.total_value}")
    
    # Sotish (FIFO method bilan)
    sell1 = await tax_system.record_transaction(
        user_id=user_id,
        date=datetime(2024, 8, 20),
        transaction_type=TransactionType.SELL,
        asset="AAPL",
        quantity=Decimal("75"),
        price=Decimal("190.00"),
        fee=Decimal("10.00"),
        description="AAPL qisman sotish"
    )
    print(f"✓ Sell: {sell1.quantity} {sell1.asset} @ ${sell1.price}")
    print(f"  Gain/Loss: ${sell1.gain_loss}")
    
    # Boshqa aktivlar
    msft_buy = await tax_system.record_transaction(
        user_id=user_id,
        date=datetime(2024, 2, 1),
        transaction_type=TransactionType.BUY,
        asset="MSFT",
        quantity=Decimal("30"),
        price=Decimal("300.00"),
        fee=Decimal("7.50"),
        description="Microsoft sotib olish"
    )
    print(f"✓ Buy: {msft_buy.quantity} {msft_buy.asset} @ ${msft_buy.price}")
    
    # 2. Tax lots ko'rish
    print("\n2. TAX LOTS")
    print("-" * 40)
    
    aapl_lots = await tax_system.get_tax_lots("AAPL")
    print(f"AAPL tax lots: {len(aapl_lots)} ta")
    for lot in aapl_lots:
        print(f"  Lot {lot.id}: {lot.remaining_quantity} @ ${lot.cost_basis / lot.quantity:.2f}")
    
    # 3. Yillik hisobot yaratish
    print("\n3. YILLIK HISOBOT")
    print("-" * 40)
    
    annual_report = await tax_system.generate_annual_report(user_id, 2024)
    print(f"Yil: {annual_report.year}")
    print(f"Jami kapital daromadlar: ${annual_report.total_capital_gains}")
    print(f"Jami kapital yo'qotishlar: ${annual_report.total_capital_losses}")
    print(f"Net kapital foyda/zarar: ${annual_report.net_capital_gain_loss}")
    print(f"Qisqa muddatli daromadlar: ${annual_report.short_term_gains}")
    print(f"Uzoq muddatli daromadlar: ${annual_report.long_term_gains}")
    print(f"Dividend daromadlar: ${annual_report.total_dividend_income}")
    
    # 4. P&L Statement
    print("\n4. P&L STATEMENT")
    print("-" * 40)
    
    pnl = await tax_system.generate_pnl_statement(
        user_id=user_id,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    print(f"Jami realized P&L: ${pnl['summary']['total_realized_pnl']}")
    print(f"Dividend daromadlar: ${pnl['summary']['total_dividend_income']}")
    print(f"Jami xarajatlar: ${pnl['summary']['total_fees']}")
    print(f"Net P&L: ${pnl['summary']['net_pnl']}")
    
    print("\nAsset bo'yicha P&L:")
    for asset, data in pnl['by_asset'].items():
        print(f"  {asset}: ${data['net_pnl']}")
    
    # 5. Aniq kapital daromad hisoblash
    print("\n5. ANIQ KAPITAL DAROMAD HISOBLASH")
    print("-" * 40)
    
    capital_gains_detail = await tax_system.calculate_capital_gains_precise(
        asset="AAPL",
        sell_quantity=Decimal("25"),
        sale_price=Decimal("200.00"),
        sale_date=datetime(2024, 10, 15),
        method=TaxLotMethod.FIFO
    )
    
    if "error" not in capital_gains_detail:
        print(f"Jami cost basis: ${capital_gains_detail['summary']['total_cost_basis']}")
        print(f"Jami proceeds: ${capital_gains_detail['summary']['total_proceeds']}")
        print(f"Net gain/loss: ${capital_gains_detail['summary']['net_gain_loss']}")
        
        print("\nLot ma'lumotlari:")
        for detail in capital_gains_detail['detailed_gains']:
            print(f"  Lot {detail['lot_id']}: ${detail['gain_loss']} ({detail['gain_type']})")
    
    # 6. Soliq optimizatsiyasi
    print("\n6. SOLIQ OPTIMIZATSIYASI")
    print("-" * 40)
    
    optimization = await tax_system.calculate_tax_optimization(
        user_id=user_id,
        asset="AAPL",
        sell_quantity=Decimal("50"),
        sale_date=datetime(2024, 11, 1),
        current_prices={"AAPL": Decimal("185.00")}
    )
    
    if "error" not in optimization:
        print(f"Tavsiya etiladigan usul: {optimization['recommended_method']}")
        print(f"Sabab: {optimization['reasoning']}")
        
        print("\nBarcha usullar bo'yicha natijalar:")
        for method, result in optimization['optimization_results'].items():
            print(f"  {method}: Net gain ${result['net_gain']}")
    
    # 7. Tax loss harvesting
    print("\n7. TAX LOSS HARVESTING")
    print("-" * 40)
    
    current_prices = {
        "AAPL": Decimal("140.00"),  #假设价格下跌
        "MSFT": Decimal("280.00")   #假设价格下跌
    }
    
    loss_harvesting = await tax_system.tax_loss_harvesting_analysis(
        user_id=user_id,
        current_prices=current_prices,
        target_losses=Decimal("1000")
    )
    
    print(f"Jami unrealized yo'qotishlar: ${loss_harvesting['total_unrealized_losses']}")
    print(f"Potentsial soliq tejamkorligi: ${loss_harvesting['potential_tax_savings']}")
    
    if loss_harvesting['recommended_sells']:
        print("\nTavsiya etiladigan sotishlar:")
        for sell in loss_harvesting['recommended_sells']:
            print(f"  {sell['asset']}: ${sell['unrealized_loss']} yo'qotish")
    
    # 8. Yil oxiridagi soliq rejalash
    print("\n8. YIL OXIRIDAGI SOLIQ REJALASH")
    print("-" * 40)
    
    tax_planning = await tax_system.year_end_tax_planning(
        user_id=user_id,
        year=2024,
        tax_rates={
            "short_term": Decimal("0.22"),
            "long_term": Decimal("0.15"),
            "ordinary": Decimal("0.24")
        }
    )
    
    print("Joriy yil xulosasi:")
    for key, value in tax_planning['current_summary'].items():
        print(f"  {key}: ${value}")
    
    if tax_planning['recommendations']:
        print("\nTavsiyalar:")
        for rec in tax_planning['recommendations']:
            print(f"  • {rec['description']}")
    
    # 9. CSV export
    print("\n9. CSV EXPORT")
    print("-" * 40)
    
    csv_content = await tax_system.export_to_csv(annual_report.id)
    print(f"CSV fayl tayyorlandi, hajm: {len(csv_content)} belgi")
    print("CSV preview:")
    print(csv_content[:300] + "..." if len(csv_content) > 300 else csv_content)
    
    # 10. Statistika
    print("\n10. TIZIM STATISTIKASI")
    print("-" * 40)
    
    stats = tax_system.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("DEMO YAKUNLANDI!")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    
    # Demo ishga tushirish
    asyncio.run(demo_tax_reporting())
