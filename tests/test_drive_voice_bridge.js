'use strict';
// Run with node --test tests/test_drive_voice_bridge.js. No Google credentials.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const code = fs.readFileSync('tools/drive_voice_bridge/Code.gs', 'utf8');
const sandbox = {module: {exports: {}}};
vm.runInNewContext(code, sandbox);
const bridge = sandbox.module.exports;
const hash = 'a'.repeat(64);
const assignment = {issue: 4, workingSpreadsheetId: 'working_sheet_id', uploadFolderId: 'upload_folder_id',
  archiveFolderId: 'archive_folder_id', locale: 'en', role: 'squad_leader', slot: 'actor_one',
  keys: ['SL_Select', 'SL_Hold'], scriptHash: hash};
const config = () => ({coordinatorSpreadsheetId: 'coordinator_sheet_id', incomingRootFolderId: 'incoming_root_id',
  archiveRootFolderId: 'archive_root_id', assignments: [structuredClone(assignment)]});
const wav = (channels = 1, bits = 24, rate = 48000) => {
  const size = channels * bits / 8 * 2;
  const b = Buffer.alloc(44 + size);
  b.write('RIFF'); b.writeUInt32LE(b.length - 8, 4); b.write('WAVE', 8);
  b.write('fmt ', 12); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20);
  b.writeUInt16LE(channels, 22); b.writeUInt32LE(rate, 24);
  b.writeUInt32LE(rate * channels * bits / 8, 28); b.writeUInt16LE(channels * bits / 8, 32);
  b.writeUInt16LE(bits, 34); b.write('data', 36); b.writeUInt32LE(size, 40);
  return [...b];
};
const flac = (channels = 1, bits = 24, rate = 48000) => {
  const b = Buffer.alloc(48); b.write('fLaC'); b[4] = 128; b[7] = 34;
  b[18] = rate >>> 12; b[19] = (rate >>> 4) & 255;
  b[20] = ((rate & 15) << 4) | ((channels - 1) << 1) | ((bits - 1) >>> 4);
  b[21] = ((bits - 1) & 15) << 4; b[25] = 10;
  return [...b];
};

test('empty registry is deployable; assignment identity and scope are checked', () => {
  const c = config(); c.assignments = [];
  assert.equal(bridge.validateConfig_(c).assignments.length, 0);
  assert.equal(bridge.validateConfig_(config()).assignments.length, 1);
  for (const mutation of [
    c => c.assignments.push(structuredClone(c.assignments[0])),
    c => c.assignments[0].keys.push('SL_Select'),
    c => c.assignments[0].keys.push('../other'),
    c => c.assignments[0].keys.push('SL_Select.wav'),
    c => c.assignments[0].scriptHash = 'not-a-hash',
    c => c.assignments[0].workingSpreadsheetId = c.coordinatorSpreadsheetId,
    c => c.assignments[0].issue = 0,
    c => c.assignments[0].keys = Array.from({length: 201}, (_, i) => 'key' + i),
  ]) { const c = config(); mutation(c); assert.throws(() => bridge.validateConfig_(c)); }
});

test('only a full exact checked assignment is selected, in assigned source order', () => {
  const rows = [['SL_Hold.flac', '', true, ''], ['SL_Select.wav', '', true, '']];
  const selected = bridge.selectReadyRows_(rows, assignment);
  assert.equal(selected[0].key, 'SL_Select'); assert.equal(selected[1].row, 2);
  assert.throws(() => bridge.selectReadyRows_([['SL_Select.wav', '', true, '']], assignment), /every assigned/);
  assert.throws(() => bridge.selectReadyRows_([['SL_Select.wav', '', true, ''], ['SL_Select.flac', '', true, '']], assignment), /duplicate/);
  for (const bad of ['SL_Select.wav.exe', 'SL_Select.wav.wav', '../SL_Select.wav', 'other.wav', 'SL_Select.WAV']) {
    assert.throws(() => bridge.selectReadyRows_([[bad, '', true, ''], ['SL_Hold.wav', '', true, '']], assignment));
  }
  assert.throws(() => bridge.selectReadyRows_([['SL_Select.wav', '', 'TRUE', ''], ['SL_Hold.wav', '', true, '']], assignment));
});

test('Drive URLs cannot select arbitrary websites, folders, or query payloads', () => {
  assert.equal(bridge.driveId_('https://drive.google.com/file/d/abcdefghij_123/view'), 'abcdefghij_123');
  assert.equal(bridge.driveId_('https://drive.google.com/file/d/abcdefghij_123/view?usp=sharing'), 'abcdefghij_123');
  for (const bad of ['https://evil.example/file/d/abcdefghij_123/view', 'https://drive.google.com/drive/folders/abcdefghij_123',
    '=IMPORTDATA("x")', 'https://drive.google.com/file/d/abcdefghij_123/view?x=other', 'https://drive.google.com.evil/file/d/abcdefghij_123/view']) {
    assert.throws(() => bridge.driveId_(bad));
  }
});

