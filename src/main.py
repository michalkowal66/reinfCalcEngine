from json import load
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

    def get_provided_reinforcement(self, required_area, fi, fi_s, width, cover):
        pass


if __name__ == '__main__':
    test_path = '../tests/beam_support_example.rcalc'
    rc_element = Element(test_path)
