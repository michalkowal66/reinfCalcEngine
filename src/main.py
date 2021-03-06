from json import load
from math import ceil, pi, sqrt
from materialProperties.properties import properties
from jsonschema import validate
from jsonschema.exceptions import ValidationError


class Element:
    """
    Parent element class of the engine used to initialise the task calculation

    Attributes
    ----------
    None
    """
    def __init__(self, task_parameters_dict):
        """
        Initialize information about the task such as type of the element, and its scheme. Validate information with
        the appropriate schema.

        Parameters
        ----------
        task_parameters_dict : dict
            Dictionary containing parameters of the task

        Returns
        -------
        None
        """
        self.data_dict = task_parameters_dict

        self.element_type = self.data_dict['element'][:-4]
        self.element_code = self.element_type[0]
        self.parameters = self.data_dict['data']

        self.validation_schema = self.load_schema()
        self.valid = self.validate_data(data_dict=self.data_dict, validation_schema=self.validation_schema)

    def get_material_properties(self):
        """
        Return the material properties for the task from the materialProperties module

        Parameters
        ----------
        None

        Returns
        -------
        dict, dict
        """
        element_concrete_class = self.parameters[f'{self.element_code}_concr_class_combo'].replace('/', '_')
        concrete_properties = properties['concrete_class'][element_concrete_class].value

        element_steel_grade = self.parameters[f'{self.element_code}_steel_grade_combo']
        if element_steel_grade == '20G2VY':
            element_steel_grade = 'A_20G2VY'
        steel_properties = properties['steel_grade'][element_steel_grade].value

        return concrete_properties, steel_properties

    def validate_data(self, data_dict, validation_schema):
        """
        Validate the data dictionary with the appropriate schema using jsonschema module

        Parameters
        ----------
        data_dict : dict
            Dictionary containing parameters of the task
        validation_schema : dict
            Dictionary containing JSON schema for selected element type

        Returns
        -------
        bool
        """
        try:
            validate(instance=data_dict, schema=validation_schema)
        except ValidationError:
            return False
        else:
            return True

    def get_plate_reinforcement(self, required_area, min_area, max_area, bar_diam, cover):
        """
        Return provided reinforcement area and its spacing for plates, on the basis of specified requirements.

        Parameters
        ----------
        required_area : float
            Required area of the reinforcement
        min_area : float
            Minimum area of the reinforcement
        max_area : float
            Maximum area of the reinforcement
        bar_diam : float
            Desired diameter of the rebar
        cover : float
            Concrete cover

        Returns
        -------
        float/None, float/None
        """
        # List containing typical bar axial spacing for plate reinforcement
        axial_spacings = [0.3, 0.25, 0.22, 0.2, 0.19, 0.18, 0.17, 0.15, 0.15,
                          0.14, 0.13, 0.125, 0.12, 0.11, 0.1, 0.08, 0.05]

        bar_area = pi * (bar_diam / 2) ** 2

        # Find spacing of bars needed to fulfill the required reinforcement conditions
        for provided_spacing in axial_spacings:
            if provided_spacing > bar_diam + cover:
                provided_area = (1 / provided_spacing) * bar_area
                if provided_area >= required_area and min_area <= provided_area <= max_area:
                    return provided_area, provided_spacing
        return None, None

    def get_beam_reinforcement(self, required_area, min_area, max_area, bar_diam, stirrup_diam, width, cover):
        """
        Return provided reinforcement area and amount of bars, on the basis of specified requirements.

        Parameters
        ----------
        required_area : float
            Required area of the reinforcement
        min_area : float
            Minimum area of the reinforcement
        max_area : float
            Maximum area of the reinforcement
        bar_diam : float
            Desired diameter of the rebar
        stirrup_diam : float
            Desired diameter of the stirrups
        width : float
            Width of the element
        cover : float
            Concrete cover

        Returns
        -------
        float/None, float/None
        """
        # Minimum bars required
        min_bars = 2

        # Calculate left width of the element
        width_left = width - 4 * cover - 2 * stirrup_diam - min_bars * bar_diam

        # Calculate number of additional bars that can fit inside the left width
        add_bars = ceil(width_left / (cover + bar_diam))
        if width_left - add_bars * (cover + bar_diam) >= bar_diam:
            max_bars = min_bars + add_bars
        else:
            max_bars = min_bars + add_bars - 1
        # Find amount of bars needed to fulfill the required reinforcement condition
        for provided_bars in range(min_bars, max_bars + 1):
            provided_area = provided_bars * pi * (bar_diam / 2) ** 2
            if provided_area >= required_area and min_area <= provided_area <= max_area:
                return provided_area, provided_bars
        return None, None

    def get_nominal_cover(self):
        """
        Return recommended nominal concrete cover and remarks from the course of calculation process

        Parameters
        ----------
        None

        Returns
        -------
        float/None, list
        """
        remarks = []
        exposure_class = self.parameters[f'{self.element_code}_exp_combo']
        concrete_class = self.parameters[f'{self.element_code}_concr_class_combo']

        exposure_class_paroperties = properties['exp_class'][exposure_class].value
        recommended_concerete_class = exposure_class_paroperties['concrete_class']
        if int(concrete_class[1:3]) < int(recommended_concerete_class[1:3]):
            remarks.append(
                f"For exposure class {exposure_class} the minimum recommended concrete class is {recommended_concerete_class.replace('_', '/')}")

        # Assumed recommended class of the structure according to EC2
        structure_class = 4
        if exposure_class in ['X0', 'XC1', 'XC2', 'XC3', 'XD3', 'XS2', 'XS3']:
            if int(concrete_class[1:3]) >= 30:
                structure_class -= 1
        elif exposure_class in ['XC4', 'XD1', 'XD2', 'XS1']:
            if int(concrete_class[1:3]) >= 40:
                structure_class -= 1
        if self.element_code == 'p':
            structure_class -= 1

        # Minimum cover due to the durability requirement
        c_min_dur = exposure_class_paroperties[f"S{structure_class}"]
        if c_min_dur is None:
            remarks.append(f"Not able to calculate nominal cover for exposure class {exposure_class}.")
            return None, remarks
        # Minimum cover due to the bond requirement (assuming dg <= 32mm)
        c_min_b = int(self.parameters[f'{self.element_code}_bar_diam_combo'])

        c_min = 40 if self.element_code == 'f' else max(c_min_dur, c_min_b, 10)
        c_dev = 10

        recommended_c_nom = c_min + c_dev

        c_nom = self.parameters[f'{self.element_code}_concr_cover_lineEdit']
        if c_nom != recommended_c_nom:
            remarks.append(f"Recommended nominal concrete cover value is {recommended_c_nom} mm.")
        else:
            remarks.append(f"Nominal concrete cover correct.")

        return recommended_c_nom / 1000, remarks

    def load_schema(self):
        """
        Return dictionary containing schema, load from schemas directory, for data structure verification.

        Parameters
        ----------
        None

        Returns
        -------
        dict
        """
        schema_path = f'json_schema/{self.element_type}_schema.json'
        with open(schema_path, 'r') as json_schema_file:
            return load(json_schema_file)