test('WAV validates mono PCM, sample rate, bit depth, magic, size and chunks', () => {
  assert.equal(bridge.inspectAudio_('SL_Select.wav', wav()).mime, 'audio/wav');
  assert.equal(bridge.inspectAudio_('SL_Select.wav', wav(1, 16, 44100)).bits, 16);
  for (const bytes of [wav(2), wav(1, 32), wav(1, 16, 22050), wav().slice(0, 43)]) {
    assert.throws(() => bridge.inspectAudio_('SL_Select.wav', bytes));
  }
  const badMagic = wav(); badMagic[0] = 0;
  assert.throws(() => bridge.inspectAudio_('SL_Select.wav', badMagic), /header/);
  const badChunk = wav(); badChunk[40] = 255;
  assert.throws(() => bridge.inspectAudio_('SL_Select.wav', badChunk), /chunk/);
  const badFormat = wav(); badFormat[20] = 3;
  assert.throws(() => bridge.inspectAudio_('SL_Select.wav', badFormat), /PCM/);
  const badAlign = wav(); badAlign[32] = 1;
  assert.throws(() => bridge.inspectAudio_('SL_Select.wav', badAlign), /alignment/);
  const trailing = [...wav(), 0, 0]; trailing[4] = trailing.length - 8;
  assert.throws(() => bridge.inspectAudio_('SL_Select.wav', trailing), /trailing/);
  const oddSample = wav(); oddSample[40] = 1; oddSample.splice(46); oddSample[4] = oddSample.length - 8;
  assert.throws(() => bridge.inspectAudio_('SL_Select.wav', oddSample), /alignment/);
});

test('FLAC validates STREAMINFO and rejects stereo, wrong rates, bit depth and empty audio', () => {
  assert.equal(bridge.inspectAudio_('SL_Select.flac', flac()).mime, 'audio/flac');
  assert.equal(bridge.inspectAudio_('SL_Select.flac', flac(1, 16, 44100)).sampleRate, 44100);
  for (const bytes of [flac(2), flac(1, 8), flac(1, 16, 22050)]) assert.throws(() => bridge.inspectAudio_('SL_Select.flac', bytes));
  const bad = flac(); bad[7] = 33; assert.throws(() => bridge.inspectAudio_('SL_Select.flac', bad), /STREAMINFO/);
  const empty = flac(); empty[25] = 0; assert.throws(() => bridge.inspectAudio_('SL_Select.flac', empty), /samples/);
  assert.throws(() => bridge.inspectAudio_('SL_Select.flac', wav()), /STREAMINFO/);
});

test('a completed receipt is reused only with exact hash, size, MIME and script binding', () => {
  const files = [{key: 'SL_Select', sha256: hash, bytes: 50, mime: 'audio/wav'},
    {key: 'SL_Hold', sha256: hash, bytes: 60, mime: 'audio/flac'}];
  const revision = 'b'.repeat(64);
  const rows = files.map(f => [4, f.key, 'https://drive.google.com/file/d/abcdefghij_123/view', f.sha256, f.bytes, f.mime, revision, '2026-10-20T00:00:00Z', hash]);
  const sheet = input => ({getLastRow: () => input.length + 1, getRange: () => ({getValues: () => input})});
  assert.equal(bridge.receiptExists_(sheet(rows), assignment, revision, files), true);
  assert.equal(bridge.receiptExists_(sheet([]), assignment, revision, files), false);
  assert.throws(() => bridge.receiptExists_(sheet(rows.slice(1)), assignment, revision, files), /Incomplete/);
  for (const col of [1, 3, 4, 5, 8]) {
    const wrong = structuredClone(rows); wrong[0][col] = 'wrong';
    assert.throws(() => bridge.receiptExists_(sheet(wrong), assignment, revision, files));
  }
});

