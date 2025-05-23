/**
 * Dialpad Dashboard JavaScript
 * Handles data loading, filtering and display for the AutoXpress Call Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    const applyFiltersBtn = document.getElementById('apply-filters');
    const refreshDataBtn = document.getElementById('refresh-data');
    const loadingDiv = document.getElementById('loading');
    const callsTableBody = document.getElementById('calls-table-body');
    const summaryStatsDiv = document.getElementById('summary-stats');
    
    // Functions to manage cache in localStorage
    function saveCache(cache) {
        try {
            localStorage.setItem('dialpadCache', JSON.stringify({
                lastQuery: cache.lastQuery,
                data: cache.data,
                timestamp: cache.timestamp
            }));
        } catch (e) {
            console.error('Failed to save cache to localStorage:', e);
        }
    }
    
    function loadCache() {
        try {
            const cachedData = localStorage.getItem('dialpadCache');
            if (cachedData) {
                return JSON.parse(cachedData);
            }
        } catch (e) {
            console.error('Failed to load cache from localStorage:', e);
        }
        return {
            lastQuery: null,
            data: null,
            timestamp: Date.now()
        };
    }
    
    // Initialize cache from localStorage or with default values
    const callDataCache = loadCache();
    
    function clearCache() {
        // Clear cache from localStorage
        localStorage.removeItem('dialpadCache');
        
        // Reset in-memory cache
        callDataCache.lastQuery = null;
        callDataCache.data = null;
        callDataCache.timestamp = Date.now();
        
        console.log('Cache cleared');
    }
    
    applyFiltersBtn.addEventListener('click', function() {
        loadCallData(false); // false = use cache if possible
    });
    
    refreshDataBtn.addEventListener('click', function() {
        // Reset call type and call status filters to 'All' options
        filterInputs.callType.value = 'all';  // 'all' is the value for "All Calls"
        filterInputs.callStatus.value = 'all'; // 'all' is the value for "All Status"
        
        // Force reload from server
        loadCallData(true);
    });
    
    // Filter inputs - add change event listeners for real-time filtering of cached data
    const filterInputs = {
        dateFrom: document.getElementById('date-from'),
        dateTo: document.getElementById('date-to'),
        agentId: document.getElementById('agent-select'),
        callType: document.getElementById('call-type'),
        callStatus: document.getElementById('call-status')
    };
    
    function loadCallData(forceReload = false) {
        const dateFrom = filterInputs.dateFrom.value;
        const dateTo = filterInputs.dateTo.value;
        const agentId = filterInputs.agentId.value;
        const callType = filterInputs.callType.value;
        const callStatus = filterInputs.callStatus.value;
        
        // Create a query object to compare with cached queries
        const currentQuery = {
            date_from: dateFrom,
            date_to: dateTo,
            agent_id: agentId,
            call_type: callType,
            call_status: callStatus
        };
        
        // Check if we need to reload data from server
        // Either when forceReload is true or when the cache doesn't support our query
        const shouldReloadData = forceReload || shouldReload(currentQuery);
        
        if (shouldReloadData) {
            // Show loading indicator only for specific elements being reloaded
            loadingDiv.style.display = 'block';
            
            // Only clear table when reloading from server
            callsTableBody.innerHTML = '';
            
            // Fetch call data from API
            fetch('/api/dialpad-calls', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(currentQuery),
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                loadingDiv.style.display = 'none';
                
                if (data.calls && data.calls.length > 0) {
                    // Update the cache
                    callDataCache.lastQuery = {...currentQuery};
                    callDataCache.data = data.calls;
                    callDataCache.timestamp = Date.now();
                    
                    // Save cache to localStorage
                    saveCache(callDataCache);
                    
                    // Render call data
                    renderCallData(data.calls);
                    updateSummaryStats(data.calls);
                    summaryStatsDiv.style.display = 'flex';
                } else {
                    callsTableBody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No call data found for the selected filters.</td></tr>';
                    summaryStatsDiv.style.display = 'none';
                    
                    // Clear cache
                    clearCache();
                }
            })
            .catch(error => {
                console.error('Error fetching call data:', error);
                loadingDiv.style.display = 'none';
                summaryStatsDiv.style.display = 'none';
                callsTableBody.innerHTML = '<tr><td colspan="8" style="text-align: center;">Error loading call data. Please try again later.</td></tr>';
            });
        } else {
            // Use cached data with client-side filtering if needed
            console.log('Using cached data - no server request needed');
            
            // Apply any needed client-side filtering
            const filteredData = applyClientSideFilters(callDataCache.data, currentQuery);
            
            // Render filtered data
            renderCallData(filteredData);
            updateSummaryStats(filteredData);
            summaryStatsDiv.style.display = 'flex';
        }
    }
    
    // Determine if we need to reload data from server
    function shouldReload(currentQuery) {
        // If no cache exists, always reload
        if (!callDataCache.lastQuery || !callDataCache.data) {
            return true;
        }
        
        // Check if cache is older than 60 minutes (3,600,000 milliseconds)
        const cacheAge = Date.now() - callDataCache.timestamp;
        const cacheExpiryTime = 60 * 60 * 1000; // 60 minutes in milliseconds
        
        if (cacheAge > cacheExpiryTime) {
            console.log("Cache expired (older than 60 minutes). Reloading data.");
            return true;
        }
        
        // Only reload if date range changed
        if (currentQuery.date_from !== callDataCache.lastQuery.date_from || 
            currentQuery.date_to !== callDataCache.lastQuery.date_to) {
            return true;
        }
        
        // For all other filters (including agent selection), use client-side filtering
        // For this to work properly, we need to ensure the initial query uses 'all' for agent_id,
        // call_type, and call_status to have the complete dataset in the cache
        
        // Check if cached query is a superset of current query for filters
        const cacheSupportsQuery = (
            (callDataCache.lastQuery.agent_id === 'all' || 
             currentQuery.agent_id === callDataCache.lastQuery.agent_id) &&
            (callDataCache.lastQuery.call_type === 'all' || 
             currentQuery.call_type === callDataCache.lastQuery.call_type) &&
            (callDataCache.lastQuery.call_status === 'all' || 
             currentQuery.call_status === callDataCache.lastQuery.call_status)
        );
        
        // If cache contains required data, use it
        return !cacheSupportsQuery;
    }
    
    // Apply client-side filters to cached data
    function applyClientSideFilters(cachedData, query) {
        if (!cachedData) return [];
        
        return cachedData.filter(call => {
            // Apply agent filter if changed from 'all'
            if (query.agent_id !== 'all' && call.agent_id !== query.agent_id) {
                return false;
            }
            
            // Apply call_type filter if changed from 'all'
            if (query.call_type !== 'all' && call.call_type !== query.call_type) {
                return false;
            }
            
            // Apply call_status filter if changed from 'all'
            if (query.call_status !== 'all' && call.status !== query.call_status) {
                return false;
            }
            
            return true;
        });
    }
    
    function renderCallData(calls) {
        let tableHtml = '';
        // Track phone numbers for handled_elsewhere and missed status to avoid duplicates
        const handledElsewherePhones = new Map();
        const missedCallPhones = new Map();
        
        // First, consolidate handled_elsewhere and missed calls by phone number
        calls.forEach(call => {
            // For consolidating handled_elsewhere calls
            if (call.status === 'handled_elsewhere') {
                if (!handledElsewherePhones.has(call.customer_phone)) {
                    handledElsewherePhones.set(call.customer_phone, call);
                }
            } 
            // For consolidating missed calls
            else if (call.status === 'missed') {
                if (!missedCallPhones.has(call.customer_phone)) {
                    missedCallPhones.set(call.customer_phone, call);
                } else {
                    // If we already have a missed call for this phone, update status details
                    const existingCall = missedCallPhones.get(call.customer_phone);
                    if (call.status_details && !existingCall.status_details.includes(call.status_details)) {
                        existingCall.status_details += `, ${call.status_details}`;
                    }
                }
            }
        });
        
        // Render calls, skipping duplicates for handled_elsewhere and missed
        calls.forEach(call => {
            // Skip if this is a duplicate handled_elsewhere call
            if (call.status === 'handled_elsewhere' && 
                handledElsewherePhones.get(call.customer_phone) !== call) {
                return;
            }
            
            // Skip if this is a duplicate missed call
            if (call.status === 'missed' && 
                missedCallPhones.get(call.customer_phone) !== call) {
                return;
            }
            
            // Modify agent name display for consolidated entries
            let agentDisplay = call.agent_name;
            if (call.status === 'handled_elsewhere') {
                agentDisplay = 'Multiple Agents';
            } else if (call.status === 'missed' && call.status_details && 
                      call.status_details.includes('Also missed by:')) {
                agentDisplay = 'Multiple Agents';
            }
                
            tableHtml += `
                <tr class="call-type-${call.call_type}">
                    <td>${call.datetime}</td>
                    <td>${agentDisplay}</td>
                    <td>${call.customer_name || 'Unknown'}</td>
                    <td>${call.customer_phone}</td>
                    <td>${call.call_type}</td>
                    <td>${call.duration} min</td>
                    <td class="status-${call.status}">${call.status}
                    ${call.status_details ? `<div class="status-details">${call.status_details}</div>` : ''}
                </td>
                    <td>
                        ${call.recording_url 
                          ? `<a href="${call.recording_url}" target="_blank" class="recording-link">Listen</a>` 
                          : 'N/A'}
                    </td>
                </tr>
            `;
        });
        
        callsTableBody.innerHTML = tableHtml;
    }
    
    function updateSummaryStats(calls) {
        // Calculate summary statistics
        const totalCalls = calls.length;
        
        // Only count inbound calls that were completed or missed with "Also missed by:" text
        const inboundCalls = calls.filter(call => 
            call.call_type === 'inbound' && 
            (call.status === 'completed' || 
             (call.status === 'missed' && call.status_details && call.status_details.includes('Also missed by:')))
        ).length;
        
        const outboundCalls = calls.filter(call => call.call_type === 'outbound').length;
        // Count missed calls that include "Also missed by:" details
        const missedCalls = calls.filter(call => 
            call.status === 'missed' && 
            (call.status_details && call.status_details.includes('Also missed by:'))
        ).length;
        
        // Calculate average duration for completed calls
        const completedCalls = calls.filter(call => call.status === 'completed');
        let avgDuration = 0;
        if (completedCalls.length > 0) {
            const totalDuration = completedCalls.reduce((sum, call) => sum + parseFloat(call.duration), 0);
            avgDuration = (totalDuration / completedCalls.length).toFixed(1);
        }
        
        
        // Update UI
        document.getElementById('total-calls').textContent = totalCalls;
        document.getElementById('inbound-calls').textContent = inboundCalls;
        document.getElementById('outbound-calls').textContent = outboundCalls;
        document.getElementById('missed-calls').textContent = missedCalls;
        document.getElementById('avg-duration').textContent = avgDuration + ' min';
    }
    
    // Set default date range to last 7 days if not already set
    const dateFromInput = document.getElementById('date-from');
    const dateToInput = document.getElementById('date-to');
    
    if (!dateFromInput.value) {
        const lastWeek = new Date();
        lastWeek.setDate(lastWeek.getDate() - 7);
        dateFromInput.value = formatDate(lastWeek);
    }
    
    if (!dateToInput.value) {
        const today = new Date();
        dateToInput.value = formatDate(today);
    }
    
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
});