class Plate(Element):
    """
    Plate element class, used for calculations for plates

    Attributes
    ----------
    None
    """
    def __init__(self, path):
        """
        Extend Parent's __init__ method. Initialize detailed information about the task (geometry, loads).

        Parameters
        ----------
        path : str
            Path to the file

        Returns
        -------
        None
        """
        super().__init__(path)
        self.height = self.parameters['p_th_lineEdit']
        self.nom_cover = self.parameters['p_concr_cover_lineEdit']
        self.bar_diam = float(self.parameters['p_bar_diam_combo'])
        self.bend_moment = self.parameters['p_moment_lineEdit']

    def calc_reinforcement(self):
        """
        Return the results of calculations for a selected element on the basis of the prepared algorithm.

        Initialize the result variables and a remarks list. Follow the calculation algorithm to calculate
        the required area, provided area, and provided spacing of the reinforcement. Add remarks about the
        calculation progress to the remarks list. Return a dictionary containing results and parameters dictionaries.
        Dictionary results contains only essential information about the calculations (only results) in the form of
        a dictionary, whereas parameters contains a dictionary obtained using locals method, to include detailed
        information about the calculation process.

        Parameters
        ----------
        None

        Returns
        -------
        float/None, float/None, float/None
        """
        remarks = []
        required_area, provided_area, provided_spacing = None, None, None

        if not self.valid:
            remarks.append("The file is not valid.")

        else:
            remarks.append("The file is valid, starting calculations...")

            # Get material properties
            concrete_properties, steel_properties = self.get_material_properties()

            # Concrete
            f_ck = concrete_properties['fck'] * 1000  # [kPa]
            f_cd = f_ck / 1.4  # [kPa]
            f_ctm = concrete_properties['fctm'] * 1000  # [kPa]

            # Steel
            f_yd = steel_properties['fyd'] * 1000  # [kPa]
            f_yk = steel_properties['fyk'] * 1000  # [kPa]
            bar_diam = self.bar_diam / 1000  # [m]

            # Geometry
            height = self.height / 100  # [m]
            width = 1  # [m]
            nom_cover = self.nom_cover / 100  # [m]

            # Check nominal cover
            recommended_nom_cover, nom_cover_remarks = self.get_nominal_cover()
            remarks.append(*nom_cover_remarks)

            # Load
            bend_moment = self.bend_moment  # [kNm]

            # Effective height calculation
            eff_height = height - (nom_cover + 0.5 * bar_diam)  # [m]

            # Min. and max. reinforcement area
            min_area = max((0.26 * (f_ctm / f_yk) * width * eff_height), (0.0013 * width * eff_height))  # [m^2]
            max_area = 0.04 * width * height  # [m^2]

            mu_lim = 0.374  # [-]

            mu = bend_moment / (width * (eff_height ** 2) * f_cd)  # [-]
            if mu > mu_lim:
                remarks.append("Mu value too high!")
                mu_correct = False
            else:
                mu_correct = True
                remarks.append("Mu value correct.")

                alpha_1 = 0.973 - sqrt((0.974 - 1.95 * mu))  # [-]

                required_area = max(alpha_1 * width * eff_height * (f_cd / f_yd), min_area)  # [m^2]

                provided_area, provided_spacing = self.get_plate_reinforcement(required_area=required_area,
                                                                               min_area=min_area,
                                                                               max_area=max_area,
                                                                               bar_diam=bar_diam,
                                                                               cover=nom_cover)

        remarks.append("Calculations finished.")

        variables = locals()
        variables['self'] = self.__str__()

        calculation_results = {
            'provided_area': [provided_area],
            'provided_reinforcement': [provided_spacing],
            'required_area': [required_area],
            'remarks': remarks,
        }

        return {
            'results': calculation_results,
            'parameters': variables
        }

    def __str__(self):
        return f"Plate, {self.height}cm thick"


