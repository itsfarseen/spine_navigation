import multiprocessing.connection as mpc
import cv2
import numpy as np
import time

# client = mpc.Client("../spinevirtualcamera", 'AF_UNIX')
client = mpc.Client(("127.0.0.1", 5001), "AF_INET")
fb_zoom = 2
fb_width = 480 * 2 * fb_zoom
fb_height = 480 * fb_zoom

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

    # img = cv2.resize(img, (fb_width // fb_zoom, fb_height//fb_zoom), interpolation=cv2.INTER_AREA)
    cv2.imshow("Test", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
