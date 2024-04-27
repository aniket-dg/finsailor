from dashboard.models import Investment
from data_import.models import TradeBook


# def process_unread_tradebook():
#     trade_books = TradeBook.objects.filter(processed=False)
#     for trade_book in trade_books:
#         investment = Investment.objects.filter(
#             trade_book.security_id, user_id=trade_book.user_id
#         ).last()
#         if investment is None:
#             investment = Investment(
#                 security_id=trade_book.security_id, user_id=trade_book.user_id
#             )
#
#         investment.quantity += 1
