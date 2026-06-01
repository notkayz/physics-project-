from vpython import *
# canvas setup and camera 
s1 = canvas(align = "left", width = 500, height = 500, 
               background = color.white)
s1.userzoom = False
s1.userpan = False

# s2 = canvas(align = "left", width = 500, height = 500, background = color.red)

# pendulum init conditions 
mass = 0.1
length = 1
theta0 = radians(30) # radians
g = 9.81
t = 0
dt = 0.01
play = False

theta = theta0 
omega = 0
alpha = 0

# driving force
amp = .981 * 3
freq = sqrt(g) - .1

# buttons 

def playPauseButton (evt) :
    global play
    if evt.text == "Play/Pause":
        play = not play

playPause = button (bind= playPauseButton, text = "Play/Pause")

def resetButton (evt) :
    global t, theta, omega, alpha, play 
    if evt.text == "Reset":
        t = 0
        theta = theta0 
        omega = 0
        alpha = 0
        play = False
        omegaDots.delete()
        alphaDots.delete()
        driveDots.delete()
        keDots.delete()
        uDots.delete()
        thetaDots.delete()

reset = button(bind = resetButton, text = "Reset")

# graphs
t_frame = 10

g1 = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Velocity (rad/s)"), align='left')
omegaDots=gdots(color=color.green, graph=g1)

g2 = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Angular Acceleration (rad/s^2)"), align='left')
alphaDots=gdots(color=color.green, graph = g2)

g3 = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("Driving Force (N)"), align='left')
driveDots=gdots(color=color.green, graph = g3)

g4 = graph(width=350, height=250, xtitle=("Time (s)"), ytitle=("KE (red) and U (green) (J)"), align='left')
keDots=gdots(color=color.red, graph = g4)
uDots=gdots(color=color.green, graph=g4)

g5 = graph(width=350, height=250, xtitle=("Angular Position (rad)"), ytitle=("Angular Velocity (rad/s)"), align='left', xmin=-pi, xmax=pi)
thetaDots=gdots(color=color.red, graph = g5)

# object stuff

pivot = vector(0,0,0)

ball_pos = vector(length * sin(theta), -length * cos(theta), 0)

lever = cylinder(canvas = s1, pos = pivot, axis = ball_pos - pivot, color = color.black, radius = 0.01)
                
ball = sphere(canvas = s1, pos = ball_pos, radius = 0.1, color = color.red )#,make_trail = True)

# drag info

# Fd = 1/2 pv^2 CA ; p = air density, v = velocity, C = drag constant, A = area ; 1/2 bv^2

rho = 1.225
C = 0.47
A = pi * (ball.radius ** 2)

drag_constant = 0.5 * rho * C * A

# sliders 
s1.append_to_caption("\n \n <b> Parameters : </b> \n \n Mass : ")

def changeMass (evt) : 
    global mass, massText
    if evt.id == 'm':
        mass = evt.value
        massText.text = '{:1.2f} kgs'.format(massSlider.value)

massSlider = slider (bind = changeMass, max = 1, min = 0.1, step = 0.1, value = mass, id = 'm')
massText = wtext(text='{:1.2f} kgs'.format(massSlider.value))

s1.append_to_caption("\n \n Length :")

def changeLength (evt) : 
    global length, lengthText
    if evt.id == 'l':
        length = evt.value
        lengthText.text = '{:1.2f} m'.format(lengthSlider.value)
        s1.range = (length + ball.radius) * 1.5

lengthSlider = slider (bind = changeLength, max = 10, min = 1, step = 1, value = length, id = 'l')
lengthText = wtext(text='{:1.2f} m'.format(lengthSlider.value))

s1.append_to_caption("\n \n Radius : ")

def changeBall (evt) : 
    global length, radiusText
    if evt.id == 'r':
        ball.radius = evt.value
        radiusText.text = '{:1.2f} m'.format(radiusSlider.value)
        scene.range = (length + ball.radius) * 1.5

radiusSlider = slider (bind = changeBall, max = 1, min = 0.1, step = 0.1, value = ball.radius, id = 'r')
radiusText = wtext(text='{:1.2f} m'.format(radiusSlider.value))
    
s1.append_to_caption("\n \n")

while (True) :
    if (play) :
        rate(100)
        
        velocity = omega * length
        
        # torque forces
        fdrag = -drag_constant * velocity * abs(velocity)
        fg = -mass * g * sin(theta)  
        fdrive = amp * cos(freq * t)
    #    fdrive = amp * sin(3 * cos(freq * t) + sin(freq * t))
    #    fdrive = .5 * (exp(sin(t)) - 1)
    #    fdrive = amp * sign(sin(t))
    #    fdrive = 5 * cos(t)+ 2 * sin(3 * t)
        torqTotal = (fdrag + fg + fdrive) * length
        alpha = torqTotal / (mass * length**2)
        
        KE = 1/2 * mass * (velocity**2)
        U = mass * g * (length * (1 - cos( abs(theta) ) ) )

        omegaDots.plot(t, omega)
        alphaDots.plot(t, alpha)
        driveDots.plot(t, fdrive)
        keDots.plot(t, KE)
        uDots.plot(t, U)
        thetaDots.plot(theta, omega)
        
        if (t > t_frame):
            g1.xmin = t - t_frame
            g1.xmax = t
            g2.xmin = t - t_frame
            g2.xmax = t
            g3.xmin = t - t_frame
            g3.xmax = t
            g4.xmin = t - t_frame
            g4.xmax = t
        
        omega += alpha * dt
        theta += omega * dt
        
        theta %= 2 * pi
        if (theta < 0):
            theta += 2 * pi
        if (theta > pi):
            theta -= 2 * pi
        
        ball_pos = vector(length * sin(theta), -length*cos(theta), 0)
        ball.pos = ball_pos
        lever.axis = ball_pos - pivot
        
        t += dt

