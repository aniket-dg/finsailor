import tabula
import pandas as pd


def extract_data(path, password):
    dfs = tabula.read_pdf(path, password=password, pages="all")
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
        else:
            trade_df.rename(columns=named_columns_mapping, inplace=True)

        trade_book = {}
        for i, trade in trade_df.iterrows():
            order_no = trade["Order No."]
            if pd.isna(order_no) or order_no.strip() == "Total":
                print("Skipping row as it is Total or Nan.")
                continue
            try:
                order_no = int(order_no)
            except ValueError as e:
                print("Skipping row because Order No. is Nan.")
                continue
            trade_time = trade["Trade Time"]
            order_time = trade["Order Time"]
            trade_book = {
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

    return trade_book_data
