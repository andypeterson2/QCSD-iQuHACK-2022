def fallback(value, orElse):
    if (value != None):
        return value
    else:
        return orElse

# Add several noise values together

def fbm_noise(noise, amplitudes, nx, ny):
    sum = 0
    sumOfAmplitudes = 0
    for octave in range(amplitudes.length):
        frequency = 1 << octave
        sum += amplitudes[octave] * noise.noise2D(nx * frequency, ny * frequency, octave)
        sumOfAmplitudes += amplitudes[octave]

    return sum / sumOfAmplitudes

# Like GLSL. Return t clamped to the range [lo,hi] inclusive 

def clamp(t, lo, hi):
    if (t < lo):
        return lo
    if (t > hi):
        return hi
    return t

# Like GLSL. Return a mix of a and b; all a when is 0 and all b when
# t is 1; extrapolates when t outside the range [0,1] 

def mix(a, b, t):
    return a * (1.0-t) + b * t

# Componentwise mix for arrays of equal length; output goes in 'out'

def mixp(out, p, q, t):
    out.length = p.length
    for i in range(p.length):
        out[i] = mix(p[i], q[i], t)
    return out

# Like GLSL. 

def smoothstep(a, b, t):
    # https://en.wikipedia.org/wiki/Smoothstep
    if (t <= a): return 0
    if (t >= b): return 1
    t = (t - a) / (b - a)
    return (3 - 2*t) * t * t

# Circumcenter of a triangle with vertices a,b,c

def circumcenter(a, b, c):
    # https://en.wikipedia.org/wiki/Circumscribed_circle#Circumcenter_coordinates
    ad = a[0]*a[0] + a[1]*a[1]
    bd = b[0]*b[0] + b[1]*b[1]
    cd = c[0]*c[0] + c[1]*c[1]
    D = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    Ux = 1/D * (ad * (b[1] - c[1]) + bd * (c[1] - a[1]) + cd * (a[1] - b[1]))
    Uy = 1/D * (ad * (c[0] - b[0]) + bd * (a[0] - c[0]) + cd * (b[0] - a[0]))
    return [Ux, Uy]

# Intersection of line p1--p2 and line p3--p4,
# between 0.0 and 1.0 if it's in the line segment

def lineIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    # from http://paulbourke.net/geometry/pointlineplane/
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
    return {ua, ub}

# in-place shuffle of an array - Fisher-Yates
# https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle#The_modern_algorithm

def randomShuffle(array, randInt):
    for i in range(array.length-1):
        j = randInt(i+1)
        swap = array[i]
        array[i] = array[j]
        array[j] = swap
    return array