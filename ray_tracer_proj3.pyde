# This is the provided code for the ray tracing project.
#
# The most important part of this code is the command interpreter, which
# parses the scene description (.cli) files.

from __future__ import division
import traceback
from helper import *

debug_flag = False   # print debug information when this is True

# Containers
lights = []
shapes = []
coordFrame = []

# Global Vars
bgColor = PVector(0, 0, 0)
fov = float(0)
eyePos = PVector(0, 0, 0)
diffuseColor = PVector(0, 0, 0)
ambientColor = PVector(0, 0, 0)
specularColor = PVector(0, 0, 0)
spec_pow = 0
k_refl = 0

def setup():
    size(320, 320) 
    noStroke()
    colorMode(RGB, 1.0)  # Processing color values will be in [0, 1]  (not 255)
    background(0, 0, 0)
    frameRate(30)

# make sure proper error messages get reported when handling key presses
def keyPressed():
    try:
        handleKeyPressed()
    except Exception:
        traceback.print_exc()

# read and interpret a scene description .cli file based on which key has been pressed
def handleKeyPressed():
    if key == '1':
        interpreter("01_one_sphere.cli")
    elif key == '2':
        interpreter("02_three_spheres.cli")
    elif key == '3':
        interpreter("03_shiny_sphere.cli")
    elif key == '4':
        interpreter("04_many_spheres.cli")
    elif key == '5':
        interpreter("05_one_triangle.cli")
    elif key == '6':
        interpreter("06_icosahedron_and_sphere.cli")
    elif key == '7':
        interpreter("07_colorful_lights.cli")
    elif key == '8':
        interpreter("08_reflective_sphere.cli")
    elif key == '9':
        interpreter("09_mirror_spheres.cli")
    elif key == '-':
        interpreter("11_star.cli")
    elif key == '0':
        interpreter("10_reflections_in_reflections.cli")

# You should add code for each command that calls routines that you write.
# Some of the commands will not be used until Part B of this project.
def interpreter(fname):
    global bgColor, fov, currMaterial, eyePos, currShape, diffuseColor, ambientColor, specularColor, spec_pow, k_refl
    
    reset_scene()  # you should initialize any data structures that you will use here
    
    fname = "data/" + fname
    # read in the lines of a file
    with open(fname) as f:
        lines = f.readlines()

    # parse the lines in the file in turn
    for line in lines:
        words = line.split()  # split up the line into individual tokens
        if len(words) == 0:   # skip empty lines
            continue
        if words[0] == 'sphere':
            xyz = PVector(float(words[2]), float(words[3]), float(words[4])) 
            radius = float(words[1])
            shapes.append(Sphere(xyz, radius, diffuseColor, ambientColor, specularColor, spec_pow, k_refl))
        elif words[0] == 'fov':
            fov = float(words[1])
        elif words[0] == 'eye':
            eyePos = PVector(float(words[1]), float(words[2]), float(words[3]))
        elif words[0] == 'uvw':
            for i in range(1, 10):
                coordFrame.append(float(words[i]))
        elif words[0] == 'background':
            bgColor = PVector(float(words[1]), float(words[2]), float(words[3]))
        elif words[0] == 'light':
            xyz = PVector(float(words[1]), float(words[2]), float(words[3]))
            rgb = PVector(float(words[4]), float(words[5]), float(words[6]))
            lights.append(Light(xyz, rgb))
        elif words[0] == 'surface':
            diffuseColor = PVector(float(words[1]), float(words[2]), float(words[3]))
            ambientColor = PVector(float(words[4]), float(words[5]), float(words[6]))
            specularColor = PVector(float(words[7]), float(words[8]), float(words[9]))
            spec_pow = float(words[10])
            k_refl = float(words[11])
        elif words[0] == 'begin':
            currShape = []
        elif words[0] == 'vertex':
            pos = PVector(float(words[1]), float(words[2]), float(words[3]))
            currShape.append(pos)
        elif words[0] == 'end':
            currShape.extend([diffuseColor, ambientColor, specularColor, spec_pow, k_refl])
            shapes.append(Triangle(*currShape))
        elif words[0] == 'render':
            render_scene()    # render the scene (this is where most of the work happens)
        elif words[0] == '#':
            pass  # ignore lines that start with the comment symbol (pound-sign)
        else:
            print ("unknown command: " + word[0])

# render the ray tracing scene
def render_scene():
    global debug_flag, fov, eyePos
    
    for j in range(height):
        for i in range(width):
            # Maybe set a debug flag to true for ONE pixel.
            # Have routines (like ray/sphere intersection)print extra information if this flag is set.
            debug_flag = False
            if i == -1 and j == -1:
                debug_flag = True

            # create an eye ray for pixel (i,j) and cast it into the scene
            
            # calculate direction scalar coefficients
            d = 1/tan(radians(fov)/2) # focal length
            U = ((2*i)/width) - 1
            V = ((2*j)/height) - 1

            # get uvw coordinate frame
            u = PVector(*coordFrame[:3])
            v = PVector(*coordFrame[3:6])
            w = PVector(*coordFrame[6:])
       
            # calculate direction coordinate vectors, -dw, Vv, Uu
            dw = PVector.mult(w, -1 * d) # * -1
            Vv = PVector.mult(v, V)
            Uu = PVector.mult(u, U)

            # calculate direction vector, -dw + Vv + Uu
            dir = PVector.add(dw, PVector.add(Vv, Uu)).normalize()
            
            # create ray vector
            eye_ray = Ray(eyePos, dir)
            
            scene_hit = ray_intersect_scene(eye_ray)

            pix_color = color(*color_shader(scene_hit, eye_ray))
            
            set(i, height - j, pix_color)
            
