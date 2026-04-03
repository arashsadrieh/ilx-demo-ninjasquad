/*
SCORM 1.2 API Wrapper
Cloud Computing: Multi-Cloud Migration Strategy — GCP to AWS Platform Transition

Based on ADL SCORM 1.2 Runtime Environment specification.
Implements API discovery, initialization, data access, and error handling.
*/

// ADL API Discovery Algorithm
var findAPITries = 0;

function findAPI(win) {
    while ((win.API == null) && (win.parent != null) && (win.parent != win)) {
        findAPITries++;
        if (findAPITries > 7) {
            alert("Error finding API -- too deeply nested.");
            return null;
        }
        win = win.parent;
    }
    return win.API;
}

function getAPI() {
    var theAPI = findAPI(window);
    if ((theAPI == null) && (window.opener != null) && (typeof(window.opener) != "undefined")) {
        theAPI = findAPI(window.opener);
    }
    if (theAPI == null) {
        alert("Unable to find an API adapter");
    }
    return theAPI;
}

// Constants
var SCORM_TRUE = "true";
var SCORM_FALSE = "false";
var SCORM_NO_ERROR = "0";

var finishCalled = false;
var initialized = false;
var API = null;

function ScormProcessInitialize() {
    var result;
    API = getAPI();
    if (API == null) {
        alert("ERROR - Could not establish a connection with the LMS.\n\nYour results may not be recorded.");
        return;
    }
    result = API.LMSInitialize("");
    if (result == SCORM_FALSE) {
        var errorNumber = API.LMSGetLastError();
        var errorString = API.LMSGetErrorString(errorNumber);
        var diagnostic = API.LMSGetDiagnostic(errorNumber);
        var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
        alert("Error - Could not initialize communication with the LMS.\n\nYour results may not be recorded.\n\n" + errorDescription);
        return;
    }
    initialized = true;
}

function ScormProcessFinish() {
    var result;
    if (initialized == false || finishCalled == true) { return; }
    result = API.LMSFinish("");
    finishCalled = true;
    if (result == SCORM_FALSE) {
        var errorNumber = API.LMSGetLastError();
        var errorString = API.LMSGetErrorString(errorNumber);
        var diagnostic = API.LMSGetDiagnostic(errorNumber);
        var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
        alert("Error - Could not terminate communication with the LMS.\n\nYour results may not be recorded.\n\n" + errorDescription);
        return;
    }
}

function ScormProcessGetValue(element) {
    var result;
    if (initialized == false || finishCalled == true) { return ""; }
    result = API.LMSGetValue(element);
    if (result == "") {
        var errorNumber = API.LMSGetLastError();
        if (errorNumber != SCORM_NO_ERROR) {
            var errorString = API.LMSGetErrorString(errorNumber);
            var diagnostic = API.LMSGetDiagnostic(errorNumber);
            var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
            alert("Error - Could not retrieve a value from the LMS.\n\n" + errorDescription);
            return "";
        }
    }
    return result;
}

function ScormProcessSetValue(element, value) {
    var result;
    if (initialized == false || finishCalled == true) { return; }
    result = API.LMSSetValue(element, value);
    if (result == SCORM_FALSE) {
        var errorNumber = API.LMSGetLastError();
        var errorString = API.LMSGetErrorString(errorNumber);
        var diagnostic = API.LMSGetDiagnostic(errorNumber);
        var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
        alert("Error - Could not store a value in the LMS.\n\nYour results may not be recorded.\n\n" + errorDescription);
        return;
    }
}

function ScormProcessCommit() {
    var result;
    if (initialized == false || finishCalled == true) { return; }
    result = API.LMSCommit("");
    if (result == SCORM_FALSE) {
        var errorNumber = API.LMSGetLastError();
        var errorString = API.LMSGetErrorString(errorNumber);
        var diagnostic = API.LMSGetDiagnostic(errorNumber);
        var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
        alert("Error - Could not commit data to the LMS.\n\n" + errorDescription);
        return;
    }
}
