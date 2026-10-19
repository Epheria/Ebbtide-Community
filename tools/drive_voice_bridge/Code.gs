/* Ebbtide recording intake. Keep this standalone Apps Script project owner-only.
 * No web app, GitHub token, OAuth token, or shared-sheet script is required.
 */
var VB = Object.freeze({
  uploads: 'Recording Uploads', outbox: 'Recording Outbox',
  inputHeaders: ['Take file', 'Drive URL', 'Ready to submit', 'Result'],
  outputHeaders: ['Work order', 'Take file', 'Drive snapshot', 'SHA256', 'Bytes',
    'MIME type', 'Revision', 'Submitted', 'Script SHA256'],
  maxFile: 20 * 1024 * 1024, maxBatch: 100 * 1024 * 1024, maxKeys: 200, maxOutboxRows: 20000,
  configPrefix: 'VOICE_BRIDGE_CONFIG_', configChunk: 7000
});

/** Initial Ebbtide setup; preserves any assignments already registered by owner. */
function bootstrapOwnerConfiguration() {
  var existing = PropertiesService.getScriptProperties().getProperty(VB.configPrefix + 'COUNT');
  var config = existing ? loadConfig_() : {
    coordinatorSpreadsheetId: '1ObgnTm9lYXfxNpR1gkrFSkhU_OmkFCkIqfEqps0S-Vs',
    incomingRootFolderId: '17PYW1pdUd9GtPSUNoOtxieipN873Toi8',
    archiveRootFolderId: '14Av9lG72g3m_q_7fE5KusGtkXeGQvJ2l',
    assignments: []
  };
  return setupCoordinator(config);
}

/** Run as the coordinator once after reviewing the configuration in the guide. */
function setupCoordinator(config) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    config = validateConfig_(config);
    requireOwner_(DriveApp.getFileById(config.coordinatorSpreadsheetId));
    assertPrivateFolder_(DriveApp.getFolderById(config.incomingRootFolderId));
    assertPrivateFolder_(DriveApp.getFolderById(config.archiveRootFolderId));
    config.assignments.forEach(function (a) {
      requireOwner_(DriveApp.getFileById(a.workingSpreadsheetId));
      assertChildFolder_(a.uploadFolderId, config.incomingRootFolderId, false);
      assertChildFolder_(a.archiveFolderId, config.archiveRootFolderId, true);
    });
    var outbox = SpreadsheetApp.openById(config.coordinatorSpreadsheetId).getSheetByName(VB.outbox);
    if (!outbox) throw new Error('Coordinator workbook is missing Recording Outbox.');
    requireHeaders_(outbox, VB.outputHeaders);
    protectOutbox_(outbox);
    saveConfig_(config);
    // Only this project creates these triggers; leave unrelated project triggers alone.
    ScriptApp.getProjectTriggers().filter(function (t) {
      return ['voiceBridgeOnEdit', 'voiceBridgeOnOpen'].indexOf(t.getHandlerFunction()) >= 0;
    }).forEach(function (t) { ScriptApp.deleteTrigger(t); });
    var workbookIds = Array.from(new Set(config.assignments.map(function (a) { return a.workingSpreadsheetId; })));
    workbookIds.forEach(function (id) {
      var book = SpreadsheetApp.openById(id);
      var sheet = book.getSheetByName(VB.uploads);
      if (!sheet) throw new Error('An assigned workbook is missing Recording Uploads.');
      requireHeaders_(sheet, VB.inputHeaders);
      ScriptApp.newTrigger('voiceBridgeOnEdit').forSpreadsheet(id).onEdit().create();
    });
    return {assignments: config.assignments.length, workbooks: workbookIds.length, ready: true};
  } finally { lock.releaseLock(); }
}

