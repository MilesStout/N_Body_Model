import numpy as np
import matplotlib.pyplot as plt  
from scipy.integrate import solve_ivp
import matplotlib.animation as animation
import time as time
np.set_printoptions(threshold=np.inf)



#possible problems:

#Users can input the same xyz pair for each body in initialarray. This could result in a crash

#Writing output to a txt file seems really inefficient

#Run time gets very long as bodies increases.

#No error handling

#Spaghetti Code

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#debug methods

def timedebug(timedatacheck):
    print(type(timedatacheck))
    f = open("timefile.txt", "w")
    f.write(str(timedatacheck))
    f.close
    return "Time Debug Complete: Check Generated .txt File. "

def soldebug(solcheck):
    print(np.shape(solcheck))
    print(type(solcheck))
    with open("solutionarrayfile.txt", "w") as f:
        f.write(str(solcheck))

    
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Helper Functions

#Prompts the user to select their constant of gravitation which will be assigned to a global variable
def selectgravitationconst():
    select_var = float(input("Please enter the constant of gravitation you would like to use.\nType 0 for the default: "))
    match select_var:
        case 0:
            grav_const = 6.67430e-11
        case _:
            grav_const = select_var
   
    return grav_const

#This method takes the zero 1-array and prompts the user to fill each entry with a float. returns a 1-array with inputted values
def initialarray(n):
        
    ticker = 0
    bodies = int(n)
    entries = 6*bodies
    init_array = bodiesarray(bodies)
    bodycount = 1
    for i in range(entries):
        clock = i % 6
        match clock:
            case 0:
                init_array[ticker:(ticker + 1)] = float(input(f"Please input the starting x position (as a float) for body {bodycount}: "))
                clock += 1
                ticker += 1
            case 1:
                init_array[ticker:(ticker + 1)] = float(input(f"Please input the starting y position (as a float) for body {bodycount}: "))
                clock += 1
                ticker += 1
            case 2:
                init_array[ticker:(ticker + 1)] = float(input(f"Please input the starting z position (as a float) for body {bodycount}: "))
                clock += 1
                ticker += 1
            case 3:
                init_array[ticker:(ticker + 1)] = float(input(f"Please input the starting x velocity (as a float) for body {bodycount}: "))
                clock += 1
                ticker += 1
            case 4:
                init_array[ticker:(ticker + 1)] = float(input(f"Please input the starting y velocity (as a float) for body {bodycount}: "))
                clock += 1
                ticker += 1
            case 5:
                init_array[ticker:(ticker + 1)] = float(input(f"Please input the starting z velocity (as a float) for body {bodycount}: "))
                clock += 1
                ticker += 1
                bodycount += 1
        

    return init_array

#This method takes the number of bodies and generates an zero 1-array with the correct size and shape
def bodiesarray(n):
    bodies = n
    entries = 6*bodies
    body_array = np.zeros(entries)
    return body_array

#Prompts the user to enter masses for all of the bodies. Organizes it as a 1-array
def massarray(n):
    ticker = 0
    bodies = int(n)
    mass_array = np.zeros(bodies)
    for i in range(bodies):
            mass_array[ticker: (ticker + 1)] = float(input(f"Enter the mass(kg) of body  {(ticker + 1)}: "))
            ticker += 1
    return mass_array

#This method converts the 1-array into a 2-array. Organized as [[p_1], [v_1], ... [p_n], [v_n]]
def c_arraygenerator(y):
    bodies = int(np.size(y)/6)
    c_array = np.zeros((2*bodies, 3))
    rows = 2*bodies

    clock_total = 0
    for i in range(rows):
        clock_outer = i
        clock_inner = 0
        


        pass
        for j in range(3):



            c_array[clock_outer, clock_inner] = y[clock_total]

            clock_inner += 1
            clock_total += 1



    #print(c_array)            
    return c_array

#This method takes c_array and chops the velocity vectors out. returns 2-array with only position information
def c_array_to_p_array(y):
    shape = np.shape(y)
    tot_rows = shape[0]
    del_rows = int(tot_rows/2)
    p_array = np.array(y)
    for i in range(del_rows):
        p_array = np.delete(p_array, i+1, 0)
    
    return p_array

