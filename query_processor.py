import re
import json
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union, Any
import time

# Precompile common regex patterns for better performance
YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')
FILLER_WORDS_PATTERN = re.compile(r"\b(for|a|the|my|an|this|that|to|on|in|with)\b")
WHITESPACE_PATTERN = re.compile(r"\s+")
DASH_PATTERN = re.compile(r"[–—]")

class EnhancedQueryProcessor:
    """
    Enhanced query processor that can handle various input formats
    and extract structured vehicle and part information.
    Updated to properly handle structured data from multiple fields.
    """
    
    def __init__(self):
        """
        Initialize the enhanced query processor with optimized data structures
        and precompiled patterns for better performance.
        """
        # Load vehicle data (in production, this would be from your database)
        self.vehicle_makes = ["acura", "alfa romeo", "aston martin", "audi", "bentley", "bmw", "buick", 
    "cadillac", "chevrolet", "chrysler", "dodge", "ferrari", "fiat", "ford", 
    "genesis", "gmc", "honda", "hyundai", "infiniti", "jaguar", "jeep", "kia", 
    "lamborghini", "land rover", "lexus", "lincoln", "lotus", "maserati", 
    "mazda", "mclaren", "mercedes-benz", "mini", "mitsubishi", "nissan", 
    "oldsmobile", "plymouth", "pontiac", "mercury", 
    "porsche", "ram", "rolls-royce", "subaru", "tesla", "toyota", "volkswagen", 
    "volvo", "bugatti", "genesis", "amc", "delorean", "desoto", 
    "edsel", "hudson", "packard", "studebaker", "nash", "willys", "imperial", 
    "international", "international harvester"]
        
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
    "chrysler": "chrysler",
    "olds": "oldsmobile",
    "cutlass": "oldsmobile",
    "ponti": "pontiac",
    "firebird": "pontiac", 
    "trans am": "pontiac",
    "goat": "pontiac",
    "merc": "mercury",
    "cougr": "mercury",
    "mopar": "chrysler",
    "plym": "plymouth",
    "barracuda": "plymouth",
    "roadrunner": "plymouth",
    "eldorado": "cadillac",
    "seville": "cadillac",
    "deville": "cadillac",
    "coupe deville": "cadillac",
    "eldo": "cadillac",
    "falcon": "ford",
    "fairlane": "ford",
    "galaxie": "ford",
    "ltd": "ford",
    "thunderbird": "ford",
    "tbird": "ford",
    "bird": "ford",
    "fury": "plymouth",
    "valiant": "plymouth",
    "duster": "plymouth",
    "belvedere": "plymouth",
    "gtx": "plymouth",
    "savoy": "plymouth",
    "polara": "dodge",
    "coronet": "dodge",
    "dart": "dodge",
    "charger": "dodge",
    "challenger": "dodge",
    "superbee": "dodge",
    "Monaco": "dodge",
    "bonneville": "pontiac",
    "catalina": "pontiac",
    "tempest": "pontiac",
    "grand prix": "pontiac",
    "parisienne": "pontiac",
    "lemans": "pontiac",
    "skylark": "buick",
    "riviera": "buick",
    "wildcat": "buick",
    "electra": "buick",
    "century": "buick",
    "regal": "buick",
    "gs": "buick",
    "grand national": "buick",
    "gnx": "buick",
    "toronado": "oldsmobile",
    "delta 88": "oldsmobile",
    "98": "oldsmobile",
    "88": "oldsmobile",
    "442": "oldsmobile",
    "hurst": "oldsmobile"
        }
        
        # Load part terminology dictionary
        self.part_terms = self._load_part_terms()
        
        # Normalized common part categories for better matching
        self.part_categories = {
           "engine": ["engine block", "short block", "long block", "engine assembly", "motor", "powertrain", "engine rebuild kit", "crate engine", "remanufactured engine", "rebuilt engine", "cylinder block", "engine swap kit", "internal combustion engine", "rotary engine", "diesel engine", "hybrid engine", "boxer engine", "inline engine", "v engine", "flat engine"],
    
    "engine_internals": ["piston", "piston ring", "connecting rod", "crankshaft", "camshaft", "lifter", "valve", "valve spring", "valve guide", "rocker arm", "push rod", "timing chain", "timing gear", "timing belt", "oil pump", "crank bearing", "rod bearing", "main bearing", "thrust bearing", "cylinder sleeve", "cylinder liner", "wrist pin", "gudgeon pin", "harmonic balancer", "crankshaft pulley", "flywheel", "flex plate", "oil pan", "valve cover", "timing cover", "engine mount", "motor mount"],
    
    "engine_accessory": ["belt", "pulley", "tensioner", "idler pulley", "serpentine belt", "v-belt", "timing belt", "timing chain", "drive belt", "accessory belt", "belt kit", "supercharger belt", "alternator pulley", "power steering pulley", "air conditioning pulley", "water pump pulley", "crankshaft pulley", "automatic tensioner", "mechanical tensioner", "belt guide", "belt cover"],
    
    "engine_electrical": ["alternator", "starter", "starter motor", "ignition coil", "coil pack", "spark plug", "spark plug wire", "distributor", "voltage regulator", "starter solenoid", "ignition switch", "ignition module", "high output alternator", "high torque starter", "ignition wire set", "magneto", "charging system", "starting system", "distributor cap", "distributor rotor", "condenser", "points", "electronic ignition", "remote starter", "generator", "voltage converter"],
    
    "engine_cooling": ["radiator", "cooling fan", "water pump", "thermostat", "coolant reservoir", "expansion tank", "overflow tank", "fan clutch", "radiator cap", "radiator hose", "coolant temperature sensor", "fan shroud", "fan blade", "electric fan", "mechanical fan", "water neck", "thermostat housing", "cooling system", "radiator support", "cooling module", "coolant bypass hose", "coolant pipe", "heat exchanger", "oil cooler", "transmission cooler", "intercooler", "coolant temperature gauge", "high flow water pump", "high flow radiator", "overflow hose", "bleed valve", "coolant bleeder", "fan switch", "fan relay", "temperature switch", "fan controller"],
    
    "engine_fuel": ["fuel pump", "fuel filter", "fuel injector", "fuel pressure regulator", "fuel rail", "carburetor", "throttle body", "fuel tank", "fuel cap", "fuel gauge", "fuel sending unit", "fuel pressure sensor", "fuel tank strap", "fuel line", "fuel hose", "fuel return line", "fuel cell", "high pressure pump", "low pressure pump", "in-tank pump", "external pump", "mechanical pump", "electric pump", "lift pump", "fuel pump relay", "fuel level sensor", "fuel vapor canister", "evap canister", "fuel filler neck", "gas cap", "diesel fuel filter", "fuel water separator", "carburetor kit", "float", "jet", "needle", "choke", "accelerator pump", "high flow injector", "injector seal", "injector o-ring", "idle air control valve", "idle control motor", "throttle position sensor", "throttle cable", "fuel gauge sending unit"],
    
    "engine_air": ["air filter", "air intake", "mass air flow sensor", "maf sensor", "intake manifold", "intake hose", "air box", "throttle body", "air cleaner", "cold air intake", "ram air intake", "short ram intake", "intake tube", "intake duct", "filter adapter", "air filter housing", "air intake resonator", "throttle body spacer", "intake manifold gasket", "intake manifold spacer", "throttle body gasket", "air intake gasket", "air filter element", "performance air filter", "oiled air filter", "dry air filter", "pre-filter", "velocity stack", "air horn", "air intake scoop", "snorkel", "air filter box", "intake manifold runner control", "variable intake manifold", "intake plenum", "positive crankcase ventilation valve", "PCV valve", "PCV hose", "breather", "oil separator", "oil catch can", "egr valve", "egr tube", "egr cooler"],
    
    "engine_exhaust": ["exhaust manifold", "header", "catalytic converter", "cat converter", "muffler", "resonator", "exhaust pipe", "tail pipe", "exhaust tip", "o2 sensor", "oxygen sensor", "exhaust manifold gasket", "header gasket", "exhaust flange gasket", "catalytic converter gasket", "exhaust donut gasket", "exhaust clamp", "exhaust hanger", "exhaust bracket", "exhaust insulator", "exhaust wrap", "header wrap", "heat shield", "complete exhaust", "cat-back exhaust", "axle-back exhaust", "header-back exhaust", "turbo-back exhaust", "down pipe", "up pipe", "mid pipe", "x-pipe", "h-pipe", "y-pipe", "flex pipe", "flex section", "exhaust cutout", "exhaust valve", "exhaust brake", "performance exhaust", "stainless steel exhaust", "dual exhaust", "quad exhaust", "diesel particulate filter", "DPF", "EGR delete", "wide band o2 sensor", "air-fuel ratio sensor", "upstream o2 sensor", "downstream o2 sensor"],
    
    "engine_electrical_sensors": ["cam sensor", "camshaft sensor", "camshaft position sensor", "crank sensor", "crankshaft sensor", "crankshaft position sensor", "o2 sensor", "oxygen sensor", "map sensor", "maf sensor", "mass air flow sensor", "coolant temp sensor", "ect sensor", "engine coolant temperature sensor", "knock sensor", "tps", "throttle position sensor", "oil pressure sensor", "oil level sensor", "oil temperature sensor", "fuel pressure sensor", "fuel level sensor", "fuel temperature sensor", "intake air temperature sensor", "IAT sensor", "barometric pressure sensor", "BARO sensor", "EGR temperature sensor", "EGR position sensor", "boost pressure sensor", "speed sensor", "vehicle speed sensor", "transmission speed sensor", "input speed sensor", "output speed sensor", "ABS sensor", "wheel speed sensor", "exhaust gas temperature sensor", "EGT sensor", "exhaust pressure sensor", "accelerator pedal position sensor", "APP sensor", "electronic throttle control", "ETC motor", "engine position sensor", "ignition timing sensor", "hall effect sensor", "cylinder deactivation sensor", "misfire detection sensor", "wideband o2 sensor", "NOx sensor", "particulate matter sensor", "DPF pressure sensor", "ambient air temperature sensor", "flex fuel sensor", "humidity sensor"],
    
    "engine_gaskets": ["head gasket", "valve cover gasket", "oil pan gasket", "intake manifold gasket", "exhaust manifold gasket", "timing cover gasket", "water pump gasket", "thermostat gasket", "gasket set", "engine gasket set", "complete gasket set", "timing chain cover gasket", "front main seal", "rear main seal", "camshaft seal", "valve stem seal", "crankshaft seal", "oil filter adapter gasket", "oil cooler gasket", "oil pump gasket", "valley pan gasket", "valve guide seal", "throttle body gasket", "EGR gasket", "fuel pump gasket", "injector o-ring", "injector seal", "water outlet gasket", "cylinder head gasket", "engine block gasket", "oil pickup tube gasket", "dipstick tube seal", "PCV grommet", "spark plug tube seal", "valve cover grommet", "head bolt washer", "sealing washer", "copper washer", "crush washer", "intake manifold o-ring", "throttle body o-ring", "water pump o-ring", "thermostat o-ring", "intake runner gasket", "cylinder head bolt set", "head stud kit", "RTV silicone", "gasket maker", "gasket sealer", "multi-layer steel gasket", "composite gasket", "cork gasket", "rubber gasket", "silicone gasket"],
    
    "engine_oiling": ["oil pump", "oil filter", "oil pan", "oil cooler", "oil pressure sensor", "oil level sensor", "oil drain plug", "oil drain plug gasket", "oil filter housing", "oil filter adapter", "oil pressure relief valve", "oil pressure switch", "oil gallery plug", "oil dipstick", "dipstick tube", "oil filler cap", "oil catch can", "oil separator", "synthetic oil", "conventional oil", "high mileage oil", "racing oil", "diesel oil", "motor oil", "engine oil", "oil additive", "oil flush", "oil change kit", "oil filter wrench", "oil analysis kit", "oil pressure gauge", "oil temperature gauge", "dry sump system", "wet sump system", "oil restrictor", "oil passage", "windage tray", "oil baffle", "oil cooler line", "oil cooler hose", "oil cooler adapter", "oil return line", "turbo oil line", "oil feed line", "pickup tube", "oil pickup screen"],
    
    # Transmission parts
    "transmission": ["transmission assembly", "automatic transmission", "manual transmission", "trans", "gearbox", "transmission rebuild kit", "transmission filter", "transmission pan", "transmission mount", "transmission fluid", "ATF fluid", "transmission cooler", "transmission cooler line", "transmission dipstick", "transmission control module", "TCM", "valve body", "transmission solenoid", "transmission speed sensor", "output shaft", "input shaft", "transmission oil pump", "torque converter", "transmission band", "transmission clutch pack", "transmission bearing", "shift kit", "shift cable", "shift linkage", "shift knob", "shift boot", "shifter assembly", "shift fork", "shift lever", "shift shaft", "transmission case", "transmission housing", "transmission bellhousing", "transmission tailshaft", "transmission adapter", "transmission crossmember", "flex plate", "transmission drain plug", "transmission pan gasket", "transmission pump seal", "transmission rebuild kit", "transmission overhaul kit", "remanufactured transmission", "rebuilt transmission", "CVT transmission", "DCT transmission", "dual clutch transmission", "SMG transmission", "sequential transmission", "manumatic transmission", "tiptronic transmission", "automatic manual transmission", "direct shift gearbox", "DSG transmission", "AMT transmission", "transaxle", "transmission controller", "transmission wiring harness", "transmission computer", "shift solenoid", "shift selector", "gear indicator", "transmission oil cooler", "transmission oil filter", "transmission pressure switch", "kickdown cable", "detent cable", "modulator valve", "governor", "accumulator", "servo", "clutch pack", "band", "one-way clutch", "sprag clutch", "roller clutch", "synchronizer", "synchro ring", "gear set", "planetary gear set", "sun gear", "ring gear", "planet carrier", "transmission extension housing", "speedometer gear", "vehicle speed sensor", "VSS", "output shaft seal", "input shaft seal", "front pump seal", "extension housing seal", "transmission mount", "transmission dust cover", "transmission dipstick tube", "transmission pan bolt", "transmission gasket set", "transmission seal kit", "transmission linkage bushing", "transmission filter gasket"],
    
    "transmission_clutch": ["clutch kit", "clutch disc", "pressure plate", "throwout bearing", "release bearing", "slave cylinder", "master cylinder", "flywheel", "clutch cable", "clutch line", "clutch fork", "slave cylinder line", "clutch pedal", "clutch fluid", "clutch fluid reservoir", "clutch master cylinder reservoir", "clutch alignment tool", "pilot bearing", "flywheel bolt", "flywheel dowel pin", "clutch fork boot", "clutch pivot ball", "clutch release arm", "clutch release shaft", "clutch spring", "clutch dampener", "clutch friction plate", "clutch pressure spring", "clutch cover", "clutch housing", "clutch dust cover", "clutch plate", "clutch hub", "clutch disc hub", "clutch facing", "clutch lining", "dual mass flywheel", "DMF", "solid flywheel conversion kit", "lightweight flywheel", "flywheel ring gear", "clutch alignment dowel", "clutch release bearing guide tube", "clutch release bearing clip", "clutch plate spline", "concentric slave cylinder", "CSC", "hydraulic clutch system", "mechanical clutch system", "cable clutch system", "clutch pedal assembly", "clutch pedal stop", "clutch pedal return spring", "clutch pushrod", "clutch bleeder valve", "clutch bleeding kit", "clutch alignment dowel", "clutch kit with flywheel", "heavy duty clutch", "racing clutch", "performance clutch", "stage 1 clutch", "stage 2 clutch", "stage 3 clutch", "twin disc clutch", "multi disc clutch", "competition clutch", "organic clutch", "ceramic clutch", "metal clutch", "kevlar clutch", "sprung hub clutch disc", "unsprung hub clutch disc", "clutch pressure plate bolt", "clutch fork pivot", "clutch fork pivot ball", "clutch fork return spring", "clutch fork boot", "clutch fork bushing"],
    
    "transmission_transfer": ["transfer case", "transfer case motor", "transfer case switch", "transfer case chain", "transfer case seal", "transfer case encoder motor", "transfer case shift fork", "transfer case synchronizer", "transfer case bearing", "transfer case gasket", "transfer case oil", "transfer case fluid", "transfer case cover", "transfer case housing", "transfer case mounting bracket", "transfer case skid plate", "transfer case shift module", "transfer case control module", "transfer case shift lever", "transfer case shift linkage", "transfer case actuator", "transfer case shift motor", "4WD actuator", "transfer case input shaft", "transfer case output shaft", "transfer case drive chain", "transfer case front output shaft", "transfer case rear output shaft", "transfer case pump", "transfer case viscous coupling", "transfer case mode fork", "transfer case shift rail", "transfer case rebuild kit", "transfer case overhaul kit", "transfer case adapter", "transfer case vacuum switch", "transfer case vacuum line", "transfer case breather", "transfer case drain plug", "transfer case fill plug", "4WD indicator switch", "AWD coupler", "AWD solenoid", "4WD hub", "locking hub", "manual locking hub", "automatic locking hub", "free wheeling hub", "4WD switch", "4WD indicator", "4WD control module", "center differential", "center differential lock"],
    
    "transmission_differential": ["differential", "differential cover", "differential bearing", "axle shaft", "axle bearing", "axle seal", "pinion seal", "ring and pinion", "spider gear", "differential case", "differential carrier", "differential housing", "differential gasket", "differential fluid", "gear oil", "limited slip differential", "LSD", "locking differential", "open differential", "Torsen differential", "Quaife differential", "Detroit locker", "differential rebuild kit", "differential overhaul kit", "differential breather", "differential vent", "differential pinion", "differential pinion bearing", "differential pinion flange", "differential pinion nut", "differential side gear", "thrust washer", "side gear shaft", "spider gear shaft", "cross shaft", "differential crush sleeve", "crush washer", "differential shim", "differential pin", "differential preload", "differential crush collar", "differential spacer", "pinion yoke", "pinion flange", "pinion gear", "crown gear", "ring gear bolt", "ring gear spacer", "differential pinion seal", "differential cover gasket", "differential cover bolt", "differential fill plug", "differential drain plug", "differential bearing race", "differential bearing cup", "differential bearing retainer", "differential side bearing", "differential carrier bearing", "axle bearing retainer", "axle bearing race", "axle shaft spacer", "axle shaft key", "axle shaft flange", "axle shaft nut", "axle shaft washer", "axle shaft snap ring", "axle shaft oil seal", "axle housing", "axle tube", "axle vent", "axle breather", "axle shaft bearing", "axle u-joint", "limited slip additive", "friction modifier", "traction enhancer", "posi traction additive", "helical gear differential", "worm gear differential", "planetary gear differential", "spool", "mini spool", "differential install kit"],
    
    "transmission_driveshaft": ["drive shaft", "driveshaft", "u-joint", "universal joint", "cv axle", "cv joint", "cv boot", "half shaft", "propeller shaft", "driveshaft center support bearing", "center bearing", "carrier bearing", "driveshaft slip yoke", "driveshaft tube", "driveshaft yoke", "driveshaft flange", "driveshaft bolt", "driveshaft coupling", "driveshaft U-bolt", "driveshaft strap", "driveshaft hanger", "driveshaft guard", "driveshaft loop", "driveshaft safety loop", "cv joint boot kit", "cv axle boot", "inner cv boot", "outer cv boot", "cv boot clamp", "cv joint grease", "cv axle nut", "axle nut", "spindle nut", "hub nut", "inner cv joint", "outer cv joint", "tripod joint", "rzeppa joint", "double cardan joint", "constant velocity joint", "u-joint cross", "u-joint cap", "u-joint spider", "u-joint kit", "u-joint grease fitting", "u-joint needle bearing", "u-joint retainer", "u-joint strap", "u-joint u-bolt", "cardan joint", "giubo", "flex disc", "flex joint", "prop shaft", "tail shaft", "driveshaft seal", "driveshaft spline", "slip joint", "aluminum driveshaft", "carbon fiber driveshaft", "steel driveshaft", "one piece driveshaft", "two piece driveshaft", "three piece driveshaft", "driveshaft balancing", "driveshaft spacer", "driveshaft adapter", "driveshaft extension", "driveshaft pinion flange", "driveshaft companion flange", "driveshaft rubber coupler", "driveshaft vibration damper", "driveline vibration damper", "driveshaft boot", "half shaft assembly", "half shaft bolt", "axle assembly", "front axle", "rear axle", "axle assembly kit"],
    
    # Brake system
    "brake": ["brake pad", "brake shoe", "brake rotor", "brake drum", "brake caliper", "brake hose", "brake line", "brake master cylinder", "wheel cylinder", "abs module", "abs sensor", "brake fluid", "brake pedal", "brake booster", "brake proportioning valve", "brake bleeder valve", "brake bleeder screw", "brake pad sensor", "brake pad clip", "brake disc", "brake rotor", "brake kit", "brake pad set", "brake light switch", "brake pressure switch", "brake controller", "brake proportioning valve", "brake kit", "disc brake kit", "drum brake kit", "brake conversion kit", "brake upgrade kit", "brake rebuild kit", "brake hardware kit", "brake backing plate", "brake dust shield", "brake dust boot", "emergency brake", "parking brake", "hand brake", "brake vacuum hose", "brake vacuum pump", "brake vacuum reservoir", "brake vacuum check valve", "brake cable", "brake cable bracket", "brake line bracket", "brake line clip", "brake line tee", "brake line union", "brake line coupler", "brake line adapter", "brake pressure gauge", "brake bleeding kit", "brake fluid tester", "brake flush kit", "brake service kit", "brake rotor resurfacing", "brake caliper paint", "brake caliper cover", "brake fluid reservoir cap", "brake hose banjo bolt", "brake hose banjo washer", "brake pressure differential switch"],
    
    "brake_hydraulic": ["brake master cylinder", "wheel cylinder", "brake caliper", "brake hose", "brake line", "proportioning valve", "combination valve", "brake fluid reservoir", "brake cylinder", "master cylinder", "dual master cylinder", "tandem master cylinder", "single master cylinder", "master cylinder pushrod", "master cylinder boot", "master cylinder cap", "master cylinder rebuild kit", "master cylinder repair kit", "master cylinder bench bleeding kit", "wheel cylinder boot", "wheel cylinder rebuild kit", "wheel cylinder repair kit", "wheel cylinder bleeder screw", "wheel cylinder spring kit", "wheel cylinder retainer", "caliper piston", "caliper boot", "caliper seal", "caliper sleeve", "caliper bushing", "caliper bolt", "caliper pin", "caliper bracket", "caliper bracket bolt", "caliper guide pin", "caliper slide pin", "caliper O-ring", "caliper rebuild kit", "caliper repair kit", "caliper hardware kit", "caliper piston tool", "brake hose bracket", "brake line fitting", "brake line nut", "brake line clip", "brake line bracket", "brake line union", "brake line tee", "brake line coupler", "brake line adapter", "brake line splice", "brake line junction", "brake metering valve", "brake pressure differential valve", "brake proportioning valve", "brake warning switch", "brake check valve", "brake booster check valve", "brake booster valve", "brake pressure modulator valve", "brake pressure accumulator", "brake accumulator", "brake load sensing valve", "brake load sensing proportioning valve", "brake adjusting valve", "brake distribution valve", "brake residual pressure valve", "brake quick disconnect", "brake fluid level sensor", "brake fluid reservoir cap", "brake fluid reservoir filter", "brake fluid reservoir seal", "brake fluid pressure sensor", "brake pressure transducer", "brake fluid bleeder kit", "brake fluid bleeder wrench", "brake fluid injector", "brake fluid extractor", "brake fluid syringe", "brake fluid vacuum pump", "brake fluid catch bottle", "brake fluid DOT 3", "brake fluid DOT 4", "brake fluid DOT 5", "brake fluid DOT 5.1", "silicone brake fluid", "synthetic brake fluid", "high temperature brake fluid", "racing brake fluid"],
    
    "brake_mechanical": ["brake pad", "brake shoe", "brake rotor", "brake drum", "parking brake cable", "emergency brake cable", "brake hardware kit", "brake dust shield", "brake pad shim", "brake pad wear sensor", "brake pad clip", "brake pad abutment clip", "brake pad retainer clip", "brake pad retainer spring", "brake pad wear indicator", "brake shoe return spring", "brake shoe hold down spring", "brake shoe adjuster", "brake shoe adjuster kit", "brake shoe adjuster cable", "brake shoe lever", "brake shoe web", "brake shoe lining", "brake rotor hat", "brake rotor friction ring", "brake rotor cooling vane", "one-piece brake rotor", "two-piece brake rotor", "floating brake rotor", "brake rotor wear indicator", "brake rotor shield", "brake rotor spacer", "brake rotor bolt", "brake rotor screw", "brake drum adjuster", "brake drum backing plate", "brake drum hardware kit", "parking brake lever", "parking brake handle", "parking brake pedal", "parking brake release handle", "parking brake equalizer", "parking brake cable connector", "parking brake cable bracket", "parking brake cable guide", "parking brake cable clip", "parking brake shoe", "parking brake drum", "self-adjusting brake", "automatic brake adjuster", "brake pad spreader tool", "brake drum puller", "brake shoe spring tool", "brake lining thickness gauge", "brake pad thickness gauge", "brake pad wear gauge", "brake pad installation tool", "brake caliper compression tool", "brake drum micrometer", "brake rotor micrometer", "brake spring pliers", "brake hardware lubricant"],
    
    "brake_abs": ["abs module", "abs control unit", "abs sensor", "wheel speed sensor", "abs pump", "abs relay", "abs harness", "ABS system", "anti-lock brake system", "ABS control module", "ABS electronic control unit", "ABS hydraulic unit", "ABS hydraulic control unit", "ABS accumulator", "ABS modulator", "ABS actuator", "ABS solenoid", "ABS solenoid valve", "ABS motor", "ABS pump motor", "ABS pressure sensor", "ABS pressure switch", "ABS wheel speed sensor", "ABS reluctor ring", "ABS tone ring", "ABS exciter ring", "ABS trigger wheel", "ABS sensor harness", "ABS wiring harness", "ABS connector", "ABS reservoir", "ABS fluid", "ABS diagnosis tool", "ABS scanner", "ABS reset tool", "ABS bleeding procedure", "ABS brake line", "ABS brake hose", "ABS hydraulic line", "ABS hydraulic hose", "ABS relay", "ABS fuse", "ABS pressure regulator", "ABS valve body", "ABS warning light", "ABS indicator light", "ABS light switch", "ABS control module mounting bracket", "ABS module bracket", "ABS sensor bracket", "ABS calibration", "ABS programming", "ABS speed sensor o-ring", "ABS speed sensor seal", "ABS cable", "ABS cable bracket", "ABS module connector", "ABS system tester", "electronic brake force distribution", "EBD", "electronic stability control", "ESC", "dynamic stability control", "DSC", "stability control system", "SCS", "electronic brake assist", "EBA", "emergency brake assist", "traction control system", "TCS", "hill start assist", "HSA", "hill hold control", "automatic slip regulation", "ASR"],
    
    # Suspension and steering
    "suspension": ["shock absorber", "shock", "strut", "strut assembly", "coil spring", "leaf spring", "air spring", "air bag", "control arm", "ball joint", "tie rod", "sway bar", "stabilizer bar", "bushing", "suspension system", "strut mount", "strut bearing", "spring compressor", "spring insulator", "spring isolator", "spring perch", "spring seat", "spring spacer", "spring bolt", "suspension arm", "suspension link", "suspension bushing", "suspension mount", "suspension bracket", "suspension joint", "suspension bearing", "suspension hardware kit", "suspension rebuild kit", "suspension lowering kit", "suspension lift kit", "suspension level kit", "suspension air bag", "suspension compressor", "suspension dryer", "suspension air valve", "suspension height sensor", "suspension control module", "suspension strut brace", "suspension tower brace", "suspension tower bar", "control arm bushing", "control arm bracket", "control arm bolt", "control arm nut", "control arm washer", "trailing arm bushing", "trailing arm bracket", "trailing arm bolt", "trailing arm joint", "trailing arm mount", "panhard rod", "track bar", "lateral link", "radius rod", "radius arm", "camber bolt", "camber kit", "caster kit", "alignment kit", "toe link", "toe arm", "toe rod", "toe adjuster", "wheel alignment shim", "wheel alignment tool", "suspension grease", "ball joint grease", "suspension lubricant", "MacPherson strut", "double wishbone", "multi-link suspension", "solid axle", "independent suspension", "semi-independent suspension", "torsion bar", "torsion spring", "magnetic suspension", "adaptive suspension", "electronic suspension", "air ride suspension", "coilover", "coilover kit", "adjustable suspension", "performance suspension", "sport suspension", "off-road suspension", "heavy duty suspension", "comfort suspension"],
    
    "suspension_front": ["front shock", "front strut", "front coil spring", "front control arm", "front ball joint", "front tie rod", "front sway bar", "front stabilizer link", "front bushing", "front suspension", "front subframe", "front crossmember", "front cradle", "front suspension arm", "front suspension link", "front suspension mount", "front suspension bracket", "front suspension bushing", "front suspension joint", "front suspension bearing", "front strut mount", "front strut bearing", "front strut brace", "front spring", "front spring insulator", "front spring perch", "front spring seat", "front spring bolt", "front control arm bushing", "front control arm bracket", "front control arm bolt", "front upper control arm", "front lower control arm", "front inner tie rod", "front outer tie rod", "front sway bar bushing", "front sway bar bracket", "front sway bar link", "front sway bar mount", "front stabilizer bushing", "front stabilizer bracket", "front stabilizer link", "front stabilizer mount", "front ball joint boot", "front ball joint nut", "front strut boot", "front strut bumper", "front strut bellows", "front spindle", "front steering knuckle", "front hub carrier", "front wheel bearing", "front wheel hub", "front knuckle assembly", "front suspension kit", "front suspension rebuild kit", "front suspension overhaul kit", "front coilover", "front coilover kit", "front suspension lowering kit", "front suspension lift kit", "front camber kit", "front caster kit", "front alignment kit"],
    
    "suspension_rear": ["rear shock", "rear strut", "rear coil spring", "rear leaf spring", "rear control arm", "rear ball joint", "rear sway bar", "rear stabilizer link", "rear bushing", "trailing arm", "rear suspension", "rear subframe", "rear crossmember", "rear cradle", "rear suspension arm", "rear suspension link", "rear suspension mount", "rear suspension bracket", "rear suspension bushing", "rear suspension joint", "rear suspension bearing", "rear strut mount", "rear strut bearing", "rear strut brace", "rear spring", "rear spring insulator", "rear spring perch", "rear spring seat", "rear spring bolt", "rear control arm bushing", "rear control arm bracket", "rear control arm bolt", "rear upper control arm", "rear lower control arm", "rear trailing arm", "rear trailing arm bushing", "rear trailing arm bracket", "rear trailing arm bolt", "rear trailing arm joint", "rear trailing arm mount", "rear track bar", "rear panhard rod", "rear lateral link", "rear radius rod", "rear radius arm", "rear sway bar bushing", "rear sway bar bracket", "rear sway bar link", "rear sway bar mount", "rear stabilizer bushing", "rear stabilizer bracket", "rear stabilizer link", "rear stabilizer mount", "rear ball joint boot", "rear ball joint nut", "rear strut boot", "rear strut bumper", "rear strut bellows", "rear wheel bearing", "rear wheel hub", "rear knuckle assembly", "rear knuckle", "rear spindle", "rear suspension kit", "rear suspension rebuild kit", "rear suspension overhaul kit", "rear coilover", "rear coilover kit", "rear suspension lowering kit", "rear suspension lift kit", "rear camber kit", "rear toe kit", "rear alignment kit", "rear axle assembly", "rear axle beam", "rear torsion beam", "rear multi-link", "rear semi-trailing arm", "IRS kit", "independent rear suspension kit"],
    
    "steering": ["steering rack", "rack and pinion", "power steering pump", "steering gear", "steering box", "steering column", "steering shaft", "tie rod", "tie rod end", "idler arm", "pitman arm", "steering knuckle", "steering system", "power steering", "electric power steering", "hydraulic power steering", "electric steering", "steering wheel", "steering coupler", "steering universal joint", "steering u-joint", "steering intermediate shaft", "steering linkage", "steering drag link", "steering center link", "steering damper", "steering stabilizer", "steering rack boot", "steering rack seal", "steering rack bushing", "steering rack mount", "power steering reservoir", "power steering fluid", "power steering pressure hose", "power steering return hose", "power steering cooler", "power steering cooler line", "power steering filter", "power steering pump pulley", "power steering pump bracket", "power steering pump seal", "power steering pump rebuild kit", "power steering belt", "steering column bearing", "steering column bushing", "steering column cover", "steering column shroud", "steering column lock", "steering column switch", "steering wheel controls", "steering position sensor", "steering angle sensor", "steering torque sensor", "steering pressure sensor", "steering wheel hub", "steering wheel adapter", "steering wheel cover", "steering wheel lock", "steering wheel puller", "steering rack pinion", "steering rack end seal", "steering rack mounting bushing", "steering rack mounting bracket", "steering rack brace", "electronic power steering control module", "EPS module", "power steering control module", "power steering assist motor", "EPAS module", "steering wheel position sensor", "steering column adjustment", "steering column tilt mechanism", "steering column telescoping mechanism", "steering shaft bearing", "steering shaft seal", "steering shaft support", "steering column shaft", "inner tie rod", "outer tie rod", "tie rod boot", "tie rod dust boot", "tie rod adjusting sleeve", "tie rod castle nut", "tie rod cotter pin", "tie rod end boot", "idler arm bushing", "idler arm bracket", "pitman arm nut", "pitman arm puller", "steering box seal", "steering box adjustment", "steering box mounting bolt", "steering box mounting bracket", "power steering pressure switch", "hydro-boost", "hydroboost", "power brake booster", "steering return line", "manual steering", "power steering conversion kit", "quick ratio steering", "variable ratio steering", "steering wheel hub adapter", "steering wheel quick release", "pitman arm puller"],
    
    "wheel_hub": ["wheel hub", "wheel bearing", "hub assembly", "spindle", "axle nut", "wheel stud", "lug nut", "wheel hub assembly", "wheel hub unit", "wheel bearing assembly", "wheel bearing hub", "wheel bearing kit", "wheel hub bearing", "hub bearing", "hub unit", "wheel hub seal", "wheel bearing seal", "wheel bearing race", "wheel bearing retainer", "wheel bearing spacer", "wheel bearing lock", "wheel bearing clip", "wheel bearing grease", "wheel bearing grease seal", "wheel bearing dust cap", "wheel hub cap", "wheel bearing nut", "wheel bearing washer", "wheel bearing lock washer", "wheel bearing lock nut", "wheel bearing castle nut", "wheel bearing cotter pin", "wheel bearing tool", "wheel bearing press", "wheel hub bolt", "wheel hub flange", "wheel hub gasket", "wheel hub o-ring", "spindle nut", "spindle washer", "spindle pin", "spindle bearing", "spindle seal", "spindle bushing", "spindle lock", "spindle shaft", "spindle dust cap", "spindle cover", "wheel stud replacement", "wheel stud installer", "wheel stud remover", "wheel lug bolt", "wheel lug stud", "wheel lock set", "wheel lock key", "wheel spacer", "wheel adapter", "hub centric ring", "wheel bearing press kit", "wheel bearing driver set", "wheel bearing installer", "wheel bearing removal tool"],
    
    # Body parts
    "body_exterior": ["hood", "fender", "quarter panel", "door", "door panel", "trunk lid", "tailgate", "bumper", "bumper cover", "grille", "spoiler", "mirror", "windshield", "rear window", "body panel", "roof panel", "roof skin", "floor pan", "firewall", "cowl panel", "rocker panel", "dog leg", "door skin", "door shell", "fender liner", "inner fender", "splash shield", "bumper reinforcement", "bumper absorber", "bumper bracket", "bumper energy absorber", "bumper face bar", "bumper cover", "bumper end cap", "bumper filler", "front clip", "rear clip", "radiator support", "core support", "header panel", "grille shell", "grille insert", "grille surround", "hood scoop", "hood vent", "hood pins", "hood prop rod", "hood bumper", "hood insulator", "hood pad", "fender flare", "fender extension", "fender skirt", "fender brace", "quarter panel extension", "quarter panel skin", "decklid", "trunk lid", "hatch", "liftgate", "tailgate handle", "tailgate prop", "tailgate support", "tailgate strut", "tailgate hinge", "roof rack", "roof rail", "sunroof", "moonroof", "panoramic roof", "t-top", "targa top", "convertible top", "convertible boot", "convertible cover", "tonneau cover", "tonneau cap", "bed liner", "bed cover", "bed cap", "bed rail", "bed extender", "cab protector", "headache rack", "front apron", "rear apron", "valance panel", "front valance", "rear valance", "side skirt", "rocker cover", "rocker molding", "rocker panel", "running board", "step board", "nerf bar", "side step", "mud flap", "splash guard", "truck cap", "truck topper", "window deflector", "window visor", "wind deflector", "bug deflector", "hood protector", "hood shield", "vent visor", "rain guard", "stone guard", "clear bra", "paint protection film", "car cover", "body repair panel", "rust repair panel", "patch panel", "body filler", "body repair kit", "body molding", "body cladding", "body kit"],
    
    "body_trim": ["molding", "trim", "emblem", "badge", "weatherstrip", "window molding", "door molding", "rocker panel molding", "pillar trim", "trim panel", "trim piece", "trim clip", "trim retainer", "trim ring", "trim bezel", "trim strip", "trim cover", "trim fastener", "chrome trim", "stainless trim", "vinyl trim", "plastic trim", "rubber trim", "wood trim", "carbon fiber trim", "aluminum trim", "door trim", "door trim panel", "door sill plate", "door sill trim", "door edge guard", "window trim", "window surround", "drip rail", "drip molding", "windshield molding", "windshield trim", "windshield reveal molding", "belt molding", "belt weatherstrip", "belt line molding", "beltline molding", "rocker molding", "rocker trim", "rocker panel trim", "fender trim", "fender molding", "fender flare", "wheel opening molding", "wheel arch trim", "wheel arch molding", "wheel well trim", "wheel well molding", "quarter panel molding", "quarter panel trim", "rear quarter trim", "roof rack", "roof rail", "roof molding", "roof drip molding", "tailgate trim", "trunk trim", "decklid trim", "rear deck trim", "rear deck molding", "hood trim", "hood molding", "hood ornament", "hood emblem", "grille emblem", "grille badge", "grille trim", "grille surround", "grille insert", "grille overlay", "bumper trim", "bumper insert", "bumper end cap", "bumper molding", "bumper guard", "bumper face bar", "body side molding", "body side trim", "pillar post trim", "a-pillar trim", "b-pillar trim", "c-pillar trim", "d-pillar trim", "pillar cover", "pillar garnish", "interior trim", "interior molding", "interior trim panel", "interior trim piece", "dash trim", "console trim", "dashboard trim", "dash bezel", "dash overlay", "dash kit", "center console trim", "door trim insert", "door panel insert", "kick panel", "trim removal tool", "trim installation tool", "trim adhesive", "trim clip pliers", "trim fastener remover"],
    
    "body_hardware": ["door handle", "door lock", "door hinge", "hood latch", "hood strut", "hood hinge", "trunk latch", "trunk strut", "window regulator", "window motor", "wiper blade", "wiper arm", "wiper motor", "door actuator", "door lock actuator", "door latch", "door striker", "door check", "door limiter", "door buffer", "door stop", "door seal", "door gasket", "door weatherstrip", "window regulator", "window motor", "window channel", "window guide", "window run channel", "window sweep", "window felt", "window glass", "door glass", "quarter glass", "vent glass", "back glass", "windshield", "windshield seal", "windshield molding", "windshield washer", "windshield wiper", "wiper motor", "wiper linkage", "wiper transmission", "wiper arm", "wiper blade", "wiper cowl", "wiper switch", "wiper relay", "washer pump", "washer nozzle", "washer hose", "washer reservoir", "washer fluid", "hood latch", "hood release", "hood release cable", "hood hinge", "hood strut", "hood prop rod", "hood bumper", "hood insulator", "hood liner", "hood pad", "trunk latch", "trunk release", "trunk release cable", "trunk lock", "trunk actuator", "trunk hinge", "trunk strut", "trunk prop", "trunk support", "trunk lift support", "deck lid torsion bar", "tailgate handle", "tailgate latch", "tailgate lock", "tailgate striker", "tailgate hinge", "tailgate strut", "tailgate support", "tailgate lift support", "hatch strut", "hatch support", "hatch lift support", "power tailgate", "power liftgate", "power hatch", "power door", "power window", "power mirror", "power sunroof", "sunroof motor", "sunroof track", "sunroof seal", "sunroof glass", "sunroof shade", "sunroof switch", "sunroof drain", "moonroof motor", "moonroof track", "moonroof seal", "moonroof glass", "moonroof shade", "moonroof switch", "power vent window", "vent window handle", "vent window crank", "vent window regulator", "window crank handle", "window crank", "door handle gasket", "door handle escutcheon", "door handle bezel", "fuel door", "fuel door hinge", "fuel door spring", "fuel door release", "fuel door cable", "glove box latch", "glove box hinge", "glove box strut", "glove box light", "console latch", "console hinge", "hood release handle", "trunk release handle", "power lock", "power lock actuator", "lock cylinder", "door lock cylinder", "trunk lock cylinder", "ignition lock cylinder", "key cylinder", "key blank", "remote key", "key fob", "keyless entry", "door check strap", "door check arm", "door detent", "door catch", "door roll pin", "door latch spring", "door latch rod", "door latch clip", "window regulator clip", "window regulator roller", "window regulator pulley", "window regulator cable", "license plate bracket", "license plate frame", "body fastener", "body bolt", "body clip", "body mount", "body bushing"],
    
    # Interior parts
    "interior": ["dashboard", "dash panel", "instrument cluster", "gauge cluster", "glove box", "console", "armrest", "seat", "seat belt", "seat cover", "headliner", "sun visor", "carpet", "floor mat", "interior trim", "dash trim", "dash pad", "dash cover", "dash cap", "dashboard cover", "dashboard overlay", "dashboard skin", "dash bezel", "dash insert", "instrument panel", "center console", "console lid", "console box", "console organizer", "console tray", "console panel", "overhead console", "floor console", "center armrest", "door armrest", "door panel", "door trim", "door panel insert", "door panel cover", "door panel overlay", "door handle trim", "door panel clip", "door panel retainer", "seat cover", "seat cushion", "seat foam", "seat frame", "seat track", "seat rail", "seat slider", "seat recliner", "seat back", "seat bottom", "seat cushion cover", "seat back cover", "seat belt", "seat belt buckle", "seat belt retractor", "seat belt pretensioner", "seat belt anchor", "seat belt guide", "seat belt extender", "seat belt webbing", "headrest", "head restraint", "seat headrest", "headrest cover", "headrest guide", "headrest post", "headrest lock", "headliner", "headliner board", "headliner fabric", "headliner material", "headliner insulation", "headliner retainer", "headliner clip", "headliner adhesive", "sun visor", "visor clip", "visor mirror", "visor light", "sun visor bracket", "sun visor mount", "carpet", "floor carpet", "trunk carpet", "cargo carpet", "carpet pad", "carpet underlayment", "carpet binding", "carpet fastener", "carpet clip", "floor mat", "floor liner", "all-weather mat", "trunk mat", "cargo mat", "cargo liner", "cargo tray", "cargo cover", "cargo net", "trunk organizer", "trunk divider", "trunk lid liner", "pillar trim", "a-pillar trim", "b-pillar trim", "c-pillar trim", "d-pillar trim", "kick panel", "scuff plate", "sill plate", "door sill", "door sill guard", "door sill protector", "step plate", "step pad", "pedal pad", "accelerator pedal", "brake pedal", "clutch pedal", "pedal cover", "pedal extender", "dead pedal", "foot rest", "shifter boot", "shift boot", "shifter cover", "shift knob", "shift handle", "shift lever", "e-brake handle", "parking brake handle", "emergency brake handle", "steering wheel", "steering wheel cover", "steering wheel wrap", "steering wheel grip", "horn pad", "horn button", "horn ring", "steering wheel emblem", "roof lining", "roof panel", "grab handle", "assist handle", "coat hook", "cargo hook", "trunk hook", "trunk hanger", "package tray", "rear deck", "parcel shelf", "rear speaker deck", "rear deck lid", "front seat", "rear seat", "bench seat", "bucket seat", "captain chair", "leather seat", "cloth seat", "vinyl seat", "heated seat", "power seat", "seat heater", "seat warmer", "seat memory", "seat adjuster", "seat motor", "seat switch", "seat controller", "seat control module", "seat position sensor", "manual seat", "power seat", "rear view mirror", "inside mirror", "auto dimming mirror", "rear view mirror cover", "mirror adhesive", "dome light", "map light", "reading light", "courtesy light", "trunk light", "interior light", "interior lamp", "light lens", "light cover", "light bulb", "led light", "ambient lighting", "interior lighting kit", "seat belt warning light", "seat belt chime", "interior door handle", "interior lock knob", "interior window crank", "glove box", "glove compartment", "glove box latch", "glove box hinge", "glove box light", "glove box liner", "glove box damper", "glove box lock cylinder", "steering column cover", "steering column shroud", "knee bolster", "dash insulator", "dash mat", "dash cover", "dash cap", "dash pad", "interior sound deadening", "interior insulation", "heat shield", "sound absorber", "sound dampening", "acoustic material", "interior trim panel", "interior trim piece", "interior molding", "cup holder", "bottle holder", "beverage holder", "storage bin", "storage compartment", "storage pocket", "cigarette lighter", "power outlet", "USB port", "auxiliary port", "gauge face", "gauge overlay", "gauge pod", "gauge pillar", "gauge mount", "gauge bracket"],
    
    "interior_electrical": ["radio", "stereo", "speaker", "amplifier", "cd player", "antenna", "climate control", "power window switch", "door lock switch", "mirror switch", "seat switch", "infotainment system", "navigation system", "GPS", "head unit", "stereo receiver", "satellite radio", "AM/FM tuner", "bluetooth module", "aux input", "USB port", "media player", "CD changer", "DVD player", "rear entertainment system", "rear screen", "backup camera", "backup monitor", "reverse camera", "front camera", "360 camera", "surround view camera", "dash cam", "dashboard camera", "speaker wire", "speaker adapter", "speaker harness", "speaker bracket", "speaker grill", "speaker cover", "tweeter", "midrange speaker", "woofer", "subwoofer", "amplifier", "amp", "sound processor", "equalizer", "crossover", "audio control module", "radio antenna", "antenna mast", "antenna base", "antenna mount", "antenna adapter", "antenna cable", "power window motor", "power window regulator", "window switch", "window control", "master window switch", "power door lock", "door lock actuator", "door lock switch", "door lock relay", "door lock solenoid", "door lock control module", "keyless entry", "keyless entry module", "keyless entry receiver", "remote key", "key fob", "remote transmitter", "remote receiver", "power mirror", "mirror motor", "mirror actuator", "mirror switch", "mirror control", "mirror control module", "mirror heater", "heated mirror", "mirror defogger", "power seat", "seat motor", "seat switch", "seat control", "seat control module", "seat position sensor", "seat memory", "seat memory module", "seat heater", "seat cooler", "heated seat", "ventilated seat", "seat temperature sensor", "seat heat pad", "seat cooling pad", "seat occupancy sensor", "seat weight sensor", "airbag sensor", "seat belt sensor", "instrument cluster", "gauge cluster", "digital speedometer", "analog speedometer", "tachometer", "fuel gauge", "temperature gauge", "oil pressure gauge", "boost gauge", "vacuum gauge", "voltmeter", "ammeter", "clock", "warning light", "indicator light", "dash light", "dashboard light", "dimmer switch", "light switch", "dome light", "map light", "reading light", "courtesy light", "trunk light", "engine compartment light", "glove box light", "door light", "sunroof switch", "sunroof motor", "sunroof control", "sunroof sensor", "cruise control switch", "cruise control module", "cruise control actuator", "adaptive cruise control", "lane departure warning", "lane keep assist", "blind spot monitoring", "collision warning", "parking sensor", "parking aid", "parking assist", "backup sensor", "radar sensor", "ultrasonic sensor", "OBD port", "diagnostic port", "data link connector", "diagnostic connector", "interior wiring harness", "door wiring harness", "seat wiring harness", "dash wiring harness", "body control module", "BCM", "interior control module", "ICM", "electronic control unit", "ECU", "ignition switch", "start button", "push button start"],
    
    "interior_climate": ["heater core", "ac compressor", "ac condenser", "ac evaporator", "ac hose", "ac accumulator", "ac orifice tube", "ac expansion valve", "blower motor", "blower resistor", "heater valve", "heater hose", "climate control", "HVAC system", "HVAC control", "HVAC module", "HVAC head", "HVAC controller", "automatic climate control", "manual climate control", "temperature control", "temperature blend door", "blend door actuator", "mode door actuator", "vent door actuator", "air mix door", "air distribution door", "recirculation door", "recirculation actuator", "heater control valve", "heater control", "AC control", "air conditioning control", "AC switch", "AC relay", "AC compressor clutch", "AC pressure switch", "AC pressure sensor", "AC high pressure switch", "AC low pressure switch", "AC pressure relief valve", "AC receiver drier", "AC dryer", "AC condenser", "AC condenser fan", "AC evaporator", "AC evaporator temperature sensor", "AC evaporator pressure sensor", "cabin air filter", "pollen filter", "dust filter", "activated carbon filter", "HEPA filter", "blower motor", "blower fan", "blower wheel", "blower cage", "blower motor resistor", "blower motor regulator", "blower control module", "blower speed control", "blower relay", "blower motor wiring harness", "heater core", "heater box", "heater housing", "heater case", "heater plenum", "heater duct", "heater tube", "heater pipe", "heater hose", "heater valve", "heater control valve", "cooling system", "radiator", "radiator fan", "auxiliary fan", "auxiliary cooling fan", "coolant reservoir", "coolant tank", "coolant bottle", "expansion tank", "overflow tank", "recovery tank", "coolant level sensor", "coolant temperature sensor", "air vent", "dashboard vent", "vent duct", "vent tube", "vent hose", "vent nozzle", "vent diffuser", "vent bezel", "vent louver", "vent slat", "vent control", "defroster vent", "defogger vent", "HVAC housing", "HVAC case", "HVAC plenum", "HVAC box", "HVAC mounting bracket", "HVAC seal", "HVAC gasket", "HVAC air filter housing", "refrigerant", "refrigerant oil", "AC dye", "AC leak detector", "AC service port", "AC service valve", "AC line", "AC pipe", "AC repair kit", "AC recharge kit", "AC manifold", "AC gauge", "temperature sensor", "ambient temperature sensor", "interior temperature sensor", "sunload sensor", "humidity sensor", "climate control head", "climate control panel", "climate control unit", "climate control display", "dual zone climate control", "triple zone climate control", "quad zone climate control", "rear climate control", "rear AC", "rear heater", "auxiliary heater", "auxiliary air conditioner", "auxiliary blower", "auxiliary climate control", "heating element", "seat heater", "seat cooler", "steering wheel heater", "heated steering wheel"],
    
    # Lighting
    "lighting": ["headlight", "tail light", "fog light", "turn signal", "marker light", "brake light", "reverse light", "license plate light", "dome light", "map light", "headlight bulb", "tail light bulb", "headlamp", "taillight", "headlight assembly", "tail light assembly", "headlight housing", "tail light housing", "headlight lens", "tail light lens", "headlight cover", "tail light cover", "headlight bezel", "tail light bezel", "headlight trim", "tail light trim", "headlight bracket", "tail light bracket", "headlight mount", "tail light mount", "headlight module", "tail light module", "headlight switch", "headlight relay", "headlight wiring harness", "tail light wiring harness", "headlight socket", "tail light socket", "headlight connector", "tail light connector", "headlight pigtail", "tail light pigtail", "headlight bulb", "tail light bulb", "LED headlight", "LED tail light", "HID headlight", "HID kit", "xenon headlight", "xenon bulb", "halogen headlight", "halogen bulb", "projector headlight", "projector lens", "reflector headlight", "high beam", "low beam", "daytime running light", "DRL", "fog light", "fog lamp", "fog light assembly", "fog light housing", "fog light lens", "fog light cover", "fog light bezel", "fog light bracket", "fog light mount", "fog light bulb", "fog light switch", "fog light relay", "fog light wiring harness", "turn signal", "turn signal light", "turn signal assembly", "turn signal housing", "turn signal lens", "turn signal cover", "turn signal socket", "turn signal bulb", "turn signal switch", "turn signal relay", "turn signal flasher", "hazard light", "hazard switch", "side marker", "side marker light", "side marker assembly", "side marker lens", "side marker bulb", "corner light", "corner marker", "parking light", "brake light", "third brake light", "high mount stop light", "HMSL", "center high mount stop light", "CHMSL", "stop light", "backup light", "reverse light", "backup lamp", "reverse lamp", "backup light assembly", "backup light lens", "backup light bulb", "backup light switch", "license plate light", "tag light", "license plate lamp", "license lamp", "license plate light assembly", "license plate light bulb", "license plate light housing", "dome light", "courtesy light", "interior light", "map light", "reading light", "trunk light", "cargo light", "underhood light", "glove box light", "door light", "door courtesy light", "visor light", "vanity light", "step light", "puddle light", "halo light", "angel eye", "light bar", "LED bar", "off-road light", "spot light", "driving light", "work light", "auxiliary light", "emergency light", "strobe light", "warning light", "beacon light", "amber light", "clearance light", "marker light", "cab light", "roof light", "tailgate light", "light bulb", "LED bulb", "HID bulb", "xenon bulb", "halogen bulb", "incandescent bulb", "light socket", "light harness", "light wiring", "light controller", "light module", "light housing", "light lens", "light cover", "light gasket", "light seal", "headlight adjuster", "headlight adjustment screw", "headlight aiming kit", "headlight alignment", "headlight restoration kit", "headlight polish", "headlight cleaner", "headlight protector", "headlight guard", "light tint", "light film", "smoked light", "light cover", "light overlay", "light trim", "light surround", "sequential light", "sequential turn signal", "switchback LED", "RGB light", "color changing light", "light bar mount", "light bar bracket", "light bracket", "light mount", "light pod", "light kit", "light conversion kit", "HID conversion kit", "LED conversion kit", "headlight upgrade", "tail light upgrade", "lighting upgrade"],
    
    # Electrical
    "electrical": ["battery", "alternator", "starter", "relay", "fuse", "fuse box", "junction box", "wiring harness", "wire harness", "sensor", "switch", "computer", "control module", "control module", "ecu", "ecm", "pcm", "battery terminal", "battery cable", "battery clamp", "battery hold down", "battery tray", "battery box", "battery cover", "battery insulator", "battery mat", "battery charger", "battery tender", "battery maintainer", "battery jump starter", "battery booster", "battery tester", "battery isolator", "battery disconnect", "battery cut off switch", "battery monitor", "lithium battery", "AGM battery", "deep cycle battery", "gel cell battery", "lead acid battery", "car battery", "truck battery", "marine battery", "motorcycle battery", "powersports battery", "RV battery", "starting battery", "dual battery", "auxiliary battery", "backup battery", "starter battery", "cranking battery", "reserve battery", "alternator", "alternator pulley", "alternator belt", "alternator bracket", "alternator mounting kit", "alternator bearing", "alternator brush", "alternator regulator", "alternator rectifier", "alternator diode", "alternator slip ring", "alternator rotor", "alternator stator", "alternator cooling fan", "high output alternator", "heavy duty alternator", "performance alternator", "rebuilt alternator", "remanufactured alternator", "starter", "starter motor", "starter solenoid", "starter relay", "starter drive", "starter bendix", "starter pinion", "starter armature", "starter commutator", "starter brush", "starter field coil", "high torque starter", "mini starter", "gear reduction starter", "starter shim", "starter heat shield", "starter mounting kit", "rebuilt starter", "remanufactured starter", "wire", "wiring", "electrical wire", "primary wire", "ground wire", "power wire", "battery wire", "ignition wire", "spark plug wire", "wire loom", "wire conduit", "wire sleeve", "wire wrap", "wire cover", "wire protector", "wire connector", "wire terminal", "wire harness", "wire connector kit", "wire splice", "wire crimp", "wire stripper", "wire crimper", "wiring harness", "wiring loom", "wiring kit", "wiring connector", "wiring adapter", "wiring terminal", "wiring repair kit", "electrical tape", "electrical connector", "electrical terminal", "electrical splice", "electrical junction", "electrical box", "electrical enclosure", "electrical panel", "circuit breaker", "fuse", "fuse holder", "fuse block", "fuse box", "fuse relay box", "fuse panel", "fuse kit", "mini fuse", "blade fuse", "ATO fuse", "ATC fuse", "maxi fuse", "micro fuse", "cartridge fuse", "ceramic fuse", "glass fuse", "thermal fuse", "circuit breaker", "reset breaker", "relay", "relay socket", "relay harness", "relay kit", "relay panel", "relay board", "power relay", "starter relay", "fuel pump relay", "cooling fan relay", "blower motor relay", "horn relay", "headlight relay", "flasher relay", "turn signal relay", "fog light relay", "AC relay", "main relay", "control relay", "solid state relay", "time delay relay", "switch", "toggle switch", "rocker switch", "push button switch", "slide switch", "rotary switch", "momentary switch", "pressure switch", "temperature switch", "limit switch", "proximity switch", "float switch", "reed switch", "micro switch", "tactile switch", "power switch", "ignition switch", "starter switch", "kill switch", "light switch", "dimmer switch", "headlight switch", "fog light switch", "turn signal switch", "wiper switch", "washer switch", "cruise control switch", "window switch", "door lock switch", "mirror switch", "seat switch", "power seat switch", "power window switch", "hazard switch", "horn switch", "brake light switch", "backup light switch", "neutral safety switch", "clutch safety switch", "oil pressure switch", "AC pressure switch", "radiator fan switch", "battery disconnect switch", "switch panel", "switch box", "switch plate", "switch cover", "switch bezel", "switch housing", "sensor", "engine sensor", "transmission sensor", "oxygen sensor", "O2 sensor", "mass air flow sensor", "MAF sensor", "manifold absolute pressure sensor", "MAP sensor", "throttle position sensor", "TPS sensor", "crankshaft position sensor", "camshaft position sensor", "knock sensor", "coolant temperature sensor", "intake air temperature sensor", "fuel temperature sensor", "oil pressure sensor", "oil temperature sensor", "oil level sensor", "vehicle speed sensor", "wheel speed sensor", "ABS sensor", "traction control sensor", "yaw sensor", "accelerometer", "gyroscope", "g-force sensor", "impact sensor", "crash sensor", "airbag sensor", "occupant sensor", "seat weight sensor", "seat belt sensor", "parking sensor", "backup sensor", "reverse sensor", "rain sensor", "light sensor", "sun sensor", "humidity sensor", "temperature sensor", "ambient temperature sensor", "evaporator temperature sensor", "exhaust gas temperature sensor", "EGT sensor", "EGR temperature sensor", "fuel level sensor", "fuel pressure sensor", "barometric pressure sensor", "pressure sensor", "position sensor", "potentiometer", "TPMS sensor", "tire pressure sensor", "tire pressure monitoring sensor", "exhaust pressure sensor", "boost pressure sensor", "vacuum sensor", "pressure transducer", "pedal position sensor", "throttle pedal sensor", "brake pedal sensor", "clutch pedal sensor", "height sensor", "ride height sensor", "suspension sensor", "level sensor", "altitude sensor", "voltage sensor", "current sensor", "hall effect sensor", "proximity sensor", "sensor connector", "sensor harness", "sensor adapter", "sensor mount", "sensor bracket", "solenoid", "idle air control solenoid", "IAC solenoid", "EGR solenoid", "purge solenoid", "EVAP solenoid", "VVT solenoid", "variable valve timing solenoid", "transmission solenoid", "shift solenoid", "lockup solenoid", "transfer case solenoid", "4WD solenoid", "differential lock solenoid", "door lock solenoid", "trunk release solenoid", "fuel injector solenoid", "vacuum solenoid", "boost control solenoid", "wastegate solenoid", "blow off valve solenoid", "PCV solenoid", "air intake solenoid", "starter solenoid", "horn", "horn relay", "horn button", "horn contact", "horn wire", "horn connector", "air horn", "electric horn", "dual horn", "high tone horn", "low tone horn", "horn kit", "siren", "alarm siren", "backup alarm", "reverse alarm", "backup beeper", "reverse beeper", "alarm", "car alarm", "security alarm", "alarm system", "anti-theft system", "immobilizer", "security system", "remote starter", "remote start", "keyless entry", "keyless go", "proximity key", "smart key", "key fob", "remote key", "transmitter", "receiver", "antenna", "radio antenna", "GPS antenna", "satellite antenna", "cellular antenna", "WiFi antenna", "Bluetooth antenna", "AM/FM antenna", "TV antenna", "antenna mount", "antenna adapter", "antenna cable", "battery cable", "battery terminal", "ground wire", "ground strap", "ground cable", "grounding kit", "battery cable kit", "electrical kit", "digital multimeter", "circuit tester", "voltage tester", "test light", "jumper cables", "jumper wire", "jumper lead", "electrical repair kit", "wire repair kit", "solder", "soldering iron", "heat shrink", "heat shrink tubing", "wire loom", "wire conduit", "wire sleeve", "wire protection", "wire tie", "zip tie", "cable tie", "electrical tape", "anti-corrosion spray", "terminal protector", "dielectric grease", "electrical cleaner", "contact cleaner", "battery cleaner", "battery terminal cleaner", "electrical contact enhancer"],
    
    "electrical_modules": ["engine control module", "ecm", "powertrain control module", "pcm", "body control module", "bcm", "transmission control module", "tcm", "abs control module", "ebcm", "airbag control module", "srs module", "electronic control unit", "ECU", "engine control unit", "engine computer", "engine management computer", "engine management system", "EMS", "powertrain control unit", "PCU", "electronic control module", "vehicle control module", "VCM", "engine brain", "central computer", "main computer", "central processing unit", "CPU", "digital engine management", "digital motor electronics", "DME", "Motronic", "engine management", "fuel injection computer", "injection control unit", "ignition control module", "spark control module", "SCM", "injector driver module", "IDM", "glow plug control module", "GPCM", "diesel control unit", "DCU", "diesel control module", "transmission control unit", "automatic transmission computer", "valve body controller", "valve body solenoid pack", "transmission brain", "shift control module", "transfer case control module", "transfer case module", "TCCM", "four wheel drive control module", "4WD control module", "AWD control module", "all wheel drive control module", "anti-lock brake system module", "anti-lock brake control unit", "brake control module", "BCM", "electronic brake control module", "EBCM", "hydraulic control unit", "HCU", "electronic stability control module", "ESC module", "traction control module", "TCM", "vehicle stability assist module", "VSA module", "vehicle stability control module", "VSC module", "dynamic stability control module", "DSC module", "electronic brakeforce distribution module", "EBD module", "brake assist module", "roll stability control module", "RSC module", "active suspension control module", "air suspension module", "adaptive suspension module", "electronic damping control module", "EDC module", "active body control module", "ABC module", "electronic air suspension control module", "EAS module", "ride control module", "height control module", "level control module", "supplemental restraint system module", "SRS module", "airbag control unit", "ACU", "airbag control module", "air bag computer", "air bag electronic crash sensor", "occupant classification module", "OCM", "occupant detection module", "occupant position detection module", "OPDM", "seat weight sensor module", "passenger presence module", "PPM", "body control unit", "body electronics module", "body electrical control module", "convenience control module", "interior control module", "central control module", "general electronic module", "GEM", "smart junction box", "SJB", "totally integrated power module", "TIPM", "interior electronic module", "function control module", "FCM", "generic electronic module", "integrated control module", "central gateway module", "CGM", "data link connector module", "DLC module", "communication control module", "climate control module", "automatic temperature control module", "HVAC control module", "electronic climate control module", "heating, ventilation, and air conditioning module", "air conditioning control module", "instrument cluster", "instrument panel cluster", "IPC", "dashboard control module", "gauge cluster", "meter control module", "combination meter", "console control module", "memory seat module", "power seat module", "heated seat module", "seat control module", "seat memory module", "SMM", "power door module", "door control module", "door function module", "door lock control module", "keyless entry module", "remote entry module", "remote keyless entry module", "RKE module", "remote start module", "immobilizer module", "anti-theft module", "security module", "alarm module", "security control module", "passive entry module", "passive start module", "remote access module", "sunroof control module", "moonroof control module", "convertible top module", "convertible roof module", "folding roof module", "top control module", "roof function module", "power top module", "power window module", "window control module", "window lift module", "power mirror module", "mirror control module", "mirror adjustment module", "mirror memory module", "parking assist module", "park aid module", "backup sensor module", "parking sensor module", "PDC module", "sonar module", "ultrasonic module", "radio module", "audio module", "amplifier module", "sound module", "audio control module", "entertainment module", "multimedia module", "infotainment module", "navigation module", "GPS module", "display module", "head unit module", "stereo module", "Bluetooth module", "telematics module", "OnStar module", "cellular module", "wireless communication module", "hands free module", "phone module", "battery control module", "battery management system", "BMS", "hybrid control module", "HCM", "hybrid system control module", "electric vehicle control module", "EVCM", "EV module", "motor control module", "MCM", "inverter module", "drive motor control module", "DMCM", "high voltage battery module", "HVBM", "electronic power steering module", "EPS module", "steering control module", "SCM", "steering angle sensor module", "SAS module", "lane keeping module", "lane departure module", "lane assist module", "adaptive cruise control module", "ACC module", "radar module", "radar sensor module", "distance control module", "DCM", "collision avoidance module", "collision warning module", "forward collision module", "blind spot module", "blind spot detection module", "BSD module", "trailer module", "trailer brake control module", "TBCM", "trailer connector module", "module bracket", "module mount", "module connector", "module harness", "module cover", "module housing", "module seal", "module gasket", "module relay", "module fuse", "control module programming", "ECU programming", "ECU flashing", "ECU tuning", "PCM programming", "PCM flashing", "TCM programming", "TCM flashing", "BCM programming", "module reset", "module relearn", "module adaptation", "module coding"],
    
    "electrical_switches": ["power window switch", "door lock switch", "mirror switch", "seat switch", "headlight switch", "wiper switch", "turn signal switch", "ignition switch", "brake light switch", "cruise control switch", "switch", "toggle switch", "rocker switch", "push button switch", "slide switch", "rotary switch", "momentary switch", "pressure switch", "temperature switch", "limit switch", "proximity switch", "float switch", "reed switch", "micro switch", "tactile switch", "power switch", "ignition switch", "starter switch", "kill switch", "light switch", "dimmer switch", "headlight switch", "fog light switch", "turn signal switch", "wiper switch", "washer switch", "cruise control switch", "window switch", "door lock switch", "mirror switch", "seat switch", "power seat switch", "power window switch", "hazard switch", "horn switch", "brake light switch", "backup light switch", "neutral safety switch", "clutch safety switch", "oil pressure switch", "AC pressure switch", "radiator fan switch", "battery disconnect switch", "switch panel", "switch box", "switch plate", "switch cover", "switch bezel", "switch housing", "ignition starter switch", "combination switch", "multifunction switch", "steering column switch", "column switch", "turn signal lever", "wiper lever", "headlight lever", "blinker switch", "windshield wiper switch", "windshield washer switch", "dome light switch", "interior light switch", "map light switch", "reading light switch", "trunk light switch", "underhood light switch", "glove box light switch", "door jamb switch", "door ajar switch", "door open switch", "hood switch", "trunk switch", "tailgate switch", "hatch switch", "power tailgate switch", "power liftgate switch", "power sliding door switch", "sunroof switch", "moonroof switch", "convertible top switch", "top control switch", "mirror adjustment switch", "mirror fold switch", "mirror heat switch", "window lockout switch", "child lock switch", "power lock switch", "central locking switch", "power door lock switch", "trunk release switch", "hood release switch", "fuel door release switch", "parking brake switch", "emergency brake switch", "drive mode switch", "economy mode switch", "sport mode switch", "winter mode switch", "snow mode switch", "off-road mode switch", "four wheel drive switch", "4WD switch", "all wheel drive switch", "AWD switch", "differential lock switch", "diff lock switch", "traction control switch", "TCS switch", "stability control switch", "ESC switch", "VSC switch", "hill descent control switch", "HDC switch", "hill start assist switch", "HSA switch", "downhill assist control switch", "DAC switch", "trailer brake control switch", "trailer gain switch", "trailer mode switch", "tow/haul mode switch", "exhaust brake switch", "engine brake switch", "idle control switch", "idle up switch", "fast idle switch", "throttle control switch", "overdrive switch", "overdrive cancel switch", "gear selector switch", "gear shift switch", "transmission shift switch", "PRNDL switch", "park neutral position switch", "PNP switch", "clutch position switch", "clutch pedal switch", "clutch start switch", "brake pedal switch", "brake light switch", "cruise control switch", "resume switch", "set switch", "accelerate switch", "decelerate switch", "coast switch", "cancel switch", "adaptive cruise control switch", "ACC switch", "following distance switch", "gap control switch", "lane departure warning switch", "LDW switch", "lane keeping assist switch", "LKA switch", "blind spot monitoring switch", "BSM switch", "cross traffic alert switch", "CTA switch", "automatic high beam switch", "high beam assist switch", "auto high beam switch", "heated seat switch", "seat heater switch", "seat cooler switch", "ventilated seat switch", "lumbar support switch", "seat back adjuster switch", "seat cushion adjuster switch", "seat position memory switch", "heated steering wheel switch", "steering wheel heater switch", "climate control switch", "air conditioning switch", "AC switch", "heater switch", "fan speed switch", "temperature control switch", "dual zone switch", "rear defrost switch", "rear defroster switch", "front defrost switch", "front defroster switch", "windshield defrost switch", "recirculation switch", "fresh air switch", "maximum cooling switch", "max AC switch", "maximum heating switch", "max heat switch", "rear climate control switch", "rear AC switch", "rear heat switch", "air flow mode switch", "vent switch", "floor vent switch", "defrost vent switch", "heated mirror switch", "mirror defrost switch", "rear wiper switch", "rear washer switch", "intermittent wiper switch", "variable intermittent wiper switch", "rain sensing wiper switch", "automatic wiper switch", "automatic headlight switch", "auto light switch", "automatic lamp switch", "daytime running light switch", "DRL switch", "foglamp switch", "fog light switch", "auxiliary light switch", "driving light switch", "spot light switch", "interior dimmer switch", "instrument panel dimmer switch", "gauge dimmer switch", "dash light dimmer switch", "ambient light switch", "mood light switch", "parking aid switch", "parking sensor switch", "backup sensor switch", "sonar switch", "power outlet switch", "cigarette lighter switch", "auxiliary power switch", "USB power switch", "radio switch", "audio switch", "sound system switch", "media switch", "music switch", "stereo switch", "volume switch", "tuning switch", "seek switch", "scan switch", "preset switch", "band switch", "source switch", "mode switch", "mute switch", "Bluetooth switch", "phone switch", "voice command switch", "navigation switch", "GPS switch", "destination switch", "menu switch", "settings switch", "information switch", "info switch", "trip switch", "odometer switch", "display switch", "screen switch", "monitor switch", "camera switch", "view switch", "backup camera switch", "reverse camera switch", "horn switch", "power take-off switch", "PTO switch", "work light switch", "beacon light switch", "warning light switch", "emergency light switch", "strobe light switch", "auxiliary equipment switch", "auxiliary function switch", "power inverter switch", "power converter switch", "accessory switch", "remote control switch", "switch panel", "switch cluster", "switch assembly", "switch housing", "switch trim", "switch bezel", "switch cover", "switch cap", "switch knob", "switch lever", "switch button", "switch contact", "switch connector", "switch harness", "switch wiring", "switch bracket", "switch mount", "switch gasket", "switch seal", "switch boot", "switch repair kit", "switch replacement", "aftermarket switch", "OEM switch"],
    
    # Wheels and tires
    "wheel": ["wheel", "rim", "alloy wheel", "steel wheel", "wheel cover", "hub cap", "center cap", "lug nut", "wheel stud", "wheel lock", "wheel weight", "custom wheel", "aftermarket wheel", "OEM wheel", "factory wheel", "aluminum wheel", "chrome wheel", "painted wheel", "polished wheel", "machined wheel", "forged wheel", "cast wheel", "steel wheel", "split rim wheel", "multi-piece wheel", "two-piece wheel", "three-piece wheel", "billet wheel", "beadlock wheel", "wire wheel", "slotted wheel", "mesh wheel", "spoke wheel", "mag wheel", "rally wheel", "modular wheel", "directional wheel", "staggered wheels", "wheel and tire package", "wheel and tire set", "wheel adapter", "wheel spacer", "wheel hub centric ring", "wheel center cap", "wheel trim ring", "beauty ring", "wheel spinner", "knock-off spinner", "wheel cover", "full wheel cover", "hubcap", "center cap", "wheel emblem", "wheel logo", "wheel lug nut", "wheel lug bolt", "wheel stud", "lug nut cover", "wheel lock", "wheel lock kit", "wheel lock key", "tuner lug nut", "spline drive lug nut", "wheel weight", "wheel balancing weight", "stick-on wheel weight", "clip-on wheel weight", "wheel balancer", "wheel balancing machine", "wheel alignment", "wheel alignment tool", "wheel alignment kit", "wheel simulator", "dually wheel simulator", "wheel liner", "wheel well liner", "curb guard", "curb alert", "rim protector", "rim guard", "wheel repair kit", "wheel restoration kit", "wheel paint", "wheel cleaner", "wheel polish", "wheel sealant", "wheel wax", "wheel brush", "spoke brush", "wheel coating", "wheel protectant", "wheel restoration", "wheel refinishing", "wheel straightening", "wheel repair", "wheel bearing", "wheel bearing kit", "wheel bearing assembly", "wheel bearing hub", "wheel bearing race", "wheel bearing seal", "wheel bearing grease", "wheel bearing tool", "wheel bearing press", "wheel installation kit", "wheel bolt pattern gauge", "wheel fitment guide", "wheel size chart", "specialty wheel", "racing wheel", "drift wheel", "drag wheel", "off-road wheel", "rock crawler wheel", "mud terrain wheel", "all terrain wheel", "street wheel", "luxury wheel", "performance wheel", "vintage wheel", "classic wheel", "retro wheel", "wheel cover", "wheel skin", "wheel overlay", "wheel accent", "wheel inserts", "wheel dust shield", "dust cap", "grease cap", "bearing protector", "wheel well trim", "wheel arch trim", "fender trim", "fender flare", "wheel opening molding", "daisy wheel", "snowflake wheel", "turbine wheel", "star wheel", "split five spoke wheel", "five spoke wheel", "six spoke wheel", "seven spoke wheel", "eight spoke wheel", "ten spoke wheel", "fifteen spoke wheel", "multi-spoke wheel", "wheel size", "wheel diameter", "wheel width", "wheel offset", "wheel backspacing", "wheel bolt pattern", "wheel PCD", "wheel pitch circle diameter", "wheel lug pattern", "wheel bore size", "wheel centerbore", "wheel torque specification", "wheel load rating", "wheel weight rating", "whitewall wheel", "redline wheel", "goldline wheel", "wheel barrel", "wheel face", "wheel lip", "wheel flange", "wheel disc", "wheel shell", "wheel hoop", "wheel spokes", "wheel hub", "wheel valve stem", "wheel valve stem cap", "wheel TPMS sensor", "wheel pressure sensor", "tire pressure monitoring system", "TPMS", "wheel sensor", "TPMS tool", "TPMS programming tool", "TPMS reset tool", "TPMS service kit", "TPMS valve stem", "TPMS valve core", "TPMS sensor battery", "TPMS rebuild kit", "TPMS sensor service kit"],
    
    "tire": ["tire", "all season tire", "winter tire", "summer tire", "performance tire", "spare tire", "tire valve", "tire pressure sensor", "tpms sensor", "mud terrain tire", "all terrain tire", "highway terrain tire", "street tire", "track tire", "racing tire", "drag tire", "drift tire", "off-road tire", "rock crawler tire", "snow tire", "ice tire", "studded tire", "studless tire", "all-weather tire", "touring tire", "grand touring tire", "ultra high performance tire", "UHP tire", "high performance tire", "economy tire", "fuel efficient tire", "low rolling resistance tire", "run flat tire", "self-sealing tire", "tubeless tire", "tube type tire", "inner tube", "radial tire", "bias ply tire", "bias belted tire", "crossply tire", "whitewall tire", "blackwall tire", "redline tire", "raised white letter tire", "outline white letter tire", "OWL tire", "RWL tire", "directional tire", "asymmetric tire", "symmetric tire", "low profile tire", "high profile tire", "passenger tire", "light truck tire", "LT tire", "P-metric tire", "Euro-metric tire", "commercial tire", "trailer tire", "ST tire", "temporary spare tire", "donut spare", "full size spare", "matching spare", "space saver spare", "compact spare", "spare tire carrier", "spare tire mount", "spare tire cover", "spare tire lock", "new tire", "used tire", "retread tire", "recapped tire", "blemished tire", "seconds tire", "tire size", "tire width", "tire profile", "tire aspect ratio", "tire height", "tire diameter", "tire construction", "tire speed rating", "tire load index", "tire load range", "tire ply rating", "tire pressure", "tire inflation", "tire air pressure", "recommended tire pressure", "maximum tire pressure", "minimum tire pressure", "tire rotation", "tire balancing", "tire mounting", "tire dismounting", "tire repair", "tire patch", "tire plug", "tire plug patch", "tire sealant", "tire inflation sealant", "tire bead sealer", "tire lubricant", "tire mounting lubricant", "tire shine", "tire dressing", "tire cleaner", "tire black", "tire wet look", "tire protectant", "tire gauge", "tire pressure gauge", "digital tire gauge", "dial tire gauge", "stick tire gauge", "tire depth gauge", "tread depth gauge", "tire tread wear indicator", "tire wear bars", "tire aging", "tire date code", "tire DOT code", "tire sidewall", "tire tread", "tire shoulder", "tire bead", "tire construction", "tire compound", "tire rubber", "tire casing", "tire carcass", "tire belt", "tire cord", "tire ply", "tire valve", "tire valve stem", "tire valve cap", "tire valve core", "tire valve extension", "tire valve tool", "tire iron", "tire lever", "tire spoon", "tire changer", "tire machine", "tire spreader", "tire bead breaker", "tire bead blaster", "tire inflator", "tire air compressor", "portable tire inflator", "tire pump", "bicycle tire pump", "foot tire pump", "tire deflator", "tire pressure monitor", "tire pressure monitoring system", "TPMS", "tire chains", "snow chains", "tire cable chains", "tire socks", "tire boots", "tire covers", "tire storage rack", "tire storage bag", "tire tote", "seasonal tire storage", "tire rotation pattern", "tire siping", "tire grooving", "tire studs", "tire stud installation", "tire balance beads", "tire balancing compound", "wheel weight", "tire pressure label", "tire information placard", "tire buyer's guide", "tire warranty", "tire road hazard warranty", "tire manufacturer", "tire brand", "tire model", "tire line", "tire recall", "DOT approved tire", "tire and wheel package", "plus sizing", "tire upsizing", "tire downsizing", "tire fitment guide", "tire size calculator", "tire comparison tool", "winter tire changeover", "seasonal tire change", "tire service", "tire installation", "tire disposal", "tire recycling", "retreading", "recapping"],
    
    # Miscellaneous
    "fluid": ["oil", "coolant", "antifreeze", "transmission fluid", "brake fluid", "power steering fluid", "windshield washer fluid", "refrigerant", "freon", "engine oil", "motor oil", "synthetic oil", "conventional oil", "high mileage oil", "diesel oil", "racing oil", "marine oil", "oil additive", "oil treatment", "oil stabilizer", "oil flush", "oil system cleaner", "oil stop leak", "oil consumption fix", "oil viscosity", "multi-grade oil", "single grade oil", "5W-30", "10W-30", "5W-20", "0W-20", "15W-40", "20W-50", "oil weight", "oil grade", "oil specification", "oil certification", "API oil", "ILSAC oil", "ACEA oil", "OEM oil", "coolant", "antifreeze", "engine coolant", "radiator fluid", "cooling system fluid", "extended life coolant", "long life coolant", "universal coolant", "Asian coolant", "European coolant", "OEM coolant", "coolant concentrate", "pre-diluted coolant", "coolant additive", "coolant system flush", "coolant stop leak", "coolant color", "red coolant", "green coolant", "blue coolant", "yellow coolant", "orange coolant", "purple coolant", "pink coolant", "silicate coolant", "OAT coolant", "HOAT coolant", "hybrid coolant", "coolant test strip", "coolant hydrometer", "coolant protection level", "coolant freeze protection", "coolant boil protection", "transmission fluid", "automatic transmission fluid", "ATF", "manual transmission fluid", "MTF", "CVT fluid", "continuously variable transmission fluid", "dual clutch transmission fluid", "DCT fluid", "synthetic transmission fluid", "conventional transmission fluid", "transmission fluid additive", "transmission flush", "transmission fluid change", "transmission fluid filter", "transmission cooling", "transmission stop leak", "Dexron", "Mercon", "Type F", "ATF+4", "CVT-NS2", "T-IV", "SP-IV", "brake fluid", "DOT 3", "DOT 4", "DOT 5", "DOT 5.1", "silicone brake fluid", "synthetic brake fluid", "brake fluid flush", "brake fluid change", "brake fluid tester", "brake fluid moisture test", "brake system bleeder", "brake fluid color", "brake fluid contamination", "brake fluid boiling point", "power steering fluid", "power steering fluid flush", "power steering system cleaner", "power steering stop leak", "power steering fluid change", "synthetic power steering fluid", "universal power steering fluid", "OEM power steering fluid", "windshield washer fluid", "summer washer fluid", "winter washer fluid", "all-season washer fluid", "de-icer washer fluid", "bug remover washer fluid", "rain repellent washer fluid", "concentrated washer fluid", "washer fluid tablet", "washer fluid additive", "refrigerant", "AC refrigerant", "R-134a", "R-1234yf", "R-12", "air conditioning refrigerant", "refrigerant oil", "refrigerant dye", "refrigerant leak detector", "refrigerant identifier", "refrigerant recovery", "refrigerant recycling", "refrigerant recharging", "PAG oil", "ester oil", "compressor oil", "freon", "differential fluid", "gear oil", "hypoid gear oil", "limited slip differential fluid", "LSD fluid", "axle fluid", "differential lube", "75W-90", "75W-140", "75W-85", "80W-90", "85W-140", "transfer case fluid", "4WD fluid", "AWD fluid", "power transfer unit fluid", "PTU fluid", "rear differential fluid", "front differential fluid", "hydraulic fluid", "hydraulic jack oil", "hydraulic system fluid", "hydraulic clutch fluid", "hydraulic lift fluid", "hydraulic pump oil", "fuel additive", "fuel system cleaner", "fuel injector cleaner", "fuel stabilizer", "octane booster", "cetane booster", "fuel treatment", "water remover", "gas treatment", "diesel treatment", "ethanol treatment", "lead substitute", "upper cylinder lubricant", "carburetor cleaner", "throttle body cleaner", "intake valve cleaner", "combustion chamber cleaner", "deposit control", "complete fuel system cleaner", "greases", "general purpose grease", "lithium grease", "moly grease", "wheel bearing grease", "chassis grease", "CV joint grease", "high temperature grease", "white lithium grease", "marine grease", "synthetic grease", "lubricant", "penetrating oil", "penetrating lubricant", "multi-purpose lubricant", "spray lubricant", "dry lubricant", "chain lubricant", "door hinge lubricant", "lock lubricant", "silicone lubricant", "graphite lubricant", "PTFE lubricant", "thread lubricant", "anti-seize compound", "sealant", "gasket maker", "thread sealant", "pipe sealant", "silicone sealant", "anaerobic sealant", "form-in-place gasket", "chemical gasket", "high temperature sealant", "water pump sealant", "oil pan sealant", "vacuum leak sealant", "radiator sealant", "block sealant", "head gasket sealant", "exhaust sealant", "windshield sealant", "adhesive", "thread locker", "epoxy", "super glue", "plastic adhesive", "metal adhesive", "rubber adhesive", "fabric adhesive", "vinyl adhesive", "carpet adhesive", "headliner adhesive", "emblem adhesive", "weatherstrip adhesive", "rearview mirror adhesive", "tape", "double-sided tape", "body molding tape", "emblem tape", "foam tape", "automotive tape", "high temperature tape", "duct tape", "electrical tape", "masking tape", "painters tape", "wire harness tape", "wax", "car wax", "paste wax", "liquid wax", "spray wax", "carnauba wax", "synthetic wax", "cleaner wax", "polish", "car polish", "paint polish", "metal polish", "chrome polish", "aluminum polish", "plastic polish", "headlight polish", "glass polish", "compound", "rubbing compound", "polishing compound", "cutting compound", "scratch remover", "swirl remover", "paint cleaner", "clay bar", "clay lubricant", "detailer", "quick detailer", "detail spray", "spray wax", "interior protectant", "vinyl protectant", "plastic protectant", "leather conditioner", "leather cleaner", "upholstery cleaner", "carpet cleaner", "glass cleaner", "wheel cleaner", "tire cleaner", "engine degreaser", "all purpose cleaner", "bug and tar remover", "chrome cleaner", "metal cleaner", "trim cleaner", "bumper cleaner"],
    
    "maintenance": ["oil filter", "air filter", "cabin filter", "fuel filter", "pcv valve", "spark plug", "wiper blade", "battery", "belt", "hose", "oil change", "oil change kit", "oil filter wrench", "oil drain plug", "oil drain plug gasket", "oil drain pan", "oil funnel", "oil filter housing", "oil filter housing gasket", "oil filter adapter", "oil filter adapter gasket", "oil pressure switch", "oil pressure sensor", "oil level sensor", "oil dipstick", "oil dipstick tube", "oil dipstick tube seal", "oil filler cap", "oil filler tube", "oil cooler", "oil cooler line", "oil cooler hose", "oil pump", "oil pump drive", "oil pump pickup tube", "oil pump pickup screen", "oil pan", "oil pan gasket", "oil pan drain plug", "oil pan baffle", "oil gallery plug", "oil passage", "oil return line", "oil separator", "oil catch can", "oil filter housing", "engine oil cooler", "air filter", "air filter housing", "air filter box", "air filter cover", "air filter lid", "air filter clamp", "air filter seal", "air filter gasket", "air filter element", "reusable air filter", "washable air filter", "high flow air filter", "performance air filter", "cold air intake", "short ram intake", "air intake resonator", "air intake tube", "air intake duct", "air intake hose", "air intake snorkel", "air box", "ram air", "cabin air filter", "cabin filter", "pollen filter", "dust filter", "activated carbon filter", "HEPA cabin filter", "cabin filter housing", "cabin filter cover", "cabin filter access panel", "cabin filter door", "cabin filter installation tool", "fuel filter", "fuel filter housing", "fuel filter bracket", "fuel filter mount", "in-line fuel filter", "canister fuel filter", "cartridge fuel filter", "spin-on fuel filter", "fuel filter socket", "fuel filter wrench", "fuel filter cap", "fuel filter bowl", "diesel fuel filter", "primary fuel filter", "secondary fuel filter", "fuel water separator", "fuel filter water drain", "fuel filter pressure regulator", "fuel filter check valve", "PCV valve", "positive crankcase ventilation valve", "PCV valve grommet", "PCV valve hose", "PCV valve elbow", "PCV system", "PCV breather", "PCV oil separator", "PCV filter", "PCV baffle", "crankcase ventilation", "engine ventilation", "spark plug", "spark plug wire", "spark plug boot", "spark plug tube", "spark plug tube seal", "spark plug gap tool", "spark plug socket", "spark plug thread chaser", "spark plug anti-seize", "spark plug dielectric grease", "iridium spark plug", "platinum spark plug", "double platinum spark plug", "copper spark plug", "performance spark plug", "racing spark plug", "cold spark plug", "hot spark plug", "ignition coil", "coil on plug", "ignition wire", "ignition cable", "distributor cap", "distributor rotor", "distributor", "ignition module", "ignition control module", "wiper blade", "wiper arm", "wiper motor", "wiper linkage", "wiper pivot", "wiper transmission", "wiper cowl", "wiper switch", "wiper relay", "wiper module", "wiper control module", "windshield washer pump", "washer fluid reservoir", "washer fluid cap", "washer fluid level sensor", "washer fluid filter", "washer fluid hose", "washer nozzle", "battery", "battery terminal", "battery cable", "battery hold down", "battery tray", "battery box", "battery insulator", "battery mat", "battery cover", "battery charger", "battery maintainer", "battery tender", "battery tester", "battery hydrometer", "battery load tester", "battery terminal cleaner", "battery terminal protector", "battery jump starter", "jumper cables", "belt", "serpentine belt", "drive belt", "accessory belt", "v-belt", "fan belt", "timing belt", "timing chain", "belt tensioner", "belt idler pulley", "belt routing diagram", "belt tool", "belt installation tool", "hose", "radiator hose", "upper radiator hose", "lower radiator hose", "bypass hose", "heater hose", "coolant hose", "vacuum hose", "fuel hose", "power steering hose", "brake hose", "transmission cooler hose", "oil cooler hose", "PCV hose", "emissions hose", "air intake hose", "turbo hose", "intercooler hose", "hose clamp", "hose connector", "hose adapter", "hose fitting", "hose coupling", "hose mender", "hose repair kit", "tune up", "tune up kit", "minor tune up", "major tune up", "ignition tune up", "engine tune up", "preventive maintenance", "scheduled maintenance", "maintenance schedule", "service interval", "service reminder", "service indicator reset", "maintenance reminder reset", "brake service", "brake pad replacement", "brake rotor replacement", "brake fluid flush", "brake bleeding", "brake caliper service", "wheel bearing service", "wheel alignment", "tire rotation", "tire balancing", "transmission service", "transmission fluid change", "transmission filter change", "differential service", "differential fluid change", "transfer case service", "transfer case fluid change", "cooling system service", "cooling system flush", "radiator service", "thermostat replacement", "water pump replacement", "timing belt service", "timing chain service", "valve adjustment", "valve clearance", "fuel system service", "fuel injector cleaning", "fuel system cleaning", "throttle body service", "intake service", "induction system cleaning", "emissions system service", "EGR cleaning", "exhaust system service", "catalytic converter service", "oxygen sensor replacement", "air filter service", "cabin filter service", "PCV system service", "spark plug replacement", "ignition system service", "battery service", "charging system service", "starting system service", "suspension service", "steering service", "power steering service", "drivetrain service", "axle service", "CV joint service", "u-joint service", "ball joint service", "tie rod end service", "idler arm service", "pitman arm service", "sway bar link service", "control arm bushing service", "shock absorber service", "strut service", "vehicle inspection", "multi-point inspection", "safety inspection", "state inspection", "emissions test", "diagnostic scan", "check engine light diagnosis", "warning light diagnosis", "trouble code diagnosis", "fluid level check", "fluid leak inspection", "belt inspection", "hose inspection", "tire inspection", "brake inspection", "suspension inspection", "steering inspection", "exhaust inspection", "light inspection", "wiper inspection", "maintenance schedule", "maintenance log", "service record", "service history", "maintenance tracker", "DIY maintenance", "routine maintenance", "preventive maintenance", "deferred maintenance", "maintenance free", "low maintenance", "high maintenance", "severe service maintenance", "normal service maintenance", "winter maintenance", "summer maintenance", "seasonal maintenance", "pre-trip maintenance", "off-road maintenance", "high mileage maintenance", "maintenance kit", "service kit", "master service kit", "scheduled maintenance kit"]
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
    "chevrolet": ["silverado", "camaro", "corvette", "malibu", "equinox", "tahoe", "suburban", "colorado", "traverse", "blazer", "impala", "spark", "trax", "bolt", "trailblazer", "cavalier", "cobalt", "cruze", "sonic", "aveo", "s10", "monte carlo", "nova", "el camino", "chevelle", "caprice", "bel air", "avalanche", "astro", "express", "ssr", "hhr", "biscayne", "delray", "deluxe", "fleetline", "styleline", "210", "150", "nomad", "kingswood", "parkwood", "brookwood", "corvair", "chevy ii", "laguna", "vega", "monza", "chevette", "citation", "celebrity"],
    
    "ford": ["f-150", "f150", "f-250", "f250", "f-350", "f350", "mustang", "explorer", "escape", "fusion", "focus", "edge", "expedition", "ranger", "bronco", "taurus", "maverick", "ecosport", "flex", "transit", "fiesta", "crown victoria", "five hundred", "freestyle", "excursion", "e-series", "e150", "e250", "e350", "thunderbird", "probe", "contour", "tempo", "escort", "gt", "model a", "model t", "fairlane", "falcon", "galaxie", "country sedan", "country squire", "crestline", "custom", "custom 500", "customline", "deluxe", "fairlane 500", "galaxie 500", "ltd", "ltd ii", "mainline", "police interceptor", "ranch wagon", "ranchero", "starliner", "sunliner", "torino", "victoria", "pinto", "mustang boss 302", "mustang boss 429", "mustang mach 1", "fairmont", "granada", "courier", "f-100"],
    
    "gmc": ["sierra", "yukon", "acadia", "terrain", "canyon", "savana", "hummer ev", "jimmy", "envoy", "sonoma", "safari", "syclone", "typhoon", "suburban", "sprint", "rally", "vandura", "s15", "c1500", "c2500", "c3500", "k1500", "k2500", "k3500", "caballero", "carryall", "forward control", "new look bus", "panel truck", "pickup", "s-15 jimmy", "cabover", "astro", "brigadier", "topkick"],
    
    "cadillac": ["escalade", "ct4", "ct5", "xt4", "xt5", "xt6", "ct6", "ats", "cts", "xts", "srx", "sts", "dts", "eldorado", "seville", "deville", "fleetwood", "allante", "brougham", "catera", "series 60", "series 61", "series 62", "series 63", "series 65", "series 70", "series 75", "series 80", "series 90", "calais", "commercial chassis", "coupe de ville", "sedan de ville", "eldorado biarritz", "eldorado brougham", "eldorado seville", "escalade esv", "escalade ext", "sixty special", "fleetwood 75", "fleetwood brougham", "fleetwood limousine", "cimarron"],
    
    "buick": ["enclave", "encore", "lesabre", "envision", "lacrosse", "regal", "verano", "cascada", "lesabre", "century", "skylark", "park avenue", "riviera", "roadmaster", "electra", "rainier", "rendezvous", "terraza", "lucerne", "special", "super", "limited", "estate wagon", "invicta", "wildcat", "grand national", "gsx", "apollo", "centurion", "skyhawk", "somerset", "reatta", "grand sport", "roadmaster estate", "special deluxe", "super estate wagon", "electra 225", "gnx", "regal t-type", "regal gs"],
    
    "chrysler": ["300", "pacifica", "voyager", "town & country", "pt cruiser", "sebring", "200", "concorde", "crossfire", "aspen", "cirrus", "imperial", "lhs", "new yorker", "fifth avenue", "cordoba", "newport", "lebaron", "airflow", "airstream", "crown imperial", "c-300", "300b", "300c", "300d", "300e", "300f", "300g", "300h", "300j", "300k", "300l", "windsor", "saratoga", "300m", "new yorker brougham", "royal", "town and country wagon", "st. regis", "valiant", "e-class", "laser", "conquest", "tc by maserati", "nassau", "daytona", "prowler"],
    
    "dodge": ["charger", "challenger", "durango", "journey", "grand caravan", "ram", "viper", "neon", "avenger", "dart", "nitro", "caliber", "intrepid", "stealth", "magnum", "stratus", "shadow", "dynasty", "spirit", "colt", "daytona", "caravan", "omni", "custom", "d series", "coronet", "polara", "monaco", "super bee", "diplomat", "royal", "wayfarer", "meadowbrook", "kingsway", "d100", "d150", "d250", "d350", "w100", "w150", "w250", "w350", "ramcharger", "tradesman", "sportsman", "st. regis", "600", "400", "aries", "aspen", "mirada", "lancer", "charger daytona", "coronet super bee", "440", "880", "330", "024", "rampage", "raider", "demon", "monaco brougham", "charger r/t", "coronet r/t"],
    
    "jeep": ["wrangler", "grand cherokee", "cherokee", "compass", "renegade", "gladiator", "wagoneer", "grand wagoneer", "liberty", "patriot", "commander", "cj", "scrambler", "comanche"],
    
    "ram": ["1500", "2500", "3500", "promaster", "promaster city", "dakota"],
    
    "lincoln": ["navigator", "aviator", "nautilus", "corsair", "continental", "mkz", "mkt", "mks", "mkx", "mkc", "town car", "ls", "blackwood", "mark lt", "mark viii", "mark vii", "mark vi", "mark v", "mark iv", "zephyr"],
    
    "tesla": ["model 3", "model s", "model x", "model y", "cybertruck", "roadster"],
    
    # Classic American Brands
    "oldsmobile": ["cutlass", "88", "98", "442", "toronado", "alero", "aurora", "bravada", "intrigue", "silhouette", "achieva", "cutlass supreme", "cutlass ciera", "firenza", "custom cruiser", "delmont", "delta 88", "dynamic", "fiesta", "f-85", "jetstar", "starfire", "super 88", "vista cruiser", "calais", "omega", "hurst/olds", "rallye 350", "ninety-eight", "holiday", "special", "standard", "series 60", "series 70", "series 80", "series 90", "touring sedan", "jet star"],
    
    "pontiac": ["firebird", "gto", "grand prix", "trans am", "bonneville", "grand am", "fiero", "sunfire", "solstice", "sunbird", "lemans", "montana", "aztek", "g6", "g8", "vibe", "torrent", "catalina", "laurentian", "parisienne", "star chief", "chieftain", "super chief", "streamliner", "ventura", "safari", "phoenix", "6000", "j2000", "t1000", "astre", "beaumont", "strato chief", "tempest", "2+2", "can am", "executive", "torpedo"],
    
    "mercury": ["cougar", "grand marquis", "marauder", "marquis", "meteor", "milan", "monarch", "montego", "monterey", "mountaineer", "mystique", "park lane", "sable", "topaz", "tracer", "villager", "mariner", "montclair", "colony park", "comet", "commuter", "bobcat", "brougham", "capri", "cyclone", "eight", "lynx", "ln7", "m-series", "medalist", "monterey custom", "monterey s-55", "s-55", "turnpike cruiser", "voyager", "zephyr"],
    
    "plymouth": ["barracuda", "belvedere", "duster", "fury", "gtx", "horizon", "laser", "neon", "prowler", "road runner", "satellite", "valiant", "volare", "acclaim", "caravelle", "champ", "colt", "conquest", "cricket", "gran fury", "reliant", "sapporo", "sundance", "turismo", "breeze", "cambridge", "cranbrook", "concord", "deluxe", "plaza", "savoy", "superbird", "suburban", "special", "special deluxe"],
    
    # European Brands
    "bmw": ["3-series", "5-series", "7-series", "x1", "x3", "x5", "x7", "z4", "i4", "i7", "ix", "m3", "m5", "m8", "x3m", "x5m", "330i", "530i", "740i", "x3 xdrive30i", "x5 xdrive40i", "335i", "328i", "325i", "540i", "535i", "m340i", "m550i", "z3", "8-series", "6-series", "4-series", "2-series", "1-series", "x2", "x4", "x6", "i3", "i8", "318i", "318is", "320i", "323i", "325ci", "325xi", "328ci", "328xi", "330ci", "330xi", "335d", "335xi", "340i", "518i", "520i", "525i", "525xi", "528i", "528xi", "530xi", "535d", "535xi", "545i", "550i", "550xi", "740e", "740il", "745i", "745li", "750i", "750il", "750li", "760i", "760li", "840i", "840ci", "850i", "850ci", "850csi", "m235i", "m240i", "m2", "m340i", "m3 competition", "m4", "m4 competition", "m550i", "m5 competition", "m6", "m6 gran coupe", "m760i", "m760li", "m8 competition", "m8 gran coupe", "x1 sdrive28i", "x1 xdrive28i", "x2 m35i", "x3 m40i", "x4 m40i", "x5 m50i", "x5 xdrive35i", "x5 xdrive40i", "x5 xdrive45e", "x5 xdrive50i", "x6 m50i", "x6 xdrive35i", "x6 xdrive40i", "x6 xdrive50i", "x7 m50i", "x7 xdrive40i", "x7 xdrive50i", "z4 m40i", "z4 sdrive30i", "i4 edrive40", "i4 m50", "i7 xdrive60", "ix xdrive50", "ix m60"],
    
    "mercedes-benz": ["c-class", "e-class", "s-class", "a-class", "glc", "gle", "gls", "g-class", "cla", "cls", "sl", "slk", "amg gt", "eqs", "eqe", "c300", "e350", "s500", "glc300", "gle350", "gle450", "g550", "c43 amg", "e63 amg", "s63 amg", "c63 amg", "glc43 amg", "ml350", "ml550", "gl450", "gl550", "gla", "glb", "slc", "clk", "sprinter", "metris", "slk230", "slk320", "slk350", "slk55 amg", "c230", "c240", "c250", "c280", "c320", "c350", "c400", "c450", "e300", "e320", "e400", "e420", "e430", "e500", "e550", "s320", "s350", "s400", "s420", "s430", "s550", "s600", "s65 amg", "cl500", "cl550", "cl600", "cl63 amg", "cl65 amg", "clk320", "clk350", "clk430", "clk500", "clk55 amg", "clk550", "clk63 amg", "sl320", "sl350", "sl500", "sl550", "sl55 amg", "sl63 amg", "sl65 amg", "slr", "sls", "glk350", "ml320", "ml430", "ml500", "ml55 amg", "ml63 amg", "gl320", "gl350", "gl500", "gl63 amg", "g500", "g55 amg", "g63 amg", "g65 amg", "gla250", "gla35 amg", "gla45 amg", "glb250", "glc43", "glc63", "gle43", "gle53", "gle63", "gls450", "gls550", "gls580", "gls63", "maybach s560", "maybach s580", "maybach s600", "maybach s650", "maybach gls600", "r350", "r500", "cla250", "cla35 amg", "cla45 amg", "cls400", "cls500", "cls550", "cls55 amg", "cls63 amg", "s550e", "eqb", "eqc", "eqa", "190e", "300e", "300ce", "300te", "400e", "500e"],
    
    "audi": ["a3", "a4", "a5", "a6", "a7", "a8", "q3", "q5", "q7", "q8", "tt", "r8", "e-tron", "s3", "s4", "s5", "s6", "s7", "s8", "rs3", "rs5", "rs7", "sq5", "sq7", "sq8", "a4 allroad", "a6 allroad", "allroad", "a3 sportback", "80", "90", "100", "200", "v8", "cabriolet", "coupe quattro", "a3 e-tron", "a3 quattro", "a4 avant", "a4 quattro", "a5 cabriolet", "a5 coupe", "a5 sportback", "a6 avant", "a6 quattro", "a7 sportback", "a7 quattro", "a8 l", "a8 quattro", "e-tron gt", "e-tron sportback", "q3 sportback", "q4 e-tron", "q5 sportback", "q5 e-tron", "q8 e-tron", "rs q3", "rs q8", "rs3 sportback", "rs4", "rs4 avant", "rs6", "rs6 avant", "tt rs", "tt coupe", "tt roadster", "tt quattro", "r8 spyder", "r8 v10", "r8 v10 plus", "s3 sedan", "s4 avant", "s4 sedan", "s5 cabriolet", "s5 coupe", "s5 sportback", "sq7 tfsi", "sq8 tfsi", "rs5 coupe", "rs5 sportback", "rs7 sportback", "sq5 sportback"],
    
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
        
        # Initialize regex pattern caches for better performance
        self._initialize_regex_patterns()
        
        # Initialize part term patterns
        self._initialize_part_patterns()
        
        # Stats for monitoring performance
        self.cache_hits = 0
        self.cache_misses = 0
        
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
    
    @lru_cache(maxsize=1000)
    def normalize_query(self, query):
        """
        Normalize the query text (lowercase, remove excess whitespace, etc.)
        Added caching to improve performance for repeated searches.
        """
        if not query:
            return ""
        
        # Convert to lowercase
        query = query.lower()
        
        # Replace special characters with spaces using precompiled pattern
        query = DASH_PATTERN.sub("-", query)
        
        # Remove common filler words that don't add meaning using precompiled pattern
        query = FILLER_WORDS_PATTERN.sub(" ", query)
        
        # Clean up whitespace using precompiled pattern
        query = WHITESPACE_PATTERN.sub(" ", query).strip()
        
        return query
    
    # Precompiled patterns for year extraction
    YEAR_RANGE_PATTERN = re.compile(r'\b((?:19|20)?\d{2})[-/](?:19|20)?\d{2}\b')
    FIRST_YEAR_PATTERN = re.compile(r'\b((?:19|20)?\d{2})')
    FULL_YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')
    
    @lru_cache(maxsize=1000)
    def _extract_year(self, query):
        """
        Extract vehicle year from query with enhanced year range detection.
        Optimized with caching and precompiled patterns for better performance.
        """
        # First, try to match year ranges in various formats using precompiled pattern
        year_range_match = self.YEAR_RANGE_PATTERN.search(query)
        if year_range_match:
            year_range = year_range_match.group(0)
            
            # Extract the first year from the range using precompiled pattern
            first_year_match = self.FIRST_YEAR_PATTERN.search(year_range)
            if first_year_match:
                year = first_year_match.group(0)
                
                # Handle 2-digit years with improved logic
                if len(year) == 2:
                    current_year = time.gmtime().tm_year % 100
                    year_num = int(year)
                    
                    # Use a rolling window approach based on current year
                    if year_num > current_year + 10:  # Likely a past year (19xx)
                        return "19" + year
                    else:  # Likely current or future year (20xx)
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
        
        # Match 4-digit years from 1900-2099 using precompiled pattern
        year_match = self.FULL_YEAR_PATTERN.search(query)
        if year_match:
            return year_match.group(0)
        
        # Precompiled pattern for 2-digit years
        SHORT_YEAR_PATTERN = re.compile(r'\b\d{2}\b')
        
        # Match 2-digit years and convert to 4 digits with improved logic
        short_year_match = SHORT_YEAR_PATTERN.search(query)
        if short_year_match:
            year = short_year_match.group(0)
            current_year = time.gmtime().tm_year % 100
            year_num = int(year)
            
            # Use a smarter window based on current year and automotive context
            # Cars are typically sold up to 2 years in advance
            if year_num > current_year + 2:  # Likely past model year
                return "19" + year
            else:  # Current or future model year
                return "20" + year
        
        return None

    # Precompiled patterns for makes and synonyms
    def _initialize_regex_patterns(self):
        """Initialize regex patterns once for better performance"""
        if not hasattr(self, '_make_patterns'):
            self._make_patterns = {
                make: re.compile(r'\b' + re.escape(make.lower()) + r'\b') 
                for make in self.vehicle_makes
            }
            
        if not hasattr(self, '_synonym_patterns'):
            self._synonym_patterns = {
                synonym.lower(): re.compile(r'\b' + re.escape(synonym.lower()) + r'\b')
                for synonym in self.make_synonyms
            }
    
    @lru_cache(maxsize=1000)
    def _extract_make(self, query):
        """
        Extract vehicle make from query with improved brand recognition.
        Optimized with pattern caching and fuzzy matching for better results.
        """
        query_lower = query.lower()
        
        # Initialize regex patterns if not already done
        self._initialize_regex_patterns()
        
        # Check for exact make matches using precompiled patterns
        for make, pattern in self._make_patterns.items():
            if pattern.search(query_lower):
                return make
        
        # Check for synonyms with word boundary using precompiled patterns
        for synonym_lower, pattern in self._synonym_patterns.items():
            if pattern.search(query_lower):
                # Find the original synonym with case preserved
                for synonym in self.make_synonyms:
                    if synonym.lower() == synonym_lower:
                        return self.make_synonyms[synonym]
        
        # Try partial matching for certain premium brands that might be abbreviated
        # This helps with queries like "benz front bumper" instead of "mercedes-benz"
        # Precompile patterns for special cases
        if not hasattr(self, '_special_case_patterns'):
            self._special_case_patterns = {
                key: re.compile(r'\b' + re.escape(key) + r'\b')
                for key in {
                    "benz": "mercedes-benz",
                    "merc": "mercedes-benz",
                    "chevy": "chevrolet", 
                    "vw": "volkswagen",
                    "bmw": "bmw",
                    "audi": "audi",
                    "yota": "toyota",
                    "ford": "ford",
                    "caddy": "cadillac",
                    "subie": "subaru",
                    "lexus": "lexus"
                }
            }
            self._special_case_makes = {
                "benz": "mercedes-benz",
                "merc": "mercedes-benz",
                "chevy": "chevrolet", 
                "vw": "volkswagen",
                "bmw": "bmw",
                "audi": "audi",
                "yota": "toyota",
                "ford": "ford",
                "caddy": "cadillac",
                "subie": "subaru",
                "lexus": "lexus"
            }
        
        for partial, pattern in self._special_case_patterns.items():
            if pattern.search(query_lower):
                return self._special_case_makes[partial]
        
        # Add fuzzy matching for commonly misspelled car brands
        words = query_lower.split()
        for word in words:
            if len(word) >= 3:  # Only check words of reasonable length
                # Check against all makes
                for make in self.vehicle_makes:
                    if " " not in make:  # Only compare single word makes
                        make_lower = make.lower()
                        # Simple similarity check for misspelled brands
                        if self._string_similarity(word, make_lower) > 0.75:  # 75% similar
                            return make
        
        return None
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate a simple string similarity ratio
        Returns a value between 0.0 (completely different) and 1.0 (identical)
        """
        if not s1 or not s2:
            return 0.0
            
        if s1 == s2:
            return 1.0
            
        # Use shorter string as base
        shorter = s1 if len(s1) < len(s2) else s2
        longer = s2 if len(s1) < len(s2) else s1
        
        # Count matching characters
        matches = sum(1 for c in shorter if c in longer)
        
        # Calculate similarity
        return matches / max(len(s1), len(s2))

    @lru_cache(maxsize=1000)
    def _extract_model(self, query):
        """
        Extract vehicle model from query with improved model variation handling.
        Optimized with caching and better pattern matching for accuracy.
        """
        # Get the make first to narrow down model search
        make = self._extract_make(query)
        query_lower = query.lower()
        
        # Initialize model patterns if not already done
        if not hasattr(self, '_model_patterns'):
            self._model_patterns = {}
            for make_name, models in self.make_models.items():
                self._model_patterns[make_name] = {
                    model: re.compile(r'\b' + re.escape(model.lower()) + r'\b')
                    for model in models
                }
        
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
        
        # Special handling for models with dash variations (F-150 vs F150)
        dash_normalized_query = re.sub(r'(\w)-(\d)', r'\1\2', query_lower)
        space_normalized_query = re.sub(r'(\w)-(\d)', r'\1 \2', query_lower)
            
        # Sort models by length (descending) to match longer model names first
        # This prevents 'civic' from matching before 'civic type r'
        sorted_models = sorted(models, key=len, reverse=True)
            
        # Try to find models with exact word boundaries first - improved matching
        for model in sorted_models:
            model_lower = model.lower()
            
            # Special case for Ford F-series trucks and similar models with dashes
            if "-" in model_lower:
                no_dash_model = model_lower.replace("-", "")
                space_model = model_lower.replace("-", " ")
                
                if re.search(r'\b' + re.escape(no_dash_model) + r'\b', dash_normalized_query) or \
                   re.search(r'\b' + re.escape(space_model) + r'\b', space_normalized_query) or \
                   re.search(r'\b' + re.escape(model_lower) + r'\b', query_lower):
                    return model
            elif re.search(r'\b' + re.escape(model_lower) + r'\b', query_lower):
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

    # Part extraction patterns - precompiled once for better performance
    def _initialize_part_patterns(self):
        """Initialize regex patterns for parts once for better performance"""
        if not hasattr(self, '_part_patterns'):
            # Organize parts by category for better context understanding
            self._parts_by_category = {
                "bumper": [
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
                ],
                # Add other categories here
            }
            
            # Create pattern dictionary for all parts
            self._part_patterns = {}
            for category, parts in self._parts_by_category.items():
                for part in parts:
                    self._part_patterns[part] = re.compile(r'\b' + re.escape(part) + r'\b')
                    
            # Also create patterns for the part_terms dictionary (generic parts)
            self._part_term_patterns = {}
            for part in self._load_part_terms():
                self._part_term_patterns[part] = re.compile(r'\b' + re.escape(part) + r'\b')
    
    @lru_cache(maxsize=1000)
    def _extract_part(self, query):
        """
        Extract part information from query with improved compound part recognition.
        Optimized with pattern caching and contextual understanding.
        """
        query_lower = query.lower()
        
        # Initialize patterns if not already done
        self._initialize_part_patterns()
        
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
        """
        Extract position information like 'front', 'rear', 'driver side', etc.
        Also handles abbreviations like RR (rear right), FL (front left), etc.
        """
        positions = []
        query_lower = query.lower()
        
        # Define abbreviation mappings first to check for compound positions
        abbr_mappings = {
            'rr': ['rear', 'right'],
            'rl': ['rear', 'left'],
            'fr': ['front', 'right'],
            'fl': ['front', 'left'],
            'rf': ['front', 'right'],
            'lf': ['front', 'left'],
            'lr': ['rear', 'left'],
            'l/r': ['left', 'right'],
            'f/r': ['front', 'rear'],
            'f/l': ['front', 'left'],
            'f/s': ['front'],
            'r/s': ['rear'],
            'l/s': ['left'],
            'r/h': ['right'],
            'l/h': ['left'],
            'ps': ['right'],
            'ds': ['left']
        }
        
        # Check for abbreviations at word boundaries
        for abbr, pos_list in abbr_mappings.items():
            pattern = r'\b' + re.escape(abbr) + r'\b'
            if re.search(pattern, query_lower):
                positions.extend(pos_list)
        
        # Also check for standard position terms
        position_terms = {
            "front": ["front", "forward", "frt"],
            "rear": ["rear", "back", "rr"],
            "left": ["left", "driver", "driver's", "driver side", "driver-side", "lh", "ds"],
            "right": ["right", "passenger", "passenger's", "passenger side", "passenger-side", "rh", "ps"],
            "upper": ["upper", "top"],
            "lower": ["lower", "bottom"],
            "inner": ["inner", "inside"],
            "outer": ["outer", "outside"]
        }
        
        for position, terms in position_terms.items():
            if position not in positions:  # Only check if not already added from abbreviations
                for term in terms:
                    pattern = r'\b' + re.escape(term) + r'\b'
                    if re.search(pattern, query_lower):
                        positions.append(position)
                        break
        
        # Check for combined position phrases that may not be caught by the above
        if 'front' in positions and 'left' in positions and 'front left' not in positions:
            if 'front driver' in query_lower or 'driver front' in query_lower:
                positions.append('front left')
                
        if 'front' in positions and 'right' in positions and 'front right' not in positions:
            if 'front passenger' in query_lower or 'passenger front' in query_lower:
                positions.append('front right')
                
        if 'rear' in positions and 'left' in positions and 'rear left' not in positions:
            if 'rear driver' in query_lower or 'driver rear' in query_lower:
                positions.append('rear left')
                
        if 'rear' in positions and 'right' in positions and 'rear right' not in positions:
            if 'rear passenger' in query_lower or 'passenger rear' in query_lower:
                positions.append('rear right')
        
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
    
        
    # Create a compound key for the query cache
    def _make_cache_key(self, query, structured_data=None):
        if structured_data:
            # Create a stable representation of structured data for caching
            sorted_items = sorted((k, v) for k, v in structured_data.items() if v)
            return f"{query}::{sorted_items}"
        return query
    
    # Query processing results cache
    _query_cache = {}
    _cache_hits = 0
    _cache_misses = 0
    _CACHE_MAX_SIZE = 1000
    
    @lru_cache(maxsize=1000)
    def process_query(self, query, structured_data=None):
        """
        Main processing function that takes a raw query and returns structured results
        with extracted information and optimized search terms.
        
        Now supports structured data input from multi-field form.
        Optimized with caching for better performance on repeated queries.
        """
        # Use structured data if provided, otherwise extract from query
        if structured_data:
            vehicle_info = self.process_structured_data(structured_data)
        else:
            vehicle_info = self.extract_vehicle_info(query)
            
        search_terms = self.generate_search_terms(vehicle_info)
        
        # Add processing timestamp for cache freshness tracking
        timestamp = int(time.time())
        
        result = {
            "vehicle_info": vehicle_info,
            "search_terms": search_terms,
            "confidence": vehicle_info.get("search_confidence", 0),
            "processed_at": timestamp
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

    @lru_cache(maxsize=1000)
    def extract_vehicle_info(self, query):
        """
        Extract structured vehicle information from query
        Returns a dict with year, make, model, and part.
        Optimized with caching for better performance.
        """
        normalized = self.normalize_query(query)
        
        # Use parallel attribute extraction for better performance
        # Each extraction method is already cached
        year = self._extract_year(normalized)
        make = self._extract_make(normalized)
        model = self._extract_model(normalized)
        part = self._extract_part(normalized)
        position = self._extract_position(normalized)
        engine_specs = self._extract_engine_specs(normalized)
        
        # Incorporate position terms into the part name for better part matching
        enhanced_part = part
        if position and part:
            # First check if position terms are already in the part name
            part_lower = part.lower()
            
            # Only add position terms if they're not already in the part name
            if not any(pos in part_lower for pos in position):
                # Check for compound positions (front left, rear right, etc.)
                compound_positions = []
                if 'front' in position and 'left' in position and 'front left' not in part_lower:
                    compound_positions.append('front left')
                if 'front' in position and 'right' in position and 'front right' not in part_lower:
                    compound_positions.append('front right')
                if 'rear' in position and 'left' in position and 'rear left' not in part_lower:
                    compound_positions.append('rear left')
                if 'rear' in position and 'right' in position and 'rear right' not in part_lower:
                    compound_positions.append('rear right')
                
                # If we have compound positions, use those instead of individual positions
                if compound_positions:
                    position_prefix = ' '.join(compound_positions)
                    enhanced_part = f"{position_prefix} {part}"
                    print(f"[DEBUG] QueryProcessor - Enhanced part with compound positions: {enhanced_part}")
                # Otherwise add individual positions that aren't already in the part name
                else:
                    position_keywords = ['front', 'rear', 'left', 'right', 'upper', 'lower', 'inner', 'outer']
                    positions_to_add = [pos for pos in position if pos in position_keywords and pos not in part_lower.split()]
                    
                    if positions_to_add:
                        position_prefix = ' '.join(positions_to_add)
                        enhanced_part = f"{position_prefix} {part}"
                        print(f"[DEBUG] QueryProcessor - Enhanced part with positions: {enhanced_part}")
        
        result = {
            "year": year,
            "make": make,
            "model": model,
            "part": enhanced_part,  # Use the enhanced part name
            "position": position,
            "engine_specs": engine_specs,
            "original_query": query,
            "normalized_query": normalized
        }
        
        # Additional fields that might be useful
        result["search_confidence"] = self._calculate_confidence(result)
        
        # Add year range information for specific models (useful for parts compatibility)
        if year and make and model:
            result["year_range"] = self._get_year_range(year, make, model)
            
            # Add chassis/platform code if available (helps with part compatibility)
            if hasattr(self, 'vehicle_platforms') and make.lower() in self.vehicle_platforms:
                platforms = self.vehicle_platforms[make.lower()]
                for platform_info in platforms:
                    if platform_info.get('model') == model.lower() and platform_info.get('year_start') <= int(year) <= platform_info.get('year_end'):
                        result["platform"] = platform_info.get('platform_code')
                        break
        
        return result