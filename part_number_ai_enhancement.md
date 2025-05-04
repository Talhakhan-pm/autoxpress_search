# Part Number Search AI Enhancement

This document outlines the enhancements made to the part number search functionality using OpenAI and SerpAPI integration.

## Overview

The part number search feature has been upgraded to use real data instead of mock information:

1. When a user searches for a part number, the system now:
   - Performs a Google search for the part number via SerpAPI
   - Sends the search results to OpenAI for intelligent extraction
   - Returns structured part information from real search results

2. The AI extracts the following data:
   - Part type/category
   - Manufacturer information
   - Part description
   - Compatible vehicles
   - Alternative part numbers

3. Fallback mechanisms:
   - If SerpAPI search fails, falls back to pattern-based guessing
   - If OpenAI processing fails, falls back to pattern-based guessing
   - Maintains backward compatibility with all existing features

## Implementation Details

### New Functions

1. `get_part_number_search_results(part_number, include_oem, exclude_wholesalers)`
   - Uses SerpAPI to search for the part number on Google
   - Formats the search results for AI processing
   - Returns structured search result content

2. `extract_part_info_with_ai(part_number, search_results, include_alt)`
   - Creates a detailed prompt for OpenAI
   - Extracts structured information from search results
   - Returns a standardized JSON object with part details
   - Includes error handling and fallbacks

3. Enhanced `part_number_search()` function
   - Integrates real search results and AI processing
   - Adds an "ai_enhanced" flag to the response
   - Improved error handling and fallback logic

## Testing

To test the enhanced functionality:

1. Try various part numbers:
   - Common part numbers like "NGK 7090" (spark plug)
   - OEM part numbers like "Toyota 90915-YZZF1" (oil filter)
   - Aftermarket part numbers like "K&N 33-2304" (air filter)
   - Less common part numbers to test fallback behavior

2. Test with different options:
   - With/without "Include OEM terms" option
   - With/without "Include alternative part numbers" option
   - With/without "Exclude wholesalers" option

3. Check the returned data for accuracy:
   - Vehicle compatibility information should be realistic
   - Part type and manufacturer should be accurate
   - Alternative part numbers should be valid

The API returns an "ai_enhanced" field that indicates whether the data came from AI processing (true) or pattern-based fallback (false).

## Technical Requirements

- OpenAI API key must be configured
- SerpAPI key must be configured
- Internet connectivity for search results

## Future Enhancements

Possible future improvements:
- Add caching for part number information to reduce API costs
- Improve the AI prompt with more specific automotive knowledge
- Add support for part interchange databases
- Implement direct RockAuto/eBay search for even better results