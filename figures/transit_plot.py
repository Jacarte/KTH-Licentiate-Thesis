
from PIL import Image, ImageDraw
import sys 
import json
import re
import math
import random
import numpy as np
from scipy import interpolate

WIDTH=2000
HEIGHT=2000
PADDING=200
SPREAD = 25

LOW = False
if LOW:
    WIDTH = 500
    HEIGHT = 500
    PADDING = 10

# Colors
BACKGROUND_COLOR=(255,255,255, 255) # black, alpha
FOREGROUND_COLOR=(0,0,0,255) # white
DECAY_FACTOR = 0.1
COLORS = [
    FOREGROUND_COLOR,
    (255,0,0,255),
    (0,255,0, 255),
    (255, 255, 0, 255),
    (0, 0, 255, 255),
    (125, 125, 255, 255),
    (0, 255, 255, 255)
]

VARIANT_RE = re.compile(r"(_\d+_?)")

class CallGradient:
    
    def __init__(self, direction = (0,0), color = FOREGROUND_COLOR, x = 0, y  = 0, speed = 3, x0 = 0, y0 = 0, x1=0, y1  = 0, delay=0, trigger=None):
        self.direction = direction
        self.x = x
        self.y = y
        self.speed = speed

        self.x0 = x0
        self.x1 = x1

        self.y0 = y0
        self.y1 = y1

        self.moving = True
        self.head = 0
        self.delay = delay
        self.color = color
        self.trigger = trigger

        self.path = self.precalculate_path_linear()

    def precalculate_path_linear(self):

        path = []

        for x in range(int(self.x0), int(self.x1)):
            ny = self.y0 + (self.y1 - self.y0)*(x - self.x0)/(self.x1 - self.x0)
            path.append((x, ny))

        return path

    def precalculate_path_quad(self):

        
        #print(self.x0, self.x1, self.y0, self.y1)
        mid = [
            random.randint(0, abs(int(self.x0) - int(self.x1))),
            random.randint(0, abs(int(self.y0) - int(self.y1)))
        ]

        DIRECTION = 1
        if self.x1 < self.x0:
            mid[0] = self.x0 - mid[0]
            DIRECTION = -1
        else:
            mid[0] = self.x0 + mid[0]    

        if self.y1 < self.y0:
            mid[1] = self.y0 - mid[1]
        else:
            if self.y1 == self.y0:
                mid[1] == self.y0 + 2*(0.5 - random.random())
            else:
                mid[1] = self.y0 + mid[1]    
        
        xs = [self.x0, mid[0],  self.x1]
        ys = [self.y0, mid[1],  self.y1]

        if DIRECTION == -1:
            xs = xs[::-1]
            ys = ys[::-1]

        try:
            #print(len(xs), len(ys))
            paths = interpolate.splrep(xs, ys,  k=2)
            
            x2 = np.linspace(xs[0], xs[-1], 200 if not LOW else 20)
            y2 = interpolate.splev(x2, paths)
            #print(y2)
            paths= [ (x, y) for x, y in zip(x2, y2) ]

            if DIRECTION == -1:
                paths = paths[::-1]
            
            #print(paths, self.x0, self.y0, self.x1, self.y1)
        except Exception as e:
            #print(e, self.x1 < self.x0)
            #print(mid, self.x0, self.x1, self.y0, self.y1)
            paths = self.precalculate_path_linear()
        # exit(1)
        return paths

    @staticmethod
    def draw_thick(x, y, board, masks, color, rad=2):
        
        data = board.load()

        for j in np.arange(-rad, rad):
            for i in np.arange(-rad, rad):
                # if is inside circle
                if i*i + j*j <= rad * rad:
                    if i + x >= 0 and i + x <= HEIGHT:
                        if  j + y >= 0 and  j + y <= WIDTH:
                            #color[-1] = 125
                            data[int(i + x), int(j + y)] = color
                            masks[int(i + x)][int(j + y)] = 1


    def move(self, board, masks):
        
        if not self.moving:
            #print("Not executed anymore", self.trigger)
            #if self.trigger:
                #print(self.trigger.moving)
            return

        self.head += self.speed

        if self.head  <= self.delay:
            return
        
        #data = board.load()
        #nextx = [int(self.x + i*self.direction[0]) for i in range(1, self.speed + 1)]
        #nexty = [int(self.y + i*self.direction[1]) for i in range(1, self.speed + 1)]

        if self.head - self.delay < len(self.path):
            current = self.path[self.head - self.delay]

            x, y = current
            CallGradient.draw_thick(x, y, board, masks, self.color, rad = 6)
        else:
            self.moving = False
            if self.trigger:
                self.trigger.moving = True
                self.trigger.move(board, masks)

