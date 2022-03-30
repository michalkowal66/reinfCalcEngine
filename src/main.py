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
                self.calc_beam()

            elif self.el_type == 'col':
                self.calc_column()

            elif self.el_type == 'foot':
                self.calc_foot()

            elif self.el_type == 'plate':
                self.calc_plate()

    def get_material_properties(self):
        element_code = self.el_type[0]

        element_concrete_class = self.el_data[f'{element_code}_concr_class_combo'].replace('/', '_')
        concrete_properties = properties['concrete_class'][element_concrete_class].value

        element_steel_grade = self.el_data[f'{element_code}_steel_grade_combo']
        steel_properties = properties['steel_grade'][element_steel_grade].value

        return concrete_properties, steel_properties

    def validate_data(self, data_dict):
        pass

    def calc_beam(self):
        # Get material properties
        concrete_prop, steel_prop = self.get_material_properties()

        # Concrete
        f_ck = concrete_prop['fck']
        f_cd = f_ck / 1.4

        # Steel
        f_yd = steel_prop['fyd']
        bar_diam = float(self.el_data['b_bar_diam_combo']) / 10
        stirrup_diam = 0.8

        # Geometry
        h = float(self.el_data['b_height_lineEdit'])
        width = float(self.el_data['b_width_lineEdit'])
        nom_cover = float(self.el_data['b_concr_cover_lineEdit'])

        # Load
        bend_moment = float(self.el_data['b_moment_lineEdit'])

        # Effective width calculation
        d = h - (nom_cover + stirrup_diam + 0.5 * bar_diam)

        # check whether beam section is in support or span area
        if self.el_data['b_sup_section_radioBtn']:
            # Calculations for support section
            mi = bend_moment / (width / 100 * ((d / 100) ** 2) * f_cd * 1000)

            mi_lim = 0.374
            if mi > mi_lim:
                print("Error!")

            alpha_1 = 0.973 - sqrt((0.974 - 1.95 * mi))

            required_area = alpha_1 * width * d * (f_cd / f_yd)

        else:
            # Calculations for span section
            pass

        # Find provided area of reinforcement and amount of bars
        provided_area, provided_bars = self.get_provided_reinforcement(required_area=required_area,
                                                                       bar_diam=bar_diam,
                                                                       stirrup_diam=stirrup_diam,
                                                                       width=width,
                                                                       cover=nom_cover)
        return provided_area, provided_bars, required_area

    def calc_column(self):
        pass

    def calc_foot(self):
        pass

    def calc_plate(self):
        pass

    def get_provided_reinforcement(self, required_area, bar_diam, stirrup_diam, width, cover):
        # Minimum bars required
        min_bars = 2

        # Calculate left width of the element
        width_left = width - 4*cover - 2*stirrup_diam - min_bars*bar_diam

        # Calculate number of additional bars that can fit inside the left width
        add_bars = ceil(width_left/(cover+bar_diam))
        if width_left - add_bars*(cover+bar_diam) >= bar_diam:
            max_bars = min_bars + add_bars
        else:
            max_bars = min_bars + add_bars - 1

        # Find amount of bars needed to fulfill the required reinforcement condition
        for provided_bars in range(min_bars, max_bars+1):
            provided_area = provided_bars * pi * (bar_diam/2)**2
            if provided_area >= required_area:
                return provided_area, provided_bars
        return None, None


if __name__ == '__main__':
    test_path = '../tests/beam_support_example.rcalc'
    rc_element = Element(test_path)
