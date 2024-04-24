from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.serializers import (
    UploadedContractNoteSerializer,
    UploadedDematReportSerializer,
)
from data_import.forms import TradeBookForm
from data_import.models import TradeBook, InvestmentBook
from data_import.serializers import TradeBookSerializer, InvestmentBookSerializer
from data_import.utils import (
    extract_groww_data_from_contract_note,
    convert_groww_trade_book_data_to_trade_obj,
    extract_data_from_demat_report,
    convert_demat_report_to_investment_book_obj,
)
from data_import.views import Groww, Zerodha


class ImportContractNoteData(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=UploadedContractNoteSerializer,
        responses={201: TradeBookSerializer(many=True)},
    )
    def post(self, *args, **kwargs):
        serializer = UploadedContractNoteSerializer(data=self.request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)

        contract_note = serializer.save()
        broker = Zerodha(dry_run=True)
        if contract_note.broker == "groww":
            broker = Groww(contract_note.password, dry_run=True)

        trade_books, imported = broker.import_data_from_contract_note(
            path=contract_note.pdf_file.path, date=contract_note.date.isoformat()
        )
        serialized_trade_books = None
        if imported:
            serialized_trade_books = TradeBookSerializer(trade_books, many=True).data

        return Response(
            {"trades": serialized_trade_books}, status=status.HTTP_201_CREATED
        )


class ImportDematReportData(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=UploadedDematReportSerializer,
        responses={201: InvestmentBookSerializer(many=True)},
    )
    def post(self, *args, **kwargs):
        serializer = UploadedDematReportSerializer(data=self.request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)

        if serializer.validated_data.get("broker") != "groww":
            return Response(
                {"message": "Currently not available to process Zerodha Demat Report"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        demat_report = serializer.save()

        broker = Groww(demat_report.password, dry_run=True)

        investment_books, imported = broker.import_data_from_demat_report(
            path=demat_report.pdf_file.path
        )
        serialized_investment_books = None
        if imported:
            serialized_investment_books = InvestmentBookSerializer(
                investment_books, many=True
            ).data

        return Response(
            {"investment_books": serialized_investment_books},
            status=status.HTTP_201_CREATED,
        )
