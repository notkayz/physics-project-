Web VPython 3.2
# canvas setup and camera 
scene = canvas(width = 1000, height = 1000, 
               center = vector(0, -1, 0), 
               background = color.white)

# pendulum init conditions 
mass = 0.1
length = 1
theta0 = radians(30) # radians
g = 9.81
t = 0
dt = 0.01

theta = theta0 
omega = 0
alpha = 0

# driving force
amp = .981
freq = pi / 3

# graphs

g1 = graph(width=350, height=250, xtitle=("Time"), ytitle=("Angular Velocity"), align='left')
omegaDots=gdots(color=color.green, graph=g1)

g2 = graph(width=350, height=250, xtitle=("Time"), ytitle=("Angular Acceleration"), align='left')
alphaDots=gdots(color=color.green, graph = g2)

g3 = graph(width=350, height=250, xtitle=("Time"), ytitle=("Driving Force"), align='left')
driveDots=gdots(color=color.green, graph = g3)

g4 = graph(width=350, height=250, xtitle=("Time"), ytitle=("Kinetic and Potential"), align='left')
keDots=gdots(color=color.red, graph = g4)
uDots=gdots(color=color.green, graph=g4)

g5 = graph(width=350, height=250, xtitle=("Angular Position"), ytitle=("Angular Velocity"), align='left', xmin=-pi, xmax=pi)
thetaDots=gdots(color=color.red, graph = g5)

# object stuff

pivot = vector(0,0,0)

ball_pos = vector(length * sin(theta), -length * cos(theta), 0)

lever = cylinder(pos = pivot, axis = ball_pos - pivot, color = color.black, radius = 0.01)
                
ball = sphere(pos = ball_pos, radius = 0.1, color = color.red )#,make_trail = True)

# drag info

# Fd = 1/2 pv^2 CA ; p = air density, v = velocity, C = drag constant, A = area ; 1/2 bv^2

rho = 1.225
C = 0.47
A = pi * (ball.radius ** 2)

drag_constant = 0.5 * rho * C * A


while (True) :
    rate(100)
    
    velocity = omega * length
    
    # torque forces
    fdrag = -drag_constant * velocity * abs(velocity)
    fg = -mass * g * sin(theta)  
    fdrive = amp * cos(freq * t)
    
    torqTotal = (fdrag + fg + fdrive) * length
    alpha = torqTotal / (mass * length**2)
    
    KE = 1/2 * mass * (velocity**2)
    U = mass * g * (length * (1 - cos( abs(theta) ) ) )
    
    omegaDots.plot(t,omega)
    alphaDots.plot(t, alpha)
    driveDots.plot(t, fdrive)
    keDots.plot(t, KE)
    uDots.plot(t, U)
    thetaDots.plot(theta, omega)
    
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
