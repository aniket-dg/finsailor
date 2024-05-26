from django.shortcuts import render
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from dashboard.serializers import (
    UploadedContractNoteSerializer,
    UploadedDematReportSerializer,
    UploadedMutualFundReportSerializer,
)
from data_import.forms import TradeBookForm
from data_import.models import TradeBook, InvestmentBook
from data_import.serializers import (
    TradeBookSerializer,
    InvestmentBookSerializer,
    MutualFundBookSerializer,
)
from data_import.utils import (
    extract_groww_data_from_contract_note,
    convert_groww_trade_book_data_to_trade_obj,
    extract_data_from_demat_report,
    convert_demat_report_to_investment_book_obj,
)
from data_import.views import Groww, Zerodha
from datahub.models import GeneralInfo
from datahub.serializers import GeneralInfoSerializer
from datahub.utils import get_general_info_obj


@extend_schema(tags=["Dashboard App"])
class ImportContractNoteData(APIView):
    parser_classes = (MultiPartParser, FormParser)
    # serializer_class = UploadedContractNoteSerializer

    @extend_schema(
        request=UploadedContractNoteSerializer,
        responses={201: TradeBookSerializer(many=True)},
    )
    def post(self, *args, **kwargs):
        serializer = UploadedContractNoteSerializer(data=self.request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)

        contract_note = serializer.save()

        broker = Zerodha()
        if contract_note.broker == "groww":
            broker = Groww(contract_note.password)

        trade_books, imported = broker.import_data_from_contract_note(
            path=contract_note.pdf_file.path, date=contract_note.date.isoformat()
        )
        serialized_trade_books = None
        if imported:
            serialized_trade_books = TradeBookSerializer(trade_books, many=True).data
            general_info = get_general_info_obj()
            general_info.tradebook_last_uploaded = contract_note.date
            general_info.save()
            contract_note.processed = True

        return Response(
            {"trades": serialized_trade_books}, status=status.HTTP_201_CREATED
        )


@extend_schema(tags=["Dashboard App"])
class ImportDematReportData(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=UploadedDematReportSerializer,
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
            demat_report.processed = True
            serialized_investment_books = InvestmentBookSerializer(
                investment_books, many=True
            ).data

        return Response(
            {"investment_books": serialized_investment_books},
            status=status.HTTP_201_CREATED,
        )

