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
    def sorted_view(key, reverse=True):
        return {zone: sorted(zone_neighbors, key=key, reverse=reverse) for zone, zone_neighbors in neighbors.items()}.get
    return sorted_view
neighbors_by = make_neighbor_getter()
#plain_neighbors = neighbors_by(lambda zone: zone)
#magnetism = {zone: platinum(zone) + sum(platinum(neighbor) for neighbor in plain_neighbors(zone)) for zone in range(nzones)}.get
neighbors = neighbors_by(platinum)
map = sorted(range(nzones), key=platinum, reverse=True)


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

while True:
    platinum = stdin(0)
    _zone_states = {zone: zone_state for zone, *zone_state in stdin(nzones)}
    
    my_squadrons = filter(occupied_by_me, map)
    if my_squadrons:
        for squadron in my_squadrons:
            possible_destination = neighbors(squadron)
            possible_destinations_not_owned = tuple(filter(not_owned, possible_destination))
            if possible_destinations_not_owned:
                selected_destinations = possible_destinations_not_owned[:nmy_pods(squadron)]
            else:
                selected_destinations = random.sample(possible_destination, nmy_pods(squadron))
            for selected_destination in selected_destinations:
                print("1", squadron, selected_destination, sep=" ", end=" ")
        print()
    else:
        print("WAIT")
    
    nnew_pods = platinum // 20
    if nnew_pods:
        for zone_kind in (neutral, frontline, border):
            nnew_pods = place_pods(filter(zone_kind, map), nnew_pods)
            if not nnew_pods: break
        print()
    else: print("WAIT")
    