#This method computes all of the relationships between the bodies. Returns d_array with shape it takes p_array as the input
def directioncalc(y,n):
    bodies = n
    p_array = np.array(y) #looks like [[r_1x,r_1y,r_1z],[r_2x,r_2y,r_2z],[r_3x,r_3y_r_3z], ... , [r_nx, r_ny, r_nz]]
    d_array = np.zeros((bodies,bodies,3 )) 
    #fill d_array with correct values
    for i in range(bodies):
        d_array[i: i+1] = p_array[i: i+1]
    for i in range(bodies):
        d_array[i: i+1] = p_array - p_array[i: i+1]
    return d_array

#Computes and stores norms between all bodies in a 2-array
def normcalculator(y, n):
    bodies = n
    temp_array = np.zeros((bodies,bodies))
    d_array = np.array(y)
    norm_array = np.zeros((bodies, bodies))
    for i in range(bodies):
        temp_array = np.squeeze(d_array[i: i+1])
        for k in range(bodies):
            norm_array[i,k] = np.linalg.norm(temp_array[k:k+1])

    return norm_array

#this is the diffeq that the acceleration_comp method calls
def gravitation_equation(r_ij, R_ij, G, m_j, i = 0, j = 0):
    accel_component = np.zeros(3)
    r_ij = np.squeeze(r_ij)
    accel_component = G*((m_j*r_ij)/(R_ij**3))
    return accel_component

#creates a 2-array with acceleration values for all of the bodies
def acceleration_comp(directionarray, normarray, mass_array, G_const, nbodies_const):
    eps = 1e-12
    #number of bodies in the system
    bodies = nbodies_const
    #will contain all needed direction vectors
    d_array = directionarray
    #will contain all needed norms
    n_array = normarray
    #this will end up being the finished array
    accel_array = np.zeros((bodies, 3))

    for i in range(bodies):
        accel_temp_array = np.zeros((bodies,3))
        temp_darray = np.squeeze(d_array[i:i+1])
        for j in range(bodies):

            temp_darray2 = np.squeeze(temp_darray[j: j+1]) 
            temp_normconst = n_array[(i,j)]
            temp_massconst = mass_array[(j)] 
            if i == j:
                continue
            if temp_normconst < eps:
                print("Zero division detected, doing small regularization")
                temp_normconst = eps
            
            #we will then send our information to the method gravitation_equation. This method could technically be switched out for any other diffeq which takes the same inputs.
            accel_temp_array[j:j+1] = gravitation_equation(temp_darray2,temp_normconst,G_const,temp_massconst)
            

            accel_array[i:i+1] += accel_temp_array[j:j+1]

            

    #print(accel_array)
    return accel_array

#This will have the user determine the length of the simulation, and the amount of time steps modelled by the integrator
def timeselect():
    
    #once again using global variables because i am lazy
    global time_tot
    time_tot = int(input("Please enter the number of seconds you would like the system to be modelled for: "))
    
    global time_subdivide
    time_subdivide = int(input("Please enter the amount of simulation steps you would like modelled (the more steps the more accurate): "))
    
    time_eval = np.linspace(0.0, time_tot, time_subdivide)
    
    return time_eval

