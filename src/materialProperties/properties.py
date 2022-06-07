from enum import Enum


class ExpClass(Enum):
    """Enum Class containing concrete exposure classes

    exposure classes are stored as class attributes referring to dictionaries with related values and remarks
    in accordance to PN-EN 1992-1-1:2008/NA: 2010

    Each attribute holds fixed number of keys that represent values of concrete properties:

    - exp_class: exposure class,
    - concrete_class: minimum concrete class that may be used with given exposure class,
    - max_wc: maximum water/cement ration
    - min_cem: minimum content of cement [kg/m^3]
    - remarks: remarks about exposure class
    - S1-6: minimum concrete cover in [mm] for selected Strcutre class
    """
    X0 = {"exp_class": "X0", "concrete_class": "C12/15", "max_wc": None, "min_cem": None,
          "remarks": "No corrosion risk", "S1": 10, "S2": 10, "S3": 10, "S4": 10, "S5": 15, "S6": 20}
    XC1 = {"exp_class": "XC1", "concrete_class": "C20/25", "max_wc": 0.65, "min_cem": 260,
           "remarks": "Corrosion due to carbonation hazard", "S1": 10, "S2": 10, "S3": 10, "S4": 15, "S5": 20, "S6": 25}
    XC2 = {"exp_class": "XC2", "concrete_class": "C25/30", "max_wc": 0.6, "min_cem": 280,
           "remarks": "Corrosion due to carbonation hazard", "S1": 10, "S2": 15, "S3": 20, "S4": 25, "S5": 30, "S6": 35}
    XC3 = {"exp_class": "XC3", "concrete_class": "C30/37", "max_wc": 0.55, "min_cem": 280,
           "remarks": "Corrosion due to carbonation hazard", "S1": 10, "S2": 15, "S3": 20, "S4": 25, "S5": 30, "S6": 35}
    XC4 = {"exp_class": "XC4", "concrete_class": "C30/37", "max_wc": 0.5, "min_cem": 300,
           "remarks": "Corrosion due to carbonation hazard", "S1": 15, "S2": 20, "S3": 25, "S4": 30, "S5": 35, "S6": 40}
    XD1 = {"exp_class": "XD1", "concrete_class": "C30/37", "max_wc": 0.55, "min_cem": 300,
           "remarks": "Corrosion due to chlorides hazard", "S1": 20, "S2": 25, "S3": 30, "S4": 35, "S5": 40, "S6": 45}
    XD2 = {"exp_class": "XD2", "concrete_class": "C30/37", "max_wc": 0.55, "min_cem": 300,
           "remarks": "Corrosion due to chlorides hazard", "S1": 25, "S2": 30, "S3": 35, "S4": 40, "S5": 45, "S6": 50}
    XD3 = {"exp_class": "XD3", "concrete_class": "C35/45", "max_wc": 0.45, "min_cem": 320,
           "remarks": "Corrosion due to chlorides hazard", "S1": 30, "S2": 35, "S3": 40, "S4": 45, "S5": 50, "S6": 55}
    XS1 = {"exp_class": "XS1", "concrete_class": "C30/37", "max_wc": 0.5, "min_cem": 300,
           "remarks": "Corrosion due to sea water chlorides hazard", "S1": 20, "S2": 25, "S3": 30, "S4": 35, "S5": 40, "S6": 45}
    XS2 = {"exp_class": "XS2", "concrete_class": "C35/45", "max_wc": 0.45, "min_cem": 320,
           "remarks": "Corrosion due to sea water chlorides hazard", "S1": 25, "S2": 30, "S3": 35, "S4": 40, "S5": 45, "S6": 50}
    XS3 = {"exp_class": "XS3", "concrete_class": "C35/45", "max_wc": 0.45, "min_cem": 340,
           "remarks": "Corrosion due to sea water chlorides hazard", "S1": 30, "S2": 35, "S3": 40, "S4": 45, "S5": 50, "S6": 55}
    XF1 = {"exp_class": "XF1", "concrete_class": "C30/37", "max_wc": 0.55, "min_cem": 300,
           "remarks": "Freeze and thaw hazard", "S1": None, "S2": None, "S3": None, "S4": None, "S5": None, "S6": None}
    XF2 = {"exp_class": "XF2", "concrete_class": "C25/30", "max_wc": 0.55, "min_cem": 300,
           "remarks": "Freeze and thaw hazard", "S1": None, "S2": None, "S3": None, "S4": None, "S5": None, "S6": None}
    XF3 = {"exp_class": "XF3", "concrete_class": "C30/37", "max_wc": 0.5, "min_cem": 320,
           "remarks": "Freeze and thaw hazard", "S1": None, "S2": None, "S3": None, "S4": None, "S5": None, "S6": None}
    XF4 = {"exp_class": "XF4", "concrete_class": "C30/37", "max_wc": 0.45, "min_cem": 340,
           "remarks": "Freeze and thaw hazard", "S1": None, "S2": None, "S3": None, "S4": None, "S5": None, "S6": None}
    XA1 = {"exp_class": "XA1", "concrete_class": "C30/37", "max_wc": 0.55, "min_cem": 300,
           "remarks": "Chemical hazard", "S1": None, "S2": None, "S3": None, "S4": None, "S5": None, "S6": None}
    XA2 = {"exp_class": "XA2", "concrete_class": "C30/37", "max_wc": 0.5, "min_cem": 320,
           "remarks": "Chemical hazard", "S1": None, "S2": None, "S3": None, "S4": None, "S5": None, "S6": None}
    XA3 = {"exp_class": "XA3", "concrete_class": "C35/45", "max_wc": 0.45, "min_cem": 360,
           "remarks": "Chemical hazard", "S1": None, "S2": None, "S3": None, "S4": None, "S5": None, "S6": None}


