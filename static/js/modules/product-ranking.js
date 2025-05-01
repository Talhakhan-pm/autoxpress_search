/**
 * Product Ranking Module
 * Provides advanced scoring and ranking of products based on multiple factors
 */

const ProductRanking = (function() {
  // Configuration for ranking weights (can be adjusted)
  const CONFIG = {
    // Primary factors
    EXACT_YEAR_MATCH: 30,
    YEAR_RANGE_MATCH: 20,
    TITLE_RELEVANCE: 25,
    CONDITION_NEW: 15,
    CONDITION_REFURB: 8,
    
    // Part type identification
    PART_TYPE: {
      EXACT: 40,     // Exact part match
      MAJOR: 30,     // Major component (engine, transmission)
      STANDARD: 20,  // Standard part (brake pads, alternator)
      ACCESSORY: 5   // Accessory (trim, covers)
    },
    
    // Secondary factors
    FREE_SHIPPING: 8,
    OEM_PART: 15,
    BRAND_TIER: {
      PREMIUM: 10,
      STANDARD: 5,
      UNKNOWN: 0
    },
    
    // Maximum available score (for percentage calculation)
    MAX_SCORE: 100
  };
  
  // Keywords for identifying major components
  const MAJOR_COMPONENTS = [
    'engine', 'motor', 'transmission', 'gearbox', 'differential', 
    'axle', 'chassis', 'frame', 'body', 'complete'
  ];
  
  // Keywords for identifying standard parts
  const STANDARD_PARTS = [
    'brake', 'rotor', 'caliper', 'alternator', 'starter', 'radiator',
    'suspension', 'strut', 'shock', 'spring', 'pump', 'battery', 'sensor',
    'bumper assembly', 'complete assembly', 'door', 'window', 'mirror'
  ];
  
  // Keywords for identifying accessories
  const ACCESSORIES = [
    'cover', 'cap', 'trim', 'molding', 'emblem', 'badge', 'sticker',
    'protector', 'mat', 'liner', 'guard', 'grip', 'holder', 'bracket only',
    'cable', 'wire', 'bulb', 'filter'
  ];
  
  // Keywords that indicate OEM parts
  const OEM_INDICATORS = [
    'oem', 'genuine', 'original', 'factory', 'manufacturer'
  ];
  
  // Premium brands by make
  const PREMIUM_BRANDS = {
    'universal': ['bosch', 'brembo', 'bilstein', 'k&n', 'moog', 'acdelco', 'monroe'],
    'ford': ['motorcraft', 'ford racing', 'roush'],
    'toyota': ['trd', 'lexus'],
    'honda': ['acura', 'mugen'],
    'nissan': ['nismo', 'infiniti'],
    'chevrolet': ['gm', 'acdelco', 'chevrolet performance'],
    'dodge': ['mopar', 'srt']
  };
  
  /**
   * Calculate a score for a product based on multiple factors
   * @param {Object} product - Product object with details
   * @param {Object} vehicleInfo - Vehicle information for comparison
   * @return {Object} Enhanced product with score and badges
   */
  function rankProduct(product, vehicleInfo) {
    if (!product || !vehicleInfo) return product;
    
    let score = 0;
    const badges = [];
    const titleLower = product.title.toLowerCase();
    const debug = { factors: {} };
    
    // 1. Check for exact year match
    if (product.exactYearMatch || 
        (vehicleInfo.year && titleLower.includes(vehicleInfo.year))) {
      score += CONFIG.EXACT_YEAR_MATCH;
      badges.push({ type: 'year', label: 'Exact Year', priority: 2 });
      debug.factors.exactYear = CONFIG.EXACT_YEAR_MATCH;
    } 
    // 2. Check for year range match
    else if (product.compatibleRange || 
             (vehicleInfo.year && isYearInRange(titleLower, vehicleInfo.year))) {
      score += CONFIG.YEAR_RANGE_MATCH;
      badges.push({ type: 'yearRange', label: 'Year Compatible', priority: 3 });
      debug.factors.yearRange = CONFIG.YEAR_RANGE_MATCH;
    }
    
    // 3. Part type identification
    const partTypeScore = identifyPartType(titleLower, vehicleInfo.part);
    score += partTypeScore.score;
    if (partTypeScore.type === 'exact' || partTypeScore.type === 'major') {
      badges.push({ type: 'partType', label: 'Exact Part', priority: 1 });
    }
    debug.factors.partType = partTypeScore.score;
    
    // 4. Condition evaluation
    if (product.condition.toLowerCase().includes('new')) {
      score += CONFIG.CONDITION_NEW;
      badges.push({ type: 'condition', label: 'New', priority: 4 });
      debug.factors.condition = CONFIG.CONDITION_NEW;
    } else if (product.condition.toLowerCase().includes('refurbished')) {
      score += CONFIG.CONDITION_REFURB;
      badges.push({ type: 'condition', label: 'Refurbished', priority: 4 });
      debug.factors.condition = CONFIG.CONDITION_REFURB;
    } else if (product.condition.toLowerCase().includes('used') || 
               product.condition.toLowerCase().includes('pre-owned')) {
      badges.push({ type: 'condition', label: 'Used', priority: 4 });
    }
    
    // 5. Check for free shipping
    if (product.shipping.toLowerCase().includes('free')) {
      score += CONFIG.FREE_SHIPPING;
      badges.push({ type: 'shipping', label: 'Free Shipping', priority: 5 });
      debug.factors.freeShipping = CONFIG.FREE_SHIPPING;
    }
    
    // 6. Check for OEM parts
    if (OEM_INDICATORS.some(term => titleLower.includes(term))) {
      score += CONFIG.OEM_PART;
      badges.push({ type: 'oem', label: 'OEM', priority: 2 });
      debug.factors.oem = CONFIG.OEM_PART;
    }
    
    // 7. Brand tier evaluation
    const brandTierScore = evaluateBrandTier(titleLower, vehicleInfo.make);
    score += brandTierScore.score;
    if (brandTierScore.tier === 'premium') {
      badges.push({ type: 'brand', label: 'Premium Brand', priority: 3 });
    }
    debug.factors.brandTier = brandTierScore.score;
    
    // Cap the score at the maximum and convert to percentage
    score = Math.min(score, CONFIG.MAX_SCORE);
    const scorePercentage = Math.round((score / CONFIG.MAX_SCORE) * 100);
    
    // Add relevance category based on score
    let relevanceCategory = 'low';
    if (scorePercentage >= 80) {
      relevanceCategory = 'high';
      if (!badges.find(b => b.priority === 1)) {
        badges.push({ type: 'relevance', label: 'Best Match', priority: 1 });
      }
    } else if (scorePercentage >= 50) {
      relevanceCategory = 'medium';
    }
    
    // Sort badges by priority (lower number = higher priority)
    badges.sort((a, b) => a.priority - b.priority);
    
    // Return enhanced product with ranking data
    return {
      ...product,
      relevanceScore: scorePercentage,
      relevanceCategory,
      primaryBadge: badges.length > 0 ? badges[0] : null,
      secondaryBadges: badges.slice(1),
      allBadges: badges,
      rankingDebug: debug
    };
  }
  
  /**
   * Check if a year is in a compatible range mentioned in the title
   */
  function isYearInRange(title, year) {
    // Look for patterns like "2015-2020" or "2015 to 2020" or "fits 2015 2016 2017"
    const yearNumber = parseInt(year, 10);
    
    // Case 1: Range with dash or 'to'
    const rangePattern = /(\d{4})(?:\s*-\s*|\s*to\s*)(\d{4})/gi;
    let match;
    while ((match = rangePattern.exec(title)) !== null) {
      const startYear = parseInt(match[1], 10);
      const endYear = parseInt(match[2], 10);
      if (yearNumber >= startYear && yearNumber <= endYear) {
        return true;
      }
    }
    
    // Case 2: List of years "fits 2015 2016 2017"
    const years = title.match(/\b(19|20)\d{2}\b/g) || [];
    if (years.includes(year)) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Identify the type of part from the title and calculate a score
   */
  function identifyPartType(title, searchedPart) {
    if (!searchedPart) {
      // Without a searched part, try to identify from the title
      if (MAJOR_COMPONENTS.some(term => title.includes(term))) {
        return { type: 'major', score: CONFIG.PART_TYPE.MAJOR };
      } else if (STANDARD_PARTS.some(term => title.includes(term))) {
        return { type: 'standard', score: CONFIG.PART_TYPE.STANDARD };
      } else if (ACCESSORIES.some(term => title.includes(term))) {
        return { type: 'accessory', score: CONFIG.PART_TYPE.ACCESSORY };
      }
      return { type: 'unknown', score: 0 };
    }
    
    // With a searched part, compare to title
    const searchTermLower = searchedPart.toLowerCase();
    
    // Check for exact match first
    if (title.includes(searchTermLower)) {
      // Ensure it's not just a partial match (e.g. "bumper" in "bumper cover")
      // by checking for accessory indicators
      if (ACCESSORIES.some(term => title.includes(term) && 
          searchTermLower.indexOf(term) === -1)) {
        return { type: 'standard', score: CONFIG.PART_TYPE.STANDARD };
      }
      return { type: 'exact', score: CONFIG.PART_TYPE.EXACT };
    }
    
    // Check if searched part is a major component
    if (MAJOR_COMPONENTS.some(term => searchTermLower.includes(term))) {
      if (MAJOR_COMPONENTS.some(term => title.includes(term))) {
        return { type: 'major', score: CONFIG.PART_TYPE.MAJOR };
      }
    }
    
    // Check if searched part is a standard part
    if (STANDARD_PARTS.some(term => searchTermLower.includes(term))) {
      if (STANDARD_PARTS.some(term => title.includes(term))) {
        return { type: 'standard', score: CONFIG.PART_TYPE.STANDARD };
      }
    }
    
    // Check if title contains accessory terms
    if (ACCESSORIES.some(term => title.includes(term))) {
      return { type: 'accessory', score: CONFIG.PART_TYPE.ACCESSORY };
    }
    
    // Default score for unknown match
    return { type: 'unknown', score: 0 };
  }
  
  /**
   * Evaluate the brand tier based on known premium brands
   */
  function evaluateBrandTier(title, make) {
    if (!make) return { tier: 'unknown', score: 0 };
    
    const makeLower = make.toLowerCase();
    
    // Check universal premium brands first
    if (PREMIUM_BRANDS.universal.some(brand => title.includes(brand))) {
      return { tier: 'premium', score: CONFIG.BRAND_TIER.PREMIUM };
    }
    
    // Check make-specific premium brands
    if (PREMIUM_BRANDS[makeLower] && 
        PREMIUM_BRANDS[makeLower].some(brand => title.includes(brand))) {
      return { tier: 'premium', score: CONFIG.BRAND_TIER.PREMIUM };
    }
    
    // Default to standard score if the make is mentioned
    if (title.includes(makeLower)) {
      return { tier: 'standard', score: CONFIG.BRAND_TIER.STANDARD };
    }
    
    return { tier: 'unknown', score: 0 };
  }
  
  /**
   * Process an array of products and enhance them with ranking data
   */
  function rankProducts(products, vehicleInfo) {
    if (!products || !Array.isArray(products) || products.length === 0) {
      return products;
    }
    
    // Enhance each product with ranking data
    const rankedProducts = products.map(product => rankProduct(product, vehicleInfo));
    
    // Sort by relevance score (highest first)
    rankedProducts.sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0));
    
    return rankedProducts;
  }
  
  // Public API
  return {
    rankProduct,
    rankProducts
  };
})();

// Export globally
window.ProductRanking = ProductRanking;