class FunctionNode:

    def __init__(self, id, clusterid, tpe, rad=1, color=FOREGROUND_COLOR, x=0, y = 0):
        self.id = id
        self.clusterid = clusterid
        self.rad = rad
        self.tpe = tpe

        self.x = x
        self.y = y
        self.color = color
    

    def draw(self, board, masks):
        data = board.load()

        for j in np.arange(- self.rad, self.rad, 0.5):
            for i in np.arange(- self.rad, self.rad, 0.5):
                # if is inside circle
                if i*i + j*j <= self.rad * self.rad:
                    if i + self.x < WIDTH and j + self.y < HEIGHT:
                        if i + self.x >= 0 and j + self.y >= 0:
                            data[int(i + self.x), int(j + self.y)] = self.color
                            masks[int(i + self.x)][int(j + self.y)] = 1

def decay(board, maskmap):

    data = board.load()

    for i in range(WIDTH):
        for j in range(HEIGHT):
            if maskmap[i][j]:
                data[i, j] = (
                    int(((1-DECAY_FACTOR)*data[i,j][0] + DECAY_FACTOR*BACKGROUND_COLOR[0])),
                    int(((1-DECAY_FACTOR)*data[i,j][1] + DECAY_FACTOR*BACKGROUND_COLOR[1])),
                    int(((1-DECAY_FACTOR)*data[i,j][2] + DECAY_FACTOR*BACKGROUND_COLOR[2])),
                    255
                )
                if data[i, j] == 0:
                    maskmap[i][j] = 0

def get_board():
    img = Image.new('RGBA', (WIDTH, HEIGHT), color = BACKGROUND_COLOR)

    return img, [[0 for _ in range(HEIGHT)] for _ in range(WIDTH)]

def load_from_traces(board, masks):
    # get function nodes from traces
    fcontent = open(sys.argv[1], 'r').read()
    data = json.loads(fcontent)
    # POP filter
    POPs = ["bma", "ams", "yyz", "vie", "wdc"]
    #POPs = []



    instrumented = data['bin2base64']['instrumented']
    pathsall = instrumented['paths']
    paths = []

    for POP in pathsall.keys():
        paths += pathsall[POP]

    NODES_IN_CLUSTERS, REVERSE= load_map(sys.argv[2])

    #print(CLUSTER_BY_MAP)
    uniqueids = []
    CLUSTERS = {}
    clusterids = set()
    REAL_ID = []
    VISITED = []
    for pathinfo in paths:
        print(pathinfo)
        path = pathinfo['path']
        #clusterids.add(0)
        path = path
        for i in path:
            if i in VISITED:
                continue
            else:
                VISITED.append(i)
            #if i not in uniqueids:
            #uniqueids.append(i)
            # get cluster id
            #if NODES_IN_CLUSTERS[i]['id'] not in clusterids:
            #    REAL_ID.append((NODES_IN_CLUSTERS[NODES_IN_CLUSTERS[i]['id']][0][2], len(clusterids)))
            mx, idx = REVERSE[i]
            clusterids.add(NODES_IN_CLUSTERS[mx]['id'])
            clusterid = len(clusterids) - 1

            # Add all nodes in the cluster
            print(f"Adding node variants for {NODES_IN_CLUSTERS[mx]['id']} {len(NODES_IN_CLUSTERS[mx]['nodes'])}")
            for name, nodeid, raw, tpe in NODES_IN_CLUSTERS[mx]['nodes']:
                #print(name)
                if nodeid not in uniqueids:
                    node = FunctionNode(nodeid, clusterid,tpe, 30, color=color_by_type(tpe), x = 0, y = 0)

                    if clusterid not in CLUSTERS:
                        CLUSTERS[clusterid] = []
                    CLUSTERS[clusterid].append(node)
                    uniqueids.append(nodeid)
            print("")
        break

    CLUSTER_X_POS_SIZE = int((WIDTH - 2*PADDING)   / len(CLUSTERS))   
    
    #print(CLUSTERS.keys(), REAL_ID, VISITED)

    NODES_BY_ID = {}
    CENTERY = HEIGHT/2

    CLUSTERIDS = CLUSTERS.keys()
    CLUSTERIDS = list(CLUSTERIDS)
    #CUSTOMORDER = [0, 1, 2, 3, 4]
    #CLUSTERIDS = sorted(CLUSTERIDS, key =lambda x: CUSTOMORDER[x])
    # CLUSTERIDS sort, dispatchers before variants
    for clusterid in CLUSTERIDS:
        #CLUSTER_Y_POS_SIZE = int((HEIGHT-2*PADDING)/len(CLUSTERS[clusterid]))
        c = 1
        print(clusterid, len(CLUSTERS[clusterid]))
        #print(CLUSTERS[clusterid][0].id)
        delta = 7
        for node in CLUSTERS[clusterid]:
            #print(node)
            if node.tpe == "DISPATCHER" or node.tpe == "ORIGINAL":

                node.x = PADDING + clusterid*CLUSTER_X_POS_SIZE
                node.y = CENTERY# PADDING + c*CLUSTER_Y_POS_SIZE
            else:
                r = 200 + SPREAD * math.sqrt(random.random())
                theta = random.random() * 2 * math.pi
                rx = node.x + r * math.cos(theta)
                yr = node.y + r * math.sin(theta)

                node.x = PADDING + clusterid*CLUSTER_X_POS_SIZE + rx
                node.y = CENTERY + delta*c + yr# PADDING + c*CLUSTER_Y_POS_SIZE

                print(node.x, node.y)

            NODES_BY_ID[node.id] = node
            c += 1
            if c >= len(CLUSTERS[clusterid])/2:
                delta = -7
                c = 1


    return CLUSTERS, paths, NODES_BY_ID

