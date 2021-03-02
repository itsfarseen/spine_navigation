import multiprocessing.connection as mpc
import params
import glm
import cv2
from math import radians, tan, atan2
from utils import centroid, findRotMat, dist2
import numpy as np

fb_zoom = params.FB_ZOOM
cam_fov = radians(params.CAM_FOV_DEGREES)
img_width = params.CAM_SENSOR_WIDTH * fb_zoom
img_height = params.CAM_SENSOR_HEIGHT * fb_zoom
full_img_width = img_width * 2
full_img_height = img_height

camXDelta = params.CAM_X_DELTA
camY = params.CAM_Y
camZ = params.CAM_Z

camPoseOrig = glm.vec3(0, 0, 1)
camPose = glm.vec3(*params.CAM_POSE)
camRotMat = findRotMat(camPoseOrig, camPose)

focalLength = img_width / (2 * tan(cam_fov / 2))


class Tracker:
    def __init__(self):
        self.client = None
        self.last_img = None

    def _isConnected(self):
        return self.client is not None

    def _getImg(self):
        if self.client == None:
            try:
                self.client = mpc.Client(("127.0.0.1", 5001), "AF_INET")
            except ConnectionError:
                return None

        try:
            arr = self.client.recv_bytes()
        except EOFError:
            self.client = None
            return None

        arr = np.frombuffer(
            arr,
            (
                np.float32,
                (
                    full_img_width,
                    3,
                ),
            ),
        )

        img = np.round(arr * 255).astype(np.uint8)
        self.last_img = img
        return img

    def getInstrCoords(self):
        img = self._getImg()
        if img is None:
            return None, None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Blur using 3 * 3 kernel.
        # gray = cv2.blur(gray, (3, 3))
        gray = cv2.GaussianBlur(gray, (3, 3), 2)

        # Apply Hough transform on the blurred image.
        detected_circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            1,
            30,
            param1=50,
            param2=20,
            minRadius=4,
            maxRadius=50,
        )

        # Process circles that are detected.
        if detected_circles is not None:

            circlesL = []
            circlesR = []

            for pt in detected_circles[0, :]:
                a, b, r = pt[0], pt[1], pt[2]

                x, y = a, b
                isRight = False
                if x > img_width:
                    x -= img_width
                    isRight = True

                # make (0,0) origin and flip y axis
                x = x - (img_width / 2)
                y = (img_height / 2) - y

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

            circlesLC = centroid(circlesL)
            circlesRC = centroid(circlesL)

            def angleFromOrigin(p, origin):
                x, y = p[0] - origin[0], p[1] - origin[1]
                return atan2(y, x)

            # sort by angle to find corresponding points
            circlesL.sort(key=lambda p: angleFromOrigin(p, circlesLC))
            circlesR.sort(key=lambda p: angleFromOrigin(p, circlesRC))

            points = []

            for i, (pL, pR) in enumerate(zip(circlesL, circlesR)):
                xDiff = abs(pL[0] - pR[0])
                x = camXDelta * (pL[0] + pR[0]) / (2 * xDiff)
                y = camXDelta * (pL[1]) / xDiff
                z = camXDelta * focalLength / xDiff

                vec = glm.vec4(x, y, z, 0)
                vec = camRotMat * vec
                points.append((vec.x, vec.y + camY, vec.z + camZ))

            if len(points) == 3:
                c = centroid(points)

                dists = [dist2(p, c) for p in points]
                points_dists = list(zip(points, dists))

                points_dists.sort(key=lambda pt_dist: pt_dist[1])
                top, _ = points_dists[0]
                a, b = points_dists[1][0], points_dists[2][0]
                m = centroid([a, b])

                m = glm.vec3(*m)
                top = glm.vec3(*top)
                instrDir = glm.normalize(top - m)
                # instrDirOrig = glm.vec3(0, 0, 1)

                instrPos = glm.vec3(*c)

                return instrPos, instrDir

        return None, None
