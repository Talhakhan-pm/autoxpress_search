import re

def has_vehicle_info(query):
    """
    Check if a query contains sufficient vehicle information.
    Returns True if it has year + make/model indicators, False otherwise.
    """
    # Clean and normalize the query
    query = query.lower().strip()
    
    # Check for year patterns (2-digit or 4-digit years)
    year_pattern = r'\b(19|20)\d{2}\b|\b\d{2}\b'
    has_year = bool(re.search(year_pattern, query))
    
    # List of common vehicle makes
    common_makes = [
        'acura', 'audi', 'bmw', 'buick', 'cadillac', 'chevrolet', 'chevy',
        'chrysler', 'dodge', 'ford', 'gmc', 'honda', 'hyundai', 'infiniti',
        'jaguar', 'jeep', 'kia', 'lexus', 'lincoln', 'mazda', 'mercedes',
        'benz', 'mitsubishi', 'nissan', 'porsche', 'ram', 'subaru', 'toyota',
        'volkswagen', 'vw', 'volvo'
    ]
    
    # Check if any make is in the query
    has_make = any(make in query.split() for make in common_makes)
    
    # Return True only if we have both year and make
    return has_year and has_make

def get_missing_info_message(query):
    """
    Returns a message indicating what vehicle information is missing from the query.
    """
    query = query.lower().strip()
    
    # Check for year patterns
    year_pattern = r'\b(19|20)\d{2}\b|\b\d{2}\b'
    has_year = bool(re.search(year_pattern, query))
    
    # List of common vehicle makes
    common_makes = [
        'acura', 'audi', 'bmw', 'buick', 'cadillac', 'chevrolet', 'chevy',
        'chrysler', 'dodge', 'ford', 'gmc', 'honda', 'hyundai', 'infiniti',
        'jaguar', 'jeep', 'kia', 'lexus', 'lincoln', 'mazda', 'mercedes',
        'benz', 'mitsubishi', 'nissan', 'porsche', 'ram', 'subaru', 'toyota',
        'volkswagen', 'vw', 'volvo'
    ]
    
    has_make = any(make in query.split() for make in common_makes)
    
    if not has_year and not has_make:
        return "Please include both year and vehicle make/model (e.g., '2020 Honda Accord front bumper')"
    elif not has_year:
        return "Please include the vehicle year (e.g., '2020 front bumper')"
    elif not has_make:
        return "Please include the vehicle make and model (e.g., 'Honda Accord front bumper')"
    
    return None