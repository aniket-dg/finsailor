import datetime
from typing import List

import pandas as pd
import tabula

from data_import.models import TradeBook, InvestmentBook


class Groww:
    def __init__(self, password=None, dry_run=False):
        self.password = password
        self.dry_run = dry_run

    @staticmethod
    def convert_trade_book_data_to_trade_obj(trade_book_data: list) -> List[TradeBook]:
        trade_book_objs = []
        for trade in trade_book_data:
            security = trade["security"]
            exchange = trade["exchange"]
            date = trade["date"]
            execution_datetime = datetime.datetime.strptime(
                date + " " + trade["trade_time"], "%Y-%m-%d %H:%M:%S"
            )
            trade_book = TradeBook(
                order_no=trade["order_no"],
                execution_datetime=execution_datetime,
                security=security,
                exchange=exchange,
                buy_sell=trade["buy_sell"],
                quantity=trade["quantity"] if not pd.isna(trade["quantity"]) else None,
                gross_rate=(
                    trade["gross_rate"] if not pd.isna(trade["gross_rate"]) else None
                ),
                brokerage=(
                    trade["brokerage"] if not pd.isna(trade["brokerage"]) else None
                ),
                net_rate=trade["net_rate"] if not pd.isna(trade["net_rate"]) else None,
                closing_rate=(
                    trade["closing_rate"]
                    if not pd.isna(trade["closing_rate"])
                    else None
                ),
                total=trade["total"] if not pd.isna(trade["total"]) else None,
                remarks=trade["remarks"] if not pd.isna(trade["remarks"]) else None,
            )
            trade_book_objs.append(trade_book)

        return trade_book_objs

    def import_data_from_contract_note(
        self, path: str, date: str
    ) -> [bool, List[TradeBook]]:
        dfs = tabula.read_pdf(path, password=self.password, pages="all")

        if len(dfs) < 2:
            print("No trades found in trade book")
            return

        named_columns_mapping = {
            "Order\rno.": "Order No.",
            "Order\rtime": "Order Time",
            "Trade\rno.": "Trade No.",
            "Trade\rtime": "Trade Time",
            "Security/Contract\rdescription": "Security",
            "Exchange": "Exchange",
            "Buy(B)/\rSell(S)": "Buy(B)/Sell(S)",
            "Quantity": "Quantity",
            "Gross Rate/\rTrade Price\rPer unit (Rs)": "Gross Rate/ Trade Price per unit (Rs)",
            "Brokerage\rper Unit\r(Rs)": "Brokerage per Unit (Rs)",
            "Net Rate\rper Unit\r(Rs)": "Net Rate per Unit (Rs)",
            "Closing Rate\rper Unit (only for\rDerivatives)\r(Rs)": "Closing Rate per Unit (only for Derivatives) (Rs)",
            "Net Total\r(Before\rLevies)\r(Rs)": "Net Total (Before Levies) (Rs)",
            "Remarks": "Remarks",
        }

        unnamed_columns_mapping = {
            "Unnamed: 0": "Order No.",
            "Unnamed: 1": "Order Time",
            "Unnamed: 2": "Trade No.",
            "Unnamed: 3": "Trade Time",
            "Unnamed: 4": "Security",
            "Unnamed: 5": "Exchange",
            "Unnamed: 6": "Buy(B)/Sell(S)",
            "Unnamed: 7": "Quantity",
            "Unnamed: 8": "Gross Rate/ Trade Price per unit (Rs)",
            "Unnamed: 9": "Brokerage per Unit (Rs)",
            "Unnamed: 10": "Net Rate per Unit (Rs)",
            "Closing Rate": "Closing Rate per Unit (only for Derivatives) (Rs)",
            "Net Total": "Net Total (Before Levies) (Rs)",
            "Unnamed: 11": "Remarks",
        }

        trades_dfs = dfs[1:-1]

        trade_book_data = []
        for trade_df in trades_dfs:
            if "Unnamed: 0" in trade_df.columns:
                trade_df.rename(columns=unnamed_columns_mapping, inplace=True)
            elif "Order\rno." in trade_df.columns or "Quantity" in trade_df.columns:
                trade_df.rename(columns=named_columns_mapping, inplace=True)
            else:
                print("Skipping df as it doesn't contain Trades")
                continue

            for i, trade in trade_df.iterrows():
                order_no = trade["Order No."]
                security = trade["Security"]
                if pd.isna(order_no) or order_no.strip() == "Total":
                    print("Skipping row as it is Total or Nan.")
                    continue

                if pd.isna(security):
                    print("Skipping row as it contains Nan.")
                    continue
                try:
                    order_no = int(order_no)
                except ValueError as e:
                    print("Skipping row because Order No. is Nan.")
                    continue
                trade_time = trade["Trade Time"]
                order_time = trade["Order Time"]
                trade_book = {
                    "date": date,
                    "order_no": order_no,
                    "order_time": order_time,
                    "trade_time": trade_time,
                    "security": trade["Security"],
                    "exchange": trade["Exchange"],
                    "buy_sell": trade["Buy(B)/Sell(S)"],
                    "quantity": trade["Quantity"],
                    "gross_rate": trade["Gross Rate/ Trade Price per unit (Rs)"],
                    "brokerage": trade["Brokerage per Unit (Rs)"],
                    "net_rate": trade["Net Rate per Unit (Rs)"],
                    "closing_rate": trade[
                        "Closing Rate per Unit (only for Derivatives) (Rs)"
                    ],
                    "total": trade["Net Total (Before Levies) (Rs)"],
                    "remarks": trade["Remarks"],
                }
                trade_book_data.append(trade_book)

        trade_book_objs = self.convert_trade_book_data_to_trade_obj(trade_book_data)

        if not self.dry_run:
            trade_books = TradeBook.objects.bulk_create(trade_book_objs)
            print(f"Total trades imported - {len(trade_books)}")

        else:
            trade_books = trade_book_data
            print(f"Total trades imported - {len(trade_book_objs)}")

        return trade_books, True

    def import_data_from_demat_report(self, path: str) -> [bool, List[InvestmentBook]]:
        dfs = tabula.read_pdf(path)[0]
        investment_books = {}
        for i, row in dfs.iterrows():
            scrip = row["Scrip"]
            total_quantity = row["Total Quantity"]
            investment_books[scrip] = total_quantity

        investment_books_to_create = []
        for scrip, quantity in investment_books.items():
            investment_book = InvestmentBook(security=scrip, quantity=quantity)
            investment_books_to_create.append(investment_book)

        if not self.dry_run:
            investment_books = InvestmentBook.objects.bulk_create(
                investment_books_to_create
            )
        else:
            investment_books = investment_books_to_create
            print(f"Total InvestmentBook processed - {len(investment_books_to_create)}")

        return investment_books, True


class Zerodha:
    def __init__(self, dry_run=False):
        self.broker = "Zerodha"
        self.dry_run = dry_run

    def import_data_from_contract_note(self, path, *args, **kwargs):
        df = pd.read_csv(path)
        trade_books_to_crate = []
        for i, row in df.iterrows():
            trade_book = TradeBook(
                symbol=row["symbol"],
                isin=row["isin"],
                execution_datetime=row["order_execution_time"],
                order_no=row["order_id"],
                security=row["symbol"],
                exchange=row["exchange"],
                buy_sell=row["trade_type"],
                quantity=row["quantity"],
                gross_rate=row["price"],
                net_rate=row["price"],
                broker=self.broker,
            )
            trade_books_to_crate.append(trade_book)

        if not self.dry_run:
            trade_books = TradeBook.objects.bulk_create(trade_books_to_crate)
            print(f"Total trades imported - {len(trade_books)}")
        else:
            trade_books = trade_books_to_crate
            print(f"Total trades imported - {len(trade_books_to_crate)}")

        return trade_books, True