def ray_intersect_scene(ray):
    # Set placeholder values
    hit = None
    
    for object in shapes:
        currHit = object.intersect(ray)
        if hit == None and currHit != None:
            hit = currHit.copy()
        elif hit != None and currHit != None and currHit.t_val < hit.t_val:
            hit = currHit.copy()

    return hit
    

# here you should reset any data structures that you will use for your scene (e.g. list of spheres)
def reset_scene():
    global bgColor, fov, eyePos, lights, shapes, coordFrame
    # Containers
    lights = []
    shapes = []
    coordFrame = []
    pass

def color_shader(scene_hit, eye_ray, max_depth=10):
    global lights, debug_flag, bgColor
    
    if scene_hit == None:
        return bgColor
    
    pix_color = PVector(0, 0, 0)
    ambientShader = scene_hit.getAmbientColor()
    pix_color = PVector.add(pix_color, ambientShader)
    
    if max_depth > 0 and scene_hit.object.krefl > 0:
        # Calculate reflection
        tinyoffset = PVector.mult(scene_hit.normal, 0.0001)
        point1 = PVector.add(scene_hit.v, tinyoffset)
        point2 = PVector.sub(scene_hit.v, tinyoffset)
        
        if scene_hit.object.type == "sphere":
            d1 = PVector.dist(scene_hit.object.v, point1)
            d2 = PVector.dist(scene_hit.object.v, point2)
            if d1 > d2:
                refl_pos = point1
            else:
                refl_pos = point2
        else:
            d1 = PVector.dist(eye_ray.v, point1)
            d2 = PVector.dist(eye_ray.v, point2)
            if d1 < d2:
                refl_pos = point1
            else:
                refl_pos = point2
        
        ###########
        refl_slope = PVector.add(eye_ray.slope, PVector.mult(scene_hit.normal, PVector.dot(scene_hit.normal, PVector.mult(eye_ray.slope, -1)) * 2))
        refl_ray = Ray(refl_pos, refl_slope)
        refl_hit = ray_intersect_scene(refl_ray)
        refl_color = color_shader(refl_hit, refl_ray, max_depth-1)
        refl_contribution = PVector.mult(refl_color, scene_hit.object.krefl)
        
        pix_color = PVector.add(pix_color, refl_contribution)
        
        if debug_flag:
            print "current hit is: ", scene_hit
            print "reflection ray origin (should be the hit position slightly offset away from the surface): ", refl_pos
            print "R (reflection ray direction): ", refl_slope
            print "reflection hit:", refl_hit
            print "reflected color:", refl_color
            print "reflection contribution (k_refl * reflect_color):", refl_contribution
    
    
    for light in lights:
        show_shadow = False
        
        # Light Normal
        light_norm = PVector.sub(light.v, scene_hit.v).normalize()
        
        # Calculate shadow
        tinyoffset = PVector.mult(light_norm, 0.0001)
        point1 = PVector.add(scene_hit.v, tinyoffset)
        point2 = PVector.sub(scene_hit.v, tinyoffset)
        
        if scene_hit.object.type == "sphere":
            d1 = PVector.dist(scene_hit.object.v, point1)
            d2 = PVector.dist(scene_hit.object.v, point2)
            if d1 > d2:
                shadow_pos = point1
            else:
                shadow_pos = point2
        else:
            d1 = PVector.dist(light.v, point1)
            d2 = PVector.dist(light.v, point2)
            if d1 < d2:
                shadow_pos = point1
            else:
                shadow_pos = point2
        
        shadow_ray = Ray(shadow_pos, light_norm)
        shadow_hit = ray_intersect_scene(shadow_ray)
        
        if shadow_hit != None and (shadow_hit.t_val < PVector.dist(light.v, scene_hit.v)):
            show_shadow = True
            
        if debug_flag:
            print "checking shadow for light with position: ", light.v
            print "hit position: ", scene_hit.v
            print "shadow ray origin (should be the hit position slightly offset away from the surface): ", shadow_ray.v 
            print "shadow ray direction: ", shadow_ray.slope
            print "shadow hit: ", shadow_hit
            print "distance from light to original hit:", PVector.dist(light.v, scene_hit.v)
            print ""
        
        if not show_shadow:
            # Calculate color
            rgb = [0, 0, 0]
            diffuseShader = light.diffuseLight(scene_hit)
            specularShader = light.specularLight(scene_hit, eye_ray)
            
            for i in range(0, 3):
                rgb[i] = diffuseShader[i] + specularShader[i]
            
            pix_color = PVector.add(pix_color, PVector(rgb[0], rgb[1], rgb[2]))
        
    return pix_color
         
    
# prints mouse location clicks, for help debugging
def mousePressed():
    print ("You pressed the mouse at " + str(mouseX) + " " + str(mouseY))

# this function should remain empty for this assignment
def draw():
    pass
