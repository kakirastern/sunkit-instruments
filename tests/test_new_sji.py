# -*- coding: utf-8 -*-
# """Tests for functions in sji.py"""
import datetime

import pytest
import numpy as np
from astropy import units as u
from ndcube.utils.wcs import WCS
from ndcube.tests.helpers import assert_cubes_equal

from irispy import iris_tools
from irispy.new_sji import IRISMapCube, IRISMapCubeSequence

# Sample data for tests
data = np.array([[[1, 2, 3, 4], [2, 4, 5, 3], [0, 1, 2, 3]],
                 [[2, 4, 5, 1], [10, 5, 2, 2], [10, 3, 3, 0]]])
data_2D = np.array([[1, 2, 3, 4], [2, 4, 5, 3]])
data_1D = np.array([1, 2])
data_4D = np.array([[[[1, 2, 3, 4], [2, 4, 5, 3], [0, 1, 2, 3]],
                     [[2, 4, 5, 1], [10, 5, 2, 2], [10, 3, 3, 0]]],
                    [[[1, 2, 3, 4], [2, 4, 5, 3], [0, 1, 2, 3]],
                     [[2, 4, 5, 1], [10, 5, 2, 2], [10, 3, 3, 0]]]])

header = {'CTYPE1': 'HPLN-TAN', 'CUNIT1': 'arcsec', 'CDELT1': 0.4,
          'CRPIX1': 0, 'CRVAL1': 0, 'NAXIS1': 4,
          'CTYPE2': 'HPLT-TAN', 'CUNIT2': 'arcsec', 'CDELT2': 0.5,
          'CRPIX2': 0, 'CRVAL2': 0, 'NAXIS2': 3,
          'CTYPE3': 'Time    ', 'CUNIT3': 'seconds', 'CDELT3': 0.3,
          'CRPIX3': 0, 'CRVAL3': 0, 'NAXIS3': 2}
wcs = WCS(header=header, naxis=3)
header_2D = {'CTYPE1': 'Time    ', 'CUNIT1': 'seconds', 'CDELT1': 0.4,
             'CRPIX1': 0, 'CRVAL1': 0, 'NAXIS1': 4,
             'CTYPE2': 'HPLT-TAN', 'CUNIT2': 'arcsec', 'CDELT2': 0.5,
             'CRPIX2': 0, 'CRVAL2': 0, 'NAXIS2': 2}
wcs_2D = WCS(header=header_2D, naxis=2)
header_4D = {'CTYPE1': 'Time    ', 'CUNIT1': 'seconds', 'CDELT1': 0.4,
             'CRPIX1': 0, 'CRVAL1': 0, 'NAXIS1': 4,
             'CTYPE2': 'HPLT-TAN', 'CUNIT2': 'arcsec', 'CDELT2': 0.5,
             'CRPIX2': 0, 'CRVAL2': 0, 'NAXIS2': 3,
             'CTYPE3': 'Time    ', 'CUNIT3': 'seconds', 'CDELT3': 0.4,
             'CRPIX3': 0, 'CRVAL3': 0, 'NAXIS3': 2,
             'CTYPE4': 'HPLN-TAN', 'CUNIT4': 'arcsec', 'CDELT4': 0.5,
             'CRPIX4': 0, 'CRVAL4': 0, 'NAXIS4': 2}
wcs_4D = WCS(header=header_4D, naxis=4)
header_1D = {'CTYPE1': 'Time    ', 'CUNIT1': 'seconds', 'CDELT1': 0.4,
             'CRPIX1': 0, 'CRVAL1': 0, 'NAXIS1': 2}
wcs_1D = WCS(header=header_1D, naxis=1)

unit = iris_tools.DN_UNIT["SJI"]

mask_cube = data >= 0
mask_4D = data_4D >= 0

uncertainty = [1]

times = np.array([datetime.datetime(2014, 12, 11, 19, 39, 0, 480000),
                  datetime.datetime(2014, 12, 11, 19, 43, 7, 600000)])

exposure_times = 2*np.ones((2), float)
extra_coords = [('TIME', 0, times),
                ('EXPOSURE TIME', 0, exposure_times)]

scaled_T = True
scaled_F = False

cube = IRISMapCube(data, wcs, uncertainty=uncertainty, mask=mask_cube, unit=unit,
                   extra_coords=extra_coords, scaled=scaled_T)
