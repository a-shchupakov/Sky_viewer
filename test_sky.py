import unittest
import datetime
import sys
import os

sys.path.append(os.path.join(sys.path[0], 'modules'))

import star_handler
import coordinates_handler


class TestVectors(unittest.TestCase):
    def test_operations(self):
        vector1 = coordinates_handler.Vector(1, 2, 3)
        vector2 = coordinates_handler.Vector(1, 1, 0)

        self.assertEqual(vector1 + vector2, coordinates_handler.Vector(2, 3, 3))

        self.assertEqual(vector1 * 2, coordinates_handler.Vector(2, 4, 6))

        dot_product = coordinates_handler.Vector.dot_product(vector1, vector2)
        self.assertAlmostEqual(dot_product, 3, delta=1e-4)

        vector3 = coordinates_handler.Vector.cross_product(vector1, vector2)
        self.assertEqual(vector3, coordinates_handler.Vector(-3, 3, -1))

        self.assertAlmostEqual(vector1.get_length(), 3.74165738677, delta=1e-4)

        vector1.normalize()
        self.assertAlmostEqual(vector1.get_length(), 1, 1e-4)

    def test_equals(self):
        vector1 = coordinates_handler.Vector(1, 2, 3)

        self.assertEqual(vector1, vector1)

        self.assertFalse(vector1 == 'abc')

    def test_spherical_to_cartesian(self):
        vector = coordinates_handler.spherical_to_cartesian(45, 45, radius=1)

        all(self.assertAlmostEqual(i, j, delta=1e-4) for i, j in [(vector.x, 0.500),
                                                                  (vector.y, 0.500),
                                                                  (vector.z, 0.7071)])


class TestQuaternions(unittest.TestCase):
    def test_operations(self):
        quaternion1 = coordinates_handler.Quaternion(coordinates_handler.Vector(1, 1, 1), 5)
        quaternion2 = coordinates_handler.Quaternion(coordinates_handler.Vector(1, 1, 0), 3)

        self.assertEqual(quaternion1 + quaternion2,
                         coordinates_handler.Quaternion(coordinates_handler.Vector(2, 2, 1), 8))

        quaternion1_reversed = quaternion1.reversed()
        res = quaternion1 * quaternion1_reversed
        res.normalize()
        self.assertEqual(res, coordinates_handler.Quaternion(coordinates_handler.Vector(0, 0, 0), 1))

    def test_rotation(self):
        basic_vector = coordinates_handler.Vector(1, 0, 0)

        rotate_to = coordinates_handler.Vector(0, 0, 1)
        rotate_to.normalize()

        quaternion = coordinates_handler.Quaternion.get_quaternion(basic_vector, rotate_to)
        rotated_vector = quaternion.rotate_vector(basic_vector)

        rotated_vector.normalize()
        self.assertEqual(rotated_vector, rotate_to)

    def test_equals(self):
        quaternion1 = coordinates_handler.Quaternion(coordinates_handler.Vector(1, 1, 1), 5)

        self.assertEqual(quaternion1, quaternion1)

        self.assertFalse(quaternion1 == 'abc')


