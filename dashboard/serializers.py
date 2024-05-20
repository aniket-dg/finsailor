from rest_framework import serializers

from data_import.models import (
    UploadedContractNotePDF,
    UploadedDematReportPDF,
    UploadedMutualFundReport,
)
from datahub.models import Broker


class UploadedContractNoteSerializer(serializers.ModelSerializer):
    pdf_file = serializers.FileField(write_only=True)

    class Meta:
        model = UploadedContractNotePDF
        fields = ("pdf_file", "broker", "password", "date", "user")


class UploadedDematReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDematReportPDF
        fields = ("pdf_file", "broker", "password", "date", "user")


class UploadedMutualFundReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedMutualFundReport
        fields = ("excel_file", "broker", "date", "user")
