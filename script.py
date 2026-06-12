from vpython import *

scene.append_to_caption("\n\n")

scene.visible = False

t = 0
dt = 0.01
play = False
active_tab = 0

class Graphs:
    def __init__(self, c, color_name):
        self.t_frame = 10
        
        line_color = getattr(color, color_name)
        c.select()
        self.omega_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Velocity (rad/s)"), align="left", xmin=0, xmax=10)
        self.omega_line = gcurve(color=line_color)
        self.omega_graph.foreground = line_color
        
        self.alpha_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Acceleration (rad/s^2)"), align="left", xmin=0, xmax=10)
        self.alpha_line = gcurve(color=line_color)
        self.alpha_graph.foreground = line_color

        self.drive_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Driving Force (N)"), align="left", xmin=0, xmax=10)
        self.drive_line = gcurve(color=line_color)
        self.drive_graph.foreground = line_color

        self.energy_graph = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=(f"KE (green) and U ({color_name}) (J)"), align="left", xmin=0, xmax=10)
        self.ke_line = gcurve(color=color.green)
        self.u_line = gcurve(color=line_color)
        self.energy_graph.foreground = line_color

        self.phase_graph = graph(width=350, height=250, xtitle=("Angular Position (rad)"), ytitle=("Angular Velocity (rad/s)"), align="left", xmin=-pi, xmax=pi)
        self.phase_line = gcurve(color=line_color)
        self.phase_graph.foreground = line_color

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
        for g in self.graphs:
            if (g == self.phase_graph):
                continue
            g.xmin = 0
            g.xmax = 10
        for c in self.curves:
            c.delete()
        for lines in self.phase_lines:
            lines.delete()
            
    def delete_graphs(self):
        for g in self.graphs:
            g.delete()

class Pendulum:
    def __init__(self, canvas, drive):
        self.canvas = canvas
        self.theta = pi/6
        self.omega = 0
        self.alpha = 0
        self.drive = drive
        self.pivot_ball = sphere(canvas = canvas, pos = vec(0, 0, 0), radius = .02, color = color.green)
        self.air_density = 1.23
        
        self.current_method = self.euler_kromer
        self.current_method_name = "Euler-Kromer"

    def update(self):
        if (t * 100 // 1 % 2 == 0):
            self.graphs.update_graphs(t, self.theta, self.omega, self.alpha, self.drive_force, self.ke, self.u)

    def euler_kromer(self):
        self.alpha = self.get_alpha(t, self.theta, self.omega)
        self.omega += self.alpha * dt
        self.theta += self.omega * dt
        if (self.theta > pi or self.theta < -pi): 
            self.theta = self.theta_shift()
            self.graphs.shifted = True
    
    def rk4(self):
        k1_theta = self.omega
        k1_omega = self.get_alpha(t, self.theta, self.omega)
        
        k2_theta = self.omega + k1_omega * dt / 2
        k2_omega = self.get_alpha(t + dt / 2, self.theta + k1_theta * dt / 2, self.omega + k1_omega * dt / 2)
        
        k3_theta = self.omega + k2_omega * dt / 2
        k3_omega = self.get_alpha(t + dt / 2, self.theta + k2_theta * dt / 2, self.omega + k2_omega * dt / 2)
        
        k4_theta = self.omega + k3_omega * dt 
        k4_omega = self.get_alpha(t + dt, self.theta + k3_theta * dt, self.omega + k3_omega * dt)
        
        self.theta += dt * (k1_theta + 2 * k2_theta + 2 * k3_theta + k4_theta) / 6 
        self.omega += dt * (k1_omega + 2 * k2_omega + 2 * k3_omega + k4_omega) / 6
        self.alpha = self.get_alpha(t, self.theta, self.omega)
                
        if (self.theta > pi or self.theta < -pi): 
            self.theta = self.theta_shift()
            self.graphs.shifted = True

    def reset(self):
        self.theta = pi/6
        self.omega = 0
        self.alpha = 0
        
        self.update_angle_slider()
        
    def update_angle_slider(self):
        self.angle_slider.display.text = f"{self.theta / pi * 180:1.2f} deg"
        self.angle_slider.value = self.theta / pi * 180

    def render(self):
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)

    def create_inputs(self, user_inputs):
        user_inputs.append_to_caption("\nApproximation Method: ")
        
        self.method_dropdown = menu(bind=self.change_method, choices=["Euler-Kromer", "Runge-Kutta Order 4"], selected=self.current_method_name)
        self.method_dropdown.pendulum = self # to get around glowscript class issues
        

    def hide_inputs(self):
        for input in self.inputs_list:
            input.delete()
            
    def change_method(self, evt):
        if evt.index == 0: 
            evt.pendulum.current_method = evt.pendulum.euler_kromer
            evt.pendulum.current_method_name = "Euler-Kromer"
        elif evt.index == 1: 
            evt.pendulum.current_method = evt.pendulum.rk2
            evt.pendulum.current_method_name = "Runge-Kutta Order 2"
        elif evt.index == 2: 
            evt.pendulum.current_method = evt.pendulum.rk4
            evt.pendulum.current_method_name = "Runge-Kutta Order 4"