class TestAdditionalToolsInCoordinates(unittest.TestCase):
    def test_degrees_and_radians_transform(self):
        degrees = 71
        test_rad = coordinates_handler.degrees_to_radians(degrees)
        self.assertAlmostEqual(test_rad, 1.239183, delta=1e-4)

        radians = 2.193132
        test_deg = coordinates_handler.radians_to_degrees(radians)
        self.assertAlmostEqual(test_deg, 125.657, delta=1e-1)

    @staticmethod
    def extract_format(object_, format_):
        if format_ == 'dms':
            string = '{}:{}:{}'.format(object_.degrees, object_.minutes, round(object_.seconds, ndigits=1))
            if object_.sign == -1:
                string = '-' + string
            return string
        if format_ == 'hms':
            string = '{}:{}:{}'.format(object_.hours, object_.minutes, round(object_.seconds, ndigits=1))
            return string

    def test_degrees_to_dms(self):
        deg1 = -42.9765
        deg2 = 0.0

        obj1 = coordinates_handler.AngleMeasuresDMS()
        obj1.decimal = deg1
        obj1.fill_dms_with_decimal()
        res1 = TestAdditionalToolsInCoordinates.extract_format(obj1, 'dms')

        obj2 = coordinates_handler.AngleMeasuresDMS()
        obj2.decimal = deg2
        obj2.fill_dms_with_decimal()
        res2 = TestAdditionalToolsInCoordinates.extract_format(obj2, 'dms')

        expected1 = '-42:58:35.4'
        expected2 = '0:0:0.0'

        self.assertEqual(res1, expected1)
        self.assertEqual(res2, expected2)

    def test_dms_to_degrees(self):
        obj1 = coordinates_handler.AngleMeasuresDMS()
        obj1.sign = 1
        obj1.degrees = 31
        obj1.minutes = 24
        obj1.seconds = 12.5

        obj1.fill_decimal_with_dms()
        res1 = obj1.decimal
        expected = 31.40347

        self.assertAlmostEqual(res1, expected, delta=1e-4)

    def test_degrees_to_hms(self):
        deg = 141.3833
        obj = coordinates_handler.AngleMeasuresHMS()
        obj.decimal = deg
        obj.fill_hms_with_decimal()

        res = TestAdditionalToolsInCoordinates.extract_format(obj, 'hms')
        expected = '9:25:32.0'

        self.assertEqual(res, expected)

    def test_hms_to_degrees(self):
        obj = coordinates_handler.AngleMeasuresHMS()
        obj.hours = 21
        obj.minutes = 56
        obj.seconds = 42

        obj.fill_decimal_with_hms()
        res = obj.decimal
        expected = 329.1750

        self.assertAlmostEqual(res, expected, delta=1e-3)

    def test_parsing_with_decimal(self):
        dms = coordinates_handler.AngleMeasuresDMS()
        dms.parse_coordinates('-12.25', decimal=True)

        is_not_dms_filled = (dms.sign is None
                             or dms.degrees is None
                             or dms.minutes is None
                             or dms.seconds is None
                             or dms.decimal is None)

        self.assertFalse(is_not_dms_filled)

        hms = coordinates_handler.AngleMeasuresHMS()
        hms.parse_coordinates('24.75', decimal=True)

        is_not_hms_filled = (hms.hours is None
                             or hms.minutes is None
                             or hms.seconds is None
                             or hms.decimal is None)

        self.assertFalse(is_not_hms_filled)

    def test_parsing_with_dms(self):
        dms = coordinates_handler.AngleMeasuresDMS()
        dms.parse_coordinates('-13:45:21', decimal=False)

        is_not_dms_filled = (dms.sign is None
                             or dms.degrees is None
                             or dms.minutes is None
                             or dms.seconds is None
                             or dms.decimal is None)

        self.assertFalse(is_not_dms_filled)

    def test_parsing_with_hms(self):
        hms = coordinates_handler.AngleMeasuresHMS()
        hms.parse_coordinates('3:45:21', decimal=False)

        is_not_hms_filled = (hms.hours is None
                             or hms.minutes is None
                             or hms.seconds is None
                             or hms.decimal is None)

        self.assertFalse(is_not_hms_filled)

    def test_observer_sidereal_time(self):
        observer = coordinates_handler.Observer()
        observer.set_date(datetime.datetime(1998, 8, 10, 23, 10, 0))
        observer.set_decimal_coordinates('25', '-1.9166667')
        observer.calibrate_sidereal_time()
        sidereal = observer.local_sidereal_time

        self.assertAlmostEqual(304.80762, sidereal, delta=1e-4)

    def test_observer_view_vector(self):
        vector = '1, 2, 3'
        observer = coordinates_handler.Observer()
        observer.set_view_vector(vector)
        vector = observer.view_vector

        self.assertTrue(isinstance(vector, coordinates_handler.Vector))
        self.assertEqual('X: 1.0, Y: 2.0, Z: 3.0', 'X: {}, Y: {}, Z: {}'.format(vector.x, vector.y, vector.z))

    def test_observer_coordinates(self):
        observer = coordinates_handler.Observer()
        observer.set_geo_dms_coordinates('25:65:15', '-10:12:42')

        result = all(isinstance(i, coordinates_handler.AngleMeasuresDMS) for i in [observer.lat, observer.long])
        self.assertTrue(result)

        self.assertAlmostEqual(26.0875, observer.lat.decimal, delta=1e-4)
        self.assertAlmostEqual(-10.21167, observer.long.decimal, delta=1e-4)


