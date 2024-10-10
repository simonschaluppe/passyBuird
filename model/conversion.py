import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT_PATH = Path(__file__).parent.parent
sys.path.append(str(Path(__file__).parent.parent))

DATA_PATH = ROOT_PATH / "data"

CONVERSION_FILE = DATA_PATH / "peeco2.xlsx"
PEE_SHEET = "PEE"
CO2_SHEET = "CO2"


class DEFAULT_PROFILES:
    OIB2018_monthly = "OIB2018 (Monatswerte)"
    OIB2018_annually = "OIB2018 (Jahresmittelwert)"
    OIB2019_monthly = "OIB2019 (interpolierte Monatswerte)"
    OIB2019_annually = "OIB2019 (Jahresmittelwert)"
    ElectricityMap2015 = "Electricity Map 2015"
    ElectricityMap2017 = "Electricity Map 2017"
    ElectricityMap2018 = "Electricity Map 2018"


def get_profile(
    file_name,
    sheet_name,
    profile: str,
) -> np.array:
    df = pd.read_excel(file_name, sheet_name=sheet_name)
    if profile not in df.columns:
        raise ValueError(
            "Profile {profile} not found in Conversion File {CONVERSION_FILE} column headers."
        )
    return df[profile].to_numpy()


def get_default_pee_profile(profile: str):
    return get_profile(CONVERSION_FILE, PEE_SHEET, profile)


def get_default_co2_profile(profile: str):
    return get_profile(CONVERSION_FILE, CO2_SHEET, profile)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    test = get_default_co2_profile(DEFAULT_PROFILES.ElectricityMap2017)
    plt.plot(test)
    plt.show()
