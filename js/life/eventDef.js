function toInt(value, fallback = 0) {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    return fallback;
  }
  return Math.trunc(n);
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function asIntArray(raw) {
  const out = [];
  if (!Array.isArray(raw)) {
    return out;
  }
  for (const item of raw) {
    out.push(toInt(item, 0));
  }
  return out;
}

function mergeEffects(raw, attrKeys, eventId) {
  const out = {};
  for (const key of attrKeys) {
    out[key] = 0;
  }
  if (!isPlainObject(raw)) {
    return out;
  }
  for (const key of attrKeys) {
    if (raw[key] !== undefined && raw[key] !== null) {
      out[key] = toInt(raw[key], 0);
    }
  }
  for (const key of Object.keys(raw)) {
    if (attrKeys.indexOf(key) < 0) {
      console.error(`事件 #${eventId} effects 未知属性: ${key}`);
    }
  }
  return out;
}

function asCooldownGroups(data) {
  const out = [];
  const seen = {};
  let raw = data.cooldownGroups;
  if (raw === undefined || raw === null) {
    raw = data.cooldownGroup;
  }
  let items = [];
  if (Array.isArray(raw)) {
    items = raw;
  } else if (raw !== undefined && raw !== null && String(raw) !== '') {
    items = [raw];
  }
  for (const item of items) {
    const name = String(item);
    if (name === '' || seen[name]) {
      continue;
    }
    seen[name] = true;
    out.push(name);
  }
  return out;
}

export default class EventDef {
  constructor() {
    this.eventId = 0;
    this.type = 'normal';
    this.desc = '';
    this.effects = {};
    this.minAge = 0;
    this.maxAge = 120;
    this.ageModifiers = null;
    this.baseWeight = 10;
    this.minInterval = 0;
    this.maxTriggers = 999;
    this.group = null;
    this.requiredEvents = [];
    this.excludeEvents = [];
    this.requiredFlags = [];
    this.requiredAttrs = {};
    this.mutexEvents = [];
    this.naturalUnlock = true;
    this.unlockEvents = [];
    this.unlockDelayed = [];
    this.followUp = [];
    this.flags = {};
    this.weightModifiers = [];
    this.cooldownGroups = [];
    this.cooldownMinInterval = 0;
    this.cooldownMaxTriggers = 999;
    this.flagsDelayed = [];
    this.groupFallbackAge = -1;
  }

  static fromDict(data, attrKeys = []) {
    const e = new EventDef();
    if (!isPlainObject(data)) {
      return e;
    }
    e.eventId = toInt(data.eventId, 0);
    e.type = data.type === undefined || data.type === null ? 'normal' : String(data.type);
    if (e.type === '') {
      e.type = 'normal';
    }
    e.desc = data.desc === undefined || data.desc === null ? '' : String(data.desc);
    e.effects = mergeEffects(data.effects, attrKeys, e.eventId);
    e.minAge = toInt(data.minAge, 0);
    e.maxAge = data.maxAge === undefined || data.maxAge === null ? 120 : toInt(data.maxAge, 120);
    e.ageModifiers = isPlainObject(data.ageModifiers) ? data.ageModifiers : null;
    e.baseWeight = data.baseWeight === undefined || data.baseWeight === null
      ? 10
      : toInt(data.baseWeight, 10);
    e.minInterval = toInt(data.minInterval, 0);
    e.maxTriggers = data.maxTriggers === undefined || data.maxTriggers === null
      ? 999
      : toInt(data.maxTriggers, 999);
    const group = data.group;
    if (group === undefined || group === null || String(group) === '') {
      e.group = null;
    } else {
      e.group = String(group);
    }
    e.requiredEvents = asIntArray(data.requiredEvents);
    e.excludeEvents = asIntArray(data.excludeEvents);
    e.requiredFlags = Array.isArray(data.requiredFlags) ? data.requiredFlags : [];
    e.requiredAttrs = isPlainObject(data.requiredAttrs) ? data.requiredAttrs : {};
    e.mutexEvents = asIntArray(data.mutexEvents);
    e.naturalUnlock = data.naturalUnlock === undefined ? true : Boolean(data.naturalUnlock);
    e.unlockEvents = asIntArray(data.unlockEvents);
    e.unlockDelayed = Array.isArray(data.unlockDelayed) ? data.unlockDelayed : [];
    e.followUp = Array.isArray(data.followUp) ? data.followUp : [];
    e.flags = isPlainObject(data.flags) ? data.flags : {};
    e.weightModifiers = Array.isArray(data.weightModifiers) ? data.weightModifiers : [];
    e.cooldownGroups = asCooldownGroups(data);
    e.cooldownMinInterval = toInt(data.cooldownMinInterval, 0);
    e.cooldownMaxTriggers = data.cooldownMaxTriggers === undefined || data.cooldownMaxTriggers === null
      ? 999
      : toInt(data.cooldownMaxTriggers, 999);
    e.flagsDelayed = Array.isArray(data.flagsDelayed) ? data.flagsDelayed : [];
    if (Object.prototype.hasOwnProperty.call(data, 'groupFallbackAge')) {
      e.groupFallbackAge = toInt(data.groupFallbackAge, -1);
    } else {
      e.groupFallbackAge = -1;
    }
    return e;
  }
}