function integrationHarness() {
  const files = new Map(), folders = new Map(), reads = [];
  let next = 100, copies = 0;
  const owner = {getEmail: () => 'owner@example.test'};
  const iter = values => { let i = 0; return {hasNext: () => i < values.length, next: () => values[i++]}; };
  const blob = (bytes, name = '') => ({bytes: [...bytes], name, getBytes() { return this.bytes; },
    setName(n) { this.name = n; return this; }, setContentType(m) { this.mime = m; return this; }});
  function file(id, name, bytes, parent, mime = 'audio/wav') {
    const obj = {id, name, bytes: [...bytes], parent, mime,
      getId() { return this.id; }, getName() { return this.name; }, getMimeType() { return this.mime; },
      getSize() { return this.sizeOverride ?? this.bytes.length; }, getBlob() { reads.push(id); return blob(this.bytes, this.name); },
      getOwner: () => owner, getSharingAccess: () => 'PRIVATE', getEditors: () => [], getViewers: () => [],
      getParents() { return iter([{getId: () => this.parent}]); }};
    files.set(id, obj); return obj;
  }
  function folder(id, parent, name = '') {
    const obj = {id, parent, name, getId() { return this.id; }, getOwner: () => owner,
      getSharingAccess: () => 'PRIVATE', getEditors: () => [], getViewers: () => [],
      getParents() { return iter([{getId: () => this.parent}]); },
      getFilesByName(n) { return iter([...files.values()].filter(f => f.parent === id && f.name === n)); },
      getFoldersByName(n) { return iter([...folders.values()].filter(f => f.parent === id && f.name === n)); },
      createFolder(n) { return folder('folder_' + (++next), id, n); },
      createFile(b) { copies++; return file('copy_file_' + (++next), b.name, b.bytes, id, b.mime); }};
    folders.set(id, obj); return obj;
  }
  const protection = {getDescription: () => 'Ebbtide owner-only recording receipts',
    setWarningOnly() {}, addEditor() {}, getEditors: () => [owner], canDomainEdit: () => false, setUnprotectedRanges() {}};
  function sheet(name, headers, body) {
    const rows = [headers, ...body];
    return {rows, getName: () => name, getLastRow: () => rows.length,
      getProtections: () => [protection],
      getRange(r, c, nr = 1, nc = 1) { return {
        getValues: () => Array.from({length: nr}, (_, y) => Array.from({length: nc}, (_, x) => rows[r - 1 + y]?.[c - 1 + x] ?? '')),
        setValues(values) { values.forEach((row, y) => { rows[r - 1 + y] ||= []; row.forEach((value, x) => rows[r - 1 + y][c - 1 + x] = value); }); },
        setValue(value) { rows[r - 1] ||= []; rows[r - 1][c - 1] = value; }
      }; }};
  }
  const uploads = sheet('Recording Uploads', [...bridge.VB.inputHeaders], [['SL_Select.wav', '', true, ''], ['SL_Hold.wav', '', true, '']]);
  const outbox = sheet('Recording Outbox', [...bridge.VB.outputHeaders], []);
  const c = config(), serialized = JSON.stringify(c);
  const properties = {[bridge.VB.configPrefix + 'COUNT']: '1', [bridge.VB.configPrefix + '0']: serialized};
  folder(c.incomingRootFolderId, 'private_top'); folder(c.archiveRootFolderId, 'private_top');
  folder(assignment.uploadFolderId, c.incomingRootFolderId); folder(assignment.archiveFolderId, c.archiveRootFolderId);
  const first = file('source_file_first', 'SL_Select.wav', wav(), assignment.uploadFolderId);
  const second = file('source_file_second', 'SL_Hold.wav', wav(), assignment.uploadFolderId);
  let spreadsheetAccess = 0;
  const globals = {module: {exports: {}}, Session: {getEffectiveUser: () => owner},
    LockService: {getScriptLock: () => ({tryLock: () => true, releaseLock() {}})},
    PropertiesService: {getScriptProperties: () => ({getProperty: k => properties[k] ?? null})},
    DriveApp: {Access: {PRIVATE: 'PRIVATE'}, getFileById: id => { if (!files.has(id)) throw new Error('Unexpected file access'); return files.get(id); },
      getFolderById: id => { if (!folders.has(id)) throw new Error('Unexpected folder access'); return folders.get(id); }},
    SpreadsheetApp: {ProtectionType: {SHEET: 'SHEET'}, flush() {}, openById(id) {
      spreadsheetAccess++;
      if (id === assignment.workingSpreadsheetId) return {getSheetByName: n => n === 'Recording Uploads' ? uploads : null};
      if (id === c.coordinatorSpreadsheetId) return {getSheetByName: n => n === 'Recording Outbox' ? outbox : null};
      throw new Error('Unexpected spreadsheet access');
    }},
    Utilities: {DigestAlgorithm: {SHA_256: 'sha256'}, newBlob: x => blob(Buffer.from(x)),
      computeDigest: (_, bytes) => [...crypto.createHash('sha256').update(Buffer.from(bytes.map(b => b & 255))).digest()]}
  };
  vm.runInNewContext(code, globals);
  return {globals, uploads, outbox, first, second, folders, reads,
    run: id => globals.processWorkbook_(id || assignment.workingSpreadsheetId),
    check: () => uploads.rows.slice(1).forEach(row => row[2] = true),
    copies: () => copies, spreadsheetAccess: () => spreadsheetAccess};
}