#        print(evt.pendulum.current_method_name)

    #converts theta to equivalent angle in [-pi, pi]
    def theta_shift(self):
        theta_shifted = self.theta % (2 * pi)
        if (theta_shifted < 0):
            theta_shifted += 2 * pi
        if (theta_shifted > pi):
            theta_shifted -= 2 * pi
        return theta_shifted

class SimplePendulum(Pendulum):
    def __init__(self, c, drive, line_color, user_inputs, graphs):
        Pendulum.__init__(self, c, drive)
        
        self.length = 1
        self.mass = .1
        self.radius = .1
        self.amp = 1
        self.freq = .3
        self.type = "Simple Pendulum"
        self.line_color = line_color

        self.pivot = vector(0,0,0)
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)
        self.string = cylinder(canvas = c, pos = self.pivot, axis = self.pos - self.pivot, color = color.black, radius = 0.01)
        self.bob = sphere(canvas = c, pos = self.pos, radius = self.radius, color = getattr(color, line_color))
    
        self.drag_coefficient = .5 * self.air_density * .47 * pi * self.bob.radius ** 2

        user_inputs.select()
        self.create_inputs(user_inputs)
        self.graphs = graphs
        c.range = (self.length + self.radius) * 1.5

    def change_values(self, evt):
        if not hasattr(evt, 'parameter'):
            return
    
        if (evt.parameter == "theta"):
            setattr(self, evt.parameter, evt.value * pi / 180)
        else:
            setattr(self, evt.parameter, evt.value) #takes parameter as string and sets to value
        evt.display.text = f"{evt.value:1.2f} {evt.unit}"
        self.nfreq_text.text = f"Natural Frequency: {sqrt(9.81 / self.length) / 2 / pi:1.4f} hz"
        self.bob.radius = self.radius
        self.canvas.range = (self.length + self.radius) * 1.5
        self.drag_coefficient = .5 * self.air_density * .47 * pi * self.bob.radius ** 2
        self.render()
        
    def change_method(self, evt):
        Pendulum.change_method(self, evt)
        
    def update(self):
        self.current_method()
        
        self.ke = .5 * self.mass * (self.length * self.omega) ** 2
        self.u = self.mass * 9.81 * (self.length * (1 - cos(self.theta)))
        Pendulum.update(self)
    
    def get_alpha(self, time, theta, omega):
        self.drag_component = - self.drag_coefficient * self.length / self.mass * omega * abs(omega)
        self.g_component = - 9.81 / self.length * sin(theta)
        self.drive_force = self.drive(time, self.amp, self.freq)
        self.drive_component = self.drive_force / self.length / self.mass      
        
        return self.drag_component + self.g_component + self.drive_component
        
    def reset(self):
        Pendulum.reset(self)

    def render(self):
        Pendulum.render(self)

        self.bob.pos = self.pos
        self.string.axis = self.pos - self.pivot

    def create_inputs(self, user_inputs):
        Pendulum.create_inputs(self, user_inputs)
        
        user_inputs.append_to_caption("\n\nMass: ")

        self.mass_slider = slider(bind = self.change_values, max = 10, min = 0.1, step = 0.1, value = self.mass)
        self.mass_slider.parameter = "mass"
        self.mass_slider.display = wtext(text=f"{self.mass_slider.value:1.2f} kg")
        self.mass_slider.unit = "kg"

        user_inputs.append_to_caption("\n\nString Length: ")
        self.length_slider = slider(bind = self.change_values, max = 10, min = 1, step = .1, value = self.length)
        self.length_slider.parameter = "length"
        self.length_slider.display = wtext(text=f"{self.length_slider.value:1.2f} m")
        self.length_slider.unit = "m"

        user_inputs.append_to_caption("\n\nBall Radius: ")
        self.radius_slider = slider(bind = self.change_values, max = 1, min = 0.1, step = 0.01, value = self.radius)
        self.radius_slider.parameter = "radius"
        self.radius_slider.display = wtext(text=f"{self.radius_slider.value:1.2f} m")
        self.radius_slider.unit = "m"

        user_inputs.append_to_caption("\n\nAngle: ")
        self.angle_slider = slider(bind = self.change_values, max = 180, min = -180, step = 1, value = self.theta * 180 / pi)        
        self.angle_slider.parameter = "theta"
        self.angle_slider.display = wtext(text=f"{self.angle_slider.value:1.2f} deg")
        self.angle_slider.unit = "deg"
        
        user_inputs.append_to_caption("\n\nAir Density: ")
        self.density_slider = slider(bind = self.change_values, max = 5, min = 0, step = .01, value = self.air_density)        
        self.density_slider.parameter = "air_density"
        self.density_slider.display = wtext(text=f"{self.density_slider.value:1.2f} kg/m^3")
        self.density_slider.unit = "kg/m^3"

        user_inputs.append_to_caption("\n\nDrive Amplitude: ")
        self.amp_slider = slider(bind = self.change_values, max = 100, min = 0, step = 0.1, value = self.amp)
        self.amp_slider.parameter = "amp"
        self.amp_slider.display = wtext(text=f"{self.amp_slider.value:1.2f} N")
        self.amp_slider.unit = "N"

        user_inputs.append_to_caption("\n\nDrive Frequency: ")
        self.freq_slider = slider(bind = self.change_values, max = 1, min = 0, step = .01, value = self.freq)        
        self.freq_slider.parameter = "freq"
        self.freq_slider.display = wtext(text=f"{self.freq_slider.value:1.2f} hz")
        self.freq_slider.unit = "hz"
        user_inputs.append_to_caption("\n\n")
        self.nfreq_text = wtext(text=f"Natural Frequency: {sqrt(9.81 / self.length) / 2 / pi:1.4f} hz")
        user_inputs.append_to_caption("\n \n")

        self.inputs_list = [self.mass_slider, self.length_slider, self.radius_slider, self.angle_slider, self.density_slider, self.amp_slider, self.freq_slider]

    def hide_inputs(self):
        Pendulum.hide_inputs(self)
        
    def erase(self):
        self.string.visible = False
        self.bob.visible = False