class ConcreteClass(Enum):
    """ Enum Class containing concrete classes

    Concrete classes are stored as class attributes referring to classes' characteristic values
    in accordance to PN-EN 1992-1-1:2008/NA: 2010

    Each attribute holds fixed number of keys that represent values of concrete properties:

    - concrete_class: concrete class,
    - fck: characteristic compressive strength of cylinder sample [MPa],
    - fck_cube: characteristic compressive strength of cube sample [MPa],
    - fcm: mean compressive strength of cylinder sample [MPa],
    - fctm: mean tensile strength [MPa],
    - fctk_0.05: 5% fractile tensile strength [MPa],
    - fctk_0.95: 95% fractile tensile strength [MPa],
    - Ecm: Elastic modulus [GPa]
    - area_coefficient: Coefficient for min. reinforcement area
     """
    C12_15 = {"concrete_class": "C12/15", "fck": 12, "fck_cube": 15, "fcm": 20, "fctm": 1.6, "fctk_0.05": 1.1,
              "fctk_0.95": 2.0, "Ecm": 27, "area_coefficient": 0.0013}
    C16_20 = {"concrete_class": "C16/20", "fck": 16, "fck_cube": 20, "fcm": 24, "fctm": 1.9, "fctk_0.05": 1.3,
              "fctk_0.95": 2.5, "Ecm": 29, "area_coefficient": 0.0013}
    C20_25 = {"concrete_class": "C20/25", "fck": 20, "fck_cube": 25, "fcm": 28, "fctm": 2.2, "fctk_0.05": 1.5,
              "fctk_0.95": 2.9, "Ecm": 30, "area_coefficient": 0.0013}
    C25_30 = {"concrete_class": "C25/30", "fck": 25, "fck_cube": 30, "fcm": 33, "fctm": 2.6, "fctk_0.05": 1.8,
              "fctk_0.95": 3.3, "Ecm": 31, "area_coefficient": 0.00135}
    C30_37 = {"concrete_class": "C30/37", "fck": 30, "fck_cube": 37, "fcm": 38, "fctm": 2.9, "fctk_0.05": 2.0,
              "fctk_0.95": 3.8, "Ecm": 33, "area_coefficient": 0.0015}
    C35_45 = {"concrete_class": "C35/45", "fck": 35, "fck_cube": 45, "fcm": 43, "fctm": 3.2, "fctk_0.05": 2.2,
              "fctk_0.95": 4.2, "Ecm": 34, "area_coefficient": 0.00165}
    C40_50 = {"concrete_class": "C40/50", "fck": 40, "fck_cube": 50, "fcm": 48, "fctm": 3.5, "fctk_0.05": 2.5,
              "fctk_0.95": 4.6, "Ecm": 35, "area_coefficient": 0.0018}
    C45_55 = {"concrete_class": "C45/55", "fck": 45, "fck_cube": 55, "fcm": 53, "fctm": 3.8, "fctk_0.05": 2.7,
              "fctk_0.95": 4.9, "Ecm": 36, "area_coefficient": 0.00195}
    C50_60 = {"concrete_class": "C50/60", "fck": 50, "fck_cube": 60, "fcm": 58, "fctm": 4.1, "fctk_0.05": 2.9,
              "fctk_0.95": 5.3, "Ecm": 37, "area_coefficient": 0.0021}


class RebarGrade(Enum):
    """ Enum Class containing steel classes

    Steel classes are stored as class attributes referring to classes' characteristic values
    in accordance to PN-B-03264:2002

    Each attribute holds fixed number of keys that represent values of concrete properties:

    - steel_grade: steel grade,
    - fyd: design yield strength of steel grade
    """
    A_20G2VY = {
        "steel_grade": "20G2VY", "fyd": 420, "fyk": 490
    }
    RB500 = {
        "steel_grade": "RB500", "fyd": 420, "fyk": 500
    }
    RB500W = {
        "steel_grade": "RB500W", "fyd": 420, "fyk": 500
    }


properties = {
    "exp_class": ExpClass,
    "concrete_class": ConcreteClass,
    "steel_grade": RebarGrade,
}
"""dict: Dictionary with material property classes
"""

diameters = [*[n for n in range(6, 24, 2)], 25, 28, 30, 32, 35, 38, 40]
"""list: List of popular rebar diameters
"""

translate = {
    "exp_class": "Exposure class",
    "concrete_class": "Concrete class",
    "max_wc": "Maximum water/cement ratio",
    "min_cem": "Minimum cement content [kg/m^3]",
    "remarks": "Remarks about class",
    "concrete_class": "Concrete class",
    "fck": "Characteristic compressive strength of cylinder sample [MPa]",
    "fck_cube": "Characteristic compressive strength of cube sample [MPa]",
    "fcm": "Mean compressive strength of cylinder sample [MPa]",
    "fctm": "Mean tensile strength [MPa]",
    "fctk_0.05": "5% fractile tensile strength [MPa]",
    "fctk_0.95": "95% fractile tensile strength [MPa]",
    "Ecm": "Elastic modulus [GPa]",
    "steel_grade": "Steel grade",
    "fyd": "Design yield strength [MPa]",
    "fyk": "Characteristic yield strength [MPa]",
    "area_coefficient": "Area coefficient",
}
"""dict: Dictionary with elaborated keys of property classes
"""