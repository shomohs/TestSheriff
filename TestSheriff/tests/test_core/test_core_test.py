import os, sys
import uuid
import datetime


def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_core_test(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'

    def teardown_method(self, method):
        from core import Base
        Base.Base().get_base()['test'].drop()

    def test_repr_getter_setter(self):
        from core.Test import Test
        from core.Base import time_format
        test_id = str(uuid.uuid4())
        owner = str(uuid.uuid4())
        test_type = str(uuid.uuid4())
        test = Test(test_id, owner, test_type)
        assert '{0}'.format(test) == '<Test {0} ({1}) by {2}>'.format(test_id, test_type, owner)
        assert test.to_dict() == {'test_id': test_id, 'owner': owner, 'type': test_type}
        test._last_seen = datetime.datetime.now()
        assert test.to_dict()['last_seen'] == test._last_seen.strftime(time_format)
        test2 = test.from_dict(test.to_dict())
        assert test2.to_dict() == test.to_dict()

    def test_save(self):
        from core.Test import Test
        from core.Base import Base, time_format
        test_id = str(uuid.uuid4())
        owner = str(uuid.uuid4())
        test_type = str(uuid.uuid4())
        test = Test(test_id, owner, test_type)
        now = datetime.datetime.now()
        res = test.save()
        assert res
        at = Base().get_all('test', {})
        assert len(at) == 1
        assert at[0]['_id'] == test_id
        assert at[0]['owner'] == owner
        assert at[0]['test_id'] == test_id
        assert at[0]['type'] == test_type
        assert at[0]['last_seen'] == now.strftime(time_format)

    def test_get_all(self):
        from core.Test import Test
        test_id1 = str(uuid.uuid4())
        test_id2 = str(uuid.uuid4())
        test_id3 = str(uuid.uuid4())
        owner = str(uuid.uuid4())
        owner2 = str(uuid.uuid4())
        test_type = str(uuid.uuid4())
        Test(test_id1, owner, test_type).save()
        Test(test_id2, owner, test_type).save()
        Test(test_id3, owner2, test_type).save()
        test = Test(owner=owner)
        list = test.get_all()
        assert len(list) == 2

    def test_get_one(self):
        from core.Test import Test
        test_id1 = str(uuid.uuid4())
        test_id2 = str(uuid.uuid4())
        test_id3 = str(uuid.uuid4())
        owner1 = str(uuid.uuid4())
        owner2 = str(uuid.uuid4())
        test_type = str(uuid.uuid4())
        Test(test_id1, owner1, test_type).save()
        Test(test_id2, owner1, test_type).save()
        Test(test_id2, owner2, test_type).save()
        test = Test(test_id=test_id1)
        one = test.get_one()
        assert one is not None
        assert one._test_id == test_id1
        assert one._owner == owner1
        test = Test(test_id=test_id2)
        one = test.get_one()
        assert one._test_id == test_id2
        assert one._owner == owner2
        assert one is not None
        test = Test(test_id=test_id3)
        one = test.get_one()
        assert one is None