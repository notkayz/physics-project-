from vpython import * 

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

# object stuff

pivot = vector(0,0,0)

ball_pos = vector(length * sin(theta), -length * cos(theta), 0)

lever = cylinder(pos = pivot, axis = ball_pos - pivot, color = color.black, radius = 0.01)
                
ball = sphere(pos = ball_pos, radius = 0.1, color = color.red, make_trail = True)

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
    
    torqTotal = (fdrag + fg) * length
    alpha = torqTotal / (mass * length**2)
    
    omega += alpha * dt
    theta += omega * dt
    
    ball_pos = vector(length * sin(theta), -length*cos(theta), 0)
    ball.pos = ball_pos
    lever.axis = ball_pos - pivot
    
    t += dt

