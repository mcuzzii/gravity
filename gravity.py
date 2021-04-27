from manimlib.imports import *      # import Manim library


# Here, the Planet class is defined. An instance of this class stores variables like mass, velocity, and force,
# essentially representing a planet in the simulation
#
class Planet(Sphere):
    def __init__(self, init_pos, init_vel, **kwargs):
        Sphere.__init__(self, **kwargs)
        self.move_to(init_pos)
        self.mass = 4 * PI * self.radius * self.radius * self.radius / 3
        self.velocity = init_vel
        self.force = np.array([0, 0, 0])

    def get_velocity(self):
        return self.velocity

    def get_force(self):
        return self.force

    def get_mass(self):
        return self.mass

    def get_radius(self):
        return self.radius

    def set_mass(self, mass):
        self.mass = mass

    def set_velocity(self, vel):
        self.velocity = vel

    def set_force_vector(self, force):
        self.force = force


# The class where all animation is created
#
class scene_1(ThreeDScene):
    #
    # Some useful constants. 'runtime' indicates the duration of the simulation in seconds; 'orbit_duration' indicates
    # the duration at which the traced path of the planets will fade away; changing 'steps_per_frame' changes the
    # refresh rate of the simulation--in other words, if steps_per_frame is 2 on a 60 fps simulation, planets will
    # update their locations 120 times per second. The higher the refresh rate, the more accurate and stable the
    # simulation but this will significantly slow down the render time.
    #
    # 'path_predictor_mode' can either be 0 or 1. If it is 1, then rendering this class as an image will create a
    # preview of the orbits/paths that your planets will trace in the entire simulation--which is quicker than
    # rendering an entire video--for testing purposes.
    #
    CONFIG = {
        "path_predictor_mode": 0,
        "runtime": 40,
        "orbit_duration": 15,
        "steps_per_frame": 60
    }

    # Setting up the 3D scene
    def construct(self):
        axis_config = {
            "x_min": -10,
            "x_max": 10,
            "y_min": -10,
            "y_max": 10,
            "z_min": -10,
            "z_max": 10,
            "x_axis_config": {
                "stroke_width": 1
            },
            "y_axis_config": {
                "stroke_width": 1
            },
            "z_axis_config": {
                "stroke_width": 1
            }
        }
        self.set_camera_orientation(phi=80 * DEGREES, theta=45 * DEGREES, distance=20)
        self.add(ThreeDAxes(**axis_config))
        self.begin_ambient_camera_rotation(0.02)
        self.planets = VGroup()
        self.orbits = VGroup()
        self.initialize()
        if not self.path_predictor_mode:
            self.add(self.planets)
        self.add(self.orbits)
        if not self.path_predictor_mode:
            self.wait(self.runtime)

    def initialize(self):
        self.big_G = 5       # This is Newton's gravitation constant which for our purposes has a default value of 5.

        # Some useful mathematical functions
        #
        def squared_distance(mob1, mob2):
            a = mob1.get_center()
            b = mob2.get_center()
            return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2])
        palette = [[RED_A, RED_C], [GREEN_A, GREEN_C], [BLUE_A, BLUE_C], [PURPLE_A, PURPLE_C]]

        def get_rotated_vector(vector, phi_x, phi_y, phi_z):
            r_matrices = [
                np.array([
                    [1, 0, 0],
                    [0, math.cos(phi_x), -math.sin(phi_x)],
                    [0, math.sin(phi_x), math.cos(phi_x)]
                ]),
                np.array([
                    [math.cos(phi_y), 0, math.sin(phi_y)],
                    [0, 1, 0],
                    [-math.sin(phi_y), 0, math.cos(phi_x)]
                ]),
                np.array([
                    [math.cos(phi_z), -math.sin(phi_z), 0],
                    [math.sin(phi_z), math.cos(phi_z), 0],
                    [0, 0, 1]
                ]),
            ]
            return np.dot(r_matrices[0], np.dot(r_matrices[1], np.dot(r_matrices[2], vector)))

        # The following six functions are presets, i.e. premade initial conditions for the simulation. Each function
        # returns an array of planets with carefully determined placements and initial velocities conducive to
        # forming quasi-stable orbits that last for some time.
        #
        def two_bodies():
            spawn_distance = 1
            max_init_speed = 1
            max_radius = 0.5
            planets = []
            body1 = Planet(
                (0, -spawn_distance, 1.5),
                RIGHT * max_init_speed,
                radius=max_radius * 0.5, checkerboard_colors=palette[2]
            )
            body1.set_mass(body1.get_mass() / body1.get_radius())
            body2 = Planet(
                (0, spawn_distance, -1.5),
                0, radius=max_radius, checkerboard_colors=palette[0]
            )
            body2.set_mass(body2.get_mass() / body2.get_radius())
            body2.set_velocity(-body1.get_mass() * body1.get_velocity() / body2.get_mass())
            planets.append(body1)
            planets.append(body2)
            return planets

        def three_bodies_1():
            spawn_distance = 4
            max_init_speed = 1
            max_radius = 0.5
            planets = [
                Planet(
                    np.array([0, -0.2, 0]) + RIGHT * spawn_distance,
                    max_init_speed * (RIGHT / 2 + (UP + OUT) / math.sqrt(2)),
                    radius=max_radius * 0.2, checkerboard_colors=palette[1]
                ),
                Planet(
                    np.array([0, 0.2, 0]) + RIGHT * spawn_distance,
                    max_init_speed * (LEFT / 2 + (UP + OUT) / math.sqrt(2)),
                    radius=max_radius * 0.2, checkerboard_colors=palette[2]
                ),
                Planet(
                    ORIGIN, 0, radius=max_radius, checkerboard_colors=palette[3]
                )
            ]
            planets[0].set_mass(planets[0].get_mass() / planets[0].get_radius())
            planets[1].set_mass(planets[1].get_mass() / planets[1].get_radius())
            planets[2].set_mass(planets[2].get_mass() / planets[2].get_radius())
            planets[2].set_velocity(-(planets[0].get_velocity() * planets[0].get_mass() + planets[1].get_velocity() *
                                      planets[1].get_mass()) / planets[2].get_mass())
            return planets

        def planetary_system():
            spawn_distance = 6
            max_radius = 0.5
            plane_vectors = [
                get_rotated_vector(RIGHT, 0, math.atan(0.5), 0),
                get_rotated_vector(UP, 0, math.atan(0.5), 0)
            ]
            central_planet = Planet(ORIGIN, 0, radius=max_radius, checkerboard_colors=palette[3])
            central_planet.set_mass(central_planet.get_mass() / central_planet.get_radius())
            planets = [
                Planet(
                    plane_vectors[0] * spawn_distance / 6,
                    plane_vectors[1] * math.sqrt(self.big_G * central_planet.mass / (spawn_distance / 6)),
                    radius=max_radius / 10, checkerboard_colors=palette[0]
                ),
                Planet(
                    -plane_vectors[0] * spawn_distance / 4,
                    -plane_vectors[1] * math.sqrt(self.big_G * central_planet.mass / (spawn_distance / 4)),
                    radius=max_radius / 10, checkerboard_colors=palette[1]
                ),
                Planet(
                    plane_vectors[1] * spawn_distance / 3,
                    -plane_vectors[0] * math.sqrt(self.big_G * central_planet.mass / (spawn_distance / 3)),
                    radius=max_radius / 10, checkerboard_colors=palette[2]
                ),
                Planet(
                    -plane_vectors[1] * spawn_distance / 2,
                    plane_vectors[0] * math.sqrt(self.big_G * central_planet.mass / (spawn_distance / 2)),
                    radius=max_radius / 10, checkerboard_colors=palette[3]
                ),
                Planet(
                    plane_vectors[0] * 2 * spawn_distance / 3,
                    plane_vectors[1] * math.sqrt(self.big_G * central_planet.mass / (2 * spawn_distance / 6)),
                    radius=max_radius / 10, checkerboard_colors=palette[1]
                ),
            ]
            for planet in planets:
                planet.set_mass(planet.get_mass() / planet.get_radius())
            planets.append(central_planet)
            return planets

        def three_bodies_2():
            spawn_distance = 4
            max_radius = 1 / 3
            self.big_G = 16
            plane_vectors = [
                get_rotated_vector(RIGHT, 0, 0.6, 0.6),
                get_rotated_vector(UP, 0, 0.6, 0.6)
            ]
            planets = [
                Planet(
                    plane_vectors[0] * spawn_distance * -0.97000436 + plane_vectors[1] * spawn_distance * 0.24308753,
                    plane_vectors[0] * spawn_distance * 0.4662036850 + plane_vectors[1] * spawn_distance * 0.4323657300,
                    radius=max_radius, checkerboard_colors=palette[0]
                ),
                Planet(
                    ORIGIN,
                    plane_vectors[0] * spawn_distance * -0.93240737 + plane_vectors[1] * spawn_distance * -0.86473146,
                    radius=max_radius, checkerboard_colors=palette[1]
                ),
                Planet(
                    plane_vectors[0] * spawn_distance * 0.97000436 + plane_vectors[1] * spawn_distance * -0.24308753,
                    plane_vectors[0] * spawn_distance * 0.4662036850 + plane_vectors[1] * spawn_distance * 0.4323657300,
                    radius=max_radius, checkerboard_colors=palette[2]
                ),
            ]
            for planet in planets:
                planet.set_mass(4)
            return planets

        def three_bodies_3():
            max_radius = 0.1
            self.big_G = 16
            plane_vectors = [
                get_rotated_vector(RIGHT, 0, 3.9, 3.9),
                get_rotated_vector(UP, 0, 3.9, 3.9)
            ]
            planets = [
                Planet(
                    -plane_vectors[0] * 4,
                    plane_vectors[0] * 4 * 0.4227625247 + plane_vectors[1] * 4 * 0.2533646387,
                    radius=max_radius, checkerboard_colors=palette[0]
                ),
                Planet(
                    plane_vectors[0] * 4,
                    plane_vectors[0] * 4 * 0.4227625247 + plane_vectors[1] * 4 * 0.2533646387,
                    radius=max_radius, checkerboard_colors=palette[1]
                ),
                Planet(
                    ORIGIN,
                    plane_vectors[0] * -8 * 0.4227625247 / 0.75 + plane_vectors[1] * -8 * 0.2533646387 / 0.75,
                    radius=max_radius, checkerboard_colors=palette[2]
                ),
            ]
            planets[0].set_mass(4)
            planets[1].set_mass(4)
            planets[2].set_mass(3)
            return planets

        def three_bodies_4():
            max_radius = 0.1
            self.big_G = 16
            plane_vectors = [
                get_rotated_vector(RIGHT, 0.7, 1.2, 4.4),
                get_rotated_vector(UP, 0.7, 1.2, 4.4)
            ]
            planets = [
                Planet(
                    -plane_vectors[0] * 4,
                    plane_vectors[0] * 4 * 0.2374365149 + plane_vectors[1] * 4 * 0.2536896353,
                    radius=max_radius, checkerboard_colors=palette[0]
                ),
                Planet(
                    plane_vectors[0] * 4,
                    plane_vectors[0] * 4 * 0.2374365149 + plane_vectors[1] * 4 * 0.2536896353,
                    radius=max_radius, checkerboard_colors=palette[1]
                ),
                Planet(
                    ORIGIN,
                    plane_vectors[0] * -8 * 0.2374365149 / 0.5 + plane_vectors[1] * -8 * 0.2536896353 / 0.5,
                    radius=max_radius, checkerboard_colors=palette[2]
                ),
            ]
            planets[0].set_mass(4)
            planets[1].set_mass(4)
            planets[2].set_mass(2)
            return planets

        # The following line indicates what preset you would like to use. You may change "three_bodies_4" into any of
        # the above six functions.
        #
        self.planets.add(*three_bodies_4())
        num_planets = self.planets.get_num_submobjects()
        for planet in self.planets:
            self.orbits.add(VGroup(Line(planet.get_center(), planet.get_center() + UP * 0.001,
                                        stroke_color=planet.get_checkerboard_colors()[0], stroke_width=2)))

        # Now, this is where the relevant physics is applied to the simulation to my best knowledge. It combines
        # Newton's laws of gravitation and laws of motion to produce realistic planetary movements. This function is
        # called once every single frame to move the planets in their next location in accordance to said laws of
        # physics.
        #
        def planets_updater(mob, dt):
            step_size = dt / self.steps_per_frame
            for k in range(self.steps_per_frame):
                for i in range(num_planets):
                    mob[i].set_force_vector(np.array([0, 0, 0]))
                for i in range(num_planets):
                    for j in range(i + 1, num_planets):
                        r_squared = squared_distance(mob[i], mob[j])
                        gforce = self.big_G * mob[i].get_mass() * mob[j].get_mass() / r_squared
                        unit_collision = (mob[j].get_center() - mob[i].get_center()) / math.sqrt(r_squared)
                        mob[i].set_force_vector(mob[i].get_force() + unit_collision * gforce)
                        mob[j].set_force_vector(mob[j].get_force() - unit_collision * gforce)
                for i in range(num_planets):
                    mob[i].set_velocity(mob[i].get_velocity() + mob[i].get_force() * step_size / mob[i].get_mass())
                    mob[i].shift(mob[i].get_velocity() * step_size)
            for i in range(num_planets):
                self.orbits[i].add(Line(self.orbits[i][-1].get_points()[-1], self.planets[i].get_center(),
                                        stroke_color=self.orbits[i][-1].get_stroke_color(), stroke_width=2))
                if not self.path_predictor_mode:
                    for submob in self.orbits[i]:
                        stroke_width = submob.get_stroke_width()
                        submob.set_stroke(width=stroke_width - 2 * dt / self.orbit_duration)
                        if stroke_width <= 0:
                            self.orbits[i].remove(submob)
        if self.path_predictor_mode:
            for n in range(int(60 * self.runtime)):
                planets_updater(self.planets, 1 / 60)
                print("frame: ", n * self.steps_per_frame, '/', self.runtime * 60 * self.steps_per_frame)
        else:
            self.planets.add_updater(planets_updater)
