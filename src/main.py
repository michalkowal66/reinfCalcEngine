from json import load
from math import ceil, pi
from materialProperties.properties import properties

class Element():
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
        concrete_properties = properties['concrete_class'][self.el_data[f'{element_code}_concr_class_combo'].replace('/', '_')].value
        steel_properties = properties['steel_grade'][self.el_data[f'{element_code}_steel_grade_combo']].value

        return (concrete_properties, steel_properties)

    def validate_data(self, data_dict):
        pass

    def calc_beam(self):
        pass

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
