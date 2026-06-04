from vpython import *

scene.append_to_caption("\n\n")

scene.visible = False
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
    def __init__(self, canvas, color_name):
        self.t_frame = 10
        
        line_color = getattr(color, color_name)
        
#        canvas.append_to_caption("\n \n")
        self.omega_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Velocity (rad/s)"), align="left")
        self.omega_line = gcurve(color=line_color)

        self.alpha_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Acceleration (rad/s^2)"), align="left")
        self.alpha_line = gcurve(color=line_color)

        self.drive_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Driving Force (N)"), align="left")
        self.drive_line = gcurve(color=line_color)

        self.energy_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=(f"KE (green) and U ({color_name}) (J)"), align="left")
        self.ke_line = gcurve(color=color.green)
        self.u_line = gcurve(color=line_color)

        self.phase_graph = graph(width=350, height=250, xtitle=("Angular Position (rad)"), ytitle=("Angular Velocity (rad/s)"), align="left", xmin=-pi, xmax=pi)
        self.phase_line = gcurve(color=line_color)

        self.graphs = [self.omega_graph, self.alpha_graph, self.drive_graph, self.energy_graph, self.phase_graph]
        self.curves = [self.omega_line, self.alpha_line, self.drive_line, self.ke_line, self.u_line, self.phase_line]
        self.phase_lines = [self.phase_line] # keeps track of all created phase lines for deletion
        
        self.shifted = False
        self.line_color = line_color

    def update_graphs(self, t, theta, omega, alpha, drive, ke, u):
        self.omega_line.plot(t, omega)
        self.alpha_line.plot(t, alpha)
        self.drive_line.plot(t, drive)
        self.ke_line.plot(t, ke)
        self.u_line.plot(t, u)
        if (self.shifted): # prevents line from being drawn when theta wraps from -pi to pi
            self.phase_lines.append(self.phase_line)
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
        for c in self.curves:
            c.xmin = 0
            c.xmax = 0
            c.delete()
        for lines in self.phase_lines:
            lines.delete()

class Pendulum:
    def __init__(self, canvas, drive):
        self.canvas = canvas
        self.theta = pi/6
        self.omega = 0
        self.alpha = 0
        self.drive = drive
        self.pivot_ball = sphere(canvas = canvas, pos = vec(0, 0, 0), radius = .02, color = color.green)
        
        self.method_dict = {"Euler-Kromer": Pendulum.euler_kromer, "Runge-Kutta Order 2": Pendulum.rk2, "Runge-Kutta Order 4": Pendulum.rk4}
        self.current_method = self.euler_kromer

    def change_values(self, evt):
        pass

    def update(self, t):

        self.alpha = self.drag_component + self.g_component + self.drive_component

        if (t * 100 // 1 % 2 == 0):
            self.graphs.update_graphs(t, self.theta, self.omega, self.alpha, self.drive_force, self.ke, self.u)

    def euler_kromer(self, dt):
        self.omega += self.alpha * dt
        self.theta += self.omega * dt
        if (self.theta > pi or self.theta < -pi): 
            self.theta = self.theta_shift()
            self.graphs.shifted = True
            
    def rk2(self, dt):
        pass
    
    def rk4(self, dt):
        pass

    def reset(self):
        self.theta = radians(30) 
        self.omega = 0
        self.alpha = 0

    def render(self):
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)

    def create_inputs(self):
        self.method_dropdown = menu(bind=self.change_method, choices=["Euler-Kromer", "Runge-Kutta Order 2", "Runge-Kutta Order 4"], selected=self.current_method)

    def hide_inputs(self):
        for input in self.inputs_list:
            input.delete()
            
    def change_method(self, evt):
        self.current_method = self.method_dict[evt.selected]

    #converts theta to equivalent angle in [-pi, pi]
    def theta_shift(self):
        theta_shifted = self.theta % (2 * pi)
        if (theta_shifted < 0):
            theta_shifted += 2 * pi
        if (theta_shifted > pi):
            theta_shifted -= 2 * pi
        return theta_shifted

