/*
SCORM 1.2 API Wrapper
Handles communication between the course and the LMS.
*/

var scormAPI = null;
var scormConnected = false;

function ScormFindAPI(win) {
  var attempts = 0;
  while ((!win.API) && (win.parent) && (win.parent !== win)) {
    attempts++;
    if (attempts > 10) return null;
    win = win.parent;
  }
  return win.API || null;
}

function ScormGetAPI() {
  var api = ScormFindAPI(window);
  if (!api && window.opener) {
    api = ScormFindAPI(window.opener);
  }
  return api;
}

function ScormConnect() {
  scormAPI = ScormGetAPI();
  if (scormAPI) {
    var result = scormAPI.LMSInitialize("");
    scormConnected = (result === "true" || result === true);
  }
  return scormConnected;
}

function ScormDisconnect() {
  if (scormAPI && scormConnected) {
    scormAPI.LMSFinish("");
    scormConnected = false;
  }
}

function ScormGetValue(key) {
  if (scormAPI && scormConnected) {
    return scormAPI.LMSGetValue(key);
  }
  return "";
}

function ScormSetValue(key, value) {
  if (scormAPI && scormConnected) {
    return scormAPI.LMSSetValue(key, value);
  }
  return "false";
}

function ScormCommit() {
  if (scormAPI && scormConnected) {
    return scormAPI.LMSCommit("");
  }
  return "false";
}

function ScormGetLastError() {
  if (scormAPI) {
    return scormAPI.LMSGetLastError();
  }
  return "0";
}
