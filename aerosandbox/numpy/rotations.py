from aerosandbox.numpy import sin, cos
from aerosandbox.numpy.array import array
import numpy as _onp
from typing import Union, List


def rotation_matrix_2D(
        angle,
        as_array: bool = True,
):
    """
    Gives the 2D rotation matrix associated with a counterclockwise rotation about an angle.
    Args:
        angle: Angle by which to rotate. Given in radians.
        as_array: Determines whether to return an array-like or just a simple list of lists.

    Returns: The 2D rotation matrix

    """
    s = sin(angle)
    c = cos(angle)
    rot = [
        [c, -s],
        [s, c]
    ]
    if as_array:
        return array(rot)
    else:
        return rot


def rotation_matrix_3D(
        angle: Union[float, _onp.ndarray],
        axis: Union[_onp.ndarray, List, str],
        as_array: bool = True,
        axis_already_normalized: bool = False
):
    """
    Gives the 3D rotation matrix from an angle and an axis.
    An implementation of https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle
    :param angle: can be one angle or a vector (1d ndarray) of angles. Given in radians. # TODO note deprecated functionality; must be scalar
        Direction corresponds to the right-hand rule.
    :param axis: a 1d numpy array of length 3 (x,y,z). Represents the angle.
    :param axis_already_normalized: boolean, skips normalization for speed if you flag this true.
    :return:
        * If angle is a scalar, returns a 3x3 rotation matrix.
        * If angle is a vector, returns a 3x3xN rotation matrix.
    """
    s = sin(angle)
    c = cos(angle)

    if isinstance(axis, str):
        if axis.lower() == "x":
            rot = [
                [1, 0, 0],
                [0, c, -s],
                [0, s, c]
            ]
        elif axis.lower() == "y":
            rot = [
                [c, 0, s],
                [0, 1, 0],
                [-s, 0, c]
            ]
        elif axis.lower() == "z":
            rot = [
                [c, -s, 0],
                [s, c, 0],
                [0, 0, 1]
            ]
        else:
            raise ValueError("If `axis` is a string, it must be `x`, `y`, or `z`.")
    else:
        ux, uy, uz = axis

        if not axis_already_normalized:
            norm = (ux ** 2 + uy ** 2 + uz ** 2) ** 0.5
            ux = ux / norm
            uy = uy / norm
            uz = uz / norm

        rot = [
            [c + ux ** 2 * (1 - c), ux * uy * (1 - c) - uz * s, ux * uz * (1 - c) + uy * s],
            [uy * ux * (1 - c) + uz * s, c + uy ** 2 * (1 - c), uy * uz * (1 - c) - ux * s],
            [uz * ux * (1 - c) - uy * s, uz * uy * (1 - c) + ux * s, c + uz ** 2 * (1 - c)]
        ]

    if as_array:
        return array(rot)
    else:
        return rot