cube_2D = IRISMapCube(data_2D, wcs_2D, uncertainty=uncertainty, mask=mask_cube, unit=unit,
                      extra_coords=extra_coords, scaled=scaled_T, missing_axis=[False, False, True])
cube_1D = IRISMapCube(data_1D, wcs_1D, uncertainty=uncertainty, mask=mask_cube, unit=unit,
                      extra_coords=extra_coords, scaled=scaled_T, missing_axis=[False, True, True])
cube_F = IRISMapCube(data, wcs, uncertainty=uncertainty, mask=mask_cube, unit=unit,
                     extra_coords=extra_coords, scaled=scaled_F)
cube_4D = IRISMapCube(data_4D, wcs_4D, uncertainty=uncertainty, mask=mask_4D, unit=unit,
                      extra_coords=extra_coords, scaled=scaled_T)

# Sample of data for IRISMapCubeSequence tests:

meta_1 = {"OBSID":1}
meta_2 = {"OBSID":2}

cube_seq= IRISMapCube(data, wcs, uncertainty=uncertainty, mask=mask_cube, unit=unit,
                      meta=meta_1, extra_coords=extra_coords, scaled=scaled_T)
cube_seq_2= IRISMapCube(data, wcs, uncertainty=uncertainty, mask=mask_cube, unit=unit,
                        meta=meta_2, extra_coords=extra_coords, scaled=scaled_T)

sequence = IRISMapCubeSequence(data_list=[cube_seq, cube_seq], meta=meta_1, common_axis=0)

# Tests for IRISMapCube
@pytest.mark.parametrize("test_input,expected", [
    (cube, data/exposure_times[0]),
    (cube_2D, data_2D/exposure_times[0]),
    (cube_1D, data_1D/exposure_times[0])])
def test_apply_exposure_time_correction(test_input, expected):
    np.testing.assert_array_equal(
        test_input.apply_exposure_time_correction().data, expected)

@pytest.mark.parametrize("test_input,expected", [
    (cube, data*exposure_times[0])])
def test_apply_exposure_time_correction_undo(test_input, expected):
    np.testing.assert_array_equal(
        test_input.apply_exposure_time_correction(undo=True, force=True).data, expected)

@pytest.mark.parametrize("test_input", [
    (ValueError, cube_F),
    (ValueError, cube_4D)])
def test_crop_by_coords_error(test_input):
    with pytest.raises(test_input[0]):
        test_input[1].apply_exposure_time_correction()

# Tests for IRISMapCubeSequence
@pytest.mark.parametrize("test_input,expected", [
    (sequence, [4, 3, 4]*u.pix)])
def test_dimensions(test_input, expected):
    assert np.any(test_input.dimensions == expected)

@pytest.mark.parametrize("test_input,expected", [
    (sequence, ("time", "custom:pos.helioprojective.lat", "custom:pos.helioprojective.lon"))])
def test_world_axis_physical_types(test_input, expected):
    assert test_input.world_axis_physical_types == expected

@pytest.mark.parametrize("test_input,undo,force,expected", [
    (sequence, False, False, (np.array([data/2, data/2]), np.array([data/2/2, data/2/2]))),
    (sequence, True, True, (np.array([data*2, data*2]), np.array([data*2*2, data*2*2])))])
def test_IRISMapCubeSequence_apply_exposure_time_correction(test_input, undo, force, expected):
    output_sequence = test_input.apply_exposure_time_correction(undo=undo, copy=True, force=force)
    output_data_array = np.array([output_sequence.data[0].data, output_sequence.data[1].data])
    np.testing.assert_array_equal(output_data_array, expected[0])
    output_sequence.apply_exposure_time_correction(undo=undo, force=True)
    output_data_array = np.array([output_sequence.data[0].data, output_sequence.data[1].data])
    np.testing.assert_array_equal(output_data_array, expected[1])

@pytest.mark.parametrize("test_input, cubes", [
    (ValueError, (cube_seq, cube_seq_2))])
def test_IRISMapCubeSequence_initializaton(test_input, cubes):
    with pytest.raises(test_input):
        IRISMapCubeSequence(data_list=[cubes[0], cubes[1]], meta=meta_1, common_axis=0)
