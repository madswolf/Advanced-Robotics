from Models import Actions, Zones, States

class IllegalActions:
    General = [

    ]

    Avoider = General + [

    ]

    Seeker = General + [
        
    ]

class IllegalStateActions:
    General = [
        
    ]

    Avoider = General + [

    ]

    Seeker = General + [
        
    ]

class IllegalZoneActions:
    General = [
        (Actions.Forward, Zones.EdgeFront),
        (Actions.Forward, Zones.EdgeLeft),
        (Actions.Forward, Zones.EdgeRight),
        (Actions.Left, Zones.EdgeFront),
        (Actions.Left, Zones.EdgeLeft),
        (Actions.Left, Zones.EdgeRight)
    ]

    Avoider = General + [
        #(Actions.Forward, Zones.Safe), # TODO remove after safe zone logic
        #(Actions.Right, Zones.Safe)
    ]

    Seeker = General + [
        
    ]