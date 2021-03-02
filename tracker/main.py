import multiprocessing.connection as mpc
import cv2
import numpy as np
import time
from math import sqrt, tan, radians, asin
from pprint import pprint
import glm
import time

# client = mpc.Client("../spinevirtualcamera", 'AF_UNIX')
client = mpc.Client(("127.0.0.1", 5001), "AF_INET")
fb_zoom = 5
cam_fov = radians(45.0)
cam_width = 480 * fb_zoom
cam_height = 480 * fb_zoom
fb_width = cam_width * 2
fb_height = cam_height

camXDelta = 0.58
camY = 1.7128
camZ = -2


def findRotMat(origVec, newVec):
    origVec = glm.normalize(origVec)
    newVec = glm.normalize(newVec)
    sinTheta = glm.length(glm.cross(origVec, newVec))
    theta = asin(sinTheta)

    rotMat4 = glm.identity(glm.mat4)
    rotMat4 = glm.rotate(rotMat4, theta, glm.vec3(1, 0, 0))

    return rotMat4


def printPoints(a):
    for i, p in enumerate(a):
        print(i, "{:.3f} {:.3f} {:.3f}".format(*p))


camPoseOrig = glm.vec3(0, 0, 1)
camPose = glm.vec3(0, -0.7, 1)
camRotMat = findRotMat(camPoseOrig, camPose)

# focalLength = (cam_width / 2) / tan(cam_fov / 2)
focalLength = cam_width / (2 * tan(cam_fov / 2))
print("Focal Length", focalLength)
updateRate = 2
_updateRateI = 0

while True:
    try:
        arr = client.recv_bytes()
    except EOFError:
        print("Server disconnected")
        break
    _updateRateI += 1
    if _updateRateI < updateRate:
        continue
    _updateRateI = 0

    arr = np.frombuffer(
        arr,
        (
            np.float32,
            (
                fb_width,
                3,
            ),
        ),
    )

    img = np.round(arr * 255).astype(np.uint8)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur using 3 * 3 kernel.
    gray = cv2.blur(gray, (9, 9))
    # gray = cv2.GaussianBlur(gray, (1, 1), 2)

    # Apply Hough transform on the blurred image.
    detected_circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1,
        30,
        param1=50,
        param2=20,
        minRadius=10,
        maxRadius=50,
    )

    circlesL = []
    circlesR = []

    # Draw circles that are detected.
    if detected_circles is not None:
        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]

            x, y = a, b
            isRight = False
            if x > cam_width:
                x -= cam_width
                isRight = True

            # make (0,0) origin and flip y axis
            x = x - (cam_width / 2)
            y = (cam_height / 2) - y

            if isRight:
                circlesR.append((x, y))
            else:
                circlesL.append((x, y))

            # Convert the circle parameters a, b and r to integers.
            (a, b, r) = np.uint16(np.around((a, b, r)))
            # Draw the circumference of the circle.
            cv2.circle(img, (a, b), r, (0, 255, 0), 2)

            # Draw a small circle (of radius 1) to show the center.
            cv2.circle(img, (a, b), 1, (0, 0, 255), 3)

    # sort by y coordinate to find corresponding points
    circlesL.sort(key=lambda p: p[1])
    circlesR.sort(key=lambda p: p[1])

    points = []

    for i, (pL, pR) in enumerate(zip(circlesL, circlesR)):
        xDiff = abs(pL[0] - pR[0])
        z = camXDelta * focalLength / xDiff
        # x = z * pL[0] / focalLength
        # y = z * pL[1] / focalLength
        x = camXDelta * (pL[0] + pR[0]) / (2 * xDiff)
        y = camXDelta * (pL[1]) / xDiff

        vec = glm.vec4(x, y, z, 0)
        vec = camRotMat * vec
        points.append((vec.x, vec.y + camY, vec.z + camZ))

    printPoints(points)

    def dist2(a, b):
        return sum([(a[i] - b[i]) ** 2 for i in range(3)])

    def centroid(a, b, c):
        return tuple((a[i] + b[i] + c[i]) / 3 for i in range(3))

    def median(a, b):
        return tuple((a[i] + b[i]) / 3 for i in range(3))

    # if len(points) == 3:
    #     c = centroid(*points)
    #     print("Centroid", c)
    #     pprint(points)

    # dists = [dist2(p, c) for p in points]
    # points_dists = list(zip(points, dists))
    #
    # def key(e):
    #     p, dist = e
    #     return dist
    #
    # points_dists.sort(key=key)
    # pprint(points_dists)
    #
    # top, _ = points_dists[0]
    # a, b = points_dists[1][0], points_dists[2][0]
    # m = median(a, b)
    # #
    # top = glm.vec3(*top)
    # print(top)
    # m = glm.vec3(*m)
    # #
    # instrVec = top - m
    # instrVecOrig = glm.vec3(0, 0, 1)
    # print(instrVec, m)

    # rotMatObj = findRotMat(instrVecOrig, instrVec)

    img = cv2.resize(
        img,
        (fb_width // fb_zoom, fb_height // fb_zoom),
        interpolation=cv2.INTER_AREA,
    )
    cv2.imshow("Test", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