class RodPendulum(Pendulum):
    def __init__(self, c, drive, line_color, user_inputs, graphs):
        Pendulum.__init__(self, c, drive)
        self.length = 1
        self.mass = .1
        self.radius = .1
        self.amp = 1
        self.freq = .3
        self.type = "Rod Pendulum"
        self.line_color = line_color

        self.pivot = vector(0,0,0)
        self.pos = vector(self.length * sin(self.theta), -self.length * cos(self.theta), 0)
        self.rod = cylinder(canvas = c, pos = self.pivot, axis = self.pos - self.pivot, color = getattr(color, line_color), radius = self.radius)

        self.drag_coefficient = .5 * self.air_density * 1.17 * 2 * self.radius * self.length
        
        user_inputs.select()
        self.create_inputs(user_inputs)
        self.graphs = graphs
        c.range = (self.length + self.radius) * 1.5

    def change_values(self, evt):
        if not hasattr(evt, 'parameter'):
            return
    
        if (evt.parameter == "theta"):
            setattr(self, evt.parameter, evt.value * pi / 180)
        else:
            setattr(self, evt.parameter, evt.value) #takes parameter as string and sets to value
        evt.display.text = f"{evt.value:1.2f} {evt.unit}"
        self.nfreq_text.text = f"Natural Frequency: {sqrt(3 * 9.81 / 2 / self.length) / 2 / pi:1.4f} hz"
        self.rod.radius = self.radius
        self.canvas.range = self.length * 1.5
        self.drag_coefficient = .5 * self.air_density * 1.17 * 2 * self.radius * self.length
        self.render()
        
    def update(self):
        self.current_method()

        self.ke = .5 * 1 / 3 * self.mass * (self.length * self.omega) ** 2
        self.u = self.mass * 9.81 * self.length / 2 * (1 - cos(abs(self.theta))) # center of mass
        Pendulum.update(self)
        
    def get_alpha(self, time, theta, omega):
        self.drag_component = - 3 / 4 * self.drag_coefficient * self.length ** 2 / self.mass * omega * abs(omega)
        self.g_component = - 3 / 2 * 9.81 / self.length * sin(theta) 
        self.drive_force = self.drive(time, self.amp, self.freq)
        self.drive_component = 3 / 2 * self.drive_force / self.length / self.mass # this assumes the drive force is applied at the COM
        
        return self.drag_component + self.g_component + self.drive_component

    def update_graphs(self):
        self.ke = .5 * 1 / 3 * self.mass * (self.length * self.omega) ** 2
        self.u = self.mass * 9.81 * self.length / 2 * (1 - cos(self.theta)) # center of mass
        self.graphs.update_graphs()

    def reset(self):
        Pendulum.reset(self)

    def render(self):
        Pendulum.render(self)

        self.rod.axis = self.pos - self.pivot

    def create_inputs(self, user_inputs):
        Pendulum.create_inputs(self, user_inputs)
        
        user_inputs.append_to_caption("\n\nMass: ")

        self.mass_slider = slider(bind = self.change_values, max = 10, min = 0.1, step = 0.1, value = self.mass)
        self.mass_slider.parameter = "mass"
        self.mass_slider.display = wtext(text=f"{self.mass_slider.value:1.2f} kg")
        self.mass_slider.unit = "kg"

        user_inputs.append_to_caption("\n\nRod Length: ")
        self.length_slider = slider(bind = self.change_values, max = 10, min = 1, step = .01, value = self.length)
        self.length_slider.parameter = "length"
        self.length_slider.display = wtext(text=f"{self.length_slider.value:1.2f} m")
        self.length_slider.unit = "m"

        user_inputs.append_to_caption("\n\nRod Radius: ")
        self.radius_slider = slider(bind = self.change_values, max = .5, min = 0.01, step = 0.01, value = self.radius)
        self.radius_slider.parameter = "radius"
        self.radius_slider.display = wtext(text=f"{self.radius_slider.value:1.2f} m")
        self.radius_slider.unit = "m"

        user_inputs.append_to_caption("\n\nAngle: ")
        self.angle_slider = slider(bind = self.change_values, max = 180, min = -180, step = 1, value = self.theta * 180 / pi)        
        self.angle_slider.parameter = "theta"
        self.angle_slider.display = wtext(text=f"{self.angle_slider.value:1.2f} deg")
        self.angle_slider.unit = "deg"
        
        user_inputs.append_to_caption("\n\nAir Density: ")
        self.density_slider = slider(bind = self.change_values, max = 5, min = 0, step = .01, value = self.air_density)        
        self.density_slider.parameter = "air_density"
        self.density_slider.display = wtext(text=f"{self.density_slider.value:1.2f} kg/m^3")
        self.density_slider.unit = "kg/m^3"

        user_inputs.append_to_caption("\n\nDrive Amplitude: ")
        self.amp_slider = slider(bind = self.change_values, max = 100, min = 0, step = 0.1, value = self.amp)
        self.amp_slider.parameter = "amp"
        self.amp_slider.display = wtext(text=f"{self.amp_slider.value:1.2f} N")
        self.amp_slider.unit = "N"

        user_inputs.append_to_caption("\n\nDrive Frequency: ")
        self.freq_slider = slider(bind = self.change_values, max = 1, min = 0, step = .01, value = self.freq)        
        self.freq_slider.parameter = "freq"
        self.freq_slider.display = wtext(text=f"{self.freq_slider.value:1.2f} hz")
        self.freq_slider.unit = "hz"
        user_inputs.append_to_caption("\n\n")
        self.nfreq_text = wtext(text=f"Natural Frequency: {sqrt(3 * 9.81 / 2 / self.length) / 2 / pi:1.4f} hz")