/** Owner-only health check: works with an empty assignment registry. */
function coordinatorHealthCheck() {
  var config = loadConfig_();
  requireOwner_(DriveApp.getFileById(config.coordinatorSpreadsheetId));
  assertPrivateFolder_(DriveApp.getFolderById(config.incomingRootFolderId));
  assertPrivateFolder_(DriveApp.getFolderById(config.archiveRootFolderId));
  requireHeaders_(SpreadsheetApp.openById(config.coordinatorSpreadsheetId).getSheetByName(VB.outbox), VB.outputHeaders);
  return {configured: true, assignments: config.assignments.length, githubCredentialStored: false};
}

/** Installed onEdit runs with the owner's authority; the editor is never trusted. */
function voiceBridgeOnEdit(e) {
  if (!e || !e.source || !e.range || e.range.getSheet().getName() !== VB.uploads) return;
  if (e.range.getColumn() > 3 || e.range.getLastColumn() < 3 || e.range.getLastRow() < 2) return;
  processWorkbook_(e.source.getId());
}

/** Manual fallback: run from the owner's script editor. */
function submitReadyRecordings() {
  var config = loadConfig_();
  config.assignments.forEach(function (a, i) {
    if (config.assignments.findIndex(function (b) { return b.workingSpreadsheetId === a.workingSpreadsheetId; }) === i) {
      processWorkbook_(a.workingSpreadsheetId);
    }
  });
}