class SimplePendulum(Pendulum):
    def __init__(self, canvas, drive, line_color):
        Pendulum.__init__(self, canvas, drive)
        self.length = 1
        self.mass = .1
        self.radius = .1
        self.amp = 0.981
        self.freq = sqrt(9.81 / self.length) / 2 / pi - .1

        self.pivot = vector(0,0,0)
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)
        self.string = cylinder(canvas = canvas, pos = self.pivot, axis = self.pos - self.pivot, color = color.black, radius = 0.01)
        self.bob = sphere(canvas = canvas, pos = self.pos, radius = self.radius, color = getattr(color, line_color))

        self.drag_coefficient = .5 * 1.225 * .47 * pi * self.bob.radius ** 2
        
        self.create_inputs()
        self.graphs = Graphs(self.canvas, line_color)
        self.canvas.range = (self.length + self.radius) * 1.5

    def change_values(self, evt):
        if not hasattr(evt, 'parameter'):
            return
    
        if (evt.parameter == "theta"):
            setattr(self, evt.parameter, evt.value * pi / 180)
        else:
            setattr(self, evt.parameter, evt.value) #takes parameter as string and sets to value
        evt.display.text = f"{evt.value:1.2f} {evt.unit}"
        self.bob.radius = self.radius
        self.canvas.range = (self.length + self.radius) * 1.5
        self.render()
        
    def update(self, t, dt):
        self.drag_component = - self.drag_coefficient * self.length / self.mass * self.omega * abs(self.omega)
        self.g_component = - 9.81 / self.length * sin(self.theta) #make gravitational acceleration variable
        self.drive_force = self.drive(t, self.amp, self.freq)
        self.drive_component = self.drive_force / self.length / self.mass

        self.current_method(dt)

        self.ke = .5 * self.mass * (self.length * self.omega) ** 2
        self.u = self.mass * 9.81 * (self.length * (1 - cos(abs(self.theta))))
        Pendulum.update(self, t)

    def reset(self):
        Pendulum.reset(self)

    def render(self):
        Pendulum.render(self)

        self.bob.pos = self.pos
        self.string.axis = self.pos - self.pivot

    def create_inputs(self):
        user_inputs.append_to_caption("\n \n <b> Parameters : </b> \n \n Mass : ")

        self.mass_slider = slider(bind = self.change_values, max = 10, min = 0.1, step = 0.1, value = self.mass)
        self.mass_slider.parameter = "mass"
        self.mass_slider.display = wtext(text=f"{self.mass_slider.value:1.2f} kg")
        self.mass_slider.unit = "kg"

        user_inputs.append_to_caption("\n \n Length: ")
        self.length_slider = slider(bind = self.change_values, max = 10, min = .1, step = .1, value = self.length)
        self.length_slider.parameter = "length"
        self.length_slider.display = wtext(text=f"{self.length_slider.value:1.2f} m")
        self.length_slider.unit = "m"

        user_inputs.append_to_caption("\n \n Radius: ")
        self.radius_slider = slider(bind = self.change_values, max = 1, min = 0.1, step = 0.1, value = self.radius)
        self.radius_slider.parameter = "radius"
        self.radius_slider.display = wtext(text=f"{self.radius_slider.value:1.2f} m")
        self.radius_slider.unit = "m"

        user_inputs.append_to_caption("\n \n Angle: ")
        self.angle_slider = slider(bind = self.change_values, max = 180, min = -180, step = 1, value = self.theta * 180 / pi)        
        self.angle_slider.parameter = "theta"
        self.angle_slider.display = wtext(text=f"{self.angle_slider.value:1.2f} deg")
        self.angle_slider.unit = "deg"

        user_inputs.append_to_caption("\n \n Amplitude: ")
        self.amp_slider = slider(bind = self.change_values, max = 10, min = 0, step = 0.1, value = self.amp)
        self.amp_slider.parameter = "amp"
        self.amp_slider.display = wtext(text=f"{self.amp_slider.value:1.2f} N")
        self.amp_slider.unit = "N"

        user_inputs.append_to_caption("\n \n Frequency: ")
        self.freq_slider = slider(bind = self.change_values, max = 1, min = 0, step = .01, value = self.freq)        
        self.freq_slider.parameter = "freq"
        self.freq_slider.display = wtext(text=f"{self.freq_slider.value:1.2f} hz")
        self.freq_slider.unit = "hz"
        user_inputs.append_to_caption("\n \n")
        
        Pendulum.create_inputs(self)

        self.inputs_list = [self.mass_slider, self.length_slider, self.radius_slider, self.angle_slider, self.amp_slider, self.freq_slider]

    def hide_inputs(self):
        Pendulum.hide_inputs(self)

