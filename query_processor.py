import re
import json
from functools import lru_cache

class EnhancedQueryProcessor:
    """
    Enhanced query processor that can handle various input formats
    and extract structured vehicle and part information.
    Updated to properly handle structured data from multiple fields.
    """
    
    def __init__(self):
        # Load vehicle data (in production, this would be from your database)
        self.vehicle_makes = ["acura", "alfa romeo", "aston martin", "audi", "bentley", "bmw", "buick", 
    "cadillac", "chevrolet", "chrysler", "dodge", "ferrari", "fiat", "ford", 
    "genesis", "gmc", "honda", "hyundai", "infiniti", "jaguar", "jeep", "kia", 
    "lamborghini", "land rover", "lexus", "lincoln", "lotus", "maserati", 
    "mazda", "mclaren", "mercedes-benz", "mini", "mitsubishi", "nissan", 
    "porsche", "ram", "rolls-royce", "subaru", "tesla", "toyota", "volkswagen", 
    "volvo","alfa romeo", "aston martin", "bentley", "bmw", "bugatti", 
    "genesis", "jaguar", "lamborghini", "land rover", "lotus", 
    "maserati", "mercedes-benz", "mini", "porsche", "rolls-royce"]
        
        # Common synonyms for makes
        self.make_synonyms = {
            "chevy": "chevrolet",
    "chev": "chevrolet",
    "chvy": "chevrolet",
    "vw": "volkswagen",
    "vdub": "volkswagen",
    "mercedes": "mercedes-benz",
    "benz": "mercedes-benz",
    "merc": "mercedes-benz", 
    "mb": "mercedes-benz",
    "beemer": "bmw",
    "bimmer": "bmw",
    "landrover": "land rover",
    "range rover": "land rover",
    "subie": "subaru",
    "subi": "subaru",
    "toy": "toyota",
    "yota": "toyota",
    "dodge ram": "ram",
    "ram trucks": "ram",
    "alfa": "alfa romeo",
    "lambo": "lamborghini",
    "rari": "ferrari",
    "porsche": "porsche",
    "pcar": "porsche",
    "gm": "general motors",
    "general motors": "gm",
    "hyundai motors": "hyundai",
    "caddy": "cadillac",
    "linc": "lincoln",
    "lexus": "lexus",
    "vette": "corvette",
    "stang": "mustang",
    "bimmer": "bmw",
    "audi": "audi",
    "acura": "acura",
    "infiniti": "infiniti", 
    "kia motors": "kia",
    "jeep": "jeep",
    "mini": "mini",
    "genesis": "genesis",
    "mazda": "mazda",
    "volvo": "volvo",
    "tesla": "tesla",
    "chrysler": "chrysler"
        }
        
        # Load part terminology dictionary
        self.part_terms = self._load_part_terms()
        
        # Normalized common part categories for better matching
        self.part_categories = {
           "engine": ["engine block", "short block", "long block", "engine assembly", "motor", "powertrain", "engine rebuild kit"],
    
    "engine_accessory": ["belt", "pulley", "tensioner", "idler pulley", "serpentine belt", "v-belt", "timing belt", "timing chain"],
    
    "engine_electrical": ["alternator", "starter", "starter motor", "ignition coil", "coil pack", "spark plug", "spark plug wire", "distributor", "voltage regulator"],
    
    "engine_cooling": ["radiator", "cooling fan", "water pump", "thermostat", "coolant reservoir", "expansion tank", "overflow tank", "fan clutch", "radiator cap", "radiator hose"],
    
    "engine_fuel": ["fuel pump", "fuel filter", "fuel injector", "fuel pressure regulator", "fuel rail", "carburetor", "throttle body", "fuel tank", "fuel cap", "fuel gauge"],
    
    "engine_air": ["air filter", "air intake", "mass air flow sensor", "maf sensor", "intake manifold", "intake hose", "air box", "throttle body", "air cleaner"],
    
    "engine_exhaust": ["exhaust manifold", "header", "catalytic converter", "cat converter", "muffler", "resonator", "exhaust pipe", "tail pipe", "exhaust tip", "o2 sensor", "oxygen sensor"],
    
    "engine_electrical_sensors": ["cam sensor", "camshaft sensor", "camshaft position sensor", "crank sensor", "crankshaft sensor", "crankshaft position sensor", "o2 sensor", "oxygen sensor", "map sensor", "maf sensor", "mass air flow sensor", "coolant temp sensor", "ect sensor", "engine coolant temperature sensor", "knock sensor", "tps", "throttle position sensor"],
    
    "engine_gaskets": ["head gasket", "valve cover gasket", "oil pan gasket", "intake manifold gasket", "exhaust manifold gasket", "timing cover gasket", "water pump gasket", "thermostat gasket", "gasket set"],
    
    # Transmission parts
    "transmission": ["transmission assembly", "automatic transmission", "manual transmission", "trans", "gearbox", "transmission rebuild kit", "transmission filter", "transmission pan", "transmission mount"],
    
    "transmission_clutch": ["clutch kit", "clutch disc", "pressure plate", "throwout bearing", "release bearing", "slave cylinder", "master cylinder", "flywheel", "clutch cable", "clutch line"],
    
    "transmission_transfer": ["transfer case", "transfer case motor", "transfer case switch", "transfer case chain", "transfer case seal"],
    
    "transmission_differential": ["differential", "differential cover", "differential bearing", "axle shaft", "axle bearing", "axle seal", "pinion seal", "ring and pinion", "spider gear"],
    
    "transmission_driveshaft": ["drive shaft", "driveshaft", "u-joint", "universal joint", "cv axle", "cv joint", "cv boot", "half shaft", "propeller shaft"],
    
    # Brake system
    "brake": ["brake pad", "brake shoe", "brake rotor", "brake drum", "brake caliper", "brake hose", "brake line", "brake master cylinder", "wheel cylinder", "abs module", "abs sensor"],
    
    "brake_hydraulic": ["brake master cylinder", "wheel cylinder", "brake caliper", "brake hose", "brake line", "proportioning valve", "combination valve", "brake fluid reservoir"],
    
    "brake_mechanical": ["brake pad", "brake shoe", "brake rotor", "brake drum", "parking brake cable", "emergency brake cable", "brake hardware kit", "brake dust shield"],
    
    "brake_abs": ["abs module", "abs control unit", "abs sensor", "wheel speed sensor", "abs pump", "abs relay", "abs harness"],
    
    # Suspension and steering
    "suspension": ["shock absorber", "shock", "strut", "strut assembly", "coil spring", "leaf spring", "air spring", "air bag", "control arm", "ball joint", "tie rod", "sway bar", "stabilizer bar", "bushing"],
    
    "suspension_front": ["front shock", "front strut", "front coil spring", "front control arm", "front ball joint", "front tie rod", "front sway bar", "front stabilizer link", "front bushing"],
    
    "suspension_rear": ["rear shock", "rear strut", "rear coil spring", "rear leaf spring", "rear control arm", "rear ball joint", "rear sway bar", "rear stabilizer link", "rear bushing", "trailing arm"],
    
    "steering": ["steering rack", "rack and pinion", "power steering pump", "steering gear", "steering box", "steering column", "steering shaft", "tie rod", "tie rod end", "idler arm", "pitman arm", "steering knuckle"],
    
    "wheel_hub": ["wheel hub", "wheel bearing", "hub assembly", "spindle", "axle nut", "wheel stud", "lug nut"],
    
    # Body parts
    "body_exterior": ["hood", "fender", "quarter panel", "door", "door panel", "trunk lid", "tailgate", "bumper", "bumper cover", "grille", "spoiler", "mirror", "windshield", "rear window"],
    
    "body_trim": ["molding", "trim", "emblem", "badge", "weatherstrip", "window molding", "door molding", "rocker panel molding", "pillar trim"],
    
    "body_hardware": ["door handle", "door lock", "door hinge", "hood latch", "hood strut", "hood hinge", "trunk latch", "trunk strut", "window regulator", "window motor", "wiper blade", "wiper arm", "wiper motor"],
    
    # Interior parts
    "interior": ["dashboard", "dash panel", "instrument cluster", "gauge cluster", "glove box", "console", "armrest", "seat", "seat belt", "seat cover", "headliner", "sun visor", "carpet", "floor mat"],
    
    "interior_electrical": ["radio", "stereo", "speaker", "amplifier", "cd player", "antenna", "climate control", "power window switch", "door lock switch", "mirror switch", "seat switch"],
    
    "interior_climate": ["heater core", "ac compressor", "ac condenser", "ac evaporator", "ac hose", "ac accumulator", "ac orifice tube", "ac expansion valve", "blower motor", "blower resistor", "heater valve", "heater hose"],
    
    # Lighting
    "lighting": ["headlight", "tail light", "fog light", "turn signal", "marker light", "brake light", "reverse light", "license plate light", "dome light", "map light", "headlight bulb", "tail light bulb"],
    
    # Electrical
    "electrical": ["battery", "alternator", "starter", "relay", "fuse", "fuse box", "junction box", "wiring harness", "wire harness", "sensor", "switch", "computer", "control module", "control module", "ecu", "ecm", "pcm"],
    
    "electrical_modules": ["engine control module", "ecm", "powertrain control module", "pcm", "body control module", "bcm", "transmission control module", "tcm", "abs control module", "ebcm", "airbag control module", "srs module"],
    
    "electrical_switches": ["power window switch", "door lock switch", "mirror switch", "seat switch", "headlight switch", "wiper switch", "turn signal switch", "ignition switch", "brake light switch", "cruise control switch"],
    
    # Wheels and tires
    "wheel": ["wheel", "rim", "alloy wheel", "steel wheel", "wheel cover", "hub cap", "center cap", "lug nut", "wheel stud", "wheel lock", "wheel weight"],
    
    "tire": ["tire", "all season tire", "winter tire", "summer tire", "performance tire", "spare tire", "tire valve", "tire pressure sensor", "tpms sensor"],
    
    # Miscellaneous
    "fluid": ["oil", "coolant", "antifreeze", "transmission fluid", "brake fluid", "power steering fluid", "windshield washer fluid", "refrigerant", "freon"],
    
    "maintenance": ["oil filter", "air filter", "cabin filter", "fuel filter", "pcv valve", "spark plug", "wiper blade", "battery", "belt", "hose"]
        }
    
        
        # Common vehicle models by make
        self.make_models = {
            "acura": ["mdx", "rdx", "tlx", "ilx", "nsx", "integra", "zdx", "tsx", "tl", "rl", "csx", "rsx", "legend", "vigor"],
    
    "honda": ["accord", "civic", "cr-v", "crv", "pilot", "odyssey", "ridgeline", "hr-v", "hrv", "passport", "fit", "clarity", "insight", "element", "s2000", "crosstour", "prelude", "cr-z", "crz", "del sol"],
    
    "lexus": ["es", "is", "gs", "ls", "rc", "lc", "nx", "rx", "gx", "lx", "ux", "es350", "es300h", "is300", "is350", "gs350", "ls500", "nx300", "rx350", "gx460", "lx570", "ux250h", "rcf", "lc500", "rx450h", "is500"],
    
    "toyota": ["camry", "corolla", "rav4", "highlander", "4runner", "tacoma", "tundra", "sienna", "prius", "avalon", "sequoia", "venza", "c-hr", "chr", "supra", "gr86", "mirai", "matrix", "yaris", "echo", "celica", "land cruiser", "fj cruiser", "crown"],
    
    "nissan": ["altima", "sentra", "maxima", "rogue", "pathfinder", "murano", "armada", "frontier", "titan", "kicks", "versa", "juke", "leaf", "z", "370z", "350z", "240sx", "gt-r", "gtr", "cube", "xterra", "quest"],
    
    "infiniti": ["q50", "q60", "qx50", "qx55", "qx60", "qx80", "g35", "g37", "fx35", "fx45", "m35", "m45", "ex35", "jx35", "qx4", "qx56", "q40", "q45", "q70"],
    
    "mazda": ["3", "mazda3", "6", "mazda6", "cx-3", "cx3", "cx-30", "cx30", "cx-5", "cx5", "cx-9", "cx9", "mx-5", "miata", "mx-5 miata", "rx-7", "rx7", "rx-8", "rx8", "mpv", "tribute", "cx-7", "cx7", "protege", "millenia", "navajo", "b-series", "b2300", "b4000"],
    
    "subaru": ["forester", "outback", "impreza", "legacy", "crosstrek", "ascent", "wrx", "brz", "sti", "wrx sti", "baja", "tribeca", "svx", "justy", "loyale", "sambar"],
    
    "mitsubishi": ["outlander", "eclipse cross", "mirage", "outlander sport", "lancer", "galant", "eclipse", "endeavor", "diamante", "3000gt", "montero", "raider", "expo", "precis", "mighty max"],
    
    # American Brands
    "chevrolet": ["silverado", "camaro", "corvette", "malibu", "equinox", "tahoe", "suburban", "colorado", "traverse", "blazer", "impala", "spark", "trax", "bolt", "trailblazer", "cavalier", "cobalt", "cruze", "sonic", "aveo", "s10", "monte carlo", "nova", "el camino", "chevelle", "caprice", "bel air", "avalanche", "astro", "express", "ssr", "hhr"],
    
    "ford": ["f-150", "f150", "f-250", "f250", "f-350", "f350", "mustang", "explorer", "escape", "fusion", "focus", "edge", "expedition", "ranger", "bronco", "taurus", "maverick", "ecosport", "flex", "transit", "fiesta", "crown victoria", "five hundred", "freestyle", "excursion", "e-series", "e150", "e250", "e350", "thunderbird", "probe", "contour", "tempo", "escort", "gt", "model a", "model t", "fairlane", "falcon", "galaxie"],
    
    "gmc": ["sierra", "yukon", "acadia", "terrain", "canyon", "savana", "hummer ev", "jimmy", "envoy", "sonoma", "safari", "syclone", "typhoon", "suburban", "sprint", "rally", "vandura", "s15"],
    
    "cadillac": ["escalade", "ct4", "ct5", "xt4", "xt5", "xt6", "ct6", "ats", "cts", "xts", "srx", "sts", "dts", "eldorado", "seville", "deville", "fleetwood", "allante", "brougham", "catera"],
    
    "buick": ["enclave", "encore", "lesabre", "envision", "lacrosse", "regal", "verano", "cascada", "lesabre", "century", "skylark", "park avenue", "riviera", "roadmaster", "electra", "rainier", "rendezvous", "terraza", "lucerne"],
    
    "chrysler": ["300", "pacifica", "voyager", "town & country", "pt cruiser", "sebring", "200", "concorde", "crossfire", "aspen", "cirrus", "imperial", "lhs", "new yorker", "fifth avenue", "cordoba", "newport", "lebaron"],
    
    "dodge": ["charger", "challenger", "durango", "journey", "grand caravan", "ram", "viper", "neon", "avenger", "dart", "nitro", "caliber", "intrepid", "stealth", "magnum", "stratus", "shadow", "dynasty", "spirit", "colt", "daytona", "caravan", "omni"],
    
    "jeep": ["wrangler", "grand cherokee", "cherokee", "compass", "renegade", "gladiator", "wagoneer", "grand wagoneer", "liberty", "patriot", "commander", "cj", "scrambler", "comanche"],
    
    "ram": ["1500", "2500", "3500", "promaster", "promaster city", "dakota"],
    
    "lincoln": ["navigator", "aviator", "nautilus", "corsair", "continental", "mkz", "mkt", "mks", "mkx", "mkc", "town car", "ls", "blackwood", "mark lt", "mark viii", "mark vii", "mark vi", "mark v", "mark iv", "zephyr"],
    
    "tesla": ["model 3", "model s", "model x", "model y", "cybertruck", "roadster"],
    
    # European Brands
    "bmw": ["3-series", "5-series", "7-series", "x1", "x3", "x5", "x7", "z4", "i4", "i7", "ix", "m3", "m5", "m8", "x3m", "x5m", "330i", "530i", "740i", "x3 xdrive30i", "x5 xdrive40i", "335i", "328i", "325i", "540i", "535i", "m340i", "m550i", "z3", "8-series", "6-series", "4-series", "2-series", "1-series", "x2", "x4", "x6", "i3", "i8"],
    
    "mercedes-benz": ["c-class", "e-class", "s-class", "a-class", "glc", "gle", "gls", "g-class", "cla", "cls", "sl", "slk", "amg gt", "eqs", "eqe", "c300", "e350", "s500", "glc300", "gle350", "gle450", "g550", "c43 amg", "e63 amg", "s63 amg", "c63 amg", "glc43 amg", "ml350", "ml550", "gl450", "gl550", "gla", "glb", "slc", "clk", "sprinter", "metris"],
    
    "audi": ["a3", "a4", "a5", "a6", "a7", "a8", "q3", "q5", "q7", "q8", "tt", "r8", "e-tron", "s3", "s4", "s5", "s6", "s7", "s8", "rs3", "rs5", "rs7", "sq5", "sq7", "sq8", "a4 allroad", "a6 allroad", "allroad", "a3 sportback", "80", "90", "100", "200", "v8", "cabriolet", "coupe quattro"],
    
    "volkswagen": ["jetta", "passat", "golf", "tiguan", "atlas", "id.4", "beetle", "arteon", "taos", "touareg", "rabbit", "cc", "eos", "gti", "gli", "r32", "golf r", "corrado", "scirocco", "thing", "karmann ghia", "type 1", "type 2", "type 3", "vanagon", "new beetle", "cabrio", "phaeton", "routan"],
    
    "volvo": ["xc90", "xc60", "xc40", "s60", "s90", "v60", "v90", "c40", "c30", "s40", "s80", "v40", "v50", "v70", "850", "740", "940", "960", "240", "amazon", "p1800", "pv444", "pv544", "c70"],
    
    "porsche": ["911", "cayenne", "macan", "panamera", "boxster", "cayman", "taycan", "928", "944", "968", "914", "356", "912", "718"],
    
    "land rover": ["range rover", "discovery", "defender", "range rover sport", "range rover evoque", "range rover velar", "discovery sport", "lr3", "lr4", "lr2", "freelander"],
    
    "jaguar": ["f-pace", "e-pace", "i-pace", "xf", "xe", "f-type", "xj", "xk", "s-type", "x-type", "xjs", "x300", "x308", "mark 2", "xkr", "xfr", "xjr"],
    
    "alfa romeo": ["giulia", "stelvio", "4c", "spider", "giulietta", "164", "gtv", "mito"],
    
    "fiat": ["500", "500x", "500l", "124 spider", "500e", "500 abarth", "500c"],
    
    "mini": ["cooper", "countryman", "clubman", "paceman", "coupe", "roadster", "cooper s", "john cooper works", "cooper se", "hardtop", "convertible"],
    
    # Luxury/Exotic Brands
    "bentley": ["continental", "bentayga", "flying spur", "azure", "arnage", "brooklands", "mulsanne"],
    
    "ferrari": ["f8", "roma", "portofino", "sf90", "812", "488", "458", "f12", "california", "laferrari", "enzo", "f430", "360", "550", "355", "348", "testarossa", "f40", "f50"],
    
    "lamborghini": ["huracan", "aventador", "urus", "gallardo", "murcielago", "countach", "diablo", "reventon", "veneno", "centenario", "sesto elemento"],
    
    "maserati": ["ghibli", "levante", "quattroporte", "mc20", "granturismo", "grancabrio", "spyder", "coupe", "bora", "merak", "biturbo"],
    
    "mclaren": ["720s", "765lt", "570s", "gt", "artura", "senna", "p1", "mp4-12c", "elva"],
    
    "rolls-royce": ["phantom", "ghost", "wraith", "dawn", "cullinan", "silver shadow", "silver spur", "corniche", "camargue", "silver seraph"],
    
    "aston martin": ["db11", "vantage", "dbs", "dbx", "db9", "rapide", "vanquish", "db7", "virage", "lagonda", "db5", "db4"],
    
    "lotus": ["evora", "elise", "exige", "emira", "esprit", "elan", "europa", "eletre"],
    
    "genesis": ["g70", "g80", "g90", "gv70", "gv80", "gv60"],
    "interior": [
        "dashboard", "dash", "console", "center console", "cup holder", 
        "arm rest", "armrest", "seat", "seat belt", "headliner", 
        "sun visor", "shift boot", "steering wheel", "cargo mat", "cargo liner"
    ],
    
    # Electrical parts (expanded)
    "electrical": [
        "fuse box", "junction box", "ecu", "pcm", "bcm", "tcm", 
        "mass air flow sensor", "maf sensor", "coil pack", "abs module",
        "window motor", "window switch", "window master switch", 
        "door lock actuator", "wiper motor", "washer pump", "ignitor",
        "ignition module", "body harness", "speedometer", "cruise control module"
    ],
    
    # Chassis/Frame parts (new category)
    "chassis": [
        "subframe", "crossmember", "frame rail", "impact bar",
        "body mount", "core support", "strut tower", "knuckle", "spindle"
    ],
    
    # Axle/Driveshaft parts (new category)
    "axle": [
        "axle", "rear axle", "front axle", "axle shaft", "cv axle",
        "differential", "transfer case", "drive shaft", "propeller shaft",
        "flywheel", "fly wheel", "torque converter"
    ],
    
    # Door parts (expanded)
    "door": [
        "door latch", "door handle", "door panel", "door lock", 
        "door lock actuator", "window regulator", "power window motor",
        "lock cylinder"
    ],
    
    # HVAC parts (new category)
    "hvac": [
        "heater core", "ac compressor", "blower motor", "ac condenser",
        "expansion valve", "evaporator", "heater valve", "air valve",
        "thermal vacuum switch", "air condition bracket", "ac bracket"
    ],
    
    # Fuel system (expanded)
    "fuel": [
        "fuel pump", "fuel injector", "fuel tank", "fuel line", 
        "gas tank", "fuel rail", "fuel pressure regulator", 
        "fuel door", "gas tank cap", "fuel cap", "pcv valve"
    ],
    "lighting_components": [
    "headlight lens", "headlight housing", "headlight reflector", "bulb socket",
    "projector housing", "hid kit", "led conversion", "headlight switch",
    "tail light lens", "corner light", "turn signal housing", "daytime running light"
    ],

    "interior_components": [
        "headliner material", "dash bezel", "center console lid", "cup holder insert",
        "door panel insert", "dome light lens", "seat track", "window switch panel" 
    ],

    "fluid_system_components": [
        "coolant reservoir cap", "radiator hose upper", "radiator hose lower", 
        "heater hose", "master cylinder reservoir", "power steering reservoir", 
        "overflow tank"
    ],

    "suspension_small_parts": [
        "coil spring isolator", "suspension bushing", "radius arm bushing",
        "leaf spring shackle", "sway bar link", "sway bar bushing",
        "shock mount", "strut mount bearing"
    ],
    
    # Trim/Appearance (new category)
    "trim": [
        "wheel opening molding", "hubcap", "center cap", "fender flare",
        "trim piece", "molding", "emblem", "badge"
    ],
    
    # Belt/Pulley system (new category)
    "belt": [
        "belt tensioner", "tensioner pulley", "idler pulley", 
        "serpentine belt", "timing belt", "timing chain", "drive belt"
    ],
    
    # Transmission (expanded)
    "transmission": [
        "transmission", "gearbox", "trans", "shift cable", "shifter cable",
        "flywheel", "clutch", "torque converter", "shift boot"
    ],
    
    # Lighting (new category)
    "lighting": [
        "headlight", "tail light", "turn light", "turn signal light", 
        "fog light", "brake light", "reverse light", "marker light",
        "dome light", "license plate light",
        "headlight lens", "lens cover", "light lens", "headlamp lens", 
        "clear lens", "plastic lens"
    ]
    
            # Add more makes and models as needed
        }

        # Model formatting preferences (for more accurate search queries)
        self.model_formatting = {
            "f-150": "F-150",
            "f150": "F-150",
            "f-250": "F-250",
            "f250": "F-250",
            "f-350": "F-350",
            "f350": "F-350"
        }
        
        # Year range patterns for Ford trucks (common fitment ranges)
        self.year_range_patterns = {
            "ford": {
                "f-150": {
                    "2009-2014": "12th generation",
                    "2015-2020": "13th generation",
                    "2004-2008": "11th generation"
                }
            }
        }

    def _load_part_terms(self):
        """Load the expanded part terms dictionary"""
        return {
            # Engine components
    "pcv valve": "positive crankcase ventilation valve",
    "egr valve": "exhaust gas recirculation valve",
    "maf sensor": "mass air flow sensor",
    "mass air flow sensor": "mass airflow sensor with housing",
    "o2 sensor": "oxygen sensor",
    "oxygen sensor": "oxygen sensor oem quality",
    "cam sensor": "camshaft position sensor",
    "camshaft sensor": "camshaft position sensor",
    "crank sensor": "crankshaft position sensor",
    "crankshaft sensor": "crankshaft position sensor",
    "coolant temp sensor": "coolant temperature sensor",
    "ect sensor": "engine coolant temperature sensor",
    "map sensor": "manifold absolute pressure sensor",
    "knock sensor": "engine knock sensor",
    "throttle body": "throttle body assembly complete",
    "tps": "throttle position sensor",
    "throttle position sensor": "throttle position sensor with harness",
    "idle air control valve": "idle air control valve oem",
    "iac valve": "idle air control valve",
    "purge valve": "evap purge valve solenoid",
    "evap valve": "evap purge valve solenoid",
    "canister purge valve": "evap canister purge valve",
    "valve cover gasket": "valve cover gasket set",
    "head gasket": "cylinder head gasket set complete",
    "intake manifold gasket": "intake manifold gasket set",
    "exhaust manifold gasket": "exhaust manifold gasket set",
    "oil pan gasket": "oil pan gasket set",
    "timing cover gasket": "timing cover gasket set",
    "valve stem seal": "valve stem seals kit complete",
    "pcv hose": "pcv valve hose",
    "intake manifold": "intake manifold assembly complete",
    "exhaust manifold": "exhaust manifold with gaskets",
    "cylinder head": "cylinder head assembly complete",
    "engine block": "engine block assembly",
    "oil pump": "oil pump assembly",
    "timing chain": "timing chain kit complete",
    "timing belt": "timing belt kit with water pump",
    "timing cover": "timing chain cover",
    
    # Fuel system
    "fuel pump": "fuel pump assembly complete",
    "fuel pressure regulator": "fuel pressure regulator with housing",
    "fuel filter": "fuel filter oem replacement",
    "fuel rail": "fuel rail with injectors",
    "fuel line": "fuel line assembly",
    "fuel tank": "fuel tank assembly complete",
    "fuel cap": "fuel tank cap oem",
    "fuel door": "fuel door assembly",
    "fuel sender": "fuel level sending unit",
    "fuel level sensor": "fuel level sensor sending unit",
    
    # Cooling system
    "radiator": "radiator assembly with fans",
    "radiator cap": "radiator pressure cap oem",
    "radiator hose": "radiator hose kit upper and lower",
    "upper radiator hose": "upper radiator hose oem",
    "lower radiator hose": "lower radiator hose oem",
    "coolant reservoir": "coolant overflow reservoir tank",
    "overflow tank": "coolant overflow tank with cap",
    "coolant tank": "coolant recovery tank complete",
    "expansion tank": "coolant expansion tank with sensor",
    "water pump": "water pump with gasket",
    "thermostat": "thermostat with housing assembly",
    "cooling fan": "engine cooling fan assembly",
    "fan clutch": "fan clutch assembly oem",
    "fan blade": "cooling fan blade assembly",
    "fan shroud": "radiator fan shroud assembly",
    
    # Electrical system
    "alternator": "alternator assembly oem quality",
    "battery": "battery oem replacement",
    "starter": "starter motor assembly",
    "ignition coil": "ignition coil pack",
    "coil pack": "ignition coil pack set",
    "spark plug": "spark plug set",
    "spark plug wire": "spark plug wire set",
    "ignition wire": "ignition wire set premium",
    "distributor": "distributor assembly complete",
    "distributor cap": "distributor cap and rotor kit",
    "rotor": "distributor rotor oem",
    "voltage regulator": "voltage regulator for alternator",
    "fusible link": "fusible link assembly",
    "fuse box": "fuse box assembly complete",
    "junction box": "junction box assembly",
    "relay": "relay switch oem quality",
    "flasher": "turn signal flasher relay",
    "horn": "horn assembly oem sound",
    "wiper motor": "windshield wiper motor assembly",
    "washer pump": "windshield washer pump",
    "headlight switch": "headlight switch with knob",
    "dimmer switch": "headlight dimmer switch",
    "ignition switch": "ignition switch with key",
    
    # Exhaust system
    "catalytic converter": "catalytic converter direct fit",
    "cat converter": "catalytic converter epa compliant",
    "muffler": "muffler assembly with clamps",
    "resonator": "exhaust resonator assembly",
    "exhaust pipe": "exhaust pipe assembly",
    "tail pipe": "exhaust tail pipe assembly",
    "exhaust manifold": "exhaust manifold with gaskets",
    "header": "performance header with gaskets",
    "exhaust gasket": "exhaust gasket set complete",
    "exhaust flange": "exhaust flange with gasket",
    "exhaust hanger": "exhaust hanger rubber mount",
    "exhaust clamp": "exhaust clamp heavy duty",
    "heat shield": "exhaust heat shield",
    
    # Transmission
    "transmission": "transmission assembly complete",
    "transmission mount": "transmission mount with hardware",
    "transmission pan": "transmission oil pan with gasket",
    "transmission filter": "transmission filter with gasket kit",
    "transmission cooler": "transmission oil cooler assembly",
    "transmission line": "transmission cooler line set",
    "torque converter": "torque converter assembly oem",
    "shift solenoid": "transmission shift solenoid kit",
    "clutch": "clutch kit complete",
    "clutch disc": "clutch disc and pressure plate kit",
    "pressure plate": "clutch pressure plate",
    "flywheel": "flywheel assembly",
    "throw out bearing": "clutch release bearing",
    "release bearing": "clutch release bearing",
    "pilot bearing": "clutch pilot bearing",
    "slave cylinder": "clutch slave cylinder",
    "master cylinder": "clutch master cylinder",
    "clutch line": "clutch hydraulic line",
    "shift cable": "transmission shift cable",
    "shift linkage": "transmission shift linkage",
    "transfer case": "transfer case assembly",
    "output shaft": "transmission output shaft",
    "input shaft": "transmission input shaft",
    "shift fork": "transmission shift fork",
    
    # Brakes
    "brake pad": "brake pads front set premium",
    "brake shoe": "brake shoes rear set",
    "brake rotor": "brake rotors premium",
    "brake drum": "brake drum assembly",
    "brake caliper": "brake caliper with bracket",
    "brake hose": "brake hose assembly",
    "brake line": "brake line kit complete",
    "brake master cylinder": "brake master cylinder assembly",
    "wheel cylinder": "wheel cylinder assembly",
    "abs module": "abs control module",
    "abs sensor": "abs wheel speed sensor",
    "wheel speed sensor": "wheel speed sensor with harness",
    "brake booster": "power brake booster assembly",
    "proportioning valve": "brake proportioning valve",
    "brake hardware kit": "brake hardware kit complete",
    "brake dust shield": "brake dust shield",
    "parking brake cable": "parking brake cable assembly",
    "emergency brake cable": "emergency brake cable assembly",
    
    # Suspension
    "shock": "shock absorber assembly premium",
    "strut": "strut assembly complete",
    "strut mount": "strut mount with bearing",
    "spring": "coil spring set",
    "coil spring": "coil spring set heavy duty",
    "leaf spring": "leaf spring assembly",
    "air spring": "air suspension spring",
    "air bag": "air suspension bag",
    "control arm": "control arm with ball joint",
    "upper control arm": "upper control arm assembly",
    "lower control arm": "lower control arm assembly",
    "ball joint": "ball joint premium",
    "tie rod": "tie rod end assembly",
    "tie rod end": "tie rod end premium",
    "inner tie rod": "inner tie rod assembly",
    "outer tie rod": "outer tie rod assembly",
    "idler arm": "idler arm assembly",
    "pitman arm": "pitman arm assembly",
    "center link": "steering center link",
    "drag link": "steering drag link assembly",
    "sway bar": "sway bar assembly",
    "sway bar link": "sway bar link kit",
    "stabilizer bar": "stabilizer bar assembly",
    "stabilizer link": "stabilizer link kit",
    "torsion bar": "torsion bar assembly",
    "track bar": "track bar assembly heavy duty",
    "bushing": "suspension bushing kit",
    "control arm bushing": "control arm bushing set",
    "sway bar bushing": "sway bar bushing set",
    "trailing arm": "trailing arm assembly",
    "trailing arm bushing": "trailing arm bushing set",
    "strut boot": "strut boot and bumper kit",
    "strut bumper": "strut bumper kit",
    "steering knuckle": "steering knuckle assembly",
    "spindle": "wheel spindle assembly",
    "wheel hub": "wheel hub assembly with bearing",
    "wheel bearing": "wheel bearing and hub assembly",
    "cv axle": "cv axle assembly complete",
    "cv joint": "cv joint kit with boot",
    "cv boot": "cv joint boot kit",
    "axle shaft": "axle shaft assembly",
    "axle bearing": "axle bearing and seal kit",
    "axle seal": "axle shaft seal",
    "differential": "differential assembly complete",
    "differential cover": "differential cover with gasket",
    
    # Steering
    "steering rack": "steering rack and pinion assembly",
    "rack and pinion": "rack and pinion assembly complete",
    "power steering pump": "power steering pump with reservoir",
    "steering gear": "steering gear box assembly",
    "steering box": "steering gear box assembly",
    "steering column": "steering column assembly",
    "steering shaft": "steering shaft assembly",
    "steering coupler": "steering shaft coupler",
    "power steering hose": "power steering hose assembly",
    "power steering reservoir": "power steering reservoir with cap",
    "steering wheel": "steering wheel assembly",
    "clock spring": "clock spring airbag spiral cable",
    
    # Body parts
    "hood": "hood panel assembly",
    "fender": "fender assembly",
    "quarter panel": "quarter panel assembly",
    "door": "door shell assembly",
    "door panel": "door panel assembly",
    "door handle": "door handle assembly",
    "door lock": "door lock actuator",
    "door hinge": "door hinge set",
    "trunk lid": "trunk lid assembly",
    "tailgate": "tailgate assembly",
    "bumper": "bumper assembly complete",
    "bumper cover": "bumper cover assembly",
    "bumper reinforcement": "bumper reinforcement bar",
    "grille": "front grille assembly",
    "air dam": "front air dam assembly",
    "spoiler": "rear spoiler assembly",
    "mirror": "side mirror assembly",
    "mirror glass": "mirror glass with backing",
    "windshield": "windshield glass assembly",
    "rear window": "rear window glass assembly",
    "quarter glass": "quarter window glass",
    "window regulator": "window regulator with motor",
    "window motor": "power window motor",
    "weatherstrip": "door weatherstrip seal",
    "molding": "window molding trim",
    "trim": "exterior trim piece",
    "emblem": "emblem logo oem",
    "badge": "vehicle badge emblem",
    "wiper blade": "wiper blade set premium",
    "wiper arm": "wiper arm assembly",
    "hood latch": "hood latch assembly",
    "hood strut": "hood lift support strut",
    "hood hinge": "hood hinge set",
    "trunk strut": "trunk lift support",
    "trunk latch": "trunk latch assembly",
    
    # Interior parts
    "dashboard": "dashboard assembly complete",
    "dash panel": "dash panel assembly",
    "instrument cluster": "instrument cluster assembly",
    "gauge cluster": "gauge cluster assembly",
    "speedometer": "speedometer assembly",
    "tachometer": "tachometer assembly",
    "glove box": "glove box assembly",
    "console": "center console assembly",
    "armrest": "armrest assembly",
    "seat": "seat assembly complete",
    "seat belt": "seat belt assembly",
    "seat cover": "seat cover set custom fit",
    "headliner": "headliner assembly",
    "sun visor": "sun visor assembly",
    "carpet": "floor carpet set custom fit",
    "floor mat": "floor mat set custom fit",
    "floor pan": "floor pan replacement panel",
    "shift knob": "gear shift knob",
    "shift boot": "gear shift boot",
    "pedal": "pedal assembly",
    "pedal pad": "brake pedal pad",
    "steering wheel cover": "steering wheel cover custom fit",
    "radio": "radio head unit assembly",
    "stereo": "stereo system complete",
    "speaker": "speaker set replacement",
    "amplifier": "audio amplifier assembly",
    "cd player": "cd player assembly",
    "antenna": "radio antenna assembly",
    "climate control": "climate control unit assembly",
    "heater core": "heater core assembly",
    "ac compressor": "ac compressor assembly",
    "ac condenser": "ac condenser assembly",
    "ac evaporator": "ac evaporator core assembly",
    "ac hose": "ac hose assembly",
    "ac accumulator": "ac accumulator drier assembly",
    "ac orifice tube": "ac orifice tube assembly",
    "ac expansion valve": "ac expansion valve assembly",
    "blower motor": "hvac blower motor with fan",
    "blower resistor": "blower motor resistor",
    "heater valve": "heater control valve",
    "heater hose": "heater hose set",
    
    # Lighting
    "headlight": "headlight assembly complete",
    "tail light": "tail light assembly complete",
    "fog light": "fog light assembly",
    "turn signal": "turn signal light assembly",
    "marker light": "side marker light assembly",
    "brake light": "brake light assembly",
    "reverse light": "reverse light assembly",
    "license plate light": "license plate light assembly",
    "dome light": "interior dome light assembly",
    "map light": "interior map light assembly",
    "headlight bulb": "headlight bulb high performance",
    "tail light bulb": "tail light bulb set",
    "fog light bulb": "fog light bulb high performance",
    "light switch": "headlight switch assembly",
    "dimmer switch": "headlight dimmer switch",
    
    # Wheels & Tires
    "wheel": "wheel rim replacement",
    "rim": "wheel rim replacement",
    "hub cap": "hub cap set oem style",
    "center cap": "wheel center cap oem",
    "lug nut": "lug nuts set complete",
    "wheel stud": "wheel stud replacement set",
    "wheel lock": "wheel lock set with key",
    "tire": "tire all season",
    "tire valve": "tire valve stem",
    "tire pressure sensor": "tire pressure monitoring sensor",
    "tpms sensor": "tire pressure sensor",
    "wheel weight": "wheel balance weight set",
    
    # Emissions & Air
    "air filter": "engine air filter oem quality",
    "cabin filter": "cabin air filter premium",
    "oxygen sensor": "oxygen sensor oem quality",
    "egr valve": "egr valve assembly",
    "pcv valve": "pcv valve oem replacement",
    "charcoal canister": "evap charcoal canister",
    "emission control": "emission control module",
    "smog pump": "air injection pump",
    # From first CSV analysis
    "subframe": "subframe crossmember assembly complete",
    "crossmember": "crossmember support assembly oem",
    "arm rest": "arm rest assembly oem",
    "armrest": "arm rest assembly complete",
    "console": "center console assembly oem",
    "cup holder": "center console cup holder assembly",
    "mass air flow sensor": "mass air flow sensor with housing",
    "maf sensor": "mass air flow sensor with wiring",
    "proportioning valve": "brake proportioning valve assembly",
    "brake proportioning valve": "brake proportioning valve with bracket",
    "electronic brake caliper": "electronic brake caliper assembly oem",
    "shift boot": "shift boot replacement kit",
    "coil pack": "ignition coil pack set complete",
    "fuse box": "fuse box assembly complete",
    "junction box": "junction box terminal assembly",
    "tailgate": "tailgate assembly complete",
    "headliner": "headliner assembly oem",
    "air valve": "air control valve assembly oem",
    "thermal vacuum switch": "thermal vacuum valve switch assembly",
    "axle": "rear axle assembly complete",
    "rear axle": "rear axle assembly with differential",
    "dashboard": "dashboard assembly complete",
    "dash": "dashboard assembly with harness",
    
        # Interior components
    "headliner material": "headliner fabric replacement",
    "dash bezel": "dashboard instrument panel bezel",
    "center console lid": "center console armrest lid",
    "cup holder insert": "cup holder replacement insert",
    "door panel insert": "door panel trim insert",
    "dome light lens": "interior dome light lens cover",
    "seat track": "seat slider rail track assembly",
    "window switch panel": "door panel window switch assembly",
    "headlight lens": "headlight lens cover replacement",
    "lens cover": "headlight lens cover replacement",
    "light lens": "headlight lens cover replacement",
    "headlamp lens": "headlamp lens cover replacement",
    "clear lens": "clear headlight lens replacement",
    "plastic lens": "plastic headlight lens cover",

    # Engine management
    "tune up kit": "engine tune up kit filters plugs",
    "vacuum line": "vacuum hose line replacement kit",
    "idle control valve": "idle air control valve",
    "manifold pressure sensor": "map sensor with harness",
    "air flow meter": "mass air flow meter sensor",
    "ecu": "engine control unit computer module",
    "tune module": "performance tuner programmer module",

    # Fluid systems
    "coolant reservoir cap": "coolant overflow tank cap",
    "radiator hose upper": "upper radiator hose assembly",
    "radiator hose lower": "lower radiator hose assembly",
    "heater hose": "heater core hose assembly",
    "master cylinder reservoir": "brake master cylinder reservoir",
    "power steering reservoir": "power steering fluid reservoir",
    "overflow tank": "coolant overflow tank with sensor",

    # Suspension components 
    "coil spring isolator": "coil spring insulator pad",
    "suspension bushing": "suspension control arm bushing",
    "radius arm bushing": "radius arm suspension bushing",
    "leaf spring shackle": "leaf spring mounting shackle kit",
    "sway bar link": "stabilizer sway bar end link",
    "sway bar bushing": "stabilizer bar bushing kit",
    "shock mount": "shock absorber mounting bracket",
    "strut mount bearing": "strut mounting bearing plate",
    
    # From second CSV analysis
    "gas tank": "fuel tank assembly complete",
    "gas tank cap": "fuel tank cap oem",
    "speedometer": "speedometer assembly complete",
    "speedometer cable": "speedometer cable assembly",
    "speedometer wire": "speedometer electric wire harness",
    "air condition bracket": "air conditioning bracket assembly",
    "ac bracket": "air conditioning mounting bracket",
    "cargo mat": "cargo floor mat custom fit",
    "cargo liner": "cargo area liner premium",
    "belt tensioner": "belt tensioner assembly with pulley",
    "tensioner pulley": "belt tensioner pulley assembly",
    "wheel opening molding": "wheel opening molding trim set",
    "hubcap": "hubcap wheel cover set",
    "turn light": "turn signal light assembly",
    "turn signal light": "turn signal light assembly complete",
    "pcv valve": "positive crankcase ventilation valve",
    "ignitor": "ignition ignitor module assembly",
    "ignition module": "ignition control module assembly",
    "cruise control valve": "cruise control actuator valve",
    "cruise control module": "cruise control module assembly",
    "flywheel": "flywheel assembly complete",
    "fly wheel": "flywheel assembly balanced",
    "shift cable": "transmission shift cable assembly",
    "shifter cable": "shifter cable assembly complete",
    "body harness": "body wiring harness complete",
    "window master switch": "power window master switch assembly",
    "twin window switch": "dual window control switch assembly",
    "knuckle": "steering knuckle assembly",
    "front knuckle": "front steering knuckle assembly",
    "center cap": "wheel center cap set",
    "spindle": "spindle assembly complete",
    "steering spindle": "steering spindle assembly",
    
    # Additional common parts for completeness
    "door latch": "door latch mechanism assembly",
    "seat": "seat assembly complete",
    "seat belt": "seat belt assembly oem",
    "fuel door": "fuel door assembly complete",
    "wheel hub": "wheel hub assembly with bearing",
    "steering wheel": "steering wheel assembly complete",
    "sun visor": "sun visor assembly replacement",
    "fog light": "fog light assembly complete",
    "fender flare": "fender flare kit complete",
    "differential": "differential assembly complete",
    "transfer case": "transfer case assembly oem",
    "abs module": "abs control module assembly",
    "ecu": "engine control unit complete",
    "pcm": "powertrain control module oem",
    "bcm": "body control module assembly",
    "tcm": "transmission control module oem",
    "intake manifold": "intake manifold assembly complete",
    "exhaust manifold": "exhaust manifold with gaskets",
    "valve cover": "valve cover with gasket set",
    "power window motor": "power window motor with regulator",
    "window regulator": "window regulator assembly with motor",
    "door lock actuator": "door lock actuator with rod assembly",
    "trunk latch": "trunk latch assembly with actuator",
    "hood latch": "hood latch assembly complete",
    "wiper motor": "windshield wiper motor assembly",
    "washer pump": "windshield washer pump assembly",
    "tie rod end": "tie rod end assembly premium",
    "ball joint": "ball joint assembly premium",
    "sway bar link": "sway bar link kit complete",
    "brake drum": "brake drum assembly premium",
    "idler arm": "idler arm assembly replacement",
    "pitman arm": "pitman arm steering assembly",
    "heater core": "heater core assembly complete",
    "ac compressor": "ac compressor assembly with clutch",
    "lock cylinder": "door lock cylinder with keys",
    "ignition switch": "ignition switch with cylinder",
    "fuel pressure regulator": "fuel pressure regulator oem",
    "valve stem seal": "valve stem seal kit complete",
    "throttle body": "throttle body assembly complete",
    "fuel rail": "fuel rail with injectors assembly",
    "serpentine belt": "serpentine belt premium oem quality",
    "timing chain": "timing chain kit complete",
    "timing belt": "timing belt kit with water pump",
    "idler pulley": "idler pulley assembly premium",
    "torque converter": "torque converter assembly oem",
    "muffler": "muffler assembly with clamps",
    "catalytic converter": "catalytic converter direct fit",
    "wheel stud": "wheel stud replacement set",
    "lug nut": "lug nuts complete set oem",
    "crankshaft sensor": "crankshaft position sensor oem",
    "camshaft sensor": "camshaft position sensor with harness",
    # Headlight component parts
    "headlight lens": "headlight lens cover replacement",
    "headlight housing": "headlight housing shell replacement",
    "headlight bracket": "headlight mounting bracket",
    "headlight bulb": "headlight replacement bulb",
    "headlight cover": "headlight lens cover",
    "headlight glass": "headlight glass lens",
    "lens cover": "headlight lens cover replacement",
    "light lens": "headlight lens cover replacement",
    "headlamp lens": "headlamp lens cover replacement",
    "headlamp cover": "headlamp lens cover replacement",

    # Additional part terms for Nissan Frontier specifically
    "frontier headlight": "frontier headlight assembly complete",
    "frontier tail light": "frontier tail light assembly complete",
    "frontier grille": "frontier grille assembly complete",
    "frontier bumper": "frontier front bumper assembly",

    # More detailed brake components
    "brake hardware": "brake hardware kit complete",
    "brake hose": "brake hose assembly",
    "brake line": "brake line kit complete",
    "brake bleeder": "brake bleeder screw kit",
    "brake piston": "brake caliper piston",
    "brake fluid reservoir": "brake fluid reservoir complete",

    # More electrical components
    "fuse": "fuse kit assortment",
    "relay": "electrical relay replacement",
    "wiring connector": "wiring harness connector",
    "pigtail connector": "wiring harness pigtail connector",
    "electrical connector": "electrical wiring connector",

    # Gaskets and seals
    "valve cover gasket": "valve cover gasket set",
    "oil pan gasket": "oil pan gasket set",
    "rear main seal": "rear main seal replacement",
    "head gasket": "cylinder head gasket set",
    "intake manifold gasket": "intake manifold gasket set",
    "exhaust gasket": "exhaust manifold gasket set",

    # Sensors
    "oxygen sensor": "oxygen o2 sensor",
    "crankshaft sensor": "crankshaft position sensor",
    "camshaft sensor": "camshaft position sensor",
    "throttle position sensor": "throttle position sensor",
    "map sensor": "manifold absolute pressure sensor",
    "maf sensor": "mass air flow sensor",
    "knock sensor": "engine knock sensor",
    "coolant temp sensor": "coolant temperature sensor",
    "oil pressure sensor": "oil pressure switch sensor",
    "abs sensor": "abs wheel speed sensor",

    # Window and mirror components
    "power window motor": "power window lift motor",
    "window regulator": "window regulator assembly",
    "mirror glass": "side mirror glass replacement",
    "mirror motor": "side mirror motor actuator",
    "mirror cover": "side mirror cover cap",
    "window switch": "power window switch",
    
    # Year range pattern matching terms
    "87-91": "1987-1991",
    "88-91": "1988-1991",
    "91/92": "1991-1992",
    "92/93": "1992-1993",
    "93-97": "1993-1997",
    "98-02": "1998-2002",
    "03-07": "2003-2007",
    "08-12": "2008-2012",
    "13-17": "2013-2017",
    "18-22": "2018-2022"
    }
    
    def normalize_query(self, query):
        """Normalize the query text (lowercase, remove excess whitespace, etc.)"""
        if not query:
            return ""
        
        # Convert to lowercase
        query = query.lower()
        
        # Replace special characters with spaces
        query = re.sub(r"[–—]", "-", query)
        
        # Remove common filler words that don't add meaning
        query = re.sub(r"\b(for|a|the|my|an|this|that|to|on|in|with)\b", " ", query)
        
        # Clean up whitespace
        query = re.sub(r"\s+", " ", query).strip()
        
        return query
    
    def _extract_year(self, query):
        """Extract vehicle year from query with enhanced year range detection"""
        # First, try to match year ranges in various formats
        
        # Format: 87-91, 2015-2020, etc.
        year_range_match = re.search(r'\b((?:19|20)?\d{2})[-/](?:19|20)?\d{2}\b', query)
        if year_range_match:
            year_range = year_range_match.group(0)
            
            # Extract the first year from the range
            first_year_match = re.search(r'\b((?:19|20)?\d{2})', year_range)
            if first_year_match:
                year = first_year_match.group(0)
                
                # Handle 2-digit years
                if len(year) == 2:
                    if int(year) > 50:  # Assume 19xx for years > 50
                        return "19" + year
                    else:  # Assume 20xx for years <= 50
                        return "20" + year
                else:
                    return year
        
        # Match specific year range patterns from our dictionary
        for pattern in self.part_terms.keys():
            if re.search(pattern, query) and pattern in ["87-91", "91/92", "93-97"]:
                # Extract the first year from the normalized range
                normalized_range = self.part_terms[pattern]
                first_year = normalized_range.split("-")[0]
                return first_year
        
        # Match 4-digit years from 1900-2099
        year_match = re.search(r'\b(19|20)\d{2}\b', query)
        if year_match:
            return year_match.group(0)
        
        # Match 2-digit years and convert to 4 digits
        short_year_match = re.search(r'\b\d{2}\b', query)
        if short_year_match:
            year = short_year_match.group(0)
            if int(year) > 50:  # Assume 19xx for years > 50
                return "19" + year
            else:  # Assume 20xx for years <= 50
                return "20" + year
        
        return None

    def _extract_make(self, query):
        """Extract vehicle make from query with improved brand recognition"""
        words = query.split()
        query_lower = query.lower()
        
        # Check for exact make matches
        for make in self.vehicle_makes:
            make_lower = make.lower()
            # Use word boundary check for more accurate matching
            if re.search(r'\b' + re.escape(make_lower) + r'\b', query_lower):
                return make
        
        # Check for synonyms with word boundary
        for synonym, make in self.make_synonyms.items():
            if re.search(r'\b' + re.escape(synonym.lower()) + r'\b', query_lower):
                return make
        
        # Try partial matching for certain premium brands that might be abbreviated
        # This helps with queries like "benz front bumper" instead of "mercedes-benz"
        special_cases = {
            "benz": "mercedes-benz",
            "merc": "mercedes-benz",
            "chevy": "chevrolet", 
            "vw": "volkswagen",
            "bmw": "bmw",  # Already normalized but included for completeness
            "audi": "audi"  # Already normalized but included for completeness
        }
        
        for partial, make in special_cases.items():
            if re.search(r'\b' + re.escape(partial) + r'\b', query_lower):
                return make
        
        return None

    def _extract_model(self, query):
        """Extract vehicle model from query with improved model variation handling"""
        # Get the make first to narrow down model search
        make = self._extract_make(query)
        query_lower = query.lower()
        
        if not make:
            # Try to extract model without make if possible, but with lower confidence
            for make_name, models in self.make_models.items():
                for model in models:
                    model_lower = model.lower()
                    # Use word boundary to ensure we match complete terms
                    if re.search(r'\b' + re.escape(model_lower) + r'\b', query_lower):
                        return model
            return None
                
        # Check if we have models for this make
        models = self.make_models.get(make.lower(), [])
        if not models:
            return None
            
        # Try to find models with exact word boundaries first - improved matching
        for model in models:
            model_lower = model.lower()
            if re.search(r'\b' + re.escape(model_lower) + r'\b', query_lower):
                return model
        
        # Handle special cases for models with variations
        if make.lower() == "ford":
            # F-series trucks (F-150, F150, F 150)
            f_series_match = re.search(r'\bf[-\s]?([0-9]{2,3})\b', query_lower, re.IGNORECASE)
            if f_series_match:
                model_num = f_series_match.group(1)
                return f"f-{model_num}"
        
        # Handle BMW 3-Series, 5-Series variations (335i, 530i, etc.)
        if make.lower() == "bmw":
            series_match = re.search(r'\b([1-8])[- ]?series\b', query_lower)
            if series_match:
                series_num = series_match.group(1)
                return f"{series_num}-Series"
            
            # Match patterns like 328i, 530i, X5
            bmw_model_match = re.search(r'\b([1-8][0-9]{2}i?|[mxz][1-8])\b', query_lower)
            if bmw_model_match:
                model_code = bmw_model_match.group(1)
                # Map to series if possible
                first_digit = model_code[0]
                if first_digit.isdigit():
                    return f"{first_digit}-Series"
                elif first_digit.lower() == 'x':
                    return f"X{model_code[1]}"
                return model_code
        
        # Handle Mercedes model variations (C-Class, C300, etc.)
        if make.lower() == "mercedes-benz":
            class_match = re.search(r'\b([a-glms])[- ]?class\b', query_lower)
            if class_match:
                class_letter = class_match.group(1).upper()
                return f"{class_letter}-Class"
            
            # Match models like C300, E350, etc.
            merc_model_match = re.search(r'\b([a-glms][0-9]{2,3})\b', query_lower)
            if merc_model_match:
                model_code = merc_model_match.group(1)
                class_letter = model_code[0].upper()
                return f"{class_letter}-Class"
        
        # Then try less strict matching
        for model in models:
            model_lower = model.lower()
            if model_lower in query_lower:
                return model
                    
        return None

    def _extract_engine_specs(self, query):
        """Extract engine displacement and other specifications with improved pattern matching"""
        specs = {}
        query_lower = query.lower()
        
        # Extract engine displacement (e.g., 5.3L, 2.0L, 350ci, etc.)
        # Improved pattern matching for various formats
        displacement_match = re.search(r'\b(\d+\.\d+)L\b', query, re.IGNORECASE)
        if displacement_match:
            specs["displacement"] = displacement_match.group(1) + "L"
        else:
            # Try to match formats like 5.3, 2.0 without the L
            displacement_match = re.search(r'\b(\d+\.\d+)\b', query)
            if displacement_match:
                specs["displacement"] = displacement_match.group(1) + "L"
            else:
                # Handle cubic inch displacements (350ci, 350 ci, etc.)
                ci_match = re.search(r'\b(\d{3})(?:\s?ci|\s?cubic inch)\b', query_lower)
                if ci_match:
                    # Convert to liters roughly
                    ci_value = int(ci_match.group(1))
                    liter_value = round(ci_value * 0.016387, 1)  # Convert CI to L
                    specs["displacement"] = f"{liter_value}L"
                    specs["original_ci"] = f"{ci_value}ci"
                    
        # Look for engine types (V6, V8, I4, inline 4, etc.)
        engine_type_patterns = [
            (r'\bv[468]\b', lambda m: m.group(0).upper()),  # V6, V8
            (r'\bi[3456]\b', lambda m: m.group(0).upper()),  # I4, I6
            (r'\binline[ -]?([3456])\b', lambda m: f"I{m.group(1)}"),  # Inline 4 -> I4
            (r'\bstraight[ -]?([3456])\b', lambda m: f"I{m.group(1)}")  # Straight 6 -> I6
        ]
        
        for pattern, formatter in engine_type_patterns:
            type_match = re.search(pattern, query_lower)
            if type_match:
                specs["type"] = formatter(type_match)
                break
                
        # Look for turbo/supercharged
        if re.search(r'\bturbo\b', query_lower):
            specs["forced_induction"] = "turbo"
        elif re.search(r'\bsupercharged|\bsc\b', query_lower):
            specs["forced_induction"] = "supercharged"
        elif re.search(r'\btwin[ -]?turbo\b', query_lower):
            specs["forced_induction"] = "twin-turbo"
                
        # Look for diesel/gas
        if re.search(r'\bdiesel\b', query_lower):
            specs["fuel_type"] = "diesel"
        elif re.search(r'\bgas|gasoline\b', query_lower):
            specs["fuel_type"] = "gas"
        elif re.search(r'\bhybrid\b', query_lower):
            specs["fuel_type"] = "hybrid"
        elif re.search(r'\belectric|ev\b', query_lower):
            specs["fuel_type"] = "electric"
                
        return specs if specs else None

    def _extract_part(self, query):
        """Extract part information from query with improved compound part recognition"""
        query_lower = query.lower()
        
        # Check for front-end part patterns first (most specific to most general)
        front_end_parts = [
            "complete front end assembly",
            "front end assembly",
            "front end",
            "front bumper assembly",
            "front bumper complete assembly",
            "rear bumper complete assembly",
            "rear bumper assembly",
            "front bumper cover",
            "bumper assembly",
            "bumper cover",
            "front fascia"
        ]
        
        for part in front_end_parts:
            if part in query_lower:
                return part
        
        # Check for component parts specifically before checking for assemblies
        component_parts = [
            "headlight lens",
            "lens cover",
            "light lens",
            "headlamp lens",
            "clear lens",
            "plastic lens",
            "tail light lens",
            "fog light lens",
            "turn signal lens"
        ]
        
        for part in component_parts:
            part_pattern = r'\b' + re.escape(part) + r'\b'
            if re.search(part_pattern, query_lower):
                return part
        
        # Check for compound parts 
        compound_parts = [
            "headlight assembly",
            "tail light assembly",
            "strut assembly",
            "wheel hub assembly",
            "radiator assembly",
            "engine wire harness",
            "engine wiring harness",
            "power steering pump",
            "brake master cylinder",
            "ac compressor",
            "transmission mount",
            "engine mount",
            "control arm",
            "sway bar link",
            "window regulator",
            "door lock actuator",
            "ignition coil pack",
            "timing belt kit",
            "timing chain kit",
            "water pump assembly",
            "valve cover gasket",
            "catalytic converter",
            "oxygen sensor",
            "fuel pump assembly", 
            "starter motor",
            "alternator assembly",
            "intake manifold",
            "exhaust manifold",
            "throttle body",
            "mass air flow sensor",
            "crankshaft position sensor"
        ]
        
        for part in compound_parts:
            part_pattern = r'\b' + re.escape(part) + r'\b'
            if re.search(part_pattern, query_lower):
                return part
        
        # More precise pattern matching with word boundaries for exact part matches
        for part, replacement in self.part_terms.items():
            # Skip year patterns
            if part in ["87-91", "91/92", "93-97"]:
                continue
                    
            pattern = r'\b' + re.escape(part) + r'\b'
            if re.search(pattern, query_lower):
                return part
        
        # Check for category matches (less specific)
        for category, part_list in self.part_categories.items():
            for part in part_list:
                part_pattern = r'\b' + re.escape(part) + r'\b'
                if re.search(part_pattern, query_lower):
                    return part
        
        # If no specific part found, try to extract the remainder after vehicle info
        year = self._extract_year(query)
        make = self._extract_make(query)
        model = self._extract_model(query)
        
        if any([year, make, model]):
            # Get what's left after removing vehicle info
            remaining = query_lower
            
            if year:
                remaining = re.sub(r'\b' + re.escape(year) + r'\b', '', remaining)
            if make:
                remaining = re.sub(r'\b' + re.escape(make.lower()) + r'\b', '', remaining, flags=re.IGNORECASE)
            if model:
                # Handle hyphenated models like F-150
                model_pattern = model.lower().replace('-', '[-]?')
                remaining = re.sub(r'\b' + model_pattern + r'\b', '', remaining, flags=re.IGNORECASE)
                
            # Remove common filler words
            remaining = re.sub(r'\b(for|a|the|my|i|need|want|looking|with|and|in|on|of|to|from)\b', ' ', remaining, flags=re.IGNORECASE)
                
            # Clean up and return what's left as the likely part
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            if remaining:
                return remaining    
            
            return None

    def _extract_position(self, query):
        """Extract position information like 'front', 'rear', 'driver side', etc."""
        positions = []
        query_lower = query.lower()
        
        position_terms = {
            "front": ["front", "forward"],
            "rear": ["rear", "back"],
            "left": ["left", "driver", "driver's", "driver side", "driver-side"],
            "right": ["right", "passenger", "passenger's", "passenger side", "passenger-side"],
            "upper": ["upper", "top"],
            "lower": ["lower", "bottom"],
            "inner": ["inner", "inside"],
            "outer": ["outer", "outside"]
        }
        
        for position, terms in position_terms.items():
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, query_lower):
                    positions.append(position)
                    break
        
        return positions if positions else None

    def _get_year_range(self, year, make, model):
        """
        Get the year range for specific model generations.
        Enhanced to handle more vehicles and provide compatibility information.
        """
        if not all([year, make, model]):
            return None
            
        # Convert inputs to standard format
        make_lower = make.lower()
        model_lower = model.lower().replace(" ", "-")  # Standardize spaces in model names
        year_int = int(year)
        
        # Handle common model variations
        if make_lower == "ford":
            # Standardize F-series format
            if re.match(r'f[0-9]{2,3}', model_lower):
                model_number = re.search(r'([0-9]{2,3})', model_lower).group(0)
                model_lower = f"f-{model_number}"
            elif model_lower == "f-series":
                model_lower = "f-150"  # Default to most common model
        
        elif make_lower in ["chevy", "chevrolet"]:
            # Map common name variations
            if model_lower in ["silverado-1500", "1500"]:
                model_lower = "silverado"
        
        elif make_lower == "dodge":
            if model_lower in ["ram", "ram-1500"]:
                make_lower = "ram"
                model_lower = "1500"
        
        # Check for known patterns for this make/model
        if make_lower in self.year_range_patterns and model_lower in self.year_range_patterns[make_lower]:
            ranges = self.year_range_patterns[make_lower][model_lower]
            
            # Find the correct year range
            for year_range, gen_info in ranges.items():
                start_year, end_year = map(int, year_range.split('-'))
                if start_year <= year_int <= end_year:
                    return {
                        "range": year_range,
                        "generation": gen_info,
                        "compatible_years": f"{start_year}-{end_year}"
                    }
        
        # Enhanced auto-generation of year ranges for common vehicles
        # This helps provide better compatibility ranges even for models we don't have specific data for
        common_generation_spans = {
            "ford": {
                "f-150": 6,       # 6-year generations typically
                "mustang": 8,      # ~8 year generations
                "explorer": 5      # ~5 year generations
            },
            "toyota": {
                "camry": 5,        # ~5 year generations
                "corolla": 6,
                "rav4": 5,
                "tacoma": 8
            },
            "honda": {
                "accord": 5,
                "civic": 5,
                "cr-v": 5
            },
            "chevrolet": {
                "silverado": 7,
                "malibu": 5,
                "tahoe": 7
            }
        }
        
        # Look up the appropriate generation span
        gen_span = 7  # Default to 7 years if unknown
        if make_lower in common_generation_spans and model_lower in common_generation_spans[make_lower]:
            gen_span = common_generation_spans[make_lower][model_lower]
        
        # Calculate estimated generation
        gen_start = (year_int // gen_span) * gen_span
        gen_end = gen_start + (gen_span - 1)
        
        return {
            "range": f"{gen_start}-{gen_end}",
            "generation": "estimated",
            "compatible_years": f"{gen_start}-{gen_end}",
            "note": f"Estimated generation based on typical {gen_span}-year vehicle cycles"
        }

    def _calculate_confidence(self, result):
        """Calculate a confidence score for the extracted information with improved weighting"""
        confidence = 0
        
        # Base points for each field we successfully extracted
        if result["year"]:
            confidence += 25
        if result["make"]:
            confidence += 25
        if result["model"]:
            confidence += 15
        if result["part"]:
            confidence += 25
        if result["position"]:
            confidence += 5
        if result["engine_specs"]:
            confidence += 5
            
        # Additional points for completeness
        if result["year"] and result["make"] and result["model"]:
            confidence += 5  # Bonus for having complete vehicle info
            
        # Additional points for year range detection
        if "year_range" in result and result["year_range"]:
            if result["year_range"].get("generation") != "estimated":
                confidence += 5  # Bonus for known generation
            else:
                confidence += 2  # Smaller bonus for estimated generation
                
        # Check if part is in our predefined lists (more confidence)
        if result["part"]:
            part = result["part"].lower()
            predefined_part = False
            
            # Check if it's a compound part we recognize
            for compound_part in ["front bumper assembly", "headlight assembly", 
                                "wheel hub assembly", "timing belt kit"]:
                if compound_part in part:
                    predefined_part = True
                    break
                    
            # Check if it's in our part terms dictionary
            if not predefined_part:
                for part_term in self.part_terms:
                    if part_term.lower() == part:
                        predefined_part = True
                        break
                        
            # Add bonus for recognized parts
            if predefined_part:
                confidence += 5
        
        return min(confidence, 100)
    
    def generate_search_terms(self, vehicle_info):
        """
        Generate optimized search terms based on extracted vehicle information
        Returns a list of search terms in decreasing order of specificity
        - Enhanced for better Google Shopping and eBay queries
        """
        search_terms = []
        
        year = vehicle_info.get("year")
        make = vehicle_info.get("make")
        model = vehicle_info.get("model")
        part = vehicle_info.get("part")
        position = vehicle_info.get("position")
        engine_specs = vehicle_info.get("engine_specs")
        original_query = vehicle_info.get("original_query", "")
        year_range = vehicle_info.get("year_range")
        
        # Format model properly if we have a preferred format
        formatted_model = None
        if model and model.lower() in self.model_formatting:
            formatted_model = self.model_formatting[model.lower()]
        else:
            formatted_model = model
                
        # Format make properly (capitalize)
        formatted_make = make.capitalize() if make else None
        
        # Get engine displacement if available
        engine_disp = None
        if engine_specs and "displacement" in engine_specs:
            engine_disp = engine_specs["displacement"]
        
        # Generate year range string if available
        year_range_str = None
        if year_range and "compatible_years" in year_range:
            year_range_str = year_range["compatible_years"]
        
        # Generate different types of search terms
        
        # --- GOOGLE SHOPPING OPTIMIZED TERMS ---
        
        # 1. Generate precise Google Shopping search term
        if year and make and part:
            # Format positions if any exist
            position_str = ''
            if position and len(position) > 0:
                position_str = ' ' + ' '.join(position)
            
            # Format terms for Google Shopping's preference for complete phrases
            gs_term = f"{year} {formatted_make}"
            
            if formatted_model:
                # Special handling for certain model types
                if formatted_make == "Ford" and "F-" in formatted_model:
                    gs_term += f" {formatted_model.upper()}"
                elif formatted_make in ["BMW", "Mercedes-Benz"]:
                    gs_term += f" {formatted_model}"  # Leave as-is for luxury brands
                else:
                    gs_term += f" {formatted_model.capitalize()}"
                    
            # Add position string
            gs_term += position_str
            
            # Add exact part name
            gs_term += f" {part}"
            
            # Add OEM only for certain parts and brands
            if any(oem_term in part.lower() for oem_term in ["bumper", "headlight", "taillight", "fender", "hood", "door"]):
                gs_term += " OEM"
            
            # Add compatibility for Google Shopping
            if year_range_str and year_range_str != f"{year}-{year}":
                gs_term += f" (Fits {year_range_str})"
                
            search_terms.append(gs_term)
        
        # --- EBAY OPTIMIZED TERMS ---
        
        # 2. eBay optimized term with specific formats
        if year and make and part:
            # eBay prefers keywords with + symbols and specific formats
            ebay_term = f"{year} {formatted_make}"
            
            if formatted_model:
                # Special handling for certain model types for eBay
                if formatted_make == "Ford" and "F-" in formatted_model:
                    ebay_term += f" {formatted_model.upper()}"
                else:
                    ebay_term += f" {formatted_model}"
                    
            # Add position
            if position and len(position) > 0:
                ebay_term += f" {' '.join(position)}"
                
            # Add part with enhanced terminology for eBay
            if part in self.part_terms:
                enhanced_part = self.part_terms[part]
                ebay_term += f" {enhanced_part}"
            else:
                ebay_term += f" {part}"
                
            # Add specific eBay keywords
            if "bumper" in part.lower():
                ebay_term += " complete assembly"
            elif "headlight" in part.lower():
                ebay_term += " assembly complete"
            elif "engine" in part.lower():
                ebay_term += " motor"
                
            # Only add if different from previous terms
            if ebay_term not in search_terms:
                search_terms.append(ebay_term)
        
        # 3. Original query as a search term (for both platforms)
        if original_query and original_query not in search_terms:
            # Check if query already contains 'oem', if not add it
            if 'oem' not in original_query.lower():
                search_terms.append(f"{original_query} oem")
            else:
                search_terms.append(original_query)
        
        # 4. Year range search terms (for eBay's preference for compatible parts)
        if year and make and part and year_range_str:
            # 4.1. Search term with model and year range
            if formatted_model:
                year_range_term = f"{year_range_str} {formatted_make} {formatted_model}"
                if position:
                    year_range_term += f" {' '.join(position)}"
                year_range_term += f" {part} compatible"
                
                if year_range_term not in search_terms:
                    search_terms.append(year_range_term)
        
        # 5. For certain parts like bumpers and front end assemblies, add specific search terms
        if part and any(x in part.lower() for x in ["bumper", "front end"]):
            if make and year:
                front_terms = [
                    "bumper assembly", 
                    "front end assembly", 
                    "complete front end", 
                    "bumper cover complete",
                    "front bumper complete assembly"
                ]
                
                for front_term in front_terms:
                    # Don't repeat if already in search terms
                    front_specific = f"{year} {formatted_make}"
                    if formatted_model:
                        front_specific += f" {formatted_model}"
                    front_specific += f" {front_term} oem"
                    
                    if front_specific not in search_terms:
                        search_terms.append(front_specific)
        
        # 6. Fallback search terms with less information (for Google Shopping)
        if make and part and len(search_terms) < 3:
            term6 = f"{formatted_make}"
            if formatted_model:
                term6 += f" {formatted_model}"
            if year:
                term6 += f" {year}"
            if engine_disp:
                term6 += f" {engine_disp}"
            if position:
                term6 += f" {' '.join(position)}"
            term6 += f" {part} replacement"
            
            if term6 not in search_terms:
                search_terms.append(term6)
        
        # 7. If we still don't have enough info, just use the normalized query
        if not search_terms and vehicle_info.get("normalized_query"):
            search_terms.append(vehicle_info.get("normalized_query") + " oem")
        
        # Ensure we have unique search terms
        return list(dict.fromkeys(search_terms))
    
        
    def process_query(self, query, structured_data=None):
        """
        Main processing function that takes a raw query and returns structured results
        with extracted information and optimized search terms.
        
        Now supports structured data input from multi-field form.
        """
        # Use structured data if provided, otherwise extract from query
        if structured_data:
            vehicle_info = self.process_structured_data(structured_data)
        else:
            vehicle_info = self.extract_vehicle_info(query)
            
        search_terms = self.generate_search_terms(vehicle_info)
        
        result = {
            "vehicle_info": vehicle_info,
            "search_terms": search_terms,
            "confidence": vehicle_info.get("search_confidence", 0)
        }
        
        return result
        
    def process_structured_data(self, structured_data):
        """
        Process structured data from multi-field input
        Returns a dict with extracted vehicle information
        """
        # Process structured data directly if provided
        result = {
            "year": structured_data.get("year", "").strip(),
            "make": structured_data.get("make", "").strip(),
            "model": structured_data.get("model", "").strip(),
            "part": structured_data.get("part", "").strip(),
            "original_query": "",  # Will be constructed below
            "normalized_query": ""  # Will be constructed below
        }
        
        # Extract engine specs if available
        engine = structured_data.get("engine", "").strip()
        if engine:
            result["engine_specs"] = self._parse_engine_string(engine)
        else:
            result["engine_specs"] = None
        
        # Extract position information from part field (if applicable)
        part = result["part"]
        if part:
            # Check for position indicators in part name
            position_terms = ["front", "rear", "driver", "passenger", "left", "right", "upper", "lower"]
            positions = []
            for term in position_terms:
                if term in part.lower():
                    positions.append(term)
            
            result["position"] = positions if positions else None
        else:
            result["position"] = None
        
        # Construct a normalized query string from structured data
        query_parts = []
        if result["year"]: query_parts.append(result["year"])
        if result["make"]: query_parts.append(result["make"])
        if result["model"]: query_parts.append(result["model"])
        if result["part"]: query_parts.append(result["part"])
        if engine: query_parts.append(engine)
        
        constructed_query = " ".join(query_parts)
        result["original_query"] = constructed_query
        result["normalized_query"] = self.normalize_query(constructed_query)
        
        # Calculate confidence based on fields present
        result["search_confidence"] = self._calculate_structured_confidence(result)
        
        # Add year range information for specific models (useful for parts compatibility)
        if result["year"] and result["make"] and result["model"]:
            result["year_range"] = self._get_year_range(result["year"], result["make"], result["model"])
        
        return result

    def _parse_engine_string(self, engine_str):
        """Parse engine string to extract specifications"""
        specs = {}
        engine_str_lower = engine_str.lower()
        
        # Check for displacement
        # Match patterns like 5.3L, 2.0L, 5.3, 2.0, 350ci
        patterns = [
            (r'(\d+\.\d+)L', lambda m: m.group(1) + "L"),  # 5.3L
            (r'(\d+\.\d+)', lambda m: m.group(1) + "L"),   # 5.3 -> 5.3L
            (r'(\d+)\s*ci', lambda m: str(round(int(m.group(1)) * 0.016387, 1)) + "L")  # 350ci -> 5.7L
        ]
        
        for pattern, formatter in patterns:
            displacement_match = re.search(pattern, engine_str, re.IGNORECASE)
            if displacement_match:
                specs["displacement"] = formatter(displacement_match)
                break
        
        # Check for engine type (V6, V8, I4, etc.)
        engine_type_patterns = [
            (r'(V[468])', lambda m: m.group(1)),
            (r'(I[346])', lambda m: m.group(1)),
            (r'(Straight[346])', lambda m: "I" + m.group(1)[-1]),
            (r'(Inline[346])', lambda m: "I" + m.group(1)[-1])
        ]
        
        for pattern, formatter in engine_type_patterns:
            engine_type_match = re.search(pattern, engine_str, re.IGNORECASE)
            if engine_type_match:
                specs["type"] = formatter(engine_type_match)
                break
        
        # Check for turbo/supercharged
        if re.search(r'turbo', engine_str_lower):
            specs["forced_induction"] = "turbo"
        elif re.search(r'supercharged|sc', engine_str_lower):
            specs["forced_induction"] = "supercharged"
        elif re.search(r'twin[\s-]?turbo', engine_str_lower):
            specs["forced_induction"] = "twin-turbo"
        
        # Check for fuel type
        if re.search(r'diesel', engine_str_lower):
            specs["fuel_type"] = "diesel"
        elif re.search(r'gas|gasoline', engine_str_lower):
            specs["fuel_type"] = "gas"
        elif re.search(r'hybrid', engine_str_lower):
            specs["fuel_type"] = "hybrid"
        
        return specs if specs else None

    def _calculate_structured_confidence(self, result):
        """Calculate confidence score for structured data"""
        confidence = 0
        
        # Add points for each field with data
        if result["year"] and len(result["year"]) == 4:
            confidence += 25
        if result["make"]:
            confidence += 25
        if result["model"]:
            confidence += 20
        if result["part"]:
            confidence += 25
        if result["engine_specs"]:
            confidence += 5
        
        # Bonus points for complete vehicle info
        if result["year"] and result["make"] and result["model"]:
            confidence += 10
            
        # Bonus points if year range is found
        if "year_range" in result and result["year_range"]:
            confidence += 5
        
        return min(confidence, 100)

    def extract_vehicle_info(self, query):
        """
        Extract structured vehicle information from query
        Returns a dict with year, make, model, and part
        """
        normalized = self.normalize_query(query)
        
        result = {
            "year": self._extract_year(normalized),
            "make": self._extract_make(normalized),
            "model": self._extract_model(normalized),
            "part": self._extract_part(normalized),
            "position": self._extract_position(normalized),
            "engine_specs": self._extract_engine_specs(normalized),
            "original_query": query,
            "normalized_query": normalized
        }
        
        # Additional fields that might be useful
        result["search_confidence"] = self._calculate_confidence(result)
        
        # Add year range information for specific models (useful for parts compatibility)
        if result["year"] and result["make"] and result["model"]:
            result["year_range"] = self._get_year_range(result["year"], result["make"], result["model"])
        
        return result