function processWorkbook_(spreadsheetId) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) throw new Error('Another submission is running. Try again later.');
  try {
    var config = loadConfig_();
    var assignments = config.assignments.filter(function (a) { return a.workingSpreadsheetId === spreadsheetId; });
    if (assignments.length !== 1) throw new Error('Workbook is not uniquely registered. Contact the coordinator.');
    var assignment = assignments[0];
    var book = SpreadsheetApp.openById(spreadsheetId);
    var sheet = book.getSheetByName(VB.uploads);
    requireHeaders_(sheet, VB.inputHeaders);
    if (sheet.getLastRow() > VB.maxKeys + 1) {
      sheet.getRange(2, 4).setValue('Not submitted: Keep at most 200 populated take rows in Recording Uploads.');
      throw new Error('Recording Uploads exceeds 200 populated take rows.');
    }
    var rows = sheet.getLastRow() < 2 ? [] : sheet.getRange(2, 1, sheet.getLastRow() - 1, 4).getValues();
    if (!rows.some(function (row) { return row[2] === true; })) return;
    try {
      var requested = selectReadyRows_(rows, assignment);
      assertPrivateFolder_(DriveApp.getFolderById(config.incomingRootFolderId));
      assertPrivateFolder_(DriveApp.getFolderById(config.archiveRootFolderId));
      assertChildFolder_(assignment.uploadFolderId, config.incomingRootFolderId, false);
      assertChildFolder_(assignment.archiveFolderId, config.archiveRootFolderId, true);
      var incoming = DriveApp.getFolderById(assignment.uploadFolderId);
      var total = 0;
      var files = requested.map(function (row) {
        var file = uniqueNamedFile_(incoming, row.name);
        if (row.url && driveId_(row.url) !== file.getId()) throw new Error('Drive URL does not match the assigned folder file.');
        if (file.getMimeType() === 'application/vnd.google-apps.shortcut') throw new Error('Drive shortcuts are not accepted.');
        requireImmediateParent_(file, assignment.uploadFolderId);
        if (file.getSize() > VB.maxFile) throw new Error('Audio must be at most 20 MiB per file.');
        if (total + file.getSize() > VB.maxBatch) throw new Error('Submission exceeds 100 MiB; ask for a smaller work order.');
        var bytes = file.getBlob().getBytes();
        var info = inspectAudio_(row.name, bytes);
        total += bytes.length;
        if (total > VB.maxBatch) throw new Error('Submission exceeds 100 MiB; ask for a smaller work order.');
        return {name: row.name, key: row.key, id: file.getId(), sha256: sha256_(bytes), bytes: bytes.length, mime: info.mime};
      });
      var contentDigest = sha256_(Utilities.newBlob(JSON.stringify({
        issue: assignment.issue, scriptHash: assignment.scriptHash,
        files: files.map(function (f) { return [f.key, f.name, f.sha256, f.bytes, f.mime]; })
      })).getBytes());
      var outbox = SpreadsheetApp.openById(config.coordinatorSpreadsheetId).getSheetByName(VB.outbox);
      requireHeaders_(outbox, VB.outputHeaders);
      protectOutbox_(outbox);
      var revision = resolveRevision_(outbox, assignment, contentDigest, files);
      if (receiptExists_(outbox, assignment, revision, files)) {
        verifyArchivedReceipt_(outbox, assignment, revision);
        writeResult_(sheet, requested, 'Submitted — existing receipt ' + revision, true);
        return;
      }
      if (outbox.getLastRow() - 1 + files.length > VB.maxOutboxRows) throw new Error('Outbox capacity reached. Coordinator must archive completed work orders.');
      var archive = DriveApp.getFolderById(assignment.archiveFolderId);
      var receiptFolder = uniqueReceiptFolder_(archive, 'work-' + assignment.issue + '-' + revision);
      var submitted = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
      var receipt = files.map(function (item) {
        var existing = receiptFolder.getFilesByName(item.name);
        var copy;
        if (existing.hasNext()) {
          copy = existing.next();
          if (existing.hasNext()) throw new Error('Duplicate archived take. Coordinator must resolve it.');
          requireOwner_(copy); requireImmediateParent_(copy, receiptFolder.getId());
          if (copy.getSharingAccess() !== DriveApp.Access.PRIVATE || copy.getEditors().length) throw new Error('Archived take changed. Coordinator must resolve it.');
          if (copy.getSize() !== item.bytes || copy.getSize() > VB.maxFile) throw new Error('Archived take changed. Coordinator must resolve it.');
          if (sha256_(copy.getBlob().getBytes()) !== item.sha256) throw new Error('Archived take changed. Coordinator must resolve it.');
        } else {
          var source = DriveApp.getFileById(item.id);
          requireImmediateParent_(source, assignment.uploadFolderId);
          if (source.getSize() !== item.bytes || source.getSize() > VB.maxFile) throw new Error('Upload changed during intake. Check it and submit again.');
          var blob = source.getBlob();
          if (sha256_(blob.getBytes()) !== item.sha256 || source.getName() !== item.name) {
            throw new Error('Upload changed during intake. Check it and submit again.');
          }
          copy = receiptFolder.createFile(blob.setName(item.name).setContentType(item.mime));
          requireOwner_(copy);
        }
        return [assignment.issue, item.key, 'https://drive.google.com/file/d/' + copy.getId() + '/view',
          item.sha256, item.bytes, item.mime, revision, submitted, assignment.scriptHash];
      });
      // One range write commits the entire batch only after every private copy exists.
      outbox.getRange(outbox.getLastRow() + 1, 1, receipt.length, VB.outputHeaders.length).setValues(receipt);
      SpreadsheetApp.flush();
      if (!receiptExists_(outbox, assignment, revision, files)) throw new Error('Receipt could not be verified. Retry safely.');
      writeResult_(sheet, requested, 'Submitted — receipt ' + revision + '. Awaiting listening review.', true);
    } catch (error) {
      rows.forEach(function (row, index) {
        if (row[2] === true) sheet.getRange(index + 2, 4).setValue('Not submitted: ' + safeError_(error));
      });
      throw error;
    }
  } finally { lock.releaseLock(); }
}