#        user_inputs.append_to_caption("\n \n")
        
        scene.append_to_caption("\n\n")

        self.inputs_list = [self.mass_slider, self.length_slider, self.radius_slider, self.angle_slider, self.density_slider, self.amp_slider, self.freq_slider]

    def hide_inputs(self):
        Pendulum.hide_inputs(self)
        
    def erase(self):
        self.rod.visible = False

def play_button(evt):
    global play
    play = not play
    p1.update_angle_slider()
    p2.update_angle_slider()

def reset_button(evt):
    global t, theta, omega, alpha, play 
    t = 0
    play = False
    p1.graphs.clear_graphs()
    p1.reset()
    p1.render()
    p2.graphs.clear_graphs()    
    p2.reset()
    p2.render()
    p1.phase_lines = []
    p2.phase_lines = []
    p1.shifted = False
    p2.shifted = False
    
def toggle_canvas(evt):
    if (evt.c2.active):
        evt.text = "Enable Pendulum 2"
        c2.background = color.gray(0.5)
    else:
        evt.text = "Disable Pendulum 2"
        c2.background = color.white
    evt.c2.active = not evt.c2.active
    
def simple_pendulum(c, drive, line_color, user_inputs, graphs):
    return SimplePendulum(c, drive, line_color, user_inputs, graphs)
    
