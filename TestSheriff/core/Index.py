import datetime

from . import Base
from .TestType import TestType

class Index:
    collection = 'test_index'
    _test_type = 'type'
    _field = 'field'
    _values = 'values'

    def __init__(self, test_type=None, field=None, values=None):
        self._test_type = test_type
        self._field = field
        self._values = values

    def __repr__(self):
        return '<Index {0} ({1}) : {2} values>'.format(self._field, self._test_type, len(self._values) if self._values is not None else 0)

    def to_dict(self):
        dict_of_self = {}
        if self._test_type is not None:
            dict_of_self[Index._test_type] = self._test_type
        if self._field is not None:
            dict_of_self[Index._field] = self._field
        if self._values is not None:
            dict_of_self[Index._values] = self._values
        return dict_of_self

    @staticmethod
    def from_dict(index_dict):
        index = Index()
        if Index._test_type in index_dict:
            index._test_type = index_dict[Index._test_type]
        if Index._field in index_dict:
            index._field = index_dict[Index._field]
        if Index._values in index_dict:
            index._values = index_dict[Index._values]
        return index

    @staticmethod
    def index(status):
        if status._details is not None:
            test_type = TestType(test_type=status._type).get_one()
            if test_type._doc_fields_to_index is not None:
                fields = [key for key in status._details if key in test_type._doc_fields_to_index]
                for field in fields:
                    current_index = Index(test_type=test_type._test_type, field=field, values=[])
                    index_existing = current_index.get()
                    if index_existing is not None:
                        current_index = index_existing
                    if status._details[field] not in current_index._values:
                        current_index._values.append(status._details[field])
                        current_index.save()

    def get(self):
        query_filter = self.to_dict()
        if Index._values in query_filter:
            query_filter.pop(Index._values)
        res = Base.Base().get_one(self.collection, query_filter)
        return Index.from_dict(res) if res is not None else None

    def get_all(self, additional_filter=None):
        query_filter = self.to_dict()
        if additional_filter is not None:
            query_filter.update(additional_filter)
        cursor = Base.Base().get_all(self.collection, query_filter)
        cursor._transform = lambda bi: Index.from_dict(bi)
        return cursor

    def save(self):
        index_id = "{0}-{1}".format(self._test_type, self._field)
        Base.Base().upsert_by_id(self.collection, index_id, self.to_dict())
