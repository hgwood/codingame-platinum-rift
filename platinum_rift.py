import sys, math, random, itertools, collections

def stdin(n=1):
    if n == 0: return int(input())
    def acquire(): return tuple(int(i) for i in input().split())
    if n == 1: return acquire()
    return (acquire() for _ in range(n))

nplayers, my_id, nzones, nlinks = stdin()
platinum = dict(stdin(nzones)).get
links = stdin(nlinks)

def make_neighbor_getter():
    neighbors = collections.defaultdict(list)
    for zone1, zone2 in links:
        neighbors[zone1].append(zone2)
        neighbors[zone2].append(zone1)
    return neighbors.get
neighbors = make_neighbor_getter() 

#magnetism = {zone: platinum(zone) + sum(platinum(neighbor) for neighbor in neighbors(zone)) for zone in range(nzones)}.get
map = sorted(range(nzones), key=platinum, reverse=True)

def make_border_map():
    distances_to_border = {}
    for zone in filter(border, map):
        distances_to_border[zone] = 1
    unvisited = collections.deque(distances_to_border.items())
    while unvisited:
        current, current_distance = unvisited.popleft()
        for neighbor in filter(owned, neighbors(current)):
            if neighbor not in distances_to_border:
                distances_to_border[neighbor] = current_distance + 1
                unvisited.append((neighbor, current_distance + 1))
    return distances_to_border.get

def place_pods(zones, npods):
    i = -1 # in case the loop doesn't run (no zones or no pods)
    for i, zone in enumerate(itertools.islice(zones, npods)):
        print("1", zone, sep=" ", end=" ")
    return npods - (i + 1)

def owner(zone):
    return _zone_states[zone][0]
def owned_by(zone, player):
    return owner(zone) == player 
def owned(zone):
    return owned_by(zone, my_id)
def not_owned(zone):
    return not owned(zone)
def neutral(zone):
    return owned_by(zone, -1)
def npods(zone, player):
    return _zone_states[zone][player + 1]
def occupied_by_enemy(zone):
    return any(npods(zone, player) for player in range(nplayers) if player != my_id)
def nmy_pods(zone):
    return npods(zone, my_id)
def occupied_by_me(zone):
    return nmy_pods(zone) > 0
def border(zone):
    return owned(zone) and any(not owned(neighbor) for neighbor in neighbors(zone))
def frontline(zone):
    return owned(zone) and any(occupied_by_enemy(neighbor) for neighbor in neighbors(zone))
def fight(zone):
    return occupied_by_me(zone) and occupied_by_enemy(zone)



for turn in itertools.count():
    nplatinum = stdin(0)
    _zone_states = {zone: zone_state for zone, *zone_state in stdin(nzones)}
    
    distance_to_border = make_border_map()
    
    my_squadrons = filter(occupied_by_me, map)
    if my_squadrons:
        for squadron in my_squadrons:
            possible_destination = neighbors(squadron)
            possible_destinations_not_owned = tuple(filter(not_owned, possible_destination))
            if possible_destinations_not_owned:
                possible_destinations_not_owned = sorted(possible_destinations_not_owned, key=platinum, reverse=True)
                selected_destinations = itertools.islice(possible_destinations_not_owned, nmy_pods(squadron))
            else:
                if not distance_to_border(possible_destination[0]): continue # no path to a border
                possible_destination = sorted(possible_destination, key=distance_to_border, reverse=False)
                selected_destinations = itertools.islice(possible_destination, nmy_pods(squadron))
            for selected_destination in selected_destinations:
                print("1", squadron, selected_destination, sep=" ", end=" ")
        print()
    else:
        print("WAIT")
    
    nnew_pods = nplatinum // 20
    if nnew_pods:
        for zone_kind in (border, frontline, fight, neutral):
            nnew_pods = place_pods(filter(zone_kind, map), nnew_pods)
            if not nnew_pods: break
        print()
    else: print("WAIT")
    