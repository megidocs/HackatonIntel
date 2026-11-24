"""Synthetic training families and independently worded smoke-test examples."""

from backend.report_extraction import LOCATIONS

LABELS = ("accident", "fire", "medical", "roadblock")

TRAINING_FAMILIES = {
    "accident": (
        "A taxi hit a delivery truck", "A cyclist was struck by a car",
        "Two cars crashed and one driver is trapped", "A van overturned into another vehicle",
        "A bus rear-ended a sedan", "A motorcycle collided with a taxi",
        "An SUV struck a pedestrian at a crossing", "A multi-car pileup damaged several parked vehicles",
    ),
    "fire": (
        "Flames are coming from an apartment", "A kitchen fryer caught fire",
        "There is heavy smoke and an active fire in a shop", "A dumpster is burning",
        "An electrical cabinet is on fire", "The caller sees flames coming out of a truck",
        "A hotel guest reports a mattress burning", "Fire has spread across the basement ceiling",
    ),
    "medical": (
        "A person collapsed and is unresponsive", "A patient has chest pain and difficulty breathing",
        "Someone is having a severe allergic reaction", "An adult is having a seizure",
        "A person fell and cannot move their leg", "Someone is choking and needs an ambulance",
        "The caller says an elderly person may be having a stroke", "A sick person has fainted on the sidewalk",
    ),
    "roadblock": (
        "A fallen tree is blocking the road", "A broken-down truck is stopped across the intersection",
        "A sinkhole has closed one lane", "Construction barriers block all traffic",
        "Floodwater is blocking the street", "A fallen utility pole is obstructing both lanes",
        "A protest has closed the road", "A spill has made both lanes impassable",
    ),
}

# Different phrasing and cases, with overlapping cues that can confuse either model.
TEST_REPORTS = (
    ("accident", "Near Bryant Park a cab sideswiped a coach, now both are in the bus lane."),
    ("accident", "A scooter rider is down at Union Square after a driver opened a door in front of them."),
    ("accident", "At 5th Ave near 34th St two cars crashed, one occupant trapped and smoke from the hood."),
    ("accident", "A car went into the back of a postal vehicle outside Bellevue Hospital. No flames."),
    ("accident", "Vehicle-to-vehicle impact at Washington Square Park, airbags deployed."),
    ("accident", "Two motorists exchanged insurance details after bumping each other at Columbus Circle."),
    ("accident", "A coach clipped a bicyclist at Madison Square Park. Rider is awake."),
    ("accident", "Witness at Times Square says a pedestrian was knocked down by a moving sedan."),
    ("fire", "Emergency call from Bryant Park: orange flames visible through a cafe window."),
    ("fire", "There is an active rubbish fire by Union Square, no injuries mentioned."),
    ("fire", "The caller at Fifth and 34th says a parked vehicle is burning. There was no collision."),
    ("fire", "Smoke and visible flames are coming from a generator beside Bellevue Hospital."),
    ("fire", "A grease blaze is spreading through a restaurant by Washington Square Park."),
    ("fire", "Possible people inside a building that is on fire near Columbus Circle."),
    ("fire", "At Madison Square Park a food cart's fuel cylinder ignited."),
    ("fire", "A display sign in Times Square is smoking and sparks have ignited the awning."),
    ("medical", "Outside Bryant Park a person is awake but one side of their face is drooping."),
    ("medical", "At Union Square a child has swallowed something and is struggling for air."),
    ("medical", "Someone near Fifth Avenue and 34th Street suddenly became confused and lost consciousness."),
    ("medical", "Outside Bellevue Hospital a caller reports very low blood sugar and shaking."),
    ("medical", "A person at Washington Square Park is pale, sweating and says their chest feels tight."),
    ("medical", "Someone tripped near Columbus Circle and has a badly bleeding arm. No vehicles involved."),
    ("medical", "Caller requests an ambulance at Madison Square Park for a person who stopped breathing."),
    ("medical", "Near Times Square a diabetic is disoriented and cannot stand unaided."),
    ("roadblock", "Loose scaffolding across the entire carriageway by Bryant Park. No injury or impact reported."),
    ("roadblock", "Traffic is holding at Union Square because a big branch lies across the crossing."),
    ("roadblock", "Near Fifth and 34th a flooded underpass is impassable. The vehicles are all stopped safely."),
    ("roadblock", "A delivery truck by Bellevue Hospital has a dead engine and is blocking both lanes."),
    ("roadblock", "Debris from a facade is everywhere in the lane beside Washington Square Park."),
    ("roadblock", "Caller reports a caved-in roadway at Columbus Circle and needs it closed."),
    ("roadblock", "A street festival barrier was left in the roadway at Madison Square Park."),
    ("roadblock", "A broken water main has shut the road at Times Square. Nobody needs medical aid."),
)

def training_reports():
    return [
        (kind, f"{sentence} near {location}.")
        for kind, sentences in TRAINING_FAMILIES.items()
        for sentence in sentences
        for location in LOCATIONS
    ]
