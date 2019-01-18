
import unittest
from linkbot.utils.misc import *


class TestParseDate(unittest.TestCase):
    def setUp(self):
        self.dt = datetime(1900, 2, 3)

    def test_fmt1(self):
        self.assertEqual(parse_date('02/03'), self.dt)

    def test_fmt2(self):
        self.assertEqual(parse_date('02-03'), self.dt)

    def test_fmt3(self):
        self.assertEqual(parse_date('Feb', '03'), self.dt)

    def test_fmt4(self):
        self.assertEqual(parse_date('February', '03'), self.dt)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            parse_date('notValid')


class TestFileFuncs(unittest.TestCase):
    def setUp(self):
        self.fname = './tmptmptmptmp'
        self.fname_notexists = './tmptmptmpNotExists'
        self.obj = {'abc': 123}

    def tearDown(self):
        if os.path.isfile(self.fname):
            os.remove(self.fname)

    def test_create_config(self):
        create_config(self.fname)
        self.assertTrue(os.path.isfile(self.fname))

    def test_save_json(self):
        s = json.dumps(self.obj)
        save_json(self.fname, self.obj)
        with open(self.fname) as f:
            self.assertEqual(f.read(), s)

    def test_load_json(self):
        s = json.dumps(self.obj)
        with open(self.fname, 'w') as f:
            f.write(s)
        self.assertEqual(load_json(self.fname), self.obj)

    def test_load_json_not_exist(self):
        self.assertEqual(load_json(self.fname_notexists), {})


class TestEnglishListing(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual(english_listing([]), '')

    def test_single_input(self):
        self.assertEqual(english_listing(['one']), 'one')

    def test_two_inputs(self):
        self.assertEqual(english_listing(['one', 'two']), 'one and two')

    def test_three_inputs(self):
        self.assertEqual(english_listing(['1', '2', '3']), '1, 2, and 3')

    def test_many_inputs(self):
        self.assertEqual(english_listing([str(i) for i in range(8)]), '0, 1, 2, 3, 4, 5, 6, and 7')


class TestSplitMessage(unittest.TestCase):

    def _list_equal(self, l1, l2):
        self.assertEqual(len(l1), len(l2))
        for i in range(len(l1)):
            self.assertEqual(l1[i], l2[i], f"on iteration {i}")

    def test_nosplits(self):
        s = "This is a message"
        self._list_equal([s for s in split_message(s)], [s])

    def test_split_on_space(self):
        m = "This is a message"
        self._list_equal([s for s in split_message(m, maxlength=10)], ["This is a", " message"])

    def test_split_no_space(self):
        m = "Thisisamessage"
        self._list_equal([s for s in split_message(m, maxlength=10)], ["Thisisames", "sage"])




