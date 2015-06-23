/*
 * Google Apps Script
 *
 * Deploy on Google Drive.
 */


// Some stuff we'll want to configure later:

// The Google Drive ID for the folder where spreadsheets are copied:
var FOLDER_ID = "1ZGnMcp8EeVDwpP2kVjWG3Vu317Ujdc6yXht8K2_QSf0";

//
var GEO_BOUNDS = [42.371861543730496, -71.13338470458984, 42.40393908425197, -71.0679817199707];



/**
 * Scans the contents of the given folder and returns the most recently added
 * spreadsheet document.
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
      names = namesRange.getValues()[0].map(function(s) { return s.trim(); });
      dataRange = sheet.getRange(startRow, 1, rows, columns),
        data = dataRange.getValues();

  var rowMaps = [];

  debugger;
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
* @param {Array|Object} data
* @param {Function} addressFn A function that will be called on each rowMap to retrieve its address string.
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
* @return {String} The string address
*/
function getAddress(rowMap) {
  return rowMap["Number"] + " " + rowMap["Street"];
}

function extractData() {
  var id = "1ZGnMcp8EeVDwpP2kVjWG3Vu317Ujdc6yXht8K2_QSf0",
      doc = SpreadsheetApp.openById(id),
      sheet = doc.getSheets()[0];

  var data = getData(sheet, 3, 4),
      coder = Maps.newGeocoder().setBounds(GEO_BOUNDS[0], GEO_BOUNDS[1],
                                           GEO_BOUNDS[2], GEO_BOUNDS[3]);
  addLatLong(data, getAddress, coder);
  return data;
}




function doGet(req) {
  var output = ContentService.createTextOutput(),
      data = extractData();

  output.append(JSON.stringify(data));

  return output;
}