class Beam(Element):
    """
    Beam element class, used for calculations for beams

    Attributes
    ----------
    None
    """
    def __init__(self, path):
        """
        Extend Parent's __init__ method. Initialize detailed information about the task (geometry, loads).

        Parameters
        ----------
        path : str
            Path to the file

        Returns
        -------
        None
        """
        super().__init__(path)

        self.height = self.parameters['b_height_lineEdit']
        self.width = self.parameters['b_width_lineEdit']
        self.nom_cover = self.parameters['b_concr_cover_lineEdit']
        self.bar_diam = float(self.parameters['b_bar_diam_combo'])
        self.bend_moment = self.parameters['b_moment_lineEdit']

        self.is_support_section = self.parameters['b_sup_section_radioBtn']
        if not self.is_support_section:
            self.fl_height = self.parameters['b_fl_th_lineEdit']
            self.fl_width = self.parameters['b_fl_width_lineEdit']

    def calc_reinforcement(self):
        """
        Return the results of calculations for a selected element on the basis of the prepared algorithm.

        Initialize the result variables and a remarks list. Follow the calculation algorithm to calculate
        the required area, provided area, and provided bars of the reinforcement. Add remarks about the
        calculation progress to the remarks list. Return a dictionary containing results and parameters dictionaries.
        Dictionary results contains only essential information about the calculations (only results) in the form of
        a dictionary, whereas parameters contains a dictionary obtained using locals method, to include detailed
        information about the calculation process.

        Parameters
        ----------
        None

        Returns
        -------
        float/None, float/None, float/None
        """
        remarks = []
        required_area, provided_area, provided_bars = None, None, None
        mu2_correct = True

        if not self.valid:
            remarks.append("The file is not valid.")

        else:
            remarks.append("The file is valid, starting calculations...")

            # Get material properties
            concrete_properties, steel_properties = self.get_material_properties()

            # Concrete
            f_ck = concrete_properties['fck'] * 1000  # [kPa]
            f_cd = f_ck / 1.4  # [kPa]
            f_ctm = concrete_properties['fctm'] * 1000  # [kPa]

            # Steel
            f_yd = steel_properties['fyd'] * 1000  # [kPa]
            f_yk = steel_properties['fyk'] * 1000  # [kPa]
            bar_diam = self.bar_diam / 1000  # [m]
            stirrup_diam = 0.008  # [m]

            # Geometry
            height = self.height / 100  # [m]
            width = self.width / 100  # [m]
            nom_cover = self.nom_cover / 100  # [m]
            support_section = self.is_support_section

            # Check nominal cover
            recommended_nom_cover, nom_cover_remarks = self.get_nominal_cover()
            remarks.append(*nom_cover_remarks)

            # Load
            bend_moment = self.bend_moment  # [kNm]

            # Effective height calculation
            eff_height = height - (nom_cover + stirrup_diam + 0.5 * bar_diam)  # [m]

            # Min. and max. reinforcement area
            min_area = max((0.26 * (f_ctm / f_yk) * width * eff_height), (0.0013 * width * eff_height))  # [m^2]
            max_area = 0.04 * width * height  # [m^2]

            mu_lim = 0.374  # [-]

            # check whether beam section is in support or span area
            if support_section:
                # Calculations for support section
                mu = bend_moment / (width * (eff_height ** 2) * f_cd)  # [-]

                if mu > mu_lim:
                    remarks.append("Mu value too high!")
                    mu_correct = False

                else:
                    remarks.append("Mu value correct.")
                    mu_correct = True

                    alpha_1 = 0.973 - sqrt((0.974 - 1.95 * mu))  # [-]

                    required_area = max(alpha_1 * width * eff_height * (f_cd / f_yd), min_area)  # [m^2]

            else:
                fl_height = self.fl_height / 100  # [m]
                fl_width = self.fl_width / 100  # [m]

                # Calculations for span section
                mu = bend_moment / (fl_width * f_cd * (eff_height ** 2))

                if mu > mu_lim:
                    remarks.append("Mu value too high!")
                    mu_correct = False

                else:
                    remarks.append("Mu value correct.")
                    mu_correct = True
                    eta = 1.0

                    lbda_x = ((eta - sqrt((eta ** 2) - 2 * eta * mu)) / eta) * eff_height  # [m]

                    # Check if the 'T' section is real or apparent
                    if lbda_x < fl_height:  # apparent 'T' section
                        remarks.append("Section is an apparent T section.")
                        section_real = False

                        alpha_1 = eta - sqrt((eta ** 2) - 2 * eta * mu)

                        required_area = max(alpha_1 * fl_width * eff_height * (f_cd / f_yd), min_area)  # [m^2]

                    else:  # real 'T' section
                        remarks.append("Section is a real T section.")
                        section_real = True

                        bend_moment_1 = fl_height * (fl_width - width) * (
                                    eff_height - 0.5 * fl_height) * eta * f_cd  # [kNm]
                        bend_moment_2 = bend_moment - bend_moment_1  # [kNm]

                        mu_2 = bend_moment_2 / (width * f_cd * eff_height ** 2)
                        if mu_2 > mu_lim:
                            remarks.append("Mu value after recalculation too high!")
                            mu2_correct = False

                        else:
                            required_area_1 = bend_moment_1 / ((eff_height - 0.5 * fl_height) * f_yd)  # [m^2]
                            required_area_2 = (eta - sqrt((eta ** 2) - 2 * eta * mu)) * width * eff_height * (
                                        f_cd / f_yd)  # [m^2]

                            required_area = max(required_area_1 + required_area_2, min_area)  # [m^2]

            if mu_correct and mu2_correct:
                # Find provided area of reinforcement and amount of bars
                provided_area, provided_bars = self.get_beam_reinforcement(required_area=required_area,
                                                                           min_area=min_area,
                                                                           max_area=max_area,
                                                                           bar_diam=bar_diam,
                                                                           stirrup_diam=stirrup_diam,
                                                                           width=width,
                                                                           cover=nom_cover)

        remarks.append("Calculations finished.")

        variables = locals()
        variables['self'] = self.__str__()

        calculation_results = {
            'provided_area': [provided_area],
            'provided_reinforcement': [provided_bars],
            'required_area': [required_area],
            'remarks': remarks,
        }

        return {
            'results': calculation_results,
            'parameters': variables
        }

    def __str__(self):
        return f"Beam, {self.height}cm x {self.width}cm"


