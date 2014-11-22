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
    def neighbors_getter(zone, key=lambda zone: zone, reverse=False):
        return sorted(neighbors[zone], key=key, reverse=reverse)
    return neighbors_getter
neighbors = make_neighbor_getter() 

_allzones = list(range(nzones))
random.shuffle(_allzones) # prevent grouped spawning
world = sorted(_allzones, key=platinum, reverse=True)

def make_border_map():
    distances_to_border = {}
    for zone in filter(border, world):
        distances_to_border[zone] = 1
    unvisited = collections.deque(distances_to_border.items())
    while unvisited:
        current, current_distance = unvisited.popleft()
        for neighbor in filter(owned, neighbors(current)):
            if neighbor not in distances_to_border:
                distances_to_border[neighbor] = current_distance + 1
                unvisited.append((neighbor, current_distance + 1))
    return distances_to_border.get

def make_strategic_map():
    distances_to_strategic_asset = {}
    for zone in filter(capturable_source, world):
        distances_to_strategic_asset[zone] = 0
    unvisited = collections.deque(distances_to_strategic_asset.items())
    while unvisited:
        current, current_distance = unvisited.popleft()
        for neighbor in neighbors(current):
            if neighbor not in distances_to_strategic_asset:
                distances_to_strategic_asset[neighbor] = current_distance + 1
                unvisited.append((neighbor, current_distance + 1))
    return {zone: (distance, platinum(zone)) for zone, distance in distances_to_strategic_asset.items()}.get

def place_pods(zones, npods):
    i = -1 # in case the loop doesn't run (no zones or no pods)
    for i, zone in enumerate(itertools.islice(zones, npods)):
        print("1", zone, sep=" ", end=" ")
    return npods - (i + 1)


def continent(zone):
    if zone <= 49: return "america"
    if zone in (143, 149, 150): return "japan"
    if zone in (57, 67, 78, 89, 97, 104, 113): return "antartica"
    return "eaao"
def not_antartica(zone):
    return continent(zone) != "antartica"
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
def safe(zone):
    return all(not occupied_by_enemy(neighbor) for neighbor in neighbors(zone))
def border(zone):
    return owned(zone) and any(not owned(neighbor) for neighbor in neighbors(zone))
def safe_border(zone):
    return border(zone) and safe(zone)
def defended_border(zone):
    return border(zone) and occupied_by_me(zone)
def frontline(zone):
    return owned(zone) and any(occupied_by_enemy(neighbor) for neighbor in neighbors(zone))
def active_frontline(zone):
    return frontline(zone) and occupied_by_me(zone)
def fight(zone):
    return occupied_by_me(zone) and occupied_by_enemy(zone)
def quickwin(zone):
    return neutral(zone) and all(map(safe, neighbors(zone)))
def source(zone):
    return platinum(zone) > 0
def capturable_source(zone):
    return source(zone) and not owned(zone)
def large_source(zone):
    return platinum(zone) >= 4
def capturable_large_source(zone):
    return not owned(zone) and large_source(zone)
def undefended_capturable_large_source(zone):
    return capturable_large_source(zone) and not occupied_by_enemy(zone) and not any(map(occupied_by_enemy, neighbors(zone)))
def owned_large_source(zone):
    return owned(zone) and large_source(zone)
def owned_large_source_under_attack(zone):
    return owned_large_source(zone) and frontline(zone)
def spawn(zone):
    return neutral(zone) or owned(zone)
def beachhead(zone):
    return spawn(zone) and any(map(undefended_capturable_large_source, neighbors(zone)))


for turn in itertools.count():
    nplatinum = stdin(0)
    _zone_states = {zone: zone_state for zone, *zone_state in stdin(nzones)}
    
    distance_to_border = make_border_map()
    distance_to_capturable_source = make_strategic_map()
    
    my_squadrons = filter(occupied_by_me, world)
    if my_squadrons:
        for squadron in my_squadrons:
            squadron_size = nmy_pods(squadron)
            possible_destination = neighbors(squadron)
            possible_destinations_not_owned = tuple(filter(not_owned, possible_destination))
            if possible_destinations_not_owned:
                possible_destinations_not_owned = sorted(possible_destinations_not_owned, key=platinum, reverse=True)
                selected_destinations = possible_destinations_not_owned[:squadron_size]
            else:
                if distance_to_capturable_source(possible_destination[0]) is not None:
                    distance = distance_to_capturable_source
                elif distance_to_border(possible_destination[0]) is not None:
                    distance = distance_to_border       
                else:
                    continue
                possible_destination = sorted(possible_destination, key=distance, reverse=False)
                selected_destinations = possible_destination[:squadron_size]
            for _, selected_destination in zip(range(squadron_size), itertools.cycle(selected_destinations)):
                print("1", squadron, selected_destination, sep=" ", end=" ")
        print()
    else:
        print("WAIT")
    
    nnew_pods = nplatinum // 20
    if turn == 0:
        place_pods(world[5:], nnew_pods)
        print()
    elif nnew_pods:
        for zone_kind in (owned_large_source_under_attack, beachhead, quickwin, safe_border, defended_border, neutral):
            nnew_pods = place_pods(filter(zone_kind, world), nnew_pods)
            if not nnew_pods: break
        print()
    else: print("WAIT")
    