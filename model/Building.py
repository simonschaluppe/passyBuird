from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")

class Component:
    """
    A representation of a building component of the thermal hull
    """

    def __init__(self, row):
        self.name = row["Bauteil"]
        self.u_value = row["U-Wert"]  # U-Wert [W/m²K]
        self.area = row["Fläche"]  # bezugsfläche (Brutto) [m²]
        self.temp_factor = row[
            "Temperatur-Korrekturfaktor"]  # Korrekturfaktor, der angibt, wieviel prozent des Wärmeflusses vgl zu gg. Außenwand vorliegt [-]

    @property
    def L(self):
        return self.u_value * self.area * self.temp_factor  # = U * A * f_T [W/K]

    def __repr__(self):
        return f"{self.name[:10]:<10}: {self.area:>5.0f} m² @ {self.u_value:>3.2f} W/m²K"


class Building:
    """
    A Model of a building
    """

    def __init__(self, path, u_f=0.9, fensterfl_anteil=0.4):
        print(f"initializing Building object from {path}")
        # your code here...

        self.file = path
        self.df = self.load_params(path)

        self.bgf = self.df.loc["gross_floor_area", "Value"]  # read excel
        self.gf = self.df.loc["plot_size", "Value"]
        self.heat_capacity = self.df.loc["effective_heat_capacity", "Value"]
        self.net_storey_height = self.df.loc["net_storey_height", "Value"]
        self.differential_cost = self.df.loc["differential_cost", "Value"]

        self.hull = self.load_hull(path)  # from excel

        self.components = []
        # Außenwand
        # Dach
        # fenster
        # Bodenplatte
        for i, row in self.hull.iterrows():
            bauteil = Component(row)
            self.components.append(bauteil)

    def load_params(self, path, sheetname="params"):
        """loads the sheet "params" of a excel at path and returns it as a dataframe"""
        df = pd.read_excel(path, sheet_name=sheetname)
        required_columns = {'Unit', 'Value', 'Variable'}
        common = required_columns.intersection(df.columns)
        if common != required_columns:
            raise ValueError(f"{path} sheet params is missing atleast one column names: {required_columns}")
        df.index = df["Variable"]
        return df

    def load_hull(self, path):
        """loads the sheet "thermal_ hull" of a excel at path and returns it as a dataframe"""
        hull = pd.read_excel(path, sheet_name="thermal_hull")
        return hull  # returns a dataframe



    @property
    def LT(self):
        """calculates the LT [W/K/m²BGF] from a Hull Dataframe"""
        # Todo: switch this to use self.components, as each component.L is available
        A_B = self.hull["Fläche"].sum()
        self.hull["L_B"] = self.hull["Fläche"] * self.hull["U-Wert"] * self.hull["Temperatur-Korrekturfaktor"]
        L_B = self.hull.L_B.sum()
        L_PX = max(0, (0.2 * (0.75 - L_B / A_B) * L_B))  # wärmebrücken ZUschlag
        L_T = L_B + L_PX
        return L_T / self.bgf

    def __repr__(self):
        data = 7
        string = f"""Gross floor area:   {self.bgf:>{data}} m²
Net storey height:  {self.net_storey_height:>{data}} m
Eff. Heat capacity: {self.heat_capacity:>{data}} Wh/m²/K
LT:                 {self.LT:>{data}.2f} W/K/m²
"""  # triple quote strings preserve linebreaks and indentation
        for c in self.components:
            string+=str(c)+"\n"

        return string


if __name__ == "__main__":

    #print(Building())
    test = Building(path=Path(DATA_DIR,"building_ph.xlsx"))
    print(test)
    bauteil = test.components[0]
