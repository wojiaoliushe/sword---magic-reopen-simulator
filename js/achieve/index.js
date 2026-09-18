import { showUnlockToast } from '../ui/toast';

const STORAGE_KEY = 'yishi_achievements_v1';

let catalog = [];
let eventIndex = {};
let stateCache = null;

function emptyState() {
  return { unlocked: {} };
}

function loadState() {
  try {
    if (typeof wx === 'undefined' || typeof wx.getStorageSync !== 'function') {
      return emptyState();
    }
    const raw = wx.getStorageSync(STORAGE_KEY);
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
      return emptyState();
    }
    const unlocked = raw.unlocked && typeof raw.unlocked === 'object' ? raw.unlocked : {};
    return { unlocked };
  } catch (err) {
    return emptyState();
  }
}

function saveState(state) {
  try {
    if (typeof wx === 'undefined' || typeof wx.setStorageSync !== 'function') {
      return;
    }
    wx.setStorageSync(STORAGE_KEY, state);
  } catch (err) {
    // ignore quota / private mode
  }
}

function getState() {
  if (!stateCache) {
    stateCache = loadState();
  }
  return stateCache;
}

function findDef(id) {
  const key = String(id || '');
  if (!key) {
    return null;
  }
  for (let i = 0; i < catalog.length; i += 1) {
    if (catalog[i].id === key) {
      return catalog[i];
    }
  }
  return null;
}

function parseUnlockEvents(raw) {
  const src = Array.isArray(raw) ? raw : [];
  const out = [];
  const seen = {};
  for (let i = 0; i < src.length; i += 1) {
    const n = Number(src[i]);
    if (!Number.isFinite(n)) {
      continue;
    }
    const eventId = Math.trunc(n);
    if (Object.prototype.hasOwnProperty.call(seen, eventId)) {
      continue;
    }
    seen[eventId] = true;
    out.push(eventId);
  }
  return out;
}

function parseCatalog(raw) {
  const rows = Array.isArray(raw)
    ? raw
    : raw && Array.isArray(raw.achievements)
      ? raw.achievements
      : [];
  const out = [];
  const seen = {};
  for (const row of rows) {
    if (!row || typeof row !== 'object') {
      continue;
    }
    const id = row.id === undefined || row.id === null ? '' : String(row.id).trim();
    if (!id || seen[id]) {
      continue;
    }
    seen[id] = true;
    const title = row.title === undefined || row.title === null ? id : String(row.title);
    const desc = row.desc === undefined || row.desc === null
      ? (row.description === undefined || row.description === null ? '' : String(row.description))
      : String(row.desc);
    out.push({
      id,
      title,
      desc,
      unlockEvents: parseUnlockEvents(row.unlockEvents),
    });
  }
  return out;
}

function rebuildEventIndex() {
  eventIndex = {};
  for (let i = 0; i < catalog.length; i += 1) {
    const def = catalog[i];
    const events = def.unlockEvents || [];
    for (let j = 0; j < events.length; j += 1) {
      const key = String(events[j]);
      if (!eventIndex[key]) {
        eventIndex[key] = [];
      }
      eventIndex[key].push(def.id);
    }
  }
}

/** Load achievement defs from a content-pack JSON object. */
export function loadCatalog(raw) {
  catalog = parseCatalog(raw);
  rebuildEventIndex();
  stateCache = null;
  return catalog.length;
}

/** All catalog entries with persist unlock state. */
export function listAchievements() {
  const state = getState();
  const unlocked = [];
  const locked = [];
  for (let i = 0; i < catalog.length; i += 1) {
    const def = catalog[i];
    const item = {
      id: def.id,
      title: def.title,
      desc: def.desc,
      unlocked: Boolean(state.unlocked[def.id]),
    };
    if (item.unlocked) {
      unlocked.push(item);
    } else {
      locked.push(item);
    }
  }
  return unlocked.concat(locked);
}

/**
 * Unlock by catalog id. No-op if unknown, already unlocked, or empty.
 * Returns true only when this call newly unlocks it.
 */
export function unlock(id) {
  const key = String(id || '').trim();
  const def = findDef(key);
  if (!def) {
    return false;
  }
  const state = getState();
  if (state.unlocked[key]) {
    return false;
  }
  state.unlocked[key] = { at: Date.now() };
  saveState(state);
  showUnlockToast(def.title);
  return true;
}

/**
 * Unlock catalog entries that list this event in unlockEvents.
 * No-op if the event is unbound. Returns how many achievements newly unlocked.
 */
export function unlockByEvent(eventId) {
  const n = Number(eventId);
  if (!Number.isFinite(n)) {
    return 0;
  }
  const ids = eventIndex[String(Math.trunc(n))];
  if (!ids || !ids.length) {
    return 0;
  }
  let count = 0;
  for (let i = 0; i < ids.length; i += 1) {
    if (unlock(ids[i])) {
      count += 1;
    }
  }
  return count;
}
