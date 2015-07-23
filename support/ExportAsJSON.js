/*
 * A Google Apps Script for converting the contents of a spreadsheet to
 * JSON.
 *
 * Deploy on Google Drive. From the menu, select Publish > Deploy as web
 * app.
 */


// Some stuff we'll want to configure later:

// The Google Drive ID for the folder where spreadsheets are copied:
var FOLDER_ID = "0BxbaygscqZcVfmlFU1pvNXQzWkxvVWZvdGZ3QkNPREpFRmVnN3FxVnRGaC1qVURRZ3YxQU0";

// Confine the geocoding to a specified region.
var GEO_BOUNDS = [42.371861543730496, -71.13338470458984,
                  42.40393908425197, -71.0679817199707];

var GEO_SEARCH_SUFFIX = "Somerville, MA";

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
 * @return {File} The file containing the most recently created spreadsheet
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

    return latestFile;
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

        var rowMap = rowVals.reduce(function(result, cellVal, i) {
            result[names[i]] = cellVal;
            return result;
        }, {});

        // Get the row background color, since it might contain useful
        // information:
        rowMap["numberColor"] = sheet.getRange(startRow+i, 1, 1, 1).getBackground();
        rowMap["rowColor"] = sheet.getRange(startRow+i, 2, 1, 1).getBackground();

        rowMaps.push(rowMap);
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
 * Modifies the members of the data array in place.
 *
 * @param {Array|Object} data
 * @param {Function} addressFn A function that will be called on each
 * rowMap to retrieve its address string.
 * @param {Geocoder} coder
 * @return
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
 * @nosideeffects
 * @param {Object} rowMap Object representing the data in a row.
 * @return {String} The string address
 */
function getAddress(rowMap) {
    return rowMap["number"] + " " + rowMap["street"] + " " + GEO_SEARCH_SUFFIX;
}

/**
 * Extracts data from the spreadsheet contained in the specified file. Stores the response in cache, keyed by
 * the last updated date for the spreadsheet.
 *
 * @param {File} docFile The Google Drive file containing the spreadsheet
 * @param {Boolean} noCache  Ignore the stored response
 * @return {String} JSON representing the extracted data
 */
function extractData(docFile, noCache) {
    // Check the cache first to avoid geocoding again.
    // The data is keyed by the string "data-" + the timestamp of the last
    // document modification and stored as JSON.
    var cache = CacheService.getScriptCache(),
        lastModified = docFile.getLastUpdated().valueOf().toString(),
        cacheKey = "json-data-" + lastModified,
        found = !noCache && cache.get(cacheKey);

    if (found)
        return found;

    var doc = SpreadsheetApp.open(docFile),
        sheet = doc.getSheets()[0];

    var data = getData(sheet, 3, 4),
        coder = Maps.newGeocoder().setBounds(GEO_BOUNDS[0], GEO_BOUNDS[1],
                                             GEO_BOUNDS[2], GEO_BOUNDS[3]);
    addLatLong(data, getAddress, coder);

    var json = JSON.stringify(data);

    cache.put(cacheKey, json);

    return json;
}

function getLatestFile() {
    return findLatestSpreadsheet(DriveApp.getFolderById(FOLDER_ID));
}

/**
 * Function called on a timed trigger. Calls extractData() in order to update the stored results.
 */
function runPeriodic() {
    var latestFile = getLatestFile();

    // Rely on extractData()'s side-effects to update the cache. Ignore its return value
    if (latestFile)
        extractData(latestFile, true);
}

function testGeneration() {
    Logger.log(extractData(getLatestFile(), true));
}

/**
 * Function called when the script is executed as a web service.
 * @return {TextOutput}
 */
function doGet(req) {
    var output = ContentService.createTextOutput(),
        latestFile = getLatestFile();

    if (!latestFile)
        return output;

    var data = extractData(latestFile),
        cb = req.parameter.callback;

    output.setMimeType(cb ? ContentService.MimeType.JAVASCRIPT : ContentService.MimeType.JSON);

    if (cb) {
        output.append(cb);
        output.append("(");
    }

    output.append(data);

    if (cb) {
        output.append(")");
    }

    return output;
}
