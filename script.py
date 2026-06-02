from vpython import *

scene.append_to_caption("\n\n")

c1 = canvas(align = "left", width = 500, height = 500, background = color.white)
c1.userzoom = False
c1.userpan = False

c2 = canvas(align = "right", width = 500, height = 500, background = color.white)
c2.userzoom = False
c2.userpan = False

scene.append_to_caption("\n\n")

user_inputs = canvas (width = 1000, height = 1, background = color.white)

t = 0
dt = 0.01
play = False

class Graphs:
    def __init__(self, line_color):
        self.t_frame = 10

        self.omega_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Velocity (rad/s)"), align='left')
        self.omega_line = gcurve(color=line_color)

        self.alpha_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Acceleration (rad/s^2)"), align='left')
        self.alpha_line = gcurve(color=line_color)

        self.drive_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Driving Force (N)"), align='left')
        self.drive_line = gcurve(color=line_color)

        self.energy_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=(f"KE (green) and U ({line_color}) (J)"), align='left')
        self.ke_line = gcurve(color=color.green)
        self.u_line = gcurve(color=line_color)

        self.phase_graph = graph(width=350, height=250, xtitle=("Angular Position (rad)"), ytitle=("Angular Velocity (rad/s)"), align='left', xmin=-pi, xmax=pi)
        self.phase_line = gcurve(color=line_color)

        self.graphs = [self.omega_graph, self.alpha_graph, self.drive_graph, self.energy_graph, self.phase_graph]
        self.curves = [self.omega_line, self.alpha_line, self.drive_line, self.ke_line, self.u_line, self.phase_line]
        self.shifted = False
        self.line_color = line_color

    def update_graphs(self, t, theta, omega, alpha, drive, ke, u):
        self.omega_line.plot(t, omega)
        self.alpha_line.plot(t, alpha)
        self.drive_line.plot(t, drive)
        self.ke_line.plot(t, ke)
        self.u_line.plot(t, u)
        if (self.shifted): # prevents line from being drawn when theta wraps from -pi to pi
            self.phase_line = gcurve(graph=self.phase_graph, color=self.line_color)
            self.shifted = False
        self.curves[-1] = self.phase_line
        self.phase_line.plot(theta, omega) 

        if (t > self.t_frame):
            for g in self.graphs:
                if (g == self.phase_graph):
                    continue
                g.xmin = t - self.t_frame
                g.xmax = t

    def clear_graphs(self):
        for d in self.curves:
            d.xmin = 0
            d.xmax = 0
            d.delete()

class SimplePendulum:
    def __init__(self, canvas, drive, line_color):
        self.canvas = canvas
        self.theta = radians(30)
        self.omega = 0
        self.alpha = 0
        self.length = 1
        self.mass = .1
        self.radius = .1
        self.amp = 0.981
        self.freq = sqrt(9.81) - .1
        self.drive = drive


        self.pivot = vector(0,0,0)
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)
        self.string = cylinder(canvas = canvas, pos = self.pivot, axis = self.pos - self.pivot, color = color.black, radius = 0.01)
        self.bob = sphere(canvas = canvas, pos = self.pos, radius = self.radius, color = color.red)

        self.drag_coefficient = .5 * 1.225 * .47 * pi * self.bob.radius ** 2
        
        self.create_inputs()
        self.graphs = Graphs(line_color)

        

    def change_values(self, evt):
        if (evt.parameter == "theta"):
            setattr(self, evt.parameter, evt.value * pi / 180)
        else:
            setattr(self, evt.parameter, evt.value) #takes parameter as string and sets to value
        evt.display.text = f"{evt.value:1.2f} {evt.unit}"
        self.bob.radius = self.radius
        self.canvas.range = (self.length + self.radius) * 1.5
        self.render()
        
    def update(self, t, dt):
        drag_component = - self.drag_coefficient * self.length / self.mass * self.omega * abs(self.omega)
        g_component = - 9.81 / self.length * sin(self.theta) #make gravitational acceleration variable
        drive_force = self.drive(t, self.amp, self.freq)
        drive_component = drive_force / self.length / self.mass

        self.alpha = drag_component + g_component + drive_component


        # print(drag_component, g_component, drive_component)
