from vpython import *

# canvas setup and camera 
scene = canvas(width = 1000, height = 1000, 
               center = vector(0, -1, 0), 
               background = color.white)

# pendulum init conditions 
length = 4 
theta0 = radians(30) # radians
g = 9.81
dt = 0.01 

theta = theta0 
omega = 0
velocity = omega * length

pivot_point = vector(0,0,0)

ball_pos = vector(length * sin(theta), -length*cos(theta), 0)

lever = cylinder(pos = pivot_point, axis = ball_pos - pivot_point, 
                 color = color.black, radius = 0.1
                )

ball = sphere(pos = ball_pos, radius = 0.5, 
                color = color.red)


# fd = 1/2 pv^2 CA  p = density of air, v = velocity, C = drag coeff of obj, A = area perpendicular to motion

drag_constant = 0.5 * 1.225 * pi((ball.radius)**2) * 0.47
fd = drag_constant * velocity**2

while (True):
    rate(1000)

    delt_omega = (-g / length * sin(theta)) - fd

    omega += delt_omega * dt
    theta += omega * dt 
    print(theta)

    ball_pos = vector(length * sin(theta), -length*cos(theta), 0)
    ball.pos = ball_pos
    lever.axis = ball_pos - pivot_point
