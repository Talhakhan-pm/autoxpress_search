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
        "dome light", "license plate light"
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
    "camshaft sensor": "camshaft position sensor with harness"
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
        
        # Check for displacement
        displacement_match = re.search(r'(\d+\.\d+)L', engine_str, re.IGNORECASE)
        if displacement_match:
            specs["displacement"] = displacement_match.group(0)
        else:
            # Try to match formats like 5.3, 2.0 without the L
            displacement_match = re.search(r'(\d+\.\d+)', engine_str)
            if displacement_match:
                specs["displacement"] = displacement_match.group(0) + "L"
        
        # Check for engine type (V6, V8, I4, etc.)
        engine_type_match = re.search(r'(V[468]|I[346]|Straight[346]|Inline[346])', engine_str, re.IGNORECASE)
        if engine_type_match:
            specs["type"] = engine_type_match.group(0)
        
        # Check for turbo/supercharged
        if re.search(r'turbo', engine_str, re.IGNORECASE):
            specs["forced_induction"] = "turbo"
        elif re.search(r'supercharged', engine_str, re.IGNORECASE):
            specs["forced_induction"] = "supercharged"
        
        # Check for fuel type
        if re.search(r'diesel', engine_str, re.IGNORECASE):
            specs["fuel_type"] = "diesel"
        elif re.search(r'gas|gasoline', engine_str, re.IGNORECASE):
            specs["fuel_type"] = "gas"
        
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
        
        return min(confidence, 100)
    
    def _extract_year(self, query):
        """Extract vehicle year from query"""
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
        """Extract vehicle make from query"""
        words = query.split()
        
        # Check for exact make matches
        for make in self.vehicle_makes:
            if make in query.split() or f" {make} " in f" {query} ":
                return make
        
        # Check for synonyms
        for synonym, make in self.make_synonyms.items():
            if synonym in query.split() or f" {synonym} " in f" {query} ":
                return make
        
        return None
    
    def _extract_model(self, query):
        """Extract vehicle model from query"""
        # Get the make first to narrow down model search
        make = self._extract_make(query)
        if not make:
            # Try to extract model without make if possible, but with lower confidence
            for make_name, models in self.make_models.items():
                for model in models:
                    if re.search(r'\b' + re.escape(model) + r'\b', query):
                        return model
            return None
            
        # Check if we have models for this make
        models = self.make_models.get(make, [])
        if not models:
            return None
        
        query_lower = query.lower()
            
        # Try to find models with exact word boundaries first - improved matching
        for model in models:
            if re.search(r'\b' + re.escape(model) + r'\b', query):
                return model
        
        # Then try less strict matching
        for model in models:
            if model in query:
                return model
                
        # Special case handling for F-series trucks due to varying formats (F-150, F150, etc.)
        if make == "ford" and re.search(r'\bf[-\s]?[0-9]{2,3}\b', query, re.IGNORECASE):
            match = re.search(r'\bf[-\s]?([0-9]{2,3})\b', query, re.IGNORECASE)
            if match:
                model_num = match.group(1)
                return f"f-{model_num}"
                
        return None
    
    def _extract_engine_specs(self, query):
        """Extract engine displacement and other specifications"""
        specs = {}
        
        # Extract engine displacement (e.g., 5.3L, 2.0L, 350ci, etc.)
        displacement_match = re.search(r'\b(\d+\.\d+)L\b', query, re.IGNORECASE)
        if displacement_match:
            specs["displacement"] = displacement_match.group(1) + "L"
        else:
            # Try to match formats like 5.3, 2.0 without the L
            displacement_match = re.search(r'\b(\d+\.\d+)\b', query)
            if displacement_match:
                specs["displacement"] = displacement_match.group(1) + "L"
                
        # Look for engine types (V6, V8, I4, etc.)
        engine_type_match = re.search(r'\b(V[468]|I[346]|Straight[346]|Inline[346])\b', query, re.IGNORECASE)
        if engine_type_match:
            specs["type"] = engine_type_match.group(0)
            
        # Look for turbo/supercharged
        if re.search(r'\bturbo\b', query, re.IGNORECASE):
            specs["forced_induction"] = "turbo"
        elif re.search(r'\bsupercharged\b', query, re.IGNORECASE):
            specs["forced_induction"] = "supercharged"
            
        # Look for diesel/gas
        if re.search(r'\bdiesel\b', query, re.IGNORECASE):
            specs["fuel_type"] = "diesel"
        elif re.search(r'\bgas|gasoline\b', query, re.IGNORECASE):
            specs["fuel_type"] = "gas"
            
        return specs if specs else None
    
    def _extract_part(self, query):
        """Extract part information from query"""
        # Check for compound parts first (like "front bumper assembly")
        # This is important to handle multi-word parts correctly
        compound_parts = [
            "front bumper assembly",
            "rear bumper assembly",
            "bumper assembly",
            "headlight assembly",
            "tail light assembly",
            "strut assembly",
            "wheel hub assembly",
            "radiator assembly",
            "engine wire harness",
            "engine wiring harness",
            "front end assembly"
        ]
        
        for part in compound_parts:
            if part in query:
                return part
        
        # Then check for exact matches in part terms dictionary
        for part, replacement in self.part_terms.items():
            pattern = r'\b' + re.escape(part) + r'\b'
            if re.search(pattern, query):
                return part
        
        # Then check for generic part categories
        for category, part_list in self.part_categories.items():
            for part in part_list:
                if part in query:
                    return part
        
        # If no specific part found, try to extract the remainder after vehicle info
        year = self._extract_year(query)
        make = self._extract_make(query)
        model = self._extract_model(query)
        engine_specs = self._extract_engine_specs(query)
        
        if any([year, make, model]):
            # Get what's left after removing vehicle info
            remaining = query
            
            if year:
                remaining = remaining.replace(year, '')
            if make:
                remaining = remaining.replace(make, '')
            if model:
                remaining = remaining.replace(model, '')
            if engine_specs and "displacement" in engine_specs:
                remaining = re.sub(r'\b' + re.escape(engine_specs["displacement"]) + r'\b', '', remaining, flags=re.IGNORECASE)
                
            # Clean up and return what's left as the likely part
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            if remaining:
                return remaining
        
        return None
    
    def _extract_position(self, query):
        """Extract position information like 'front', 'rear', 'driver side', etc."""
        positions = []
        
        position_terms = {
            "front": ["front", "forward"],
            "rear": ["rear", "back"],
            "left": ["left", "driver", "driver's", "driver side"],
            "right": ["right", "passenger", "passenger's", "passenger side"],
            "upper": ["upper", "top"],
            "lower": ["lower", "bottom"],
            "inner": ["inner", "inside"],
            "outer": ["outer", "outside"]
        }
        
        for position, terms in position_terms.items():
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, query):
                    positions.append(position)
                    break
        
        return positions if positions else None
    
    def _get_year_range(self, year, make, model):
        """Get the year range for specific model generations"""
        if not all([year, make, model]):
            return None
            
        # Convert to lowercase for lookup
        make_lower = make.lower()
        model_lower = model.lower()
        year_int = int(year)
        
        # Check if we have info for this make/model
        if make_lower in self.year_range_patterns and model_lower in self.year_range_patterns[make_lower]:
            ranges = self.year_range_patterns[make_lower][model_lower]
            
            for year_range, gen_info in ranges.items():
                start_year, end_year = map(int, year_range.split('-'))
                if start_year <= year_int <= end_year:
                    return {
                        "range": year_range,
                        "generation": gen_info
                    }
        
        return None
    
    def _calculate_confidence(self, result):
        """Calculate a confidence score for the extracted information"""
        confidence = 0
        
        # Add points for each field we successfully extracted
        if result["year"]:
            confidence += 25  # Reduced from 30 to account for model
        if result["make"]:
            confidence += 25  # Reduced from 30 to account for model
        if result["model"]:
            confidence += 15  # Add points for model detection
        if result["part"]:
            confidence += 25  # Reduced from 30 to account for model
        if result["position"]:
            confidence += 5   # Reduced from 10 to account for engine specs
        if result["engine_specs"]:
            confidence += 5   # Add points for engine specs
        
        return min(confidence, 100)
    
    def generate_search_terms(self, vehicle_info):
        """
        Generate optimized search terms based on extracted vehicle information
        Returns a list of search terms in decreasing order of specificity
        """
        search_terms = []
        
        year = vehicle_info.get("year")
        make = vehicle_info.get("make")
        model = vehicle_info.get("model")
        part = vehicle_info.get("part")
        position = vehicle_info.get("position")
        engine_specs = vehicle_info.get("engine_specs")
        original_query = vehicle_info.get("original_query", "")
        
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
        
        # Generate year range if available
        year_range = None
        if "year_range" in vehicle_info and vehicle_info["year_range"]:
            year_range = vehicle_info["year_range"].get("range")
        
        # Generate exact match for the original query (important for precise matching)
        if original_query:
            # Check if query already contains 'oem', if not add it
            if 'oem' not in original_query.lower():
                search_terms.append(f"{original_query} oem")
            else:
                search_terms.append(original_query)
        
        # If we have all information, generate a complete search term
        if year and make and part:
            # Most specific search terms first
            
            # 1. Search term with model properly formatted (very specific)
            if formatted_model:
                term1 = f"{year} {formatted_make} {formatted_model}"
                if position:
                    term1 += f" {' '.join(position)}"
                term1 += f" {part} oem"
                search_terms.append(term1)
            
            # 2. Search term with year range for better compatibility
            if year_range:
                term2 = f"{year_range} {formatted_make}"
                if formatted_model:
                    term2 += f" {formatted_model}"
                if position:
                    term2 += f" {' '.join(position)}"
                term2 += f" {part} oem"
                search_terms.append(term2)
            
            # 3. Search using the part terminology mapping with model
            if part in self.part_terms and formatted_model:
                enhanced_part = self.part_terms[part]
                term3 = f"{year} {formatted_make} {formatted_model}"
                if engine_disp:
                    term3 += f" {engine_disp}"
                term3 += f" {enhanced_part}"
                search_terms.append(term3)
            
            # 4. Fallback to basic year/make/part if we don't have model
            if not formatted_model:
                term4 = f"{year} {formatted_make}"
                if position:
                    term4 += f" {' '.join(position)}"
                term4 += f" {part} oem"
                search_terms.append(term4)
                
                # Also try with enhanced part terms if available
                if part in self.part_terms:
                    enhanced_part = self.part_terms[part]
                    term5 = f"{year} {formatted_make} {enhanced_part}"
                    search_terms.append(term5)
        
        # Fallback search terms with less information
        if make and part and not search_terms:
            term6 = f"{formatted_make}"
            if formatted_model:
                term6 += f" {formatted_model}"
            if year:
                term6 += f" {year}"
            if engine_disp:
                term6 += f" {engine_disp}"
            if position:
                term6 += f" {' '.join(position)}"
            term6 += f" {part} oem"
            
            if term6 not in search_terms:
                search_terms.append(term6)
        
        # If we still don't have enough info, just use the normalized query
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