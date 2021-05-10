import glm


def dist2(a, b):
    return sum([(a[i] - b[i]) ** 2 for i in range(3)])


def centroid(points):
    n = len(points)
    d = len(points[0])
    c = [0.0] * d
    for p in points:
        for i in range(d):
            c[i] += p[i]

    for i in range(d):
        c[i] /= n

    return tuple(c)


def findRotMat(origVec, newVec, normVec=None):
    origVec = glm.normalize(origVec)
    newVec = glm.normalize(newVec)
    normVec = normVec or glm.normalize(glm.cross(origVec, newVec))
    cosTheta = glm.dot(origVec, newVec)
    theta = glm.acos(cosTheta)

    rotMat4 = glm.identity(glm.mat4)
    rotMat4 = glm.rotate(rotMat4, theta, normVec)

    return rotMat4


def printPoints(a):
    for i, p in enumerate(a):
        print(i, "{:.3f} {:.3f} {:.3f}".format(*p))