function selectReadyRows_(rows, a) {
  var selected = [], seen = Object.create(null);
  rows.forEach(function (row, index) {
    if (row[2] !== true) return;
    var match = /^([A-Za-z0-9_][A-Za-z0-9_.-]{0,127})\.(wav|flac)$/.exec(String(row[0]));
    if (!match || match[1].indexOf('..') >= 0 || /\.(wav|flac)$/i.test(match[1])) throw new Error('Use one exact assigned filename with .wav or .flac.');
    var key = match[1];
    if (a.keys.indexOf(key) < 0 || seen[key]) throw new Error('Unassigned or duplicate take file.');
    var url = row[1] === '' ? '' : String(row[1]);
    if (url) driveId_(url);
    seen[key] = true;
    selected.push({key: key, name: String(row[0]), url: url, row: index + 2});
  });
  if (selected.length !== a.keys.length) throw new Error('Check every assigned take before submitting this work order.');
  return a.keys.map(function (key) { return selected.filter(function (r) { return r.key === key; })[0]; });
}

function driveId_(url) {
  var match = /^https:\/\/drive\.google\.com\/file\/d\/([A-Za-z0-9_-]{10,})\/view(?:\?usp=(?:sharing|drive_link))?$/.exec(url);
  if (!match) throw new Error('Use a direct Drive file link, or leave Drive URL blank.');
  return match[1];
}

function inspectAudio_(name, raw) {
  var b = Array.prototype.map.call(raw, function (x) { return x & 255; });
  if (b.length < 42 || b.length > VB.maxFile) throw new Error('Audio must be nonempty and at most 20 MiB per file.');
  var text = function (i, n) { return String.fromCharCode.apply(null, b.slice(i, i + n)); };
  var rate, channels, bits, hasData = false, dataLengths = [];
  if (/\.wav$/.test(name)) {
    if (text(0, 4) !== 'RIFF' || text(8, 4) !== 'WAVE' || le32_(b, 4) + 8 !== b.length) throw new Error('Invalid or truncated WAV header.');
    var fmt = false;
    for (var i = 12; i + 8 <= b.length;) {
      var length = le32_(b, i + 4), start = i + 8;
      if (start + length > b.length) throw new Error('Invalid WAV chunk length.');
      if (text(i, 4) === 'fmt ') {
        if (fmt || length < 16) throw new Error('Invalid WAV format chunk.');
        var format = le16_(b, start);
        channels = le16_(b, start + 2); rate = le32_(b, start + 4); bits = le16_(b, start + 14);
        var extensiblePcm = format === 65534 && length >= 40 && le16_(b, start + 16) >= 22 &&
          text(start + 24, 16) === '\x01\x00\x00\x00\x00\x00\x10\x00\x80\x00\x00\xaa\x00\x38\x9b\x71';
        if (format !== 1 && !extensiblePcm) throw new Error('Use PCM WAV, 16-bit or 24-bit.');
        if (le16_(b, start + 12) !== channels * bits / 8 || le32_(b, start + 8) !== rate * channels * bits / 8) throw new Error('Invalid WAV sample alignment.');
        fmt = true;
      }
      if (text(i, 4) === 'data' && length > 0) { hasData = true; dataLengths.push(length); }
      i = start + length + (length % 2);
    }
    if (!fmt || !hasData) throw new Error('WAV needs a format chunk and audio samples.');
    if (i !== b.length || dataLengths.some(function (n) { return n % (channels * bits / 8) !== 0; })) throw new Error('Invalid WAV sample alignment or trailing chunk bytes.');
  } else if (/\.flac$/.test(name)) {
    if (text(0, 4) !== 'fLaC' || (b[4] & 127) !== 0 || b[5] !== 0 || b[6] !== 0 || b[7] !== 34) throw new Error('Invalid FLAC STREAMINFO header.');
    rate = (b[18] << 12) | (b[19] << 4) | (b[20] >>> 4);
    channels = ((b[20] >>> 1) & 7) + 1; bits = (((b[20] & 1) << 4) | (b[21] >>> 4)) + 1;
    var samples = (b[21] & 15) * 4294967296 + b[22] * 16777216 + b[23] * 65536 + b[24] * 256 + b[25];
    if (!samples || b.length <= 42) throw new Error('FLAC has no declared audio samples.');
  } else { throw new Error('Only .wav or .flac files are accepted.'); }
  if (channels !== 1 || [44100, 48000].indexOf(rate) < 0 || [16, 24].indexOf(bits) < 0) throw new Error('Use mono, 44.1/48 kHz, 16/24-bit audio.');
  return {mime: /\.wav$/.test(name) ? 'audio/wav' : 'audio/flac', sampleRate: rate, channels: channels, bits: bits};
}

