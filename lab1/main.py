from argparse import ArgumentParser

b = 60
f = 6
ps = .006
xNumPix = 752
cxLeft = xNumPix/2
cxRight = xNumPix/2

# Params:
# centroidLeft - int (in pixels), centroid of ball in left image
# centroidRight - int (in pixels), centroid of ball in right image

# Returns:
# ballDepth (in mm)

def compute_ball_depth(centroidLeft, centroidRight):
    d = (abs((centroidLeft-cxLeft)-(centroidRight-cxRight))*ps)
    return (b*f) / d

if __name__ == '__main__':
    
    argumentParser = ArgumentParser()

    argumentParser.add_argument('leftCentroidPx', type=int)
    argumentParser.add_argument('rightCentroidPx', type=int)

    args = argumentParser.parse_args()

    ballDepth = compute_ball_depth(args.leftCentroidPx, args.rightCentroidPx)
    print(f"{ballDepth / 1000} meters")