class Column(Element):
    """
    Column element class, used for calculations for columns

    Attributes
    ----------
    None
    """
    def __init__(self, path):
        """
        Extend Parent's __init__ method. Initialize detailed information about the task (geometry, loads).

        Parameters
        ----------
        path : str
            Path to the file

        Returns
        -------
        None
        """
        super().__init__(path)

        self.height = self.parameters['c_height_lineEdit']
        self.width = self.parameters['c_width_lineEdit']
        self.nom_cover = self.parameters['c_concr_cover_lineEdit']
        self.bar_diam = float(self.parameters['c_bar_diam_combo'])

        self.bend_moment = self.parameters['c_moment_lineEdit']
        self.vert_force = self.parameters['c_vertical_lineEdit']

    def calc_reinforcement(self):
        """
        Return the results of calculations for a selected element on the basis of the prepared algorithm.

        Initialize the result variables and a remarks list. Follow the calculation algorithm to calculate
        the required area, provided area, and provided bars of the reinforcement. Add remarks about the
        calculation progress to the remarks list. Return a dictionary containing results and parameters dictionaries.
        Dictionary results contains only essential information about the calculations (only results) in the form of
        a dictionary, whereas parameters contains a dictionary obtained using locals method, to include detailed
        information about the calculation process.

        Parameters
        ----------
        None

        Returns
        -------
        float/None, float/None, float/None
        """
        remarks = []
        required_area_1, required_area_2 = None, None
        provided_area_1, provided_bars_1 = None, None
        provided_area_2, provided_bars_2 = None, None

        if not self.valid:
            remarks.append("The file is not valid.")

        else:
            remarks.append("The file is valid, starting calculations...")

            # Get material properties
            concrete_properties, steel_properties = self.get_material_properties()

            # Concrete
            f_ck = concrete_properties['fck'] * 1000  # [kPa]
            f_cd = f_ck / 1.4  # [kPa]

            # Steel
            f_yd = steel_properties['fyd'] * 1000  # [kPa]
            bar_diam = self.bar_diam / 1000  # [m]
            stirrup_diam = 0.008  # [m]

            # Geometry
            height = self.height / 100  # [m],
            width = self.width / 100  # [m]
            nom_cover = self.nom_cover / 100  # [m]

            # Check nominal cover
            recommended_nom_cover, nom_cover_remarks = self.get_nominal_cover()
            remarks.append(*nom_cover_remarks)

            # Load
            bend_moment = self.bend_moment  # [kNm]
            vert_force = self.vert_force  # [kN]

            eccentricity = max(height / 30, 0.02)
            if bend_moment < vert_force * eccentricity:
                remarks.append("Modifying bending moment value.")
                moment_modified = True
                bend_moment = vert_force * eccentricity  # [kNm]
            else:
                remarks.append("No need to modify bending moment value.")
                moment_modified = False

            a = (nom_cover + 0.5 * bar_diam + stirrup_diam)  # [m]
            eff_height = height - a  # [m]
            delta = a / eff_height

            s = width * eff_height * f_cd  # [kN]

            n_ed = vert_force / s
            m_ed = bend_moment / (s * eff_height)
            m_ed_1 = m_ed + 0.5 * n_ed * (1 - delta)

            alpha_1_2_min = max(0.002 * (1 + delta) * (f_yd / f_cd), 0.1 * n_ed)

            alpha_1_min = 0.5 * alpha_1_2_min
            alpha_2_min = alpha_1_min

            alpha_2 = (m_ed_1 - 0.371) / (1 - delta)
            if alpha_2 >= alpha_2_min:
                alpha_2_ge = True
                alpha_1 = max(0.5 - n_ed + alpha_2, alpha_1_min)

            elif alpha_2 < alpha_2_min:
                alpha_2_ge = False
                alpha_2 = alpha_2_min

                root_expr = 0.947 - 1.95 * m_ed_1
                if root_expr >= 0:
                    alpha_1 = max(0.973 - n_ed - sqrt(root_expr), alpha_1_min)
                else:
                    alpha_1 = alpha_1_min

            remarks.append("Alpha values calculated.")

            min_area = max((0.1 * vert_force) / f_yd, (0.002 * width * height))  # [m^2]
            max_area = 0.04 * width * height  # [m^2]

            required_area_1 = alpha_1 * (s / f_yd)  # [m^2]
            required_area_2 = alpha_2 * (s / f_yd)  # [m^2]

            if required_area_1 + required_area_2 < min_area:
                if required_area_1 < min_area / 2 and required_area_2 < min_area / 2:
                    required_area_1 = min_area / 2
                    required_area_2 = min_area / 2
                elif required_area_1 >= min_area / 2:
                    required_area_2 = min_area - required_area_1
                elif required_area_2 >= min_area / 2:
                    required_area_1 = min_area - required_area_2

            provided_area_1, provided_bars_1 = self.get_beam_reinforcement(required_area=required_area_1,
                                                                           min_area=min_area / 2,
                                                                           max_area=max_area / 2,
                                                                           bar_diam=bar_diam,
                                                                           stirrup_diam=stirrup_diam,
                                                                           width=width,
                                                                           cover=nom_cover)

            provided_area_2, provided_bars_2 = self.get_beam_reinforcement(required_area=required_area_2,
                                                                           min_area=min_area / 2,
                                                                           max_area=max_area / 2,
                                                                           bar_diam=bar_diam,
                                                                           stirrup_diam=stirrup_diam,
                                                                           width=width,
                                                                           cover=nom_cover)

        remarks.append("Calculations finished.")

        variables = locals()
        variables['self'] = self.__str__()

        calculation_results = {
            'provided_area': [provided_area_1, provided_area_2],
            'provided_reinforcement': [provided_bars_1, provided_bars_2],
            'required_area': [required_area_1, required_area_2],
            'remarks': remarks,
        }

        return {
            'results': calculation_results,
            'parameters': variables
        }

    def __str__(self):
        return f"Column, {self.height}cm x {self.width}cm"