function le16_(b, i) { return b[i] + b[i + 1] * 256; }
function le32_(b, i) { return b[i] + b[i + 1] * 256 + b[i + 2] * 65536 + b[i + 3] * 16777216; }
function sha256_(bytes) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, bytes).map(function (b) { return ('0' + ((b + 256) % 256).toString(16)).slice(-2); }).join('');
}
function validateConfig_(config) {
  if (!config || !Array.isArray(config.assignments)) throw new Error('Configuration must contain assignments.');
  if (config.assignments.length > 18) throw new Error('Use at most 18 active recording workbooks in one coordinator project.');
  ['coordinatorSpreadsheetId', 'incomingRootFolderId', 'archiveRootFolderId'].forEach(function (key) { validId_(config[key]); });
  var issues = {}, books = {}, folders = {};
  config.assignments.forEach(function (a) {
    if (!Number.isSafeInteger(a.issue) || a.issue < 1 || issues[a.issue]) throw new Error('Duplicate or invalid work-order issue.');
    ['workingSpreadsheetId', 'uploadFolderId', 'archiveFolderId'].forEach(function (key) { validId_(a[key]); });
    if (books[a.workingSpreadsheetId] || folders[a.uploadFolderId] || folders[a.archiveFolderId]) throw new Error('Assignments need distinct workbooks and folders.');
    if (a.workingSpreadsheetId === config.coordinatorSpreadsheetId || a.uploadFolderId === a.archiveFolderId) throw new Error('Keep actor inputs separate from coordinator metadata.');
    if (!/^[a-f0-9]{64}$/.test(a.scriptHash)) throw new Error('Use the bot assignment script_hash.');
    ['locale', 'role', 'slot'].forEach(function (key) { if (typeof a[key] !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(a[key])) throw new Error('Invalid assignment ' + key); });
    if (!Array.isArray(a.keys) || !a.keys.length || a.keys.length > VB.maxKeys || new Set(a.keys).size !== a.keys.length || a.keys.some(function (key) {
      return typeof key !== 'string' || !/^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$/.test(key) || key.indexOf('..') >= 0 || /\.(wav|flac)$/i.test(key);
    })) throw new Error('Use 1–200 exact assigned source keys without extensions.');
    issues[a.issue] = books[a.workingSpreadsheetId] = folders[a.uploadFolderId] = folders[a.archiveFolderId] = true;
  });
  if (JSON.stringify(config).length > 400000) throw new Error('Coordinator configuration exceeds its bounded storage.');
  return JSON.parse(JSON.stringify(config));
}
function validId_(id) { if (typeof id !== 'string' || !/^[A-Za-z0-9_-]{10,}$/.test(id)) throw new Error('Invalid Drive ID.'); }
function requireOwner_(item) {
  var owner = item.getOwner(), email = Session.getEffectiveUser().getEmail();
  if (!email || !owner || owner.getEmail() !== email) throw new Error('Coordinator must own the configured files and folders.');
}
function assertPrivateFolder_(folder) {
  requireOwner_(folder);
  if (folder.getSharingAccess() !== DriveApp.Access.PRIVATE || folder.getEditors().length || folder.getViewers().length) throw new Error('Archive/root folders must remain owner-only.');
}
function assertChildFolder_(id, parentId, ownerOnly) {
  var folder = DriveApp.getFolderById(id);
  requireOwner_(folder); requireImmediateParent_(folder, parentId);
  if (ownerOnly) assertPrivateFolder_(folder);
  else if (folder.getSharingAccess() !== DriveApp.Access.PRIVATE) throw new Error('Upload folder must use named-person access, not public link access.');
}
function requireImmediateParent_(item, id) {
  var parents = item.getParents(), found = false;
  while (parents.hasNext()) if (parents.next().getId() === id) found = true;
  if (!found) throw new Error('File/folder must be directly inside its registered parent.');
}
function uniqueNamedFile_(folder, name) {
  var iterator = folder.getFilesByName(name);
  if (!iterator.hasNext()) throw new Error('Missing assigned file: ' + name);
  var file = iterator.next();
  if (iterator.hasNext()) throw new Error('Duplicate file name: ' + name + '. Keep one current take.');
  return file;
}
function uniqueReceiptFolder_(parent, name) {
  var iterator = parent.getFoldersByName(name), folder;
  if (iterator.hasNext()) {
    folder = iterator.next();
    if (iterator.hasNext()) throw new Error('Duplicate receipt folders. Contact the coordinator.');
    assertPrivateFolder_(folder);
  } else { folder = parent.createFolder(name); assertPrivateFolder_(folder); }
  return folder;
}
function requireHeaders_(sheet, expected) {
  if (!sheet || JSON.stringify(sheet.getRange(1, 1, 1, expected.length).getValues()[0]) !== JSON.stringify(expected)) throw new Error('Sheet headers differ from the documented template.');
}
function protectOutbox_(sheet) {
  var protections = sheet.getProtections(SpreadsheetApp.ProtectionType.SHEET);
  var protection = protections.filter(function (p) { return p.getDescription() === 'Ebbtide owner-only recording receipts'; })[0] || sheet.protect().setDescription('Ebbtide owner-only recording receipts');
  protection.setWarningOnly(false);
  var owner = Session.getEffectiveUser().getEmail();
  protection.addEditor(owner);
  protection.getEditors().forEach(function (user) { if (user.getEmail() !== owner) protection.removeEditor(user); });
  if (protection.canDomainEdit()) protection.setDomainEdit(false);
  protection.setUnprotectedRanges([]);
}
function receiptExists_(sheet, a, revision, files) {
  if (sheet.getLastRow() > VB.maxOutboxRows + 1) throw new Error('Outbox capacity reached. Coordinator must archive completed work orders.');
  if (sheet.getLastRow() < 2) return false;
  var found = sheet.getRange(2, 1, sheet.getLastRow() - 1, VB.outputHeaders.length).getValues().filter(function (r) { return Number(r[0]) === a.issue && r[6] === revision; });
  if (!found.length) return false;
  if (found.length !== files.length) throw new Error('Incomplete existing receipt. Coordinator must reconcile it before retry.');
  files.forEach(function (file) {
    var rows = found.filter(function (r) { return r[1] === file.key; });
    if (rows.length !== 1 || rows[0][3] !== file.sha256 || Number(rows[0][4]) !== file.bytes || rows[0][5] !== file.mime || rows[0][8] !== a.scriptHash) throw new Error('Existing receipt differs. Coordinator must reconcile it.');
    driveId_(String(rows[0][2]));
  });
  return true;
}
function outboxRows_(sheet, issue) {
  if (sheet.getLastRow() > VB.maxOutboxRows + 1) throw new Error('Outbox capacity reached. Coordinator must archive completed work orders.');
  return sheet.getLastRow() < 2 ? [] : sheet.getRange(2, 1, sheet.getLastRow() - 1, VB.outputHeaders.length).getValues().filter(function (r) { return Number(r[0]) === issue; });
}
function resolveRevision_(sheet, a, contentDigest, files) {
  var rows = outboxRows_(sheet, a.issue);
  if (!rows.length) return contentDigest;
  var latest = rows[rows.length - 1][6];
  if (typeof latest !== 'string' || !/^[a-f0-9]{64}$/.test(latest)) throw new Error('Existing receipt differs. Coordinator must reconcile it.');
  var batch = rows.filter(function (r) { return r[6] === latest; });
  if (batch.length !== a.keys.length || new Set(batch.map(function (r) { return r[1]; })).size !== batch.length) throw new Error('Incomplete existing receipt. Coordinator must reconcile it before retry.');
  var same = batch.length === files.length && files.every(function (file) {
    return batch.some(function (r) { return r[1] === file.key && r[3] === file.sha256 && Number(r[4]) === file.bytes && r[5] === file.mime && r[8] === a.scriptHash; });
  });
  if (same) return latest;
  // Bind a new intake to its predecessor: A -> B -> A gets a fresh revision,
  // while a retry after a partial private-copy operation keeps the same revision.
  return sha256_(Utilities.newBlob(JSON.stringify([contentDigest, latest])).getBytes());
}
function verifyArchivedReceipt_(sheet, a, revision) {
  var rows = outboxRows_(sheet, a.issue).filter(function (r) { return r[6] === revision; });
  var folders = DriveApp.getFolderById(a.archiveFolderId).getFoldersByName('work-' + a.issue + '-' + revision);
  if (!folders.hasNext()) throw new Error('Archived take changed. Coordinator must resolve it.');
  var folder = folders.next();
  if (folders.hasNext()) throw new Error('Duplicate receipt folders. Contact the coordinator.');
  assertPrivateFolder_(folder);
  rows.forEach(function (row) {
    var file = DriveApp.getFileById(driveId_(String(row[2])));
    requireOwner_(file); requireImmediateParent_(file, folder.getId());
    if (file.getSharingAccess() !== DriveApp.Access.PRIVATE || file.getEditors().length || file.getSize() !== Number(row[4]) || file.getSize() > VB.maxFile || sha256_(file.getBlob().getBytes()) !== row[3]) throw new Error('Archived take changed. Coordinator must resolve it.');
  });
}
function writeResult_(sheet, rows, text, clear) {
  rows.forEach(function (row) { sheet.getRange(row.row, 4).setValue(text); if (clear) sheet.getRange(row.row, 3).setValue(false); });
}
function safeError_(error) {
  var message = String(error && error.message || 'Unknown error');
  // Avoid returning Google error details, account names or arbitrary source text to actors.
  return /^(Use |Only |Audio |Invalid |FLAC |WAV |Unassigned |Check |Missing assigned file: |Duplicate file name: |Drive URL |Drive shortcuts |File\/folder |Submission exceeds |Upload changed |Archived take changed|Duplicate archived take|Duplicate receipt folders|Incomplete existing receipt|Existing receipt differs|Receipt could not)/.test(message) ? message : 'Coordinator action required. No approval was granted.';
}
function saveConfig_(config) {
  var props = PropertiesService.getScriptProperties(), old = props.getProperties();
  Object.keys(old).filter(function (key) { return key.indexOf(VB.configPrefix) === 0; }).forEach(function (key) { props.deleteProperty(key); });
  var json = JSON.stringify(config), chunks = {};
  for (var i = 0; i < json.length; i += VB.configChunk) chunks[VB.configPrefix + (i / VB.configChunk)] = json.slice(i, i + VB.configChunk);
  chunks[VB.configPrefix + 'COUNT'] = String(Math.ceil(json.length / VB.configChunk));
  props.setProperties(chunks);
}
function loadConfig_() {
  var props = PropertiesService.getScriptProperties(), n = Number(props.getProperty(VB.configPrefix + 'COUNT')), parts = [];
  if (!Number.isSafeInteger(n) || n < 1 || n > 60) throw new Error('Coordinator is not configured.');
  for (var i = 0; i < n; i++) { var part = props.getProperty(VB.configPrefix + i); if (part === null) throw new Error('Incomplete coordinator configuration.'); parts.push(part); }
  return validateConfig_(JSON.parse(parts.join('')));
}

if (typeof module !== 'undefined') module.exports = {VB: VB, validateConfig_: validateConfig_, selectReadyRows_: selectReadyRows_, driveId_: driveId_, inspectAudio_: inspectAudio_, receiptExists_: receiptExists_, resolveRevision_: resolveRevision_};
