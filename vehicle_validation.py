
import re

def has_vehicle_info(query):
    """
    Check if query contains a valid part mention
    """
    if not query:
        return False
        
    # Expanded list of common part terms for better validation
    part_terms = [
        # Exterior/Body parts
        "bumper", "front bumper", "rear bumper", "grille", "headlight", "tail light", 
        "taillight", "fender", "hood", "trunk", "door", "mirror", "side mirror", "window",
        "windshield", "wiper", "antenna", "spoiler", "diffuser", "splash guard", "mud flap",
        
        # Engine/Drivetrain
        "engine", "motor", "transmission", "flywheel", "clutch", "differential", "axle",
        "driveshaft", "drive shaft", "cv joint", "cv axle", "transfer case", "valve", "gasket",
        "piston", "crankshaft", "camshaft", "timing", "timing belt", "timing chain", "pulley",
        "belt", "water pump", "oil pump", "radiator", "coolant", "thermostat", "injector",
        "fuel pump", "fuel filter", "fuel tank", "carburetor", "throttle body", "intake", "manifold", 
        "exhaust", "muffler", "catalytic", "converter", "turbo", "supercharger",
        
        # Electrical
        "alternator", "starter", "battery", "spark plug", "ignition", "coil", "distributor",
        "ecu", "computer", "sensor", "module", "control", "relay", "fuse", "harness", "wiring",
        "wire", "switch", "motor", "resistor", "regulator", "solenoid", "actuator",
        
        # Suspension/Steering
        "shock", "strut", "spring", "control arm", "ball joint", "tie rod", "rack", "pinion",
        "steering", "wheel bearing", "hub", "bushing", "sway bar", "stabilizer", "spindle",
        "knuckle", "suspension", "link", "idler arm", "pitman arm", "center link", "drag link",
        
        # Brakes
        "brake", "rotor", "drum", "pad", "shoe", "caliper", "cylinder", "master cylinder",
        "booster", "abs", "line", "hose", "fluid", "reservoir", "proportioning valve",
        
        # HVAC
        "heater", "ac", "a/c", "air conditioning", "compressor", "condenser", "evaporator",
        "blower", "fan", "resistor", "actuator", "valve", "expansion valve", "drier",
        
        # Interior
        "seat", "carpet", "dash", "dashboard", "console", "shifter", "gauge", "cluster",
        "stereo", "radio", "speaker", "amplifier", "control", "switch", "handle", "latch",
        "lock", "sunroof", "sun visor", "mirror", "trim", "panel", "armrest", "cup holder",
        
        # Wheels/Tires
        "wheel", "rim", "tire", "hub", "lug", "stud", "cap", "cover"
    ]
    
    # Check if any part term is found in the query
    query_lower = query.lower()
    
    # Check for exact matches first (with word boundaries)
    for part in part_terms:
        if re.search(r'\b' + re.escape(part) + r'\b', query_lower):
            return True
    
    # If no exact match, check for partial matches (for compound terms)
    has_part = any(part in query_lower for part in part_terms)
    
    return has_part

def get_missing_info_message(query):
    """
    Return informative message if no part is mentioned, otherwise None
    """
    if not has_vehicle_info(query):
        return "Please specify what auto part you're looking for (e.g., brake pads, headlight, oil filter)."
    return None