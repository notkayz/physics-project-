from vpython import *
# canvas setup and camera 
s1 = canvas(align = "left", width = 500, height = 500, 
               background = color.white)
s1.userzoom = False
s1.userpan = False

# s2 = canvas(align = "left", width = 500, height = 500, background = color.red)

t = 0
dt = 0.01
play = False

# driving force
amp = .981
freq = sqrt(9.81) - .1

class SimplePendulum:
    def __init__(self, canvas, drive, graphs):
        self.canvas = canvas
        self.theta = radians(30)
        self.omega = 0
        self.alpha = 0
        self.length = 1
        self.mass = .1
        self.drive = drive

        self.pivot = vector(0,0,0)
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)
        self.string = cylinder(canvas = canvas, pos = self.pivot, axis = self.pos - self.pivot, color = color.black, radius = 0.01)
        self.bob = sphere(canvas = canvas, pos = self.pos, radius = .1, color = color.red)

        self.drag_coefficient = .5 * 1.225 * .47 * pi * self.bob.radius ** 2
        self.graphs = graphs
        
    def update(self, t, dt):
        drag_component = - self.drag_coefficient * self.length / self.mass * self.omega * abs(self.omega)
        g_component = - 9.81 / self.length * sin(self.theta) #make gravitational acceleration variable
        drive_force = self.drive(t)
        drive_component = drive_force / self.length / self.mass

        self.alpha = drag_component + g_component + drive_component


        # print(drag_component, g_component, drive_component)
#        print(self.theta)
        # this section will go in an approx method later
        self.omega += self.alpha * dt
        self.theta += self.omega * dt
        self.theta = theta_shift(self.theta)

        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)

        ke = .5 * self.mass * (self.length * self.omega) ** 2
        u = self.mass * 9.81 * (self.length * (1 - cos(abs(self.theta))))
        self.graphs.update_graphs(t, self.theta, self.omega, self.alpha, drive_force, ke, u)

    def render(self):
        self.bob.pos = self.pos
        self.string.axis = self.pos - self.pivot



    def render_sliders(self):
        pass

class Graphs:
    def __init__(self):
        self.t_frame = 10

        self.omega_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Velocity (rad/s)"), align='left')
        self.omega_dots = gdots(color=color.green)

        self.alpha_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Acceleration (rad/s^2)"), align='left')
        self.alpha_dots = gdots(color=color.green)

        self.drive_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Driving Force (N)"), align='left')
        self.drive_dots = gdots(color=color.green)

        self.energy_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("KE (red) and U (green) (J)"), align='left')
        self.ke_dots = gdots(color=color.red)
        self.u_dots = gdots(color=color.green)

        self.phase_graph = graph(width=350, height=250, xtitle=("Angular Position (rad)"), ytitle=("Angular Velocity (rad/s)"), align='left', xmin=-pi, xmax=pi)
        self.phase_dots = gdots(color=color.red)

        self.graphs = [self.omega_graph, self.alpha_graph, self.drive_graph, self.energy_graph, self.phase_graph]

    def update_graphs(self, t, theta, omega, alpha, drive, ke, u):
        self.omega_dots.plot(t, omega)
        self.alpha_dots.plot(t, alpha)
        self.drive_dots.plot(t, drive)
        self.ke_dots.plot(t, ke)
        self.u_dots.plot(t, u)
        self.phase_dots.plot(theta, omega)

        if (t > self.t_frame):
            for g in self.graphs:
                if (g == self.phase_graph):
                    continue
                g.xmin = t - self.t_frame
                g.xmax = t

    def clear_graphs(self):
        for g in self.graphs:
            g.delete()


#converts theta to equivalent angle in [-pi, pi]
def theta_shift(theta):
    theta_shifted = theta % (2 * pi)
    if (theta_shifted < 0):
        theta_shifted += 2 * pi
    if (theta_shifted > pi):
        theta_shifted -= 2 * pi
    return theta_shifted



def drive(time):
    return amp * cos(freq * time)
    
    
graphs = Graphs() # breaks when instantiating inside pendulum class
ball = SimplePendulum(s1, drive, graphs)




while (True):
    rate(100)
    t += dt
    ball.update(t, dt)
    ball.render()


