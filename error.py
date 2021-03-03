from time import sleep
from tracker import Tracker
import glm

tracker = Tracker()

lastInstrPos = None
instrPoses = []

f = open("data.csv", "a")
f.write("x,y,z, x_true, y_true, z_true\n")

try:
    while True:
        input("Press enter to record")
        instrPos, instrDir = tracker.getInstrCoords()
        if instrPos is None:
            instrPos = glm.vec3(0, 0, 0)
        print(instrPos)
        while True:
            accept = input("Accept?")
            if accept == "y":
                line = input("Enter ground truth")
                truth = glm.vec3([float(i) for i in line.split()])
                instrPoses.append((instrPos, truth))
                p, t = instrPos, truth
                f.write(
                    "{},{},{},{},{},{}\n".format(p.x, p.y, p.z, t.x, t.y, t.z)
                )
                f.flush()
                print(len(instrPoses), instrPoses[-1])
                break
            elif accept == "n":
                break
            else:
                continue
except KeyboardInterrupt:
    pass
