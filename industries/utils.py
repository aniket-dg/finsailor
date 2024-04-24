import pandas as pd

from industries.models import *


def import_industries_data_from_csv():
    df = pd.read_csv("industries/Industries_v1.csv")

    for i, row in df.iterrows():
        mes_code = row["MES_Code"]
        mes_name = row["Macro Economic Sector"].replace("\n", " ")

        sect_code = row["Sect_Code"]
        sect_name = row["Sector"].replace("\n", " ")
        ind_code = row["Ind_Code"]
        ind_name = row["Industry"].replace("\n", " ")
        basic_ind_code = row["Basic_Ind_Code"]
        basic_ind_name = row["Basic Industry"].replace("\n", " ")
        details = row["Definition"].replace("\n", " ")

        print("-------------------------------------------")
        print(mes_name, sect_name, ind_name, basic_ind_name)
        print("-------------------------------------------")

        macro_sector, created = MacroSector.objects.get_or_create(
            mes_code=mes_code, name=mes_name
        )
        print(f"{macro_sector} created -> {created}")
        sector, created = Sector.objects.get_or_create(
            sect_code=sect_code, name=sect_name, macro_sector=macro_sector
        )
        print(f"{sector} created -> {created}")
        industry, created = Industry.objects.get_or_create(
            sector=sector, ind_code=ind_code, name=ind_name
        )
        print(f"{industry} created -> {created}")
        basic_industry, created = BasicIndustry.objects.get_or_create(
            industry=industry,
            basic_ind_code=basic_ind_code,
            name=basic_ind_name,
            details=details,
        )
        print(f"{basic_industry} created -> {created}")