def rod_pendulum(c, drive, line_color, user_inputs, graphs):
    return RodPendulum(c, drive, line_color, user_inputs, graphs)
    
def change_type(evt):
    global p1, p2, t, play
    pendulum_array = [p1, p2]
        
    p1.hide_inputs()
    p2.hide_inputs() 
    p1_graphs = p1.graphs
    p2_graphs = p2.graphs
#    user_inputs.caption = ""
#    if (evt.pendulum == 0):
#        init_buttons(user_inputs, evt.selected, p2.type)
#    else:
#        init_buttons(user_inputs, p1.type, evt.selected)
    p1.erase()
    p2.erase()
    
    # this section is a bit inefficient but i didnt want to mess w/ function-valued dicts since i was getting an issue w/ them earlier
    type_array = [0, 0]
    
    if evt.selected == "Simple Pendulum":
        type_array[evt.pendulum] = simple_pendulum
    elif evt.selected == "Rod Pendulum":
        type_array[evt.pendulum] = rod_pendulum
        
    if pendulum_array[evt.pendulum - 1].type == "Simple Pendulum":
        type_array[evt.pendulum - 1] = simple_pendulum
    elif pendulum_array[evt.pendulum - 1].type == "Rod Pendulum":
        type_array[evt.pendulum - 1] = rod_pendulum

    # glowscript was treating functions referenced by type_array[i] as async functions
    if (type_array[0] == simple_pendulum):
        pendulum_array[0] = simple_pendulum(c1, drive, p1.line_color, user_inputs, p1_graphs)
    else:
        pendulum_array[0] = rod_pendulum(c1, drive, p1.line_color, user_inputs, p1_graphs)
    if (type_array[1] == simple_pendulum):
        pendulum_array[1] = simple_pendulum(c2, drive, p2.line_color, user_inputs, p2_graphs)
    else:
        pendulum_array[1] = rod_pendulum(c2, drive, p2.line_color, user_inputs, p2_graphs)
        
    p1 = pendulum_array[0]
    p2 = pendulum_array[1]
    t = 0
    p1.graphs.clear_graphs()
    p2.graphs.clear_graphs()
    play = False
    render_tab(active_tab)
    
def init_buttons(user_inputs, p1_type, p2_type):
    user_inputs.select()
    toggle_simulation = button(bind = play_button, text = "Play/Pause")
    reset = button(bind = reset_button, text = "Reset")
    disable_c2 = button(bind = toggle_canvas, text = "Disable Pendulum 2")
    disable_c2.c2 = c2
    user_inputs.append_to_caption("\n\n")
    tab_clear = button(bind = change_tab, text="Close tabs", tab = -1)
    tab0 = button(bind = change_tab, text="Instructions", tab = 0)
    tab1 = button(bind = change_tab, text="Edit Pendulum 1", tab = 1)
    tab2 = button(bind = change_tab, text="Edit Pendulum 2", tab = 2)
    
def change_tab(evt):
    global active_tab
    active_tab = evt.tab
    render_tab(active_tab)
    
