import multiprocessing.connection as mpc
import cv2
import numpy as np
import time
from math import sqrt, tan, radians
from pprint import pprint
import glm

# client = mpc.Client("../spinevirtualcamera", 'AF_UNIX')
client = mpc.Client(("127.0.0.1", 5001), "AF_INET")
fb_zoom = 2
cam_fov = radians(45.0)
cam_width = 480 * fb_zoom
cam_height = 480 * fb_zoom
fb_width = cam_width * 2
fb_height = cam_height

camXDelta = 0.58
camY = 1.7128
camZ = -2

camPoseOrig = glm.vec3(0, 0, 1)
camPose = glm.normalize(glm.vec3(0, -0.7, 1))

sinTheta = glm.length(glm.cross(camPoseOrig, camPose))
theta = glm.asin(sinTheta)

rotMat4 = glm.identity(glm.mat4)
rotMat4 = glm.rotate(rotMat4, theta, glm.vec3(1,0,0))

focalLength = (cam_width/2)/tan(cam_fov/2)

while True:
    try:
        arr = client.recv_bytes()
    except EOFError:
        print("Server disconnected")
        break

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

    img = np.round(arr*255).astype(np.uint8)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur using 3 * 3 kernel.
    gray = cv2.blur(gray, (3, 3))

    # Apply Hough transform on the blurred image.
    detected_circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1,
        30,
        param1=50,
        param2=20,
        minRadius=0,
        maxRadius=0,
    )

    circlesL = []
    circlesR = []

    # Draw circles that are detected.
    if detected_circles is not None:
        # Convert the circle parameters a, b and r to integers.
        detected_circles = np.uint16(np.around(detected_circles))

        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]

            # Draw the circumference of the circle.
            cv2.circle(img, (a, b), r, (0, 255, 0), 2)

            # Draw a small circle (of radius 1) to show the center.
            cv2.circle(img, (a, b), 1, (0, 0, 255), 3)

            x, y = a, b
            isRight = False
            if x > cam_width:
                x -= cam_width
                isRight = True

            # make (0,0) origin and flip y axis
            x = x - (cam_width/2)
            y = (cam_height/2) - y

            if isRight:
                circlesR.append((x,y))
            else:
                circlesL.append((x,y))

    # sort by y coordinate to find corresponding points
    circlesL.sort(key=lambda p: p[1])
    circlesR.sort(key=lambda p: p[1])

    points = []
    for pL, pR in zip(circlesL, circlesR):
        xDiff = abs(pL[0]-pR[0])
        z = camXDelta*focalLength/xDiff

        x = z*pL[0]/focalLength
        y = z*pL[1]/focalLength

        vec = glm.vec4(x,y,z, 0)
        vec = rotMat4*vec
        points.append((vec.x - camXDelta/2,vec.y + camY,vec.z + camZ))

    pprint(points)

    img = cv2.resize(img, (fb_width // fb_zoom, fb_height//fb_zoom), interpolation=cv2.INTER_AREA)
    cv2.imshow("Test", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