def color_by_type(tpe):
    #0.16, 0.42, 0.705  107/255
    if tpe == "DISPATCHER":
        return (148, 194, 128, 255)
        #return (int(255*0.72), 125,  125, 255)
    if tpe == "ORIGINAL":
        return (253, 228, 158, 255)
        #return (int(255*0.16), int(255*0.42), int(255*0.705), 255)
    if tpe == "VARIANT":
        return (204,204,204, 128)
        #return (int(255*0.16), int(255*0.42), int(255*0.705), 100)

def load_map(path):
    fcontent = open(path, 'r').readlines()

    NODES_BY_CLUSTER = {

    }
    REVERSE = {

    }
    #clusters.add(0)
    for l in fcontent:
        name, _id = l.split(",")
        _id = _id.strip()
        _id = int(_id)
        TPE="DISPATCHER"
        # sanitize name
        #name = name.replace("_original", "")
        if len(VARIANT_RE.findall(name)) > 0:
            name = re.sub(VARIANT_RE, "", name)
            name = f"{name}_variant"
            TPE = "VARIANT"
            # print(name)
        if "original" in name:
            name = name.replace("_original", "")
            name = f"{name}_variant"
            TPE = "ORIGINAL"
            #print(name, "oricha")
        #else:
        #    pass
        
        if name not in NODES_BY_CLUSTER:
            NODES_BY_CLUSTER[name] = dict(
                id = len(NODES_BY_CLUSTER),
                nodes = []
            )

        NODES_BY_CLUSTER[name]['nodes'].append((name, _id, l, TPE))
        REVERSE[_id] =  (name, NODES_BY_CLUSTER[name])

        #print(len(NODES_BY_CLUSTER[CLUSTERID]))

    # Entry point
    #IDS[0] = 0
    #NODES_BY_CLUSTER[0] = [0]
    #print(clusters)
    open("test.json", 'w').write(json.dumps(NODES_BY_CLUSTER, indent=4))
    return NODES_BY_CLUSTER, REVERSE
    
def invert(board):
    
    data = board.load()

    for i in range(WIDTH):
        for j in range(HEIGHT):
                data[i, j] = tuple([int(255 - c) for c in data[i, j]])
                

def get_call_gradient(node1, node2, delay, color, trigger = None):
    direction = (
        node2.x - node1.x,
        node2.y - node1.y
    )

    # normalize
    length = direction[0]*direction[0] + direction[1]*direction[1] + 1
    # print(length)
    length = math.sqrt(length)
    direction = (direction[0]/length, direction[1]/length)

    #print(direction)
    return CallGradient(direction, color, speed=3 if not LOW else 18, x=node1.x, y = node1.y, x0 = node1.x, x1 = node2.x, y0 = node1.y, y1 = node2.y, delay = delay, trigger = trigger)

if __name__ == "__main__":
    board, masks = get_board()

    nodes, traces, NODES_BY_ID = load_from_traces(board, masks)


    # concat all traces
    gradients = []
    print(NODES_BY_ID)
    DELAY = 0
    T = 0
    for tr in traces:
        trace = tr['path']
        
        # adding entry point

        trace =  trace
        C = 0
        tracecolor =COLORS[T%len(COLORS)]
        last = None
        for f1, f2 in zip(trace, trace[1:]):
            # print(f1, f2)
            gr = get_call_gradient(NODES_BY_ID[f1], NODES_BY_ID[f2], 0 if last else DELAY, tracecolor)
            if not last:
                gr.moving = True
            else:
                gr.moving= False
                last.trigger = gr

            gradients.append(gr)
            last = gr
            C += 100
        DELAY += 60
        T += 1

    print(len(gradients))

    for clusterid in nodes.keys():
        for node in nodes[clusterid]:
            node.draw(board, masks)
    MAX = 2000

    if len(gradients) > 0:
        #first = gradients[0]
        #gradients = gradients[1:]
        for i in range(MAX):
            sys.stdout.write(f"\r{i}/{MAX}")
            # draw always the functions

            
            # draw the calls
            #for grad in gradients:
            for clusterid in nodes.keys():
                for node in nodes[clusterid]:
                    node.draw(board, masks)

            for g in gradients:
                g.move(board, masks)
            #first.move(board, masks)

            try:
                pass
                #if not first.moving:
                #    first = gradients[0]
                #    gradients = gradients[1:]
            except:
                break

            decay(board, masks)



            board.save(f"out/img{i:03d}.png")