class Foot(Element):
    """
    Foot element class, used for calculations for foot foundations

    Attributes
    ----------
    None
    """
    def __init__(self, path):
        """
        Extend Parent's __init__ method. Initialize detailed information about the task (geometry, loads).

        Parameters
        ----------
        path : str
            Path to the file

        Returns
        -------
        None
        """
        super().__init__(path)

        self.height = self.parameters['f_fheight_lineEdit']
        self.width = self.parameters['f_fwidth_lineEdit']
        self.length = self.parameters['f_flength_lineEdit']
        self.nom_cover = self.parameters['f_concr_cover_lineEdit']
        self.c_height = self.parameters['f_cheight_lineEdit']
        self.c_width = self.parameters['f_cwidth_lineEdit']

        self.bar_diam = float(self.parameters['f_bar_diam_combo'])
        self.col_bar_diam = float(self.parameters['f_col_bar_diam_combo'])

        self.vert_force = self.parameters['f_vert_lineEdit']

    def get_a_coefficient(self, dependent_val):
        """
        Return a coefficient value for the purpose of punching verification using prepared formulas

        Parameters
        ----------
        dependent_val : float
            Dependant used to determine the a coefficient value

        Returns
        -------
        float
        """
        if dependent_val <= 5:
            return 0.2
        elif 5 < dependent_val <= 35:
            return - 3.4604e-4 * dependent_val ** 2 + 4.0508e-2 * dependent_val + 6.1094e-3
        elif 35 <= dependent_val <= 50:
            return 6.9861e-6 * dependent_val ** 3 - 1.0796e-3 * dependent_val ** 2 + 6.6182e-2 * dependent_val - 2.9342e-1
        elif 50 < dependent_val <= 100:
            return 2.5424e-8 * dependent_val ** 3 - 3.5481e-5 * dependent_val ** 2 + 1.3977e-2 * dependent_val + 5.7667e-1
        elif 100 < dependent_val <= 150:
            return 9.9559e-8 * dependent_val ** 3 - 5.7721e-5 * dependent_val ** 2 + 1.6201e-2 * dependent_val + 5.0253e-1
        elif 150 < dependent_val <= 300:
            return 2.3680e-8 * dependent_val ** 3 - 2.3576e-5 * dependent_val ** 2 + 1.1079e-2 * dependent_val + 7.5862e-1
        elif 300 < dependent_val <= 500:
            return - 1e-71 * dependent_val ** 3 - 2.2634e-6 * dependent_val ** 2 + 4.6857e-3 * dependent_val + 1.3980

    def calc_reinforcement(self):
        """
        Return the results of calculations for a selected element on the basis of the prepared algorithm.

        Initialize the result variables and a remarks list. Follow the calculation algorithm to calculate
        the required area, provided area, and provided spacing of the reinforcement. Add remarks about the
        calculation progress to the remarks list. Perform calculations for punching verification.
        Return a dictionary containing results and parameters dictionaries. Dictionary results contains only essential
        information about the calculations (only results) in the form of a dictionary, whereas parameters contains
        a dictionary obtained using locals method, to include detailed information about the calculation process.

        Parameters
        ----------
        None

        Returns
        -------
        float/None, float/None, float/None
        """
        remarks = []
        required_area, provided_area, provided_spacing = None, None, None

        if not self.valid:
            remarks.append("The file is not valid.")

        else:
            remarks.append("The file is valid, starting calculations...")

            # Get material properties
            concrete_properties, steel_properties = self.get_material_properties()

            # Concrete
            f_ck = concrete_properties['fck'] * 1000  # [kPa]
            f_cd = f_ck / 1.4  # [kPa]
            f_ctk = concrete_properties['fctk_0.05'] * 1000  # [kPa]
            f_ctd = f_ctk / 1.4  # [kPa]

            # Steel
            f_yd = steel_properties['fyd'] * 1000  # [kPa]
            bar_diam = self.bar_diam / 1000  # [m]
            col_bar_diam = self.col_bar_diam / 1000  # [m]

            # Geometry
            height = self.height / 100  # [m]
            width = self.width / 100  # [m]
            length = self.length / 100  # [m]
            nom_cover = self.nom_cover / 100  # [m]
            c_height = self.c_height / 100  # [m]
            c_width = self.c_width / 100  # [m]

            # Check nominal cover
            recommended_nom_cover, nom_cover_remarks = self.get_nominal_cover()
            remarks.append(*nom_cover_remarks)

            # Load
            vert_force = self.vert_force  # [kN]

            f_bd = 2.25 * f_ctd  # [kPa]
            required_anchorage = (col_bar_diam / 4) * (f_yd / f_bd)  # [m]
            min_anchorage = max(0.6 * required_anchorage, 10 * col_bar_diam, 0.1)  # [m]
            assumed_anchorage = max(min_anchorage, ceil(required_anchorage * 100) / 100)  # [m]

            nu_rd_max = 0.4 * 0.6 * (1 - (f_ck / 250000)) * f_cd  # [kPa]

            # Internal column
            beta = 1.15

            # Column's perimeter
            u0 = 2 * (c_height + c_width)  # [m]

            # Minimum height and cover
            h_min = (beta * vert_force) / (nu_rd_max * u0)  # [m]
            h_cover = assumed_anchorage + 1.5 * bar_diam  # [m]

            if height < h_min or height < h_cover:
                remarks.append("Incorrect height of the element.")
                height_correct = False

            else:
                remarks.append("Height of the element correct.")
                height_correct = True
                area = width * length  # [m^2]

                # Stress calculation
                sigma = vert_force / area  # [kPa]

                eff_length = (width - c_width) / 2 + 0.15 * c_width  # [m]
                bend_moment = sigma * length * ((eff_length ** 2) / 2)  # [kNm]

                # Effective height calculation
                eff_height = height - nom_cover - 1.5 * bar_diam  # [m]

                # Arm of internal forces
                z = 0.9 * eff_height  # [m]

                # Min. and max. reinforcement area
                area_coefficient = concrete_properties['area_coefficient']
                min_area = area_coefficient * length * eff_height  # [m^2]
                max_area = 0.04 * length * height  # [m^2]

                total_required_area = max(bend_moment / (z * f_yd), min_area)  # [m^2]
                required_area = total_required_area / length  # [m^2]

                provided_area_per_rm, provided_spacing = self.get_plate_reinforcement(required_area=required_area,
                                                                                      min_area=min_area / length,
                                                                                      max_area=max_area / length,
                                                                                      bar_diam=bar_diam,
                                                                                      cover=nom_cover)

                provided_area = provided_area_per_rm * length  # [m^2]

            if all([provided_area, provided_spacing]):
                remarks.append("Punching verification.")
                # Punching verification
                nu_ed = vert_force / (u0 * eff_height)  # [kPa]

                if nu_ed > nu_rd_max:
                    nu_ed_correct = False
                    remarks.append("EC requirement not fulfilled, nu_ed value too high.")

                else:
                    nu_ed_correct = True
                    remarks.append("EC requirement fulfilled, nu_ed value correct.")

                    a_dependant = vert_force / (sigma * c_width * c_height)
                    a_coeff = round(self.get_a_coefficient(a_dependant), 2)

                    a = a_coeff * c_width  # [m]

                    rho_l = provided_area / (length * eff_height)
                    k = min(1 + sqrt(200 / (eff_height * 1000)), 2)
                    nu_min = 0.035 * (k ** (1.5)) * sqrt(f_ck * 1000)  # [kPa]

                    nu_rd = max(0.128 * k * ((100 * rho_l * f_ck) ** (1 / 3)), nu_min) * 2 * eff_height / a  # [kPa]

                    u = 2 * c_width + 2 * c_height + 2 * pi * a  # [m]

                    vert_force_red = vert_force - sigma * (
                                c_width * c_height + 2 * a * (c_width + c_height) + pi * a ** 2)  # [kN]
                    nu_ed_red = vert_force_red / (u * eff_height)  # [kPa]

                    if nu_ed_red > nu_rd:
                        nu_ed_red_correct = False
                        remarks.append("EC requirement not fulfilled, nu_ed_red value too high.")
                    else:
                        nu_ed_red_correct = True
                        remarks.append("EC requirement fulfilled, nu_ed_red value correct.")

        remarks.append("Calculations finished.")

        variables = locals()
        variables['self'] = self.__str__()

        calculation_results = {
            'provided_area': [provided_area],
            'provided_reinforcement': [provided_spacing],
            'required_area': [total_required_area],
            'remarks': remarks,
        }

        return {
            'results': calculation_results,
            'parameters': variables
        }

    def __str__(self):
        return f"Foundation Foot, {self.length}cm x {self.width}cm, {self.height}cm high"


dispatcher = {
    'plate': Plate,
    'beam': Beam,
    'column': Column,
    'foot': Foot,
}
"""dict: Dictionary used to automatically assign proper element class based on element type
"""

if __name__ == '__main__':
    path = '../examples/foot_example.rcalc'
    with open(path) as json_dict:
        element_parameters = load(json_dict)
    ElementClass = dispatcher[element_parameters['element'][:-4]]
    rc_element = ElementClass(element_parameters)
    print(rc_element.valid)
    results = rc_element.calc_reinforcement()
    print(results)
