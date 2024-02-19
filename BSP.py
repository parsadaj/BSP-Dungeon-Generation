import numpy as np

class BSPNode:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left = None
        self.right = None
        self.parent = None
        self.room = None
        self.corridor = None
        self.split = None
        
    def create_room(self):
        room_width = np.random.randint(self.w // 4, self.w)
        room_height = np.random.randint(self.h // 4, self.h)
        room_x = np.random.randint(self.x, self.x + (self.w  -  room_width))
        room_y = np.random.randint(self.y, self.y + (self.h - room_height))
        self.room = (room_x, room_y, room_width, room_height)
        

class BSPArray:
    def __init__(self, w, h):
        self.array = np.zeros((h, w))
    
    def __call__(self):
        return self.array
    
    def draw_room(self, room):
        room_x, room_y, room_w, room_h = room
        self.array[room_y: room_y+room_h, room_x: room_x+room_w] = 1
    
    def draw_straight_corridor(self, corridor, corridor_w):
        start, end = corridor
        x1, y1 = start
        x2, y2 = end
        
        if x1 != x2 and y1 != y2:
            raise
        
        if x1 == x2:
            x = x1 - corridor_w//2
            self.array[min([y1, y2]): max([y1, y2]), x: x+corridor_w] = 1
            
        if y1 == y2:
            y = y1 - corridor_w//2
            self.array[y: y+corridor_w, min([x1,x2]):max([x1,x2])] = 1
    
class BSPGenerator:
    def __init__(self, w, h, min_w=None, min_h=None, corridor_w=3):
        self.w = w
        self.h = h
        self.min_w = min_w if min_w is not None else w // 3
        self.min_h = min_h if min_h is not None else h // 3
        self.array = BSPArray(w, h)
        self.rooms = []
        self.corridors = []
        self.nodes = []
        self.corridor_w = corridor_w

    def generate_dungeon(self):
        self.root = BSPNode(0, 0, self.w, self.h)
        self.bsp_tree_recursive(self.root)
        self.generate_array()
        self.connect_rooms_with_same_parents()
        return self.array()

    def bsp_tree_recursive(self, node: BSPNode):
        self.nodes.append(node)
        if node.w < self.min_w or node.h < self.min_h:
            node.create_room()
            self.rooms.append(node.room)
            return
    
        split_way = np.random.choice(['h', 'v'])
        if split_way == 'h':
            self.split_horizontally(node)
        elif split_way == 'v':
            self.split_vertically(node)
        
        node.split = split_way
        
        self.bsp_tree_recursive(node.left)
        self.bsp_tree_recursive(node.right)
        
    def generate_array(self):
        for room in self.rooms:
            self.array.draw_room(room)
            
    def split_horizontally(self, node: BSPNode):
        split = np.random.randint(self.min_w//2, node.w - self.min_w//2)
        node.left = BSPNode(node.x,          node.y, split,              node.h)
        node.left.parent = node
        node.right = BSPNode(node.x + split, node.y, node.w - split, node.h)
        node.right.parent = node

    def split_vertically(self, node: BSPNode):
        split = np.random.randint(self.min_h//2, node.h - self.min_h//2)
        node.left = BSPNode(node.x, node.y, node.w, split)
        node.right = BSPNode(node.x, node.y + split, node.w, node.h - split)
    
    def connect_rooms_with_same_parents(self):
        for node in self.nodes:
            if node.split == 'v':
                if node.left.room is not None and node.right.room is not None:
                    node.corridor = self.connect_rooms_v(node.left.room, node.right.room)
            elif node.split == 'h':
                if node.left.room is not None and node.right.room is not None:
                    node.corridor = self.connect_rooms_h(node.left.room, node.right.room)

    def connect_rooms_v(self, room1, room2):
        x1, y1, w1, h1 = room1
        x2, y2, w2, h2 = room2
        
        overlap = find_overlap(x1, x1+w1, x2, x2+w2)
        if overlap is not None:
            xo1, xo2 = overlap
            xo2 = xo2 - self.corridor_w//2
            xo1 = xo1 + self.corridor_w//2
            
            x_overlap_start = min([xo1, xo2])
            x_overlap_end = max([xo1, xo2])
            x = np.random.randint(x_overlap_start, x_overlap_end+1)
            y_start = y1 + h1 if y2 > y1 else y2 + h2
            y_end = y2 if y2 > y1 else y1
            corridor = (x, y_start), (x, y_end)
            self.corridors.append(corridor)
            self.array.draw_straight_corridor(corridor, self.corridor_w)
            return corridor
            
    def connect_rooms_h(self, room1, room2):
        x1, y1, w1, h1 = room1
        x2, y2, w2, h2 = room2
        
        overlap = find_overlap(y1, y1+h1, y2, y2+h2)
        if overlap is not None:
            yo1, yo2 = overlap
            yo2 = yo2 - self.corridor_w//2
            yo1 = yo1 + self.corridor_w//2
            
            y_overlap_start = min([yo1, yo2])
            y_overlap_end = max([yo1, yo2])
            y = np.random.randint(y_overlap_start, y_overlap_end+1)
            x_start = x1 + w1 if x2 > x1 else x2 + w2
            x_end = x2 if x2 > x1 else x1
            corridor = (x_start, y), (x_end, y)
            self.corridors.append(corridor)
            self.array.draw_straight_corridor(corridor, self.corridor_w)
            return corridor
        
def find_overlap(z1_start, z1_end, z2_start, z2_end):
    # Check if there's no overlap
    if z1_end < z2_start or z2_end < z1_start:
        return None
    
    # If there's overlap, calculate overlap interval
    x_overlap_start = max(z1_start, z2_start)
    x_overlap_end = min(z1_end, z2_end)
    
    return x_overlap_start, x_overlap_end

        
                


