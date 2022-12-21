class PVector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "PVector(%f, %f, %f)" % (self.x, self.y, self.z)

    def __add__(self, other):
        return PVector.add(self, other)

    def __mul__(self, n):
        return PVector.mult(self, n)

    def __rmul__(self, n):
        return PVector.mult(self, n)

    def mag(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def magSq(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def copy(self):
        return PVector(self.x, self.y, self.z)

    def div(self, n):
        return PVector(
            a.x / n,
            a.y / n,
            a.z / n,
        )

    @staticmethod
    def dist(a, b):
        return PVector.sub(a, b).mag()

    @staticmethod
    def add(a, b):
        return PVector(
            a.x + b.x,
            a.y + b.y,
            a.z + b.z,
        )

    @staticmethod
    def sub(a, b):
        return PVector(
            a.x - b.x,
            a.y - b.y,
            a.z - b.z,
        )

    @staticmethod
    def mult(a, n):
        return PVector(
            n * a.x,
            n * a.y,
            n * a.z,
        )

    @staticmethod
    def pairwise_mult(a, b):
        return PVector(
            a.x * b.x,
            a.y * b.y,
            a.z * b.z,
        )

    @staticmethod
    def dot(a, b):
        return a.x * b.x + a.y * b.y + a.z * b.z

    @staticmethod
    def cross(a, b):
        return PVector(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x,
        )

    def normalize(self):
        mag = sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        self.x /= mag
        self.y /= mag
        self.z /= mag
        return self
    
    def get(self):
        return PVector(self.x, self.y, self.z)
    
    def __getitem__(self, t):
        return getattr(self, ('x', 'y', 'z')[t])
    
class Light:
    # Constructor Attributes: xyz coord : PVector, rgb color : PVector
    def __init__(self, pv, cv):
        self.v = pv
        self.color = cv
        self.x = pv.x
        self.y = pv.y
        self.z = pv.z
        self.r = cv.x
        self.g = cv.y
        self.b = cv.z
    
    def getV(self):
        return self.v
    
    def getColor(self):
        return self.color
    
    def diffuseLight(self, hit):
        rgb = [0, 0, 0]

        diffuseRGB = hit.object.dc
        lightRGB = self.color
        
        L = PVector.sub(self.v, hit.v).normalize()
        N = hit.normal
        nl = max(0, PVector.dot(N, L))
        
        for i in range(0, 3):
            rgb[i] = diffuseRGB[i] * lightRGB[i] * nl
        
        return PVector(*rgb[:])
    
    def specularLight(self, hit, eye_ray):
        rgb = [0, 0, 0]
        
        spec_power = hit.object.spow
        specRgb = hit.object.sc
        lightRGB = self.color
        
        L = PVector.sub(self.v, hit.v).normalize()
        D = eye_ray.slope
        H = PVector.sub(L, D).normalize()
        N = hit.normal
        specularCoeff = pow(max(0, PVector.dot(H, N)), spec_power)
        
        for i in range(0, 3):
            rgb[i] = specRgb[i] * lightRGB[i] * specularCoeff
        
        return PVector(*rgb[:])
    
class Sphere(object):
    # Constructor Attributes: xyz coord, radius, material
    def __init__(self, pv, radius, diffuseColor=PVector(0,0,0), ambientColor=PVector(0,0,0), specularColor=PVector(0,0,0), s_pow=0, k_refl=0):
        self.v = pv
        self.radius = radius
        self.type = "sphere"

        self.dc = diffuseColor
        self.ac = ambientColor
        self.sc = specularColor
        self.spow = s_pow
        self.krefl = k_refl 
        
    # def __repr__(self):
    #     return "<Class Instance> Sphere \ncoords: {} radius: {} \n{}".format(self.pv, self.radius, self.material)
    
    def getV(self):
        return self.v
    
    def getR(self):
        return self.radius
    
    def getDiffuseColor(self):
        return self.dc
    
    def getAmbientColor(self):
        return self.ac
    
    def getSpecularColor(self):
        return self.sc
    
    def getKrefl(self):
        return self.krefl
    
    def getSpecPwr(self):
        return self.spow
    
    def intersect(self, ray):

        # Quadratic coeff
        a = PVector.dot(ray.slope, ray.slope)
        b = 2 * PVector.dot(PVector.sub(ray.v, self.v), ray.slope)
        c = PVector.dot(PVector.sub(ray.v, self.v), PVector.sub(ray.v, self.v)) - self.radius**2
        
        # Find discriminant
        discriminant = (b**2) - (4 * a * c)
        
        # If no real solutions return -ve
        if discriminant < 0:
            return None
        
        # Calculate roots
        t1 = (-b + sqrt(discriminant))/(2 * a)
        t2 = (-b - sqrt(discriminant))/(2 * a)
        
        # Return closest intersection
        if t1 < t2:
            t_val = t1
        else:
            t_val = t2

        if t_val < 0.00001:
            return None
        
        p = ray.intersect(t_val)
        shape_normal = PVector.sub(p, self.v).normalize()
        hit = Hit(self, shape_normal, t_val, p)
        
        return hit
            
class Ray:
    def __init__(self, pv, dir):
        self.v = pv
        self.slope = dir
    
    def getV(self):
        return self.v
    
    def getSlope(self):
        return self.slope
    
    def intersect(self, t_val):
        return PVector.add(self.v, PVector.mult(self.slope, t_val))
    
class Hit:
    # Stores the closest "hit" object for a pixel for rendering
    def __init__(self, object, normal, t_val, v):
        self.object = object
        self.v = v
        self.normal = normal
        self.t_val = t_val
        
    
    def copy(self):
        return Hit(self.object, self.normal, self.t_val, self.v)
        
    def getT(self):
        return self.t_val
    
    def getObject(self):
        return self.object
    
    def setObject(self, newObject):
        self.object = newObject
    
    def getDiffuseColor(self):
        return self.object.getDiffuseColor()
    
    def getAmbientColor(self):
        return self.object.getAmbientColor()
    
    def getSpecularColor(self):
        return self.object.getSpecularColor()
    
    def getKrefl(self):
        return self.object.getKrefl()
    
    def getSpecPwr(self):
        return self.object.getSpecPwr()
    
    def getIntersection(self):
        return self.v
    
    def setIntersection(self, pos):
        self.v = pos
        
    def getNormal(self):
        return self.normal
    
    def setNormal(self, newNormal):
        self.normal = newNormal
        
class Triangle:
    def __init__(self, a=PVector(0, 0, 0), b=PVector(0, 0, 0), c=PVector(0, 0, 0), diffuseColor=PVector(0,0,0), ambientColor=PVector(0,0,0), specularColor=PVector(0,0,0), s_pow=0, k_refl=0):
        self.a = a
        self.b = b
        self.c = c
    
        self.ab = PVector.sub(b, a) # precompute the sides of the triangle
        self.bc = PVector.sub(c, b)
        self.ca = PVector.sub(a, c)
        
        self.vertices = (self.a, self.b, self.c)
        self.edges = (self.ab, self.bc, self.ca)
        
        self.normal = PVector.cross(self.ab, PVector.sub(self.c, self.a)).normalize()
    
        self.type = "triangle"

        self.dc = diffuseColor
        self.ac = ambientColor
        self.sc = specularColor
        self.spow = s_pow
        self.krefl = k_refl 
    
    # def __repr__(self):
        # return "<Class Instance> Triangle \ncoords: {} \n{}".format(self.a, self.b, self.c , self.material)
    
    def getV(self):
        return self.vertices
    
    def getE(self):
        return self.edges
    
    def getDiffuseColor(self):
        return self.dc
    
    def getAmbientColor(self):
        return self.ac
    
    def getSpecularColor(self):
        return self.sc
    
    def getKrefl(self):
        return self.krefl
    
    def getSpecPwr(self):
        return self.spow
    
    def intersect(self, ray):
        # Detects intersection between Ray and Triangle
        t_denom = PVector.dot(self.normal, ray.slope)
        if t_denom == 0:
            # no hit/intersection
            return None 
        
        u = PVector.sub(self.a, ray.v) # U = TriangleCoord - RayCoord
        t_norm = PVector.dot(self.normal, u)
        
        t = float(t_norm / t_denom)
        
        if t < 0:
            # no hit/intersection
            return None
        
        p = ray.intersect(t)
        # Point in Triangle Test
        
        triple_a = PVector.dot(PVector.cross(PVector.sub(p, self.a), self.ab), self.normal)
        triple_b = PVector.dot(PVector.cross(PVector.sub(p, self.b), self.bc), self.normal)
        triple_c = PVector.dot(PVector.cross(PVector.sub(p, self.c), self.ca), self.normal)
        
        if triple_a > -0.00001 and triple_b > -0.00001 and triple_c > -0.00001 :
            if t_denom < 0:
                hitNormal = self.normal 
            else: 
                hitNormal = PVector.mult(self.normal, -1)
            
            return Hit(self, hitNormal , t , p)
        elif triple_a < -0.00001 and triple_b < -0.00001 and triple_c < -0.00001:
            if t_denom < 0:
                hitNormal = self.normal
            else: 
                hitNormal = PVector.mult(self.normal, -1)
            
            return Hit(self, hitNormal , t , p)
        else:
            # Point not in triangle
            return None    
            
