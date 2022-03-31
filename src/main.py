from json import load
from math import ceil, pi, sqrt
from materialProperties.properties import properties


class Element:
    def __init__(self, path):
        self.path = path
        file_dict = self.load_savefile(self.path)
        self.el_type = file_dict['element'][:-4]
        self.el_data = file_dict['data']
        self.el_info = file_dict['info']

    def load_savefile(self, path):
        with open(path) as data_file:
            data_dict = load(data_file)
            return data_dict

    def calc_reinforcement(self):
        if self.validate_data(self.el_data):
            if self.el_type == 'beam':
                return self.calc_beam()

            elif self.el_type == 'col':
                return self.calc_column()

            elif self.el_type == 'foot':
                return self.calc_foot()

            elif self.el_type == 'plate':
                return self.calc_plate()

    def get_material_properties(self):
        element_code = self.el_type[0]

        element_concrete_class = self.el_data[f'{element_code}_concr_class_combo'].replace('/', '_')
        concrete_properties = properties['concrete_class'][element_concrete_class].value

        element_steel_grade = self.el_data[f'{element_code}_steel_grade_combo']
        steel_properties = properties['steel_grade'][element_steel_grade].value

        return concrete_properties, steel_properties

    def validate_data(self, data_dict):
        # implement function logic later
        return True

    def calc_beam(self):
        # Get material properties
        concrete_prop, steel_prop = self.get_material_properties()

        # Concrete
        f_ck = concrete_prop['fck'] * 1000  # [kPa]
        f_cd = f_ck / 1.4  # [kPa]
        f_ctm = concrete_prop['fctm'] * 1000  # [kPa]

        # Steel
        f_yd = steel_prop['fyd'] * 1000  # [kPa]
        f_yk = steel_prop['fyk'] * 1000  # [kPa]
        bar_diam = float(self.el_data['b_bar_diam_combo']) / 1000  # [m]
        stirrup_diam = 0.008  # [m]

        # Geometry
        height = float(self.el_data['b_height_lineEdit']) / 100  # [m]
        width = float(self.el_data['b_width_lineEdit']) / 100  # [m]
        nom_cover = float(self.el_data['b_concr_cover_lineEdit']) / 100  # [m]

        # Load
        bend_moment = float(self.el_data['b_moment_lineEdit'])  # [kNm]

        # Effective height calculation
        eff_height = height - (nom_cover + stirrup_diam + 0.5 * bar_diam)  # [m]

        # Min. and max. reinforcement area
        min_area = max((0.26 * (f_ctm / f_yk) * width * eff_height), (0.0013 * width * eff_height))  # [m^2]
        max_area = 0.04 * width * height  # [m^2]

        mi_lim = 0.374  # [-]
        # check whether beam section is in support or span area
        if self.el_data['b_sup_section_radioBtn']:
            # Calculations for support section
            mi = bend_moment / (width * (eff_height ** 2) * f_cd)  # [-]

            if mi > mi_lim:
                print("Error!")

            alpha_1 = 0.973 - sqrt((0.974 - 1.95 * mi))  # [-]

            required_area = alpha_1 * width * eff_height * (f_cd / f_yd)  # [m^2]

        else:
            fl_height = float(self.el_data['b_fl_th_lineEdit']) / 100  # [m]
            fl_width = float(self.el_data['b_fl_width_lineEdit']) / 100  # [m]

            # Calculations for span section
            mi = bend_moment / (fl_width * f_cd * (eff_height ** 2))

            if mi > mi_lim:
                print("Error!")

            eta = 1.0

            lbda_x = ((eta - sqrt((eta ** 2) - 2 * eta * mi)) / eta) * eff_height  # [m]

            # Check if the 'T' section is real or apparent
            if lbda_x < fl_height:  # apparent 'T' section
                alpha_1 = eta - sqrt((eta ** 2) - 2 * eta * mi)

                required_area = alpha_1 * fl_width * eff_height * (f_cd / f_yd)  # [m^2]

            else:  # real 'T' section
                bend_moment_1 = fl_height * (fl_width - width) * (eff_height - 0.5 * fl_height) * eta * f_cd  # [kNm]
                bend_moment_2 = bend_moment - bend_moment_1  # [kNm]

                mi = bend_moment_2 / (width * f_cd * eff_height ** 2)

                required_area_1 = bend_moment_1 / ((eff_height - 0.5 * fl_height) * f_yd)  # [m^2]
                required_area_2 = (eta - sqrt((eta ** 2) - 2 * eta * mi)) * width * eff_height * (f_cd / f_yd)  # [m^2]

                required_area = required_area_1 + required_area_2  # [m^2]

        # Find provided area of reinforcement and amount of bars
        provided_area, provided_bars = self.get_provided_reinforcement(required_area=required_area,
                                                                       min_area=min_area,
                                                                       max_area=max_area,
                                                                       bar_diam=bar_diam,
                                                                       stirrup_diam=stirrup_diam,
                                                                       width=width,
                                                                       cover=nom_cover)
        return provided_area, provided_bars, required_area  # [m^2, -, m^2]

    def calc_column(self):
        # Get material properties
        concrete_prop, steel_prop = self.get_material_properties()

        # Concrete
        f_ck = concrete_prop['fck'] * 1000  # [kPa]
        f_cd = f_ck / 1.4  # [kPa]

        # Steel
        f_yd = steel_prop['fyd'] * 1000  # [kPa]
        bar_diam = float(self.el_data['c_bar_diam_combo']) / 1000  # [m]
        stirrup_diam = 0.008  # [m]

        # Geometry
        height = float(self.el_data['c_height_lineEdit']) / 100  # [m],
        width = float(self.el_data['c_width_lineEdit']) / 100  # [m]
        nom_cover = float(self.el_data['c_concr_cover_lineEdit']) / 100  # [m]

        # Load
        bend_moment = float(self.el_data['c_moment_lineEdit'])  # [kNm]
        vert_force = float(self.el_data['c_vertical_lineEdit'])  # [kN]

        eccentricity = max(height / 30, 0.02)
        if bend_moment < vert_force * eccentricity:
            bend_moment = vert_force * eccentricity

        a = (nom_cover + 0.5 * bar_diam + stirrup_diam)
        eff_height = height - a
        delta = a / eff_height

        s = width * eff_height * f_cd

        n_ed = vert_force / s
        m_ed = bend_moment / (s * eff_height)
        m_ed_1 = m_ed + 0.5 * n_ed * (1 - delta)

        alpha_1_2_min = max(0.002 * (1 + delta) * (f_yd / f_cd), 0.1 * n_ed)

        alpha_1_min = 0.5 * alpha_1_2_min
        alpha_2_min = alpha_1_min

        alpha_2 = (m_ed_1 - 0.371) / (1 - delta)
        if alpha_2 >= alpha_2_min:
            alpha_1 = max(0.5 - n_ed + alpha_2, alpha_1_min)

        elif alpha_2 < alpha_2_min:
            alpha_2 = alpha_2_min

            root_expr = 0.947 - 1.95 * m_ed_1
            if root_expr >= 0:
                alpha_1 = max(0.973 - n_ed - sqrt(root_expr), alpha_1_min)
            else:
                alpha_1 = alpha_1_min

        min_area = max((0.1 * vert_force) / f_yd, (0.002 * width * height))  # [m^2]
        max_area = 0.04 * width * height  # [m^2]

        required_area_1 = alpha_1 * (s / f_yd)
        required_area_2 = alpha_2 * (s / f_yd)

        if required_area_1 + required_area_2 >= min_area:
            min_area = 0

        provided_area_1, provided_bars_1 = self.get_provided_reinforcement(required_area=required_area_1,
                                                                           min_area=min_area / 2,
                                                                           max_area=max_area / 2,
                                                                           bar_diam=bar_diam,
                                                                           stirrup_diam=stirrup_diam,
                                                                           width=width,
                                                                           cover=nom_cover)

        provided_area_2, provided_bars_2 = self.get_provided_reinforcement(required_area=required_area_2,
                                                                           min_area=min_area / 2,
                                                                           max_area=max_area / 2,
                                                                           bar_diam=bar_diam,
                                                                           stirrup_diam=stirrup_diam,
                                                                           width=width,
                                                                           cover=nom_cover)

        return provided_area_1, provided_bars_1, provided_area_2, provided_bars_2

    def calc_foot(self):
        pass

    def calc_plate(self):
        # Get material properties
        concrete_prop, steel_prop = self.get_material_properties()

        # Concrete
        f_ck = concrete_prop['fck'] * 1000  # [kPa]
        f_cd = f_ck / 1.4  # [kPa]
        f_ctm = concrete_prop['fctm'] * 1000  # [kPa]

        # Steel
        f_yd = steel_prop['fyd'] * 1000  # [kPa]
        f_yk = steel_prop['fyk'] * 1000  # [kPa]
        bar_diam = float(self.el_data['p_bar_diam_combo']) / 1000  # [m]
        stirrup_diam = 0.008  # [m]

        # Geometry
        height = float(self.el_data['p_th_lineEdit']) / 100  # [m]
        width = 1  # [m]
        nom_cover = float(self.el_data['p_concr_cover_lineEdit']) / 100  # [m]

        # Load
        bend_moment = float(self.el_data['p_moment_lineEdit'])  # [kNm]

        # Effective height calculation
        eff_height = height - (nom_cover + 0.5 * bar_diam)  # [m]

        # Min. and max. reinforcement area
        min_area = max((0.26 * (f_ctm / f_yk) * width * eff_height), (0.0013 * width * eff_height))  # [m^2]
        max_area = 0.04 * width * height  # [m^2]

        mi_lim = 0.374  # [-]

        mi = bend_moment / (width * (eff_height ** 2) * f_cd)  # [-]
        if mi > mi_lim:
            print("Error!")

        alpha_1 = 0.973 - sqrt((0.974 - 1.95 * mi))  # [-]
        required_area = alpha_1 * width * eff_height * (f_cd / f_yd)  # [m^2]

        provided_area, provided_bars = self.get_provided_reinforcement(required_area=required_area,
                                                                       min_area=min_area,
                                                                       max_area=max_area,
                                                                       bar_diam=bar_diam,
                                                                       stirrup_diam=stirrup_diam,
                                                                       width=width,
                                                                       cover=nom_cover)

        return provided_area, provided_bars, required_area  # [m^2, -, m^2]

    def get_provided_reinforcement(self, required_area, min_area, max_area, bar_diam, stirrup_diam, width, cover):
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


if __name__ == '__main__':
    test_path = '../tests/plate_example.rcalc'
    rc_element = Element(test_path)
    print(rc_element.calc_reinforcement())