class RodPendulum(Pendulum):
    def __init__(self, canvas, drive, line_color):
        Pendulum.__init__(self, canvas, drive)
        self.length = 1
        self.mass = .1
        self.radius = .1
        self.amp = 0.981
        self.freq = sqrt(9.81 / self.length) / 2 / pi - .1

        self.pivot = vector(0,0,0)
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)
        self.rod = cylinder(canvas = canvas, pos = self.pivot, axis = self.pos - self.pivot, color = getattr(color, line_color), radius = self.radius)

        self.drag_coefficient = .5 * 1.225 * 1.17 * 2 * self.radius * self.length
        
        self.create_inputs()
        self.graphs = Graphs(self.canvas, line_color)
        self.canvas.range = (self.length + self.radius) * 1.5

    def change_values(self, evt):
        if not hasattr(evt, 'parameter'):
            return
    
        if (evt.parameter == "theta"):
            setattr(self, evt.parameter, evt.value * pi / 180)
        else:
            setattr(self, evt.parameter, evt.value) #takes parameter as string and sets to value
        evt.display.text = f"{evt.value:1.2f} {evt.unit}"
        self.rod.radius = self.radius
        self.canvas.range = self.length * 1.5
        self.render()
        
    def update(self, t, dt):
        self.drag_component = - 3 / 4 * self.drag_coefficient * self.length ** 2 / self.mass * self.omega * abs(self.omega)
        self.g_component = - 3 / 2 * 9.81 / self.length * sin(self.theta) 
        self.drive_force = self.drive(t, self.amp, self.freq)
        self.drive_component = 3 / 2 * self.drive_force / self.length / self.mass # this assumes the drive force is applied at the COM
        
        self.current_method(dt)

        self.ke = .5 * 1 / 3 * self.mass * (self.length * self.omega) ** 2
        self.u = self.mass * 9.81 * self.length / 2 * (1 - cos(abs(self.theta))) # center of mass
        Pendulum.update(self, t)

    def reset(self):
        Pendulum.reset(self)

    def render(self):
        Pendulum.render(self)

        self.rod.axis = self.pos - self.pivot

    def create_inputs(self):
        user_inputs.append_to_caption("\n \n <b> Parameters : </b> \n \n Mass : ")

        self.mass_slider = slider(bind = self.change_values, max = 10, min = 0.1, step = 0.1, value = self.mass)
        self.mass_slider.parameter = "mass"
        self.mass_slider.display = wtext(text=f"{self.mass_slider.value:1.2f} kg")
        self.mass_slider.unit = "kg"

        user_inputs.append_to_caption("\n \n Length: ")
        self.length_slider = slider(bind = self.change_values, max = 10, min = .1, step = .1, value = self.length)
        self.length_slider.parameter = "length"
        self.length_slider.display = wtext(text=f"{self.length_slider.value:1.2f} m")
        self.length_slider.unit = "m"

        user_inputs.append_to_caption("\n \n Radius: ")
        self.radius_slider = slider(bind = self.change_values, max = 1, min = 0.01, step = 0.01, value = self.radius)
        self.radius_slider.parameter = "radius"
        self.radius_slider.display = wtext(text=f"{self.radius_slider.value:1.2f} m")
        self.radius_slider.unit = "m"

        user_inputs.append_to_caption("\n \n Angle: ")
        self.angle_slider = slider(bind = self.change_values, max = 180, min = -180, step = 1, value = self.theta * 180 / pi)        
        self.angle_slider.parameter = "theta"
        self.angle_slider.display = wtext(text=f"{self.angle_slider.value:1.2f} deg")
        self.angle_slider.unit = "deg"

        user_inputs.append_to_caption("\n \n Amplitude: ")
        self.amp_slider = slider(bind = self.change_values, max = 10, min = 0, step = 0.1, value = self.amp)
        self.amp_slider.parameter = "amp"
        self.amp_slider.display = wtext(text=f"{self.amp_slider.value:1.2f} N")
        self.amp_slider.unit = "N"

        user_inputs.append_to_caption("\n \n Frequency: ")
        self.freq_slider = slider(bind = self.change_values, max = 1, min = 0, step = .01, value = self.freq)        
        self.freq_slider.parameter = "freq"
        self.freq_slider.display = wtext(text=f"{self.freq_slider.value:1.2f} hz")
        self.freq_slider.unit = "hz"
        user_inputs.append_to_caption("\n \n")
        
        Pendulum.create_inputs(self)

        self.inputs_list = [self.mass_slider, self.length_slider, self.radius_slider, self.angle_slider, self.amp_slider, self.freq_slider]

    def hide_inputs(self):
        Pendulum.hide_inputs(self)




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
    return amp * cos(freq * 2 * pi * time)
    
toggle_simulation = button(bind = play_button, text = "Play/Pause")
reset = button(bind = resetButton, text = "Reset")

p1 = SimplePendulum(c1, drive, "red")
p2 = RodPendulum(c2, drive, "blue")


while (True):
    rate(100)
    if (play):
        p1.update(t, dt)
        p1.render()
        p2.update(t, dt)
        p2.render()
        t += dt