test('full checkbox path copies private files, writes one batch, clears boxes, and reuses unchanged intake', () => {
  const h = integrationHarness(); h.run();
  assert.equal(h.copies(), 2); assert.equal(h.outbox.rows.length, 3);
  for (const row of h.uploads.rows.slice(1)) { assert.equal(row[2], false); assert.match(row[3], /^Submitted/); }
  const originalRevision = h.outbox.rows[1][6];
  assert.match(originalRevision, /^[a-f0-9]{64}$/);
  assert.equal(h.outbox.rows[1][1], 'SL_Select'); assert.equal(h.outbox.rows[1][8], hash);
  assert.match(h.outbox.rows[1][2], /^https:\/\/drive\.google\.com\/file\/d\/copy_file_/);
  assert.equal(h.outbox.rows[1][7], h.outbox.rows[2][7]);
  h.check(); h.run(); assert.equal(h.copies(), 2); assert.equal(h.outbox.rows.length, 3);
});

test('retake and reverting to original bytes each create a fresh latest batch; partial retry reuses private copies', () => {
  const h = integrationHarness(); h.run(); const a = h.outbox.rows[1][6];
  const original = [...h.first.bytes]; h.first.bytes[h.first.bytes.length - 1] = 5;
  h.check(); h.run(); const b = h.outbox.rows[3][6]; assert.notEqual(a, b);
  h.first.bytes = original; h.check(); h.run(); const again = h.outbox.rows[5][6];
  assert.notEqual(a, again); assert.notEqual(b, again);
  assert.equal(h.outbox.rows.length, 7); assert.equal(h.copies(), 6);
  h.check(); h.run(); assert.equal(h.copies(), 6); assert.equal(h.outbox.rows.length, 7);

  const partial = integrationHarness();
  const create = partial.folders.get(assignment.archiveFolderId).createFolder;
  let failOnce = true;
  partial.folders.get(assignment.archiveFolderId).createFolder = name => {
    const f = create(name), createFile = f.createFile;
    f.createFile = b => { if (b.name === 'SL_Hold.wav' && failOnce) { failOnce = false; throw new Error('Transient copy failure'); } return createFile(b); };
    return f;
  };
  assert.throws(() => partial.run(), /Transient/);
  assert.equal(partial.outbox.rows.length, 1); assert.equal(partial.copies(), 1);
  partial.run(); assert.equal(partial.outbox.rows.length, 3); assert.equal(partial.copies(), 2);
});

test('unregistered workbook cannot cause spreadsheet/Drive access; oversized source rejected before blob read', () => {
  const h = integrationHarness(); assert.throws(() => h.run('unregistered_sheet_id'), /not uniquely registered/);
  assert.equal(h.spreadsheetAccess(), 0); assert.equal(h.reads.length, 0);
  h.first.sizeOverride = bridge.VB.maxFile + 1;
  assert.throws(() => h.run(), /20 MiB/); assert.equal(h.reads.length, 0); assert.equal(h.copies(), 0);
  assert.equal(h.outbox.rows.length, 1);
  const crowded = integrationHarness();
  crowded.uploads.rows.push(...Array.from({length: 199}, (_, i) => ['extra' + i, '', false, '']));
  assert.throws(() => crowded.run(), /200 populated/);
  assert.equal(crowded.reads.length, 0); assert.equal(crowded.copies(), 0);
  assert.equal(crowded.outbox.rows.length, 1);
  assert.match(crowded.uploads.rows[1][3], /200 populated/);
  const hugeOutbox = {getLastRow: () => 20002, getRange: () => { throw new Error('Must not read this range'); }};
  assert.throws(() => bridge.receiptExists_(hugeOutbox, assignment, hash, []), /capacity/);
});

test('wrong URL, folder move and changed private archive fail without a new receipt', () => {
  const h = integrationHarness();
  h.uploads.rows[1][1] = 'https://drive.google.com/file/d/other_file_id/view';
  assert.throws(() => h.run(), /does not match/); assert.equal(h.copies(), 0);
  h.uploads.rows[1][1] = ''; h.first.parent = 'unassigned_folder_id';
  assert.throws(() => h.run(), /Missing assigned/); assert.equal(h.copies(), 0); assert.equal(h.reads.length, 0);
  h.first.parent = assignment.uploadFolderId; h.run();
  const snapshots = [...h.folders.values()].find(f => f.name.startsWith('work-'));
  snapshots.getFilesByName('SL_Select.wav').next().bytes[45] ^= 1;
  h.check(); assert.throws(() => h.run(), /Archived take changed/); assert.equal(h.outbox.rows.length, 3);
});
