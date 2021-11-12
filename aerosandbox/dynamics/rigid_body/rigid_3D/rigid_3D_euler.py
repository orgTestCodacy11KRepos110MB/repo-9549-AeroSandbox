from aerosandbox.dynamics.common import _DynamicsBaseClass
import aerosandbox.numpy as np
from aerosandbox import OperatingPoint, Atmosphere, MassProperties
from typing import Union


class DynamicsRigid3DEuler(_DynamicsBaseClass):
    """
    Dynamics instance.
    
        State variables:
            x_e: x-position, in Earth axes. [meters]
            y_e: y-position, in Earth axes. [meters]
            z_e: z-position, in Earth axes. [meters]
            u_b: x-velocity, in body axes. [m/s]
            v_b: y-velocity, in body axes. [m/s]
            w_b: z-velocity, in body axes. [m/s]
            phi: roll angle. Uses yaw-pitch-roll Euler angle convention. [rad]
            theta: pitch angle. Uses yaw-pitch-roll Euler angle convention. [rad]
            psi: yaw angle. Uses yaw-pitch-roll Euler angle convention. [rad]
            p: x-angular-velocity, in body axes. [rad/sec]
            q: y-angular-velocity, in body axes. [rad/sec]
            r: z-angular-velocity, in body axes. [rad/sec]
        
        Control variables:
            Fx_b: Force along the body-x axis. [N]
            Fy_b: Force along the body-y axis. [N]
            Fz_b: Force along the body-z axis. [N]
            Mx_b: Moment about the body-x axis. [Nm]
            My_b: Moment about the body-y axis. [Nm]
            Mz_b: Moment about the body-z axis. [Nm]
            hx_b: Angular momentum (e.g., propellers) about the body-x axis. [kg*m^2/sec]
            hy_b: Angular momentum (e.g., propellers) about the body-y axis. [kg*m^2/sec]
            hz_b: Angular momentum (e.g., propellers) about the body-z axis. [kg*m^2/sec]

    """

    def __init__(self,
                 mass_props: MassProperties = None,
                 x_e: Union[np.ndarray, float] = 0,
                 y_e: Union[np.ndarray, float] = 0,
                 z_e: Union[np.ndarray, float] = 0,
                 u_b: Union[np.ndarray, float] = 0,
                 v_b: Union[np.ndarray, float] = 0,
                 w_b: Union[np.ndarray, float] = 0,
                 phi: Union[np.ndarray, float] = 0,
                 theta: Union[np.ndarray, float] = 0,
                 psi: Union[np.ndarray, float] = 0,
                 p: Union[np.ndarray, float] = 0,
                 q: Union[np.ndarray, float] = 0,
                 r: Union[np.ndarray, float] = 0,
                 ):

        # Assign parameters to attributes
        self.mass_props = MassProperties() if mass_props is None else mass_props
        self.x_e = x_e
        self.y_e = y_e
        self.z_e = z_e
        self.u_b = u_b
        self.v_b = v_b
        self.w_b = w_b
        self.phi = phi
        self.theta = theta
        self.psi = psi
        self.p = p
        self.q = q
        self.r = r

        # Initialize control variables
        self.Fx_b = 0
        self.Fy_b = 0
        self.Fz_b = 0
        self.Mx_b = 0
        self.My_b = 0
        self.Mz_b = 0
        self.hx_b = 0
        self.hy_b = 0
        self.hz_b = 0

    @property
    def state(self):
        return {
            "x_e"  : self.x_e,
            "y_e"  : self.y_e,
            "z_e"  : self.z_e,
            "u_b"  : self.u_b,
            "v_b"  : self.v_b,
            "w_b"  : self.w_b,
            "phi"  : self.phi,
            "theta": self.theta,
            "psi"  : self.psi,
            "p"    : self.p,
            "q"    : self.q,
            "r"    : self.r,
        }

    @property
    def control_variables(self):
        return {
            "Fx_b": self.Fx_b,
            "Fy_b": self.Fy_b,
            "Fz_b": self.Fz_b,
            "Mx_b": self.Mx_b,
            "My_b": self.My_b,
            "Mz_b": self.Mz_b,
            "hx_b": self.hx_b,
            "hy_b": self.hy_b,
            "hz_b": self.hz_b,
        }

    def state_derivatives(self):
        """
        Computes the state derivatives (i.e. equations of motion) for a body in 3D space.

        Based on Section 9.8.2 of Flight Vehicle Aerodynamics by Mark Drela.

        Returns:
            Time derivatives of each of the 12 state variables, given in a dictionary:
                {
                    "xe"   : d_xe,
                    "ye"   : d_ye,
                    "ze"   : d_ze,
                    "u"    : d_u,
                    "v"    : d_v,
                    "w"    : d_w,
                    "phi"  : d_phi,
                    "theta": d_theta,
                    "psi"  : d_psi,
                    "p"    : d_p,
                    "q"    : d_q,
                    "r"    : d_r,
                }
        """
        ### Shorthand everything so we're not constantly "self."-ing:
        u = self.u
        v = self.v
        w = self.w
        phi = self.phi
        theta = self.theta
        psi = self.psi
        p = self.p
        q = self.q
        r = self.r
        X = self.X
        Y = self.Y
        Z = self.Z
        L = self.L
        M = self.M
        N = self.N
        mass = self.mass
        Ixx = self.Ixx
        Iyy = self.Iyy
        Izz = self.Izz
        Ixy = self.Ixy
        Iyz = self.Iyz
        Ixz = self.Ixz
        hx = self.hx
        hy = self.hy
        hz = self.hz

        ### Trig Shorthands
        def sincos(x):
            try:
                x = np.mod(x, 2 * np.pi)
                one = np.ones_like(x)
                zero = np.zeros_like(x)

                if np.allclose(x, 0) or np.allclose(x, 2 * np.pi):
                    sin = zero
                    cos = one
                elif np.allclose(x, np.pi / 2):
                    sin = one
                    cos = zero
                elif np.allclose(x, np.pi):
                    sin = zero
                    cos = -one
                elif np.allclose(x, 3 * np.pi / 2):
                    sin = -one
                    cos = zero
                else:
                    raise ValueError()
            except:
                sin = np.sin(x)
                cos = np.cos(x)
            return sin, cos

        # Do the trig
        sphi, cphi = sincos(phi)
        sthe, cthe = sincos(theta)
        spsi, cpsi = sincos(psi)

        ##### Equations of Motion

        ### Position derivatives
        d_xe = (
                (cthe * cpsi) * u +
                (sphi * sthe * cpsi - cphi * spsi) * v +
                (cphi * sthe * cpsi + sphi * spsi) * w
        )
        d_ye = (
                (cthe * spsi) * u +
                (sphi * sthe * spsi + cphi * cpsi) * v +
                (cphi * sthe * spsi - sphi * cpsi) * w
        )
        d_ze = (
                (-sthe) * u +
                (sphi * cthe) * v +
                (cphi * cthe) * w
        )
        ### Velocity derivatives
        d_u = (
                (X / mass) -
                q * w +
                r * v
        )
        d_v = (
                (Y / mass) -
                r * u +
                p * w
        )
        d_w = (
                (Z / mass) -
                p * v +
                q * u
        )
        ### Angle derivatives
        if np.all(cthe == 0):
            d_phi = 0
        else:
            d_phi = (
                    p +
                    q * sphi * sthe / cthe +
                    r * cphi * sthe / cthe
            )

        d_theta = (
                q * cphi -
                r * sphi
        )

        if np.all(cthe == 0):
            d_psi = 0
        else:
            d_psi = (
                    q * sphi / cthe +
                    r * cphi / cthe
            )

        ### Angular velocity derivatives
        RHS_L = (
                L -
                (Izz - Iyy) * q * r -
                Iyz * (q ** 2 - r ** 2) -
                Ixz * p * q +
                Ixy * p * r -
                hz * q +
                hy * r
        )
        RHS_M = (
                M -
                (Ixx - Izz) * r * p -
                Ixz * (r ** 2 - p ** 2) -
                Ixy * q * r +
                Iyz * q * p -
                hx * r +
                hz * p
        )
        RHS_N = (
                N -
                (Iyy - Ixx) * p * q -
                Ixy * (p ** 2 - q ** 2) -
                Iyz * r * p +
                Ixz * r * q -
                hy * p +
                hx * q
        )
        i11, i22, i33, i12, i23, i13 = np.linalg.inv_symmetric_3x3(Ixx, Iyy, Izz, Ixy, Iyz, Ixz)

        d_p = i11 * RHS_L + i12 * RHS_M + i13 * RHS_N
        d_q = i12 * RHS_L + i22 * RHS_M + i23 * RHS_N
        d_r = i13 * RHS_L + i23 * RHS_M + i33 * RHS_N

        return {
            "xe"   : d_xe,
            "ye"   : d_ye,
            "ze"   : d_ze,
            "u"    : d_u,
            "v"    : d_v,
            "w"    : d_w,
            "phi"  : d_phi,
            "theta": d_theta,
            "psi"  : d_psi,
            "p"    : d_p,
            "q"    : d_q,
            "r"    : d_r,
        }

    @property
    def alpha(self):
        """The angle of attack, in degrees."""
        return np.arctan2d(
            self.w_b,
            self.u_b
        )

    @property
    def beta(self):
        """The sideslip angle, in degrees."""
        return np.arctan2d(
            self.v_b,
            (
                    self.u_b ** 2 +
                    self.w_b ** 2
            ) ** 0.5
        )

    @property
    def speed(self):
        """The speed of the object, expressed as a scalar."""
        return (
                       self.u_b ** 2 +
                       self.v_b ** 2 +
                       self.w_b ** 2
               ) ** 0.5

    @property
    def translational_kinetic_energy(self):
        speed_squared = (
                self.u_b ** 2 +
                self.v_b ** 2 +
                self.w_b ** 2
        )
        return 0.5 * self.mass_props.mass * speed_squared

    @property
    def rotational_kinetic_energy(self):
        return 0.5 * (
                self.mass_props.Ixx * self.p ** 2 +
                self.mass_props.Iyy * self.q ** 2 +
                self.mass_props.Izz * self.r ** 2
        )

    @property
    def kinetic_energy(self):
        return self.translational_kinetic_energy + self.rotational_kinetic_energy

    @property
    def potential_energy(self, g=9.81):
        """
        Gives the potential energy [J] from gravity.

        PE = mgh
        """
        return self.mass_props.mass * g * self.altitude

    def add_force(self,
                  Fx: Union[np.ndarray, float] = 0,
                  Fy: Union[np.ndarray, float] = 0,
                  Fz: Union[np.ndarray, float] = 0,
                  axes="body",
                  ):
        """
        Adds a force (in whichever axis system you choose) to this dynamics instance.

        Args:
            Fx: Force in the x-direction in the axis system chosen. [N]
            Fy: Force in the y-direction in the axis system chosen. [N]
            Fz: Force in the z-direction in the axis system chosen. [N]
            axes: The axis system that the specified force is in. One of:
                * "geometry"
                * "body"
                * "wind"
                * "stability"
                * "earth"

        Returns: None (in-place)

        """
        Fx_b, Fy_b, Fz_b = self.convert_axes(
            x_from=Fx,
            y_from=Fy,
            z_from=Fz,
            from_axes=axes,
            to_axes="body"
        )
        self.X = self.X + Fx_b
        self.Y = self.Y + Fy_b
        self.Z = self.Z + Fz_b

    def add_moment(self,
                   Mx: Union[np.ndarray, float] = 0,
                   My: Union[np.ndarray, float] = 0,
                   Mz: Union[np.ndarray, float] = 0,
                   axes="body",
                   ):
        """
        Adds a force (in whichever axis system you choose) to this dynamics instance.

        Args:
            Fx: Moment about the x-axis in the axis system chosen. Assumed these moments are applied about the center of mass. [Nm]
            Fy: Moment about the y-axis in the axis system chosen. Assumed these moments are applied about the center of mass. [Nm]
            Fz: Moment about the z-axis in the axis system chosen. Assumed these moments are applied about the center of mass. [Nm]
            axes: The axis system that the specified force is in. One of:
                * "geometry"
                * "body"
                * "wind"
                * "stability"
                * "earth"

        Returns: None (in-place)

        """

        Mx_b, My_b, Mz_b = self.convert_axes(
            x_from=Mx,
            y_from=My,
            z_from=Mz,
            from_axes=axes,
            to_axes="body"
        )
        self.L = self.L + Mx_b
        self.M = self.M + My_b
        self.N = self.N + Mz_b

    def d_translational_kinetic_energy(self):
        """
        Returns the derivative d(translational_kinetic_energy)/d(time) based on energy methods.
        """
        d_KE = (
                self.Fx_b * self.u_b +
                self.Fy_b * self.v_b +
                self.Fz_b * self.w_b
        )
        return d_KE

    def d_speed(self):
        """
        Returns the derivative d(speed)/d(time) based on energy methods.
        """
        return self.d_translational_kinetic_energy() / (self.mass_props.mass * self.speed)

    @property
    def altitude(self):
        return -self.z_e

    @property
    def op_point(self):
        return OperatingPoint(
            atmosphere=Atmosphere(altitude=self.altitude),
            velocity=self.speed,
            alpha=self.alpha,
            beta=self.beta,
            p=self.p,
            q=self.q,
            r=self.r,
        )

    def convert_axes(self,
                     x_from, y_from, z_from,
                     from_axes: str,
                     to_axes: str,
                     ):
        """
        Converts a vector [x_from, y_from, z_from], as given in the `from_axes` frame, to an equivalent vector [x_to,
        y_to, z_to], as given in the `to_axes` frame.

        Identical to OperatingPoint.convert_axes(), but adds in "earth" as a valid axis frame. For more documentation,
        see the docstring of OperatingPoint.convert_axes().

        Both `from_axes` and `to_axes` should be a string, one of:
                * "geometry"
                * "body"
                * "wind"
                * "stability"
                * "earth"

        Args:
                x_from: x-component of the vector, in `from_axes` frame.
                y_from: y-component of the vector, in `from_axes` frame.
                z_from: z-component of the vector, in `from_axes` frame.
                from_axes: The axes to convert from.
                to_axes: The axes to convert to.

        Returns: The x-, y-, and z-components of the vector, in `to_axes` frame. Given as a tuple.

        """
        if from_axes == "earth" or to_axes == "earth":
            ### Trig Shorthands
            def sincos(x):
                try:
                    x = np.mod(x, 2 * np.pi)
                    one = np.ones_like(x)
                    zero = np.zeros_like(x)

                    if np.allclose(x, 0) or np.allclose(x, 2 * np.pi):
                        sin = zero
                        cos = one
                    elif np.allclose(x, np.pi / 2):
                        sin = one
                        cos = zero
                    elif np.allclose(x, np.pi):
                        sin = zero
                        cos = -one
                    elif np.allclose(x, 3 * np.pi / 2):
                        sin = -one
                        cos = zero
                    else:
                        raise ValueError()
                except:
                    sin = np.sin(x)
                    cos = np.cos(x)
                return sin, cos

                # Do the trig

            sphi, cphi = sincos(self.phi)
            sthe, cthe = sincos(self.theta)
            spsi, cpsi = sincos(self.psi)

        if from_axes == "earth":
            x_b = (
                    (cthe * cpsi) * x_from +
                    (cthe * spsi) * y_from +
                    (-sthe) * z_from
            )
            y_b = (
                    (sphi * sthe * cpsi - cphi * spsi) * x_from +
                    (sphi * sthe * spsi + cphi * cpsi) * y_from +
                    (sphi * cthe) * z_from
            )
            z_b = (
                    (cphi * sthe * cpsi + sphi * spsi) * x_from +
                    (cphi * sthe * spsi - sphi * cpsi) * y_from +
                    (cphi * cthe) * z_from
            )
        else:
            x_b, y_b, z_b = self.op_point.convert_axes(
                x_from, y_from, z_from,
                from_axes=from_axes, to_axes="body"
            )

        if to_axes == "earth":
            x_to = (
                    (cthe * cpsi) * x_b +
                    (sphi * sthe * cpsi - cphi * spsi) * y_b +
                    (cphi * sthe * cpsi + sphi * spsi) * z_b
            )
            y_to = (
                    (cthe * spsi) * x_b +
                    (sphi * sthe * spsi + cphi * cpsi) * y_b +
                    (cphi * sthe * spsi - sphi * cpsi) * z_b
            )
            z_to = (
                    (-sthe) * x_b +
                    (sphi * cthe) * y_b +
                    (cphi * cthe) * z_b
            )
        else:
            x_to, y_to, z_to = self.op_point.convert_axes(
                x_b, y_b, z_b,
                from_axes="body", to_axes=to_axes
            )

        return x_to, y_to, z_to


if __name__ == '__main__':
    import aerosandbox as asb

    dyn = DynamicsRigid3DEuler(
        mass_props=asb.MassProperties(
            mass=1
        )
    )