def render_tab(tab):
    user_inputs.caption = ""
    init_buttons(user_inputs, p1.type, p2.type)
    if (tab == -1):
        user_inputs.append_to_caption("\n\n")
    if (tab == 0):
        info_text = wtext(text="""
            \n\n<div style='width:100px;'><b style='font-size: 20px;'>Instructions **WIP**</b>
            <p>To alter the properties of the pendula, use the tabs (the second row of buttons) to select the pendulum you’d like to edit. To change the pendulum type, click on the dropdown and select the desired pendulum. Note that this will reset the properties of both pendulums, so you should make sure that the desired types are selected before altering other settings. You can also choose the approximation method used for each pendulum: either Euler-Kromer or Runge-Kutta 4 (the latter providing a more accurate approximation). Physical properties of each pendulum can be altered using the sliders: mass, length, radius, and starting angle. There are also sliders for the air density (which affects the drag force), and the amplitude/frequency of the drive function, which is of the form Acos(f*2pi*t). The natural frequency of each pendulum (being the frequency with only the force of gravity) is also displayed, and updates as the length is changed. Note that the driving force is applied at the center of mass of the pendulum: for the simple pendulum, this is at the center of the bob; for the rod pendulum, it lies on the rod’s axis, halfway between the two ends. To reset the properties of the pendula, simply change the type of one of the pendula. Click the “close tabs” button to close all of the tabs. If you would like to read the instructions again, click the “instructions” tab.</p>
            <p>The first row of buttons are the simulation controls. The first button pauses/unpauses, the second button resets the simulation (preserving all settings), and the third button enables/disables the second pendulum, which is indicated by the background color of the canvas being white or gray, respectively. </p>
            <p>When the simulation plays, graphs are rendered for each pendulum. The red set of graphs corresponds to the first pendulum (which is also colored red), and the blue set of graphs corresponds to the second, blue pendulum. There are five different graphs for each one: angular velocity against time, angular acceleration against time, driving force against time, kinetic/potential energy against time, and angular velocity against angular position. The last graph, known as the phase graph, is useful for highlighting the chaotic behavior of the system. If the settings are correct, you will see an initial period of chaotic motion, followed by stable, almost periodic motion around an attractor (manifested in the phase graph by the curve looping around the same point many times).</p>
            <p>For the best results, set the frequency of the driving force close to the pendulum’s natural frequency, and ensure that the amplitude of the force is greater than (but still in the ballpark of) the weight of the pendulum (which, of course, is approximately 10 times the mass).</p></div>
        """)
    if (tab == 1):
        user_inputs.append_to_caption("\n\n<b style='font-size: 20px;'>Pendulum 1</b>")
        user_inputs.append_to_caption("\n\nPendulum Type: ")
        dropdown1 = menu(bind = change_type, choices=["Simple Pendulum", "Rod Pendulum"], selected = p1.type, pendulum = 0)
        user_inputs.append_to_caption("\n")
        p1.create_inputs(user_inputs)
    if (tab == 2):
        user_inputs.append_to_caption("\n\n<b style='font-size: 20px;'>Pendulum 2</b>")
        user_inputs.append_to_caption("\n\nPendulum Type: ")
        dropdown2 = menu(bind = change_type, choices=["Simple Pendulum", "Rod Pendulum"], selected = p2.type, pendulum = 1)
        user_inputs.append_to_caption("\n")
        p2.create_inputs(user_inputs)
    
def drive(time, amp, freq):
    return amp * cos(freq * 2 * pi * time)
    
c1 = canvas(width=500, height=500, background = color.white, align="left")
c1.userzoom = False
c1.userpan = False
c2 = canvas(width=500, height=500, background = color.white, align="left")
c2.userzoom = False
c2.userpan = False
c2.active = True

scene.append_to_caption("\n\n")

user_inputs = canvas(width = 1, height = 1, background = color.white)
init_buttons(user_inputs, "Simple Pendulum", "Rod Pendulum")

c2.append_to_caption("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

g1 = Graphs(c1, "red")
g2 = Graphs(c2, "blue")

p1 = SimplePendulum(c1, drive, "red", user_inputs, g1)
p2 = RodPendulum(c2, drive, "blue", user_inputs, g2)

render_tab(0)
#g_canvas = canvas(width=1000, height=1000, background = color.white)

while (True):
    rate(100)
    if (play):
        p1.update()
        p1.render()
        # add check that c2 is active
        if (c2.active):
            p2.update()
            p2.render()
        t += dt


