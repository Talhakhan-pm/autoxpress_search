# AutoXpress Smart Assistant

A web application for auto parts search and VIN decoding using AI.

## Recent Improvements

### Security Improvements
- Removed hardcoded Flask secret key, now uses environment variable or secure random value
- Added input sanitization for all user inputs
- Removed sensitive API key debug print statements
- Added VIN format validation before processing
- Added proper error handling without exposing error details to users
- Added timeouts to all external API requests

### Performance Improvements
- Implemented concurrent requests using ThreadPoolExecutor
- Added caching with lru_cache for API responses (both VIN decoder and SerpAPI)
- Separated SerpAPI requests to handle failures independently
- Added request timeouts to prevent hanging operations

### UI Improvements
- Added visual progress indicators with animation for both search and VIN decoding
- Added timeout messages for slow requests to keep users informed
- Improved error messaging with clearer instructions
- Enhanced mobile responsiveness with better styling for small screens
- Added client-side VIN format validation

### Code Organization
- Fixed duplicate Flask app instance
- Improved error handling with specific exception types
- Added validation for required API keys at startup
- Enhanced logging for easier debugging
- Used consistent coding patterns throughout the application

## Future Improvements
- Add database for storing vehicle data instead of hardcoded JS
- Implement rate limiting for API protection
- Add session management for user history
- Add pagination for results
- Create config file for better environment separation
- Split app.py into multiple modules (routes, services, utils)
- Add unit and integration tests
- Add CSRF protection

## Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_KEY=your_serpapi_key
   FLASK_SECRET_KEY=random_secret_key
   ```
4. Run the application: `python app.py`
5. Visit http://localhost:5040 in your browser# autoxpress_google