#This method will be the middle point between scipys integrator and my helper methods. It takes the solve_ivp output, differentiates it using 5 helper methods, then returns a 1-array to solve_ivp. repeat for time_subdivide steps
def deriv(t, y):
    bodies = int(np.size(y)/6)
    
    c_array = c_arraygenerator(y)
    p_array = c_array_to_p_array(c_array)
    d_array = directioncalc(p_array, bodies)
    n_array = normcalculator(d_array,bodies)
    accel_array = acceleration_comp(d_array,n_array,global_mass_array,gravitation_const,bodies)
    dydt = np.zeros_like(y)
    # print(f"This is what dydt looks like right now\n {dydt}")
    # print()
    # print(f"And this is accel_array\n{accel_array}")
    # print()
    # print(f"and this is what an indexed accel_array looks like\n {accel_array[0:1]}")
    #differentiate position
    for i in range(bodies):
        
        p_dydt_index_start = 6*i
        p_dydt_index_end = p_dydt_index_start + 3
        y_index_start = (6*i) + 3
        y_index_end = y_index_start + 3

        dydt[p_dydt_index_start:p_dydt_index_end] = y[y_index_start:y_index_end]


    #differentiate velocity
    for i in range(bodies):
        
        temp_accel = accel_array[i:i+1]

        v_dydt_index_start = (6*i) + 3
        v_dydt_index_end = v_dydt_index_start + 3

        dydt[v_dydt_index_start:v_dydt_index_end] = temp_accel

        
    #send it back to solve_ivp
    #print(dydt)
    return dydt
        
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Animation System
def update(frame):

    positions = all_positions
    current_position = np.zeros((total_bodies,3))
    for i in range(total_bodies):
        current_position[i,0] = positions[6*i,frame]
        current_position[i,1] = positions[6*i+1,frame]
        current_position[i,2] = positions[6*i+2,frame]

    for point, (x,y,z) in zip(points, current_position):
        point.set_data([x],[y])
        point.set_3d_properties([z])

    for i, (x,y,z) in enumerate(current_position):
        trail_history[i].append([x,y,z])   # store history
        xs = [p[0] for p in trail_history[i]]
        ys = [p[1] for p in trail_history[i]]
        zs = [p[2] for p in trail_history[i]]

        trails[i].set_data(xs, ys)
        trails[i].set_3d_properties(zs)

    return points, trails

def plot_ani_system(save_vid:int):
    #configures initial plot setup
    user_choice:int = save_vid
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(f"{total_bodies}-Bodies simulation:")
    ax.set_xlabel('x')
    ax.set_ylabel('y')  
    ax.set_zlabel('z')
    ax.set_xlim(-1,1)
    ax.set_ylim(-1,1)
    ax.set_zlim(-1,1)
    colors = plt.cm.tab10(np.linspace(0, 1, total_bodies))
    global points
    points = []
    global trail_history
    trail_history = [[] for _ in range(total_bodies)]
    global trails
    trails = []
    for i in range(total_bodies):
        point, = ax.plot([], [], [], 'o', color=colors[i], markersize=8)
        points.append(point)
        trail, = ax.plot([], [], [], '-', color=colors[i], alpha=0.5, linewidth=1.5)
        trails.append(trail)
    plt.tight_layout()
    frames = len(t_eval)
    ani = animation.FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=30, 
    blit=False,
    repeat = True    
)
    match user_choice:
        case 1:
            while True:
                file_name:str = str(input("Please enter a file name: ")) + ".mp4"
                if " " in file_name:
                    print("Please do not use spaces.")
                    continue
                print(f"File will be saved at Outputs/{file_name}")
                print("Rendering Video...")
                ani.save("C:/Users/mrfwa/Documents/Python/Math_Stuff/Outputs/" + file_name, writer = 'ffmpeg', fps = 20)
                print("Done!")
                break
        case 2:
            print("No .mp4 file saved")
        case _:
            print("Invalid option. No .mp4 file saved")
    
    plt.show()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Where the actual program will go
def main():

    print("[Program Begin]")

    #accuracy tolerances for the integrator
    rtol = 1e-9
    atol = 1e-12
    
    
    #using global variables because im lazy
    global total_bodies
    total_bodies = int(input("Please enter the number of bodies you would like to simulate: "))

    main_init_array = initialarray(total_bodies)

    global global_mass_array
    global_mass_array = massarray(total_bodies)

    global gravitation_const
    gravitation_const = selectgravitationconst()
    global t_eval
    t_eval = timeselect()

    print("-----------------------------------------------------------------------------------------------------------------------")

    print("Starting Integration...\n" \
    "Integration In Progress:\n")
    
    sol = solve_ivp(deriv, (0.0, time_tot), main_init_array, method= 'DOP853', t_eval=t_eval, rtol=rtol, atol=atol)
    
    print("Integration Finished;", sol.message)    

    
    soldebug(sol.y)
    global all_positions
    all_positions = sol.y


    user_save_vid:int = int(input("Select an option.\n1: Save an mp4\n2: Discard\n"))
    plot_ani_system(user_save_vid)

    





    print("[Program End]")




if __name__ == "__main__":
    main()