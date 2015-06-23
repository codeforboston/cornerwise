/*
 * A Google Apps Script for converting the contents of a spreadsheet to
 * JSON.
 *
 *
 * Deploy on Google Drive. From the menu, select Publish > Deploy as web
 * app.
 */


// Some stuff we'll want to configure later:

// The Google Drive ID for the folder where spreadsheets are copied:
var FOLDER_ID = "1ZGnMcp8EeVDwpP2kVjWG3Vu317Ujdc6yXht8K2_QSf0";

// Confine the geocoding to a specified region.
var GEO_BOUNDS = [42.371861543730496, -71.13338470458984,
                  42.40393908425197, -71.0679817199707];

// Function mapping <name in spreadsheet> to <name in JSON>
var JSON_COLUMN = function(name) {
    if (name == "Case")
        return "caseNumber";

    return name.toLowerCase();
};

/**
 * Scans the contents of the given folder and returns the most recently
 * added spreadsheet document.
 *
 * @param {Folder} folder
 * @return {File}
 */
function findLatestSpreadsheet(folder) {
    var files = folder.getFilesByType(MimeType.GOOGLE_SHEETS),
        latest = 0,
        latestFile = null;

    while (files.hasNext()) {
        var file = files.next();

        if (file.getDateCreated() > latest) {
            latest = file.getDateCreated();
            latestFile = file;
        }
    }

    return SpreadsheetApp.open(latestFile);
}

function isEmpty(cellVal) {
    if (typeof cellVal == "string") {
        return !cellVal.trim();
    }

    return false;
}

/**
 * @param {Sheet} sheet
 * @param {Number} namesRow
 * @param {Number} startRow
 *
 */
function getData(sheet, namesRow, startRow, columns, rows) {
    columns = columns || sheet.getLastColumn();
    rows = rows || sheet.getLastRow()-startRow+1;

    var namesRange = sheet.getRange(namesRow, 1, 1, columns),
        docNames = namesRange.getValues()[0].map(function(s) { return s.trim(); }),
        names = docNames.map(JSON_COLUMN);
    dataRange = sheet.getRange(startRow, 1, rows, columns),
    data = dataRange.getValues();

    var rowMaps = [];

    for (var i = 0, l = data.length; i < l; i++) {
        var rowVals = data[i];

        // Hacky: Stop execution when the first cell of a row is 'empty'.
        if (!rowVals || isEmpty(rowVals[0])) {
            break;
        }

        rowMaps.push(rowVals.reduce(function(result, cellVal, i) {
            result[names[i]] = cellVal;
            return result;
        }, {}));
    }

    return rowMaps;
}

/**
 * Convert an array of rows into an object that maps fn(row) => row.
 *
 * @param {Array} rows
 * @param {Function} fn
 * @return {Object}
 */
function indexBy(rows, fn) {
    return rows.reduce(function(result, row) {
        result[fn(row)] = row;
        return result;
    }, {});
}

/**
 * Note: Transforms the data array in place!
 *
 * @param {Array} data
 * @param {Array} transFns An array of 2-member arrays of the form [colName, transformationFunction]
 */
function transformRows(data, transFns) {
    data.forEach(function(rowData) {
        return transFns.reduce(function(result, trans) {
            var f = trans[1], colName = trans[0];
            result[colName] = f(result[colName]);
            return result;
        }, rowData);
    });
}


/**
 * @param {Array|Object} data
 * @param {Function} addressFn A function that will be called on each
 * rowMap to retrieve its address string.
 * @param {Geocoder} coder
 */
function addLatLong(data, addressFn, coder) {
    coder = coder || Maps.newGeocoder();

    data.forEach(function(rowData) {
        var response = coder.geocode(addressFn(rowData));

        if (response.results && response.results.length > 0) {
            rowData["location"] = response.results[0].geometry.location;
        }
    });
}


/**
 * @param {Object} rowMap Object representing the data in a row.
 * @return {String} The string address
 */
function getAddress(rowMap) {
    return rowMap["Number"] + " " + rowMap["Street"];
}

/**
 * @return {String} JSON representing the extracted data
 */
function extractData() {
    var id = "1ZGnMcp8EeVDwpP2kVjWG3Vu317Ujdc6yXht8K2_QSf0";

    // Check the cache first to avoid geocoding again.
    // The data is keyed by the string "data-" + the timestamp of the last
    // document modification and stored as JSON.
    var cache = CacheService.getScriptCache(),
        docFile = DriveApp.getFileById(id),
        lastModified = docFile.getLastUpdated().valueOf().toString(),
        cacheKey = "data-" + lastModified,
        found = cache.get(cacheKey)

    if (found)
        return found;

    var doc = SpreadsheetApp.openById(id),
        sheet = doc.getSheets()[0];

    var data = getData(sheet, 3, 4),
        coder = Maps.newGeocoder().setBounds(GEO_BOUNDS[0], GEO_BOUNDS[1],
                                             GEO_BOUNDS[2], GEO_BOUNDS[3]);
    addLatLong(data, getAddress, coder);

    var json = JSON.stringify(data);

    cache.put(cacheKey, json);

    return json;
}


/**
 * Function called when the script is executed as a web service.
 * @return {TextOutput}
 */
function doGet(req) {
    var output = ContentService.createTextOutput(),
        data = extractData();

    output.setMimeType(ContentService.MimeType.JSON);

    output.append(data);

    return output;
}