star1 = ' 35 23:39: 8.3 +50:28:18 111.34 -10.77    2.30   O9V                -0.017 -0.002       +009 222304  18    '
star2 = ' 37  2:13:36.3 +51: 3:57 135.85 -09.73 W  5.8    M8III:             +0.346 -0.171   111 +027  13530        '
bad_star = '5 G8III:    B9V 51: 3:57 135.85 -09.73 W  5 37  2:13:             -10.77    5.300        '


class TestToolsInStarHandler(unittest.TestCase):
    def setUp(self):
        self.observer = coordinates_handler.Observer()
        self.observer.set_date(datetime.datetime(1998, 8, 10, 23, 10, 0))
        self.observer.set_decimal_coordinates('25', '-1.9166667')
        self.observer.set_view_vector('1, 1, 1')
        self.observer.calibrate_sidereal_time()

    def test_julian_date(self):
        date = datetime.datetime(1921, 1, 5, 12, 25, 0, 0)
        julian_date = star_handler.get_julian_date(date)
        self.assertAlmostEqual(julian_date, 2422695.01736, delta=1e-4)

    def test_days_passed_since(self):
        date1 = datetime.datetime(2017, 5, 19, 12, 0, 0, 0)
        date2 = datetime.datetime(2017, 5, 1, 12, 0, 0, 0)
        day_offset = star_handler.days_passed_from_date(date1, date2=date2)
        self.assertEqual(day_offset, 18)

        date3 = datetime.datetime(2017, 5, 1, 17, 25, 0, 0)
        day_offset_since_j2000 = star_handler.days_passed_from_date(date3)
        self.assertAlmostEqual(day_offset_since_j2000, 6330.225694, delta=1e-3)

    def test_star_parser(self):
        with self.assertRaises(ValueError):
            stars = [star_handler.Star(info, self.observer) for info in [star1, star2, bad_star]]

    def test_star_color(self):
        star1_, star2_ = [star_handler.Star(info, self.observer) for info in [star1, star2]]
        color1 = '#C2FEFC'
        color2 = '#FD9C89'

        self.assertEqual(star1_.get_star_color(), color1)
        self.assertEqual(star2_.get_star_color(), color2)

    def test_star_radius(self):
        star1_, star2_ = [star_handler.Star(info, self.observer) for info in [star1, star2]]
        size1 = 3.5
        size2 = 5.5

        self.assertEqual(star1_.get_star_radius(), size1)
        self.assertEqual(star2_.get_star_radius(), size2)

    def test_rotation_done(self):
        stars = [star_handler.Star(info, self.observer) for info in [star1, star2]]
        quaternion = coordinates_handler.Quaternion.get_quaternion(self.observer.view_vector,
                                                                   coordinates_handler.Vector(0, 0, 1))

        self.assertTrue(all(isinstance(x.rotated_vector, type(None)) for x in stars))

        star_handler.rotate_vectors(stars, quaternion)

        self.assertTrue(all(isinstance(x.rotated_vector, coordinates_handler.Vector) for x in stars))


if __name__ == '__main__':
    unittest.main()
