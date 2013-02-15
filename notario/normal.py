from notario.utils import ndict, is_nested_tuple


class BaseNormalize(object):

    def __init__(self, data, schema):
        self.raw_data = data
        self.raw_schema = schema

    def ordered_dict(self, data_structure, use_n_dict=False):
        if use_n_dict:
            ordered = ndict()
        else:
            ordered = {}
        for number, value in enumerate(data_structure):
            ordered[number] = value
        return ordered


class Data(BaseNormalize):

    def _normalize(self, data_structure, sort=True):
        if sort:
            for k, v in data_structure.items():
                if isinstance(v, dict):
                    data_structure[k] = self._normalize(v)
            data_structure = sorted(data_structure.items())
        return self.ordered_dict(data_structure, use_n_dict=True)

    def normalized(self):
        """
        Normalizes the ``raw_data`` (a plain dictionary) and returns an ordered
        dictionary, with integers as keys for tuples.
        """
        normalized_data = self._normalize(self.raw_data)
        return normalized_data


class Schema(BaseNormalize):

    def _normalize(self, data):
        if len(data) == 2 and isinstance(data[1], tuple) or len(data) > 2:
            if not isinstance(data[0], tuple):
                new_struct = ndict({0: (data[0], self._normalize(data[1]))})
            else:
                new_struct = self.ordered_dict(data, use_n_dict=True)
            for i in range(len(new_struct)):
                value = new_struct.get(i)
                if is_nested_tuple(value):
                    new_struct[i] = (value[0], self._normalize(value[1]))
            if hasattr(data, 'must_validate'):
                new_struct.must_validate = data.must_validate
            return new_struct
        else:
            new_struct = ndict({0: data})
            if hasattr(data, 'must_validate'):
                new_struct.must_validate = data.must_validate
            return new_struct

    def normalized(self):
        normalized_data = self._normalize(self.raw_schema)
        return normalized_data