#        print(self.theta)
        # this section will go in an approx method later
        self.omega += self.alpha * dt
        self.theta += self.omega * dt
        if (self.theta > pi or self.theta < -pi): 
            self.theta = theta_shift(self.theta)
            self.graphs.shifted = True

        ke = .5 * self.mass * (self.length * self.omega) ** 2
        u = self.mass * 9.81 * (self.length * (1 - cos(abs(self.theta))))
        if (t * 100 // 1 % 2 == 0):
            self.graphs.update_graphs(t, self.theta, self.omega, self.alpha, drive_force, ke, u)

    def reset(self):
        self.theta = radians(30) 
        self.omega = 0
        self.alpha = 0

    def render(self):
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)
        self.bob.pos = self.pos
        self.string.axis = self.pos - self.pivot

    def create_inputs(self):

        user_inputs.append_to_caption("\n \n <b> Parameters : </b> \n \n Mass : ")

        mass_slider = slider(bind = self.change_values, max = 1, min = 0.1, step = 0.1, value = self.mass)
        mass_slider.parameter = "mass"
        mass_slider.display = wtext(text=f"{mass_slider.value:1.2f} kg")
        mass_slider.unit = "kg"

        user_inputs.append_to_caption("\n \n Length: ")
        length_slider = slider(bind = self.change_values, max = 10, min = 1, step = 1, value = self.length)
        length_slider.parameter = "length"
        length_slider.display = wtext(text=f"{length_slider.value:1.2f} m")
        length_slider.unit = "m"

        user_inputs.append_to_caption("\n \n Radius: ")
        radius_slider = slider(bind = self.change_values, max = 1, min = 0.1, step = 0.1, value = self.radius)
        radius_slider.parameter = "radius"
        radius_slider.display = wtext(text=f"{radius_slider.value:1.2f} m")
        radius_slider.unit = "m"

        user_inputs.append_to_caption("\n \n Angle: ")
        angle_slider = slider(bind = self.change_values, max = 180, min = -180, step = 1, value = self.theta * 180 / pi)        
        angle_slider.parameter = "theta"
        angle_slider.display = wtext(text=f"{angle_slider.value:1.2f} deg")
        angle_slider.unit = "deg"

        user_inputs.append_to_caption("\n \n Amplitude: ")
        amp_slider = slider(bind = self.change_values, max = 10, min = 0, step = 0.1, value = self.amp)
        amp_slider.parameter = "amp"
        amp_slider.display = wtext(text=f"{amp_slider.value:1.2f} N")
        amp_slider.unit = "N"

        user_inputs.append_to_caption("\n \n Frequency: ")
        freq_slider = slider(bind = self.change_values, max = 1, min = 0, step = .01, value = self.freq)        
        freq_slider.parameter = "freq"
        freq_slider.display = wtext(text=f"{freq_slider.value:1.2f} hz")
        freq_slider.unit = "hz"
        user_inputs.append_to_caption("\n \n")


#converts theta to equivalent angle in [-pi, pi]
def theta_shift(theta):
    theta_shifted = theta % (2 * pi)
    if (theta_shifted < 0):
        theta_shifted += 2 * pi
    if (theta_shifted > pi):
        theta_shifted -= 2 * pi
    return theta_shifted

def play_button(evt) :
    global play
    play = not play

def resetButton(evt) :
    global t, theta, omega, alpha, play 
    t = 0
    play = False
    p1.graphs.clear_graphs()
    p1.reset()
    p1.render()
    p2.graphs.clear_graphs()    
    p2.reset()
    p2.render()

def drive(time, amp, freq):
    return amp * cos(freq * time)
    
toggle_simulation = button(bind = play_button, text = "Play/Pause")
reset = button(bind = resetButton, text = "Reset")

p1 = SimplePendulum(c1, drive, color.red)
p2 = SimplePendulum(c2, drive, color.blue)


while (True):
    rate(100)
    if (play):
        p1.update(t, dt)
        p1.render()
        p2.update(t, dt)
        p2.render()
        t += dt


