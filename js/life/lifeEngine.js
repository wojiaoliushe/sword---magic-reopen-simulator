import EventDef from './eventDef';
import LifeState from './lifeState';
import { unlock, unlockByEvent } from '../achieve/index';
import { collectEventMods, getTalent, rndAttrKeys } from '../talent/index';
import { ALIGN_MORAL_KEY, ALIGN_ORDER_KEY, alignmentWeightMul } from './alignment';

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

function shallowClone(obj) {
  const out = {};
  if (!isPlainObject(obj)) {
    return out;
  }
  for (const key of Object.keys(obj)) {
    out[key] = obj[key];
  }
  return out;
}

function cloneValue(value) {
  if (value === null || typeof value !== 'object') {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map(cloneValue);
  }
  const out = {};
  for (const key of Object.keys(value)) {
    out[key] = cloneValue(value[key]);
  }
  return out;
}

function isNumber(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

export default class LifeEngine {
  constructor(mode) {
    this.mode = mode;
    this.catalog = new Map();
    this.state = new LifeState(mode);
  }

  loadEvents(parsed) {
    let rows = [];
    if (Array.isArray(parsed)) {
      rows = parsed;
    } else if (isPlainObject(parsed) && Array.isArray(parsed.events)) {
      rows = parsed.events;
    } else {
      console.error('事件表根节点必须是数组，或含 events 数组的对象');
      return '事件表根节点必须是数组，或含 events 数组的对象';
    }
    this.catalog.clear();
    const attrKeys = this.mode ? this.mode.attrKeys : [];
    for (const row of rows) {
      if (!isPlainObject(row)) {
        continue;
      }
      const event = EventDef.fromDict(row, attrKeys);
      if (event.eventId <= 0 || event.desc === '') {
        console.error('跳过无效事件:', row);
        continue;
      }
      if (this.catalog.has(event.eventId)) {
        console.error('重复 eventId，后写覆盖前写:', event.eventId);
      }
      this._warnEventSchema(event);
      this.catalog.set(event.eventId, event);
    }
    return '';
  }

  restart(attrOverrides, talentIds) {
    this.state = new LifeState(this.mode);
    if (isPlainObject(attrOverrides) && this.mode && Array.isArray(this.mode.attrs)) {
      for (const def of this.mode.attrs) {
        if (def.alloc === false) {
          continue;
        }
        if (Object.prototype.hasOwnProperty.call(attrOverrides, def.key)) {
          this.state.attrs[def.key] = toInt(attrOverrides[def.key], 0);
        }
      }
    }
    this._bindTalents(talentIds);
    this._applyAllTalentFlags();
    this._syncAttrPeaks();
    this._initUnlocked();
    this._lifeLog('[LIFE] ---- 重开 ----');
    this.settleCurrentYear();
  }

  nextYear() {
    if (this.state.dead) {
      return;
    }
    this.state.age += 1;
    this.settleCurrentYear();
  }

  settleCurrentYear() {
    const state = this.state;
    state.clearYear();
    this._fireReadyTalents();
    const unlockedDue = this._redeemDueUnlocks();
    this._redeemDueFlags();
    this._collectInevitableQueue();

    const queueStartedEmpty = state.yearQueue.length === 0;
    const mustIds = state.yearQueue.slice();
    if (queueStartedEmpty) {
      const active = this._drawActiveEvent();
      if (active) {
        this._logYearHeader(mustIds, unlockedDue, `#${active.eventId}/${active.type}`);
        this._triggerAndShow(active, active.type);
        if (state.dead) {
          return;
        }
        this._insertDelay0Followups(active);
      } else {
        this._logYearHeader(mustIds, unlockedDue, '无');
      }
    } else {
      this._logYearHeader(mustIds, unlockedDue, '跳过');
    }

    while (state.yearQueue.length > 0) {
      const eventId = toInt(state.yearQueue.shift(), 0);
      const event = this._getEvent(eventId);
      if (!event) {
        this._lifeLog(`[LIFE] ${state.age}岁 skip #${eventId} missing`);
        continue;
      }
      const reason = this._skipReason(event);
      if (reason) {
        this._lifeLog(`[LIFE] ${state.age}岁 skip #${eventId} ${reason}`);
        continue;
      }
      const via = state.yearDelay0[eventId] ? 'd0' : 'must';
      this._triggerAndShow(event, via);
      if (state.dead) {
        return;
      }
      this._insertDelay0Followups(event);
    }
  }

  _initUnlocked() {
    for (const event of this.catalog.values()) {
      if (event.naturalUnlock) {
        this.state.unlocked[event.eventId] = true;
      }
    }
  }

  _redeemDueUnlocks() {
    const due = [];
    const remain = [];
    for (const item of this.state.unlockWait) {
      if (toInt(item.fire_age, -1) === this.state.age) {
        const eventId = toInt(item.event_id, 0);
        this.state.unlocked[eventId] = true;
        due.push(eventId);
      } else {
        remain.push(item);
      }
    }
    this.state.unlockWait = remain;
    return due;
  }

  _redeemDueFlags() {
    const remain = [];
    for (const item of this.state.flagWait) {
      if (toInt(item.fire_age, -1) !== this.state.age) {
        remain.push(item);
        continue;
      }
      const patch = item.flags;
      if (!isPlainObject(patch) || Object.keys(patch).length === 0) {
        continue;
      }
      const before = shallowClone(this.state.flags);
      this._applyFlags(patch);
      const bits = this._fmtFlagPatch(before, patch);
      if (bits) {
        this._lifeLog(`[LIFE] ${this.state.age}岁 静默flags ${bits}`);
      }
    }
    this.state.flagWait = remain;
  }

  _collectInevitableQueue() {
    const remain = [];
    for (const item of this.state.followWait) {
      if (toInt(item.fire_age, -1) === this.state.age) {
        const eventId = toInt(item.event_id, 0);
        if (!this.state.yearQueue.includes(eventId)) {
          this.state.yearQueue.push(eventId);
        }
      } else {
        remain.push(item);
      }
    }
    this.state.followWait = remain;

    const forcedIds = [];
    for (const event of this.catalog.values()) {
      if (event.type !== 'forced') {
        continue;
      }
      if (this._cannotTrigger(event)) {
        continue;
      }
      forcedIds.push(event.eventId);
    }
    forcedIds.sort((a, b) => a - b);
    for (const eventId of forcedIds) {
      if (!this.state.yearQueue.includes(eventId)) {
        this.state.yearQueue.push(eventId);
      }
    }
    this._appendGroupFallbacks();
  }

  _appendGroupFallbacks() {
    const fallbackAgeByGroup = {};
    const candidatesByGroup = {};
    for (const event of this.catalog.values()) {
      if (event.group === null || event.groupFallbackAge < 0) {
        continue;
      }
      const g = String(event.group);
      if (Object.prototype.hasOwnProperty.call(fallbackAgeByGroup, g)) {
        fallbackAgeByGroup[g] = Math.min(fallbackAgeByGroup[g], event.groupFallbackAge);
      } else {
        fallbackAgeByGroup[g] = event.groupFallbackAge;
      }
      if (!candidatesByGroup[g]) {
        candidatesByGroup[g] = [];
      }
      candidatesByGroup[g].push(event.eventId);
    }
    for (const g of Object.keys(fallbackAgeByGroup)) {
      if (this.state.age < toInt(fallbackAgeByGroup[g], 0)) {
        continue;
      }
      let anyMember = false;
      for (const event of this.catalog.values()) {
        if (event.group === null || String(event.group) !== g) {
          continue;
        }
        if (this.state.experienced[event.eventId]) {
          anyMember = true;
          break;
        }
      }
      if (anyMember) {
        continue;
      }
      const ids = candidatesByGroup[g].slice();
      ids.sort((a, b) => a - b);
      for (const eventId of ids) {
        const event = this._getEvent(toInt(eventId, 0));
        if (!event || this._cannotTrigger(event)) {
          continue;
        }
        if (!this.state.yearQueue.includes(event.eventId)) {
          this.state.yearQueue.push(event.eventId);
        }
        break;
      }
    }
  }

  _drawActiveEvent() {
    const picked = this._weightedDrawType('normal');
    if (picked) {
      return picked;
    }
    return this._weightedDrawType('fallback');
  }

  _weightedDrawType(eventType) {
    const ids = [];
    const weights = [];
    let total = 0;
    for (const event of this.catalog.values()) {
      if (event.type !== eventType) {
        continue;
      }
      if (!this._canRandomDraw(event)) {
        continue;
      }
      const weight = this._calcWeight(event);
      ids.push(event.eventId);
      weights.push(weight);
      total += weight;
    }
    if (ids.length === 0 || total <= 0) {
      return null;
    }
    const roll = Math.random() * total;
    let acc = 0;
    for (let i = 0; i < ids.length; i += 1) {
      acc += weights[i];
      if (roll <= acc) {
        return this.catalog.get(ids[i]);
      }
    }
    return this.catalog.get(ids[ids.length - 1]);
  }

  _canRandomDraw(event) {
    if (this._cannotTrigger(event)) {
      return false;
    }
    if (event.baseWeight <= 0) {
      return false;
    }
    if (!this.state.unlocked[event.eventId]) {
      return false;
    }
    return this._calcWeight(event) > 0;
  }

  _cannotTrigger(event) {
    return this._skipReason(event) !== '';
  }

  _skipReason(event) {
    const state = this.state;
    if (state.age < event.minAge || state.age > event.maxAge) {
      return 'age';
    }
    if (state.disabled[event.eventId]) {
      return 'disabled';
    }
    if (state.yearFired[event.eventId]) {
      return 'fired';
    }
    for (const excludedId of event.excludeEvents) {
      if (state.experienced[excludedId]) {
        return 'exclude';
      }
    }
    if (event.group !== null) {
      const groupName = String(event.group);
      if (state.yearGroups[groupName] && !state.yearDelay0[event.eventId]) {
        return 'group';
      }
    }
    for (const requiredId of event.requiredEvents) {
      if (!state.experienced[requiredId]) {
        return 'req';
      }
    }
    if (!this._requiredAttrsOk(event.requiredAttrs)) {
      return 'attr';
    }
    if (!this._requiredFlagsOk(event.requiredFlags)) {
      return 'flag';
    }
    if (this._talentBlocked(event)) {
      return 'talent';
    }
    if (toInt(state.triggerCount[event.eventId], 0) >= event.maxTriggers) {
      return 'count';
    }
    if (Object.prototype.hasOwnProperty.call(state.lastTriggerAge, event.eventId)) {
      if (state.age - toInt(state.lastTriggerAge[event.eventId], 0) < event.minInterval) {
        return 'interval';
      }
    }
    return this._cooldownSkipReason(event);
  }

  _cooldownSkipReason(event) {
    if (event.cooldownGroups.length === 0) {
      return '';
    }
    if (this.state.yearDelay0[event.eventId]) {
      return '';
    }
    for (const gname of event.cooldownGroups) {
      if (toInt(this.state.cooldownCount[gname], 0) >= event.cooldownMaxTriggers) {
        return 'cd_count';
      }
      if (
        event.cooldownMinInterval > 0
        && Object.prototype.hasOwnProperty.call(this.state.cooldownLastAge, gname)
      ) {
        if (this.state.age - toInt(this.state.cooldownLastAge[gname], 0) < event.cooldownMinInterval) {
          return 'cd_interval';
        }
      }
    }
    return '';
  }

  _triggerAndShow(event, via) {
    const state = this.state;
    if (state.yearDelay0[event.eventId]) {
      via = 'd0';
    }
    const flagsBefore = shallowClone(state.flags);
    state.yearLog.push({
      event_id: event.eventId,
      desc: event.desc,
      effects: shallowClone(event.effects),
    });
    state.history.push(event.eventId);
    state.experienced[event.eventId] = true;
    state.yearFired[event.eventId] = true;
    state.triggerCount[event.eventId] = toInt(state.triggerCount[event.eventId], 0) + 1;
    state.lastTriggerAge[event.eventId] = state.age;
    this._noteCooldownGroups(event);
    this._applyEffects(event.effects);
    this._applyFlags(event.flags);
    for (const mutexId of event.mutexEvents) {
      state.disabled[toInt(mutexId, 0)] = true;
    }
    if (event.group !== null) {
      state.yearGroups[String(event.group)] = true;
    }
    this._scheduleUnlocks(event);
    this._scheduleFollowups(event);
    this._scheduleFlagsDelayed(event);
    if (event.type === 'death') {
      state.dead = true;
    }
    this._logFired(event, via, flagsBefore);
    unlockByEvent(event.eventId);
    if (state.dead) {
      this._lifeLog('[LIFE] ---- 人生结束 ----');
    }
  }

  _insertDelay0Followups(event) {
    const state = this.state;
    const candidates = [];
    for (const item of event.followUp) {
      if (!isPlainObject(item)) {
        continue;
      }
      if (toInt(item.delay, 0) !== 0) {
        continue;
      }
      const eventId = toInt(item.eventId, 0);
      if (eventId <= 0) {
        continue;
      }
      if (state.yearQueue.includes(eventId) || state.yearFired[eventId]) {
        continue;
      }
      const target = this._getEvent(eventId);
      if (!target) {
        continue;
      }
      state.yearDelay0[eventId] = true;
      if (this._skipReason(target)) {
        delete state.yearDelay0[eventId];
        continue;
      }
      candidates.push(eventId);
    }
    if (candidates.length === 0) {
      return;
    }
    const picked = this._pickDelay0Candidate(candidates);
    for (const eventId of candidates) {
      if (eventId !== picked) {
        delete state.yearDelay0[eventId];
      }
    }
    state.yearQueue.unshift(picked);
    state.yearDelay0[picked] = true;
  }

  _pickDelay0Candidate(candidates) {
    if (candidates.length === 1) {
      return candidates[0];
    }
    const ids = [];
    const weights = [];
    let total = 0;
    for (const eventId of candidates) {
      const target = this._getEvent(eventId);
      if (!target) {
        continue;
      }
      const weight = this._calcWeight(target);
      if (weight <= 0) {
        continue;
      }
      ids.push(eventId);
      weights.push(weight);
      total += weight;
    }
    if (ids.length === 0 || total <= 0) {
      return candidates[Math.floor(Math.random() * candidates.length)];
    }
    const roll = Math.random() * total;
    let acc = 0;
    for (let i = 0; i < ids.length; i += 1) {
      acc += weights[i];
      if (roll <= acc) {
        return ids[i];
      }
    }
    return ids[ids.length - 1];
  }

  _scheduleUnlocks(event) {
    const state = this.state;
    for (const eventIdRaw of event.unlockEvents) {
      state.unlockWait.push({
        event_id: toInt(eventIdRaw, 0),
        fire_age: state.age + 1,
      });
    }
    for (const item of event.unlockDelayed) {
      if (!isPlainObject(item)) {
        continue;
      }
      const eventId = toInt(item.eventId, 0);
      const delay = toInt(item.delay, 0);
      if (eventId <= 0) {
        continue;
      }
      if (delay <= 0) {
        state.unlocked[eventId] = true;
      } else {
        state.unlockWait.push({
          event_id: eventId,
          fire_age: state.age + delay,
        });
      }
    }
  }

  _scheduleFollowups(event) {
    for (const item of event.followUp) {
      if (!isPlainObject(item)) {
        continue;
      }
      const delay = toInt(item.delay, 0);
      if (delay < 1) {
        continue;
      }
      const eventId = toInt(item.eventId, 0);
      if (eventId <= 0) {
        continue;
      }
      this.state.followWait.push({
        event_id: eventId,
        fire_age: this.state.age + delay,
      });
    }
  }

  _scheduleFlagsDelayed(event) {
    for (const item of event.flagsDelayed) {
      if (!isPlainObject(item)) {
        continue;
      }
      const delay = toInt(item.delay, 0);
      if (delay < 1) {
        continue;
      }
      const patch = item.flags;
      if (!isPlainObject(patch) || Object.keys(patch).length === 0) {
        continue;
      }
      this.state.flagWait.push({
        fire_age: this.state.age + delay,
        flags: cloneValue(patch),
      });
    }
  }

  _noteCooldownGroups(event) {
    for (const gname of event.cooldownGroups) {
      this.state.cooldownCount[gname] = toInt(this.state.cooldownCount[gname], 0) + 1;
      this.state.cooldownLastAge[gname] = this.state.age;
    }
  }

  _warnEventSchema(event) {
    if (!this.mode) {
      return;
    }
    for (const key of Object.keys(event.requiredAttrs || {})) {
      if (!this.mode.isAttrKey(key)) {
        console.error(`事件 #${event.eventId} requiredAttrs 未知属性: ${key}`);
      }
    }
    for (const item of event.weightModifiers || []) {
      if (!isPlainObject(item)) {
        continue;
      }
      const attrName = String(item.attr || '');
      if (!attrName) {
        continue;
      }
      if (!this.mode.isAttrKey(attrName) && !this.mode.isClockName(attrName)) {
        console.error(`事件 #${event.eventId} weightModifiers 未知属性: ${attrName}`);
      }
    }
  }

  _attrKeys() {
    return this.mode && this.mode.attrKeys ? this.mode.attrKeys : [];
  }

  _bindTalents(talentIds) {
    const src = Array.isArray(talentIds) ? talentIds : [];
    const ids = [];
    const seen = {};
    for (let i = 0; i < src.length; i += 1) {
      const id = String(src[i] || '').trim();
      if (!id || seen[id] || !getTalent(id)) {
        continue;
      }
      seen[id] = true;
      ids.push(id);
    }
    this.state.talents = ids;
    this.state.talentFired = {};
    this.state.talentMods = collectEventMods(ids);
  }

  _applyAllTalentFlags() {
    const ids = this.state.talents || [];
    for (let i = 0; i < ids.length; i += 1) {
      const def = getTalent(ids[i]);
      if (def && def.flags) {
        this._applyFlags(def.flags);
      }
    }
  }

  _fireReadyTalents() {
    const ids = this.state.talents || [];
    for (let pass = 0; pass < 4; pass += 1) {
      let fired = false;
      for (let i = 0; i < ids.length; i += 1) {
        const id = ids[i];
        if (this.state.talentFired[id]) {
          continue;
        }
        const def = getTalent(id);
        if (!def) {
          this.state.talentFired[id] = true;
          continue;
        }
        if (this.state.age < def.minAge) {
          continue;
        }
        if (!this._requiredAttrsOk(def.requiredAttrs)) {
          continue;
        }
        const effects = this._talentEffectPatch(def);
        this._applyEffects(effects);
        this._applyFlags(def.flags);
        this.state.talentFired[id] = true;
        fired = true;
        this.state.yearLog.push({
          event_id: 0,
          desc: `天赋「${def.title}」发动。`,
          effects: shallowClone(effects),
        });
        this._lifeLog(`[LIFE] ${this.state.age}岁 talent ${id} ${this._fmtAttrs()}`);
      }
      if (!fired) {
        break;
      }
    }
  }

  _talentEffectPatch(def) {
    const patch = {};
    for (const key of this._attrKeys()) {
      patch[key] = 0;
    }
    const raw = def && isPlainObject(def.effects) ? def.effects : {};
    for (const key of this._attrKeys()) {
      if (raw[key] !== undefined && raw[key] !== null) {
        patch[key] = toInt(raw[key], 0);
      }
    }
    const rnd = toInt(raw.rnd, 0);
    if (rnd !== 0) {
      const keys = rndAttrKeys().filter((key) => this.mode && this.mode.isAttrKey(key));
      if (keys.length) {
        const pick = keys[Math.floor(Math.random() * keys.length)];
        patch[pick] = toInt(patch[pick], 0) + rnd;
      }
    }
    return patch;
  }

  _talentModHits(event, mod) {
    if (!event || !mod) {
      return false;
    }
    if (mod.group) {
      if (event.group === mod.group) {
        return true;
      }
      if (Array.isArray(event.cooldownGroups) && event.cooldownGroups.indexOf(mod.group) >= 0) {
        return true;
      }
      if (Array.isArray(event.tags) && event.tags.indexOf(mod.group) >= 0) {
        return true;
      }
    }
    if (mod.tag && Array.isArray(event.tags) && event.tags.indexOf(mod.tag) >= 0) {
      return true;
    }
    return false;
  }

  _talentBlocked(event) {
    const mods = this.state.talentMods || [];
    for (let i = 0; i < mods.length; i += 1) {
      const mod = mods[i];
      if (mod.op === 'block' && this._talentModHits(event, mod)) {
        return true;
      }
    }
    return false;
  }

  _talentWeightMul(event) {
    let mul = 1;
    const mods = this.state.talentMods || [];
    for (let i = 0; i < mods.length; i += 1) {
      const mod = mods[i];
      if (mod.op !== 'boost' && mod.op !== 'nerf') {
        continue;
      }
      if (!this._talentModHits(event, mod)) {
        continue;
      }
      const factor = Number(mod.mul);
      if (Number.isFinite(factor) && factor >= 0) {
        mul *= factor;
      }
    }
    if (mul < 0.05) {
      mul = 0.05;
    }
    if (mul > 8) {
      mul = 8;
    }
    return mul;
  }

  _alignmentWeightMul(event) {
    if (!this.mode || !this.mode.isAttrKey(ALIGN_ORDER_KEY) || !this.mode.isAttrKey(ALIGN_MORAL_KEY)) {
      return 1;
    }
    const fx = event && event.effects ? event.effects : {};
    return alignmentWeightMul(
      toInt(this.state.attrs[ALIGN_ORDER_KEY], 0),
      toInt(this.state.attrs[ALIGN_MORAL_KEY], 0),
      toInt(fx[ALIGN_ORDER_KEY], 0),
      toInt(fx[ALIGN_MORAL_KEY], 0),
    );
  }

  _applyEffects(effects) {
    for (const key of this._attrKeys()) {
      let nextVal = toInt(this.state.attrs[key], 0) + toInt(effects[key], 0);
      const minVal = this.mode ? this.mode.attrMin(key) : 0;
      if (minVal !== null && minVal !== undefined && nextVal < minVal) {
        nextVal = minVal;
      }
      this.state.attrs[key] = nextVal;
    }
    this._syncAttrPeaks();
  }

  _syncAttrPeaks() {
    const state = this.state;
    if (!state.attrPeak) {
      state.attrPeak = {};
    }
    for (const key of this._attrKeys()) {
      const v = toInt(state.attrs[key], 0);
      if (!Object.prototype.hasOwnProperty.call(state.attrPeak, key) || v > toInt(state.attrPeak[key], v)) {
        state.attrPeak[key] = v;
      }
    }
    this._unlockAttrPeakAchievements();
  }

  _unlockAttrPeakAchievements() {
    const peaks = this.state.attrPeak || {};
    const ids = {
      str: 'peak_str_40',
      agi: 'peak_agi_40',
      int: 'peak_int_40',
      wis: 'peak_wis_40',
      con: 'peak_con_40',
      cha: 'peak_cha_40',
      gold: 'peak_gold_40',
    };
    for (const key of Object.keys(ids)) {
      if (toInt(peaks[key], 0) >= 40) {
        unlock(ids[key]);
      }
    }
  }

  _applyFlags(patch) {
    if (!isPlainObject(patch)) {
      return;
    }
    for (const key of Object.keys(patch)) {
      const spec = patch[key];
      if (spec === null) {
        delete this.state.flags[key];
        continue;
      }
      if (isPlainObject(spec) && Object.prototype.hasOwnProperty.call(spec, 'operator')) {
        const op = String(spec.operator || '');
        let current = this.state.flags[key];
        if (!isNumber(current)) {
          current = 0;
        }
        let result = Number(current);
        const delta = Number(spec.value || 0);
        if (op === '+=') {
          result += delta;
        } else if (op === '-=') {
          result -= delta;
        }
        if (result < 0) {
          result = 0;
        }
        const rounded = Math.round(result);
        if (Math.abs(result - rounded) < 1e-5) {
          this.state.flags[key] = rounded;
        } else {
          this.state.flags[key] = result;
        }
        continue;
      }
      this.state.flags[key] = spec;
    }
  }

  _calcWeight(event) {
    let weight = Number(event.baseWeight);
    if (isPlainObject(event.ageModifiers)) {
      const peak = event.ageModifiers.peak === undefined
        ? this.state.age
        : Number(event.ageModifiers.peak);
      const decay = event.ageModifiers.decay === undefined
        ? 1
        : Number(event.ageModifiers.decay);
      weight *= Math.pow(decay, Math.abs(this.state.age - peak));
    }
    for (const item of event.weightModifiers) {
      if (!isPlainObject(item)) {
        continue;
      }
      const attrName = String(item.attr || '');
      const base = Number(item.base || 0);
      const multiplier = Number(item.multiplier || 0);
      let attrVal;
      if (this.mode && this.mode.isClockName(attrName)) {
        attrVal = this.state.age;
      } else {
        attrVal = Number(this.state.attrs[attrName] || 0);
      }
      let factor = 1 + (attrVal - base) * multiplier * 0.1;
      let minFactor = item.minFactor === undefined ? 0 : Number(item.minFactor);
      if (minFactor < 0) {
        minFactor = 0;
      }
      if (factor < minFactor) {
        factor = minFactor;
      }
      weight *= factor;
    }
    weight *= this._talentWeightMul(event);
    weight *= this._alignmentWeightMul(event);
    if (weight < 0) {
      return 0;
    }
    return weight;
  }

  _requiredAttrsOk(required) {
    if (!isPlainObject(required) || Object.keys(required).length === 0) {
      return true;
    }
    for (const key of Object.keys(required)) {
      if (this.mode && !this.mode.isAttrKey(key)) {
        return false;
      }
      const actual = this.state.attrs[key] === undefined ? 0 : this.state.attrs[key];
      if (!this._evalLeaf(actual, required[key])) {
        return false;
      }
    }
    return true;
  }

  _requiredFlagsOk(groups) {
    if (!Array.isArray(groups) || groups.length === 0) {
      return true;
    }
    for (const group of groups) {
      if (isPlainObject(group) && this._flagGroupOk(group)) {
        return true;
      }
    }
    return false;
  }

  _flagGroupOk(group) {
    for (const key of Object.keys(group)) {
      const spec = group[key];
      const actual = this._flagValue(String(key), spec);
      if (!this._evalLeaf(actual, spec)) {
        return false;
      }
    }
    return true;
  }

  _flagValue(flagName, spec) {
    if (Object.prototype.hasOwnProperty.call(this.state.flags, flagName)) {
      return this.state.flags[flagName];
    }
    let sample = spec;
    let op = '==';
    if (isPlainObject(spec) && Object.prototype.hasOwnProperty.call(spec, 'operator')) {
      op = String(spec.operator || '==');
      sample = spec.value;
    }
    if (op === '>' || op === '>=' || op === '<' || op === '<=') {
      return 0;
    }
    if (typeof sample === 'boolean') {
      return false;
    }
    if (typeof sample === 'number') {
      return 0;
    }
    if (typeof sample === 'string') {
      return '';
    }
    return null;
  }

  _evalLeaf(actual, spec) {
    if (isPlainObject(spec) && Object.prototype.hasOwnProperty.call(spec, 'operator')) {
      return this._compare(actual, String(spec.operator || '=='), spec.value);
    }
    return this._compare(actual, '==', spec);
  }

  _valuesEqual(left, right) {
    if (left === null && right === null) {
      return true;
    }
    if (left === null || right === null) {
      return false;
    }
    if (isNumber(left) && isNumber(right)) {
      return Number(left) === Number(right);
    }
    if (typeof left !== typeof right) {
      return false;
    }
    return left === right;
  }

  _compare(left, op, right) {
    if (op === '>' || op === '>=' || op === '<' || op === '<=') {
      if (!isNumber(left) || !isNumber(right)) {
        return false;
      }
      if (op === '>') {
        return left > right;
      }
      if (op === '>=') {
        return left >= right;
      }
      if (op === '<') {
        return left < right;
      }
      return left <= right;
    }
    const equal = this._valuesEqual(left, right);
    if (op === '==') {
      return equal;
    }
    if (op === '!=') {
      return !equal;
    }
    return false;
  }

  _lifeLog(line) {
    console.log(line);
  }

  _logYearHeader(mustIds, unlockedDue, drawText) {
    let extra = '';
    if (unlockedDue.length > 0) {
      extra = ` 解锁${this._joinIds(unlockedDue)}`;
    }
    this._lifeLog(`[LIFE] ${this.state.age}岁 必然${this._joinIds(mustIds)} 抽=${drawText}${extra}`);
  }

  _logFired(event, via, flagsBefore) {
    const line1 = `[LIFE] ${this.state.age}岁 #${event.eventId} ${event.type}/${via} ${this._clip(event.desc, 28)}  ${this._fmtAttrs()}`;
    this._lifeLog(line1);
    const extras = [];
    const delta = this._fmtAttrDelta(event.effects);
    if (delta) {
      extras.push(delta);
    }
    const flagImpact = this._fmtFlagImpact(event, flagsBefore);
    if (flagImpact) {
      extras.push(`flags ${flagImpact}`);
    }
    const chain = this._fmtChain(event);
    if (chain) {
      extras.push(chain);
    }
    if (event.type === 'death') {
      extras.push('DEAD');
    }
    if (extras.length === 0) {
      return;
    }
    this._lifeLog(`[LIFE]   ${extras.join('  ')}`);
  }

  _fmtAttrs() {
    if (!this.mode) {
      return '';
    }
    return this.mode.attrs
      .map((def) => `${def.short}${toInt(this.state.attrs[def.key], 0)}`)
      .join('');
  }

  _fmtAttrDelta(effects) {
    const bits = [];
    for (const def of this.mode ? this.mode.attrs : []) {
      const v = toInt(effects[def.key], 0);
      if (v !== 0) {
        bits.push(`${def.short}${v > 0 ? '+' : ''}${v}`);
      }
    }
    if (bits.length === 0) {
      return '';
    }
    return `Δ${bits.join(' ')}`;
  }

  _fmtFlagImpact(event, before) {
    if (!isPlainObject(event.flags) || Object.keys(event.flags).length === 0) {
      return '';
    }
    const bits = [];
    for (const key of Object.keys(event.flags)) {
      const oldTxt = Object.prototype.hasOwnProperty.call(before, key)
        ? this._fmtFlagVal(before[key])
        : 'ø';
      const newTxt = Object.prototype.hasOwnProperty.call(this.state.flags, key)
        ? this._fmtFlagVal(this.state.flags[key])
        : 'ø';
      if (oldTxt === newTxt) {
        continue;
      }
      bits.push(`${key}:${oldTxt}→${newTxt}`);
    }
    return bits.join(' ');
  }

  _fmtFlagPatch(before, patch) {
    const bits = [];
    for (const key of Object.keys(patch)) {
      const oldTxt = Object.prototype.hasOwnProperty.call(before, key)
        ? this._fmtFlagVal(before[key])
        : 'ø';
      const newTxt = Object.prototype.hasOwnProperty.call(this.state.flags, key)
        ? this._fmtFlagVal(this.state.flags[key])
        : 'ø';
      if (oldTxt === newTxt) {
        continue;
      }
      bits.push(`${key}:${oldTxt}→${newTxt}`);
    }
    return bits.join(' ');
  }

  _fmtFlagVal(value) {
    if (value === null || value === undefined) {
      return 'ø';
    }
    return String(value);
  }

  _fmtChain(event) {
    const bits = [];
    const d0 = [];
    const later = [];
    for (const item of event.followUp) {
      if (!isPlainObject(item)) {
        continue;
      }
      const eventId = toInt(item.eventId, 0);
      const delay = toInt(item.delay, 0);
      if (eventId <= 0) {
        continue;
      }
      if (delay === 0) {
        d0.push(String(eventId));
      } else {
        later.push(`${eventId}@+${delay}`);
      }
    }
    if (d0.length > 0) {
      bits.push(`d0+${d0.join(',')}`);
    }
    if (later.length > 0) {
      bits.push(`fu+${later.join(',')}`);
    }
    const unlocks = [];
    for (const eventId of event.unlockEvents) {
      unlocks.push(`${toInt(eventId, 0)}@+1`);
    }
    for (const item of event.unlockDelayed) {
      if (isPlainObject(item)) {
        unlocks.push(`${toInt(item.eventId, 0)}@+${toInt(item.delay, 0)}`);
      }
    }
    if (unlocks.length > 0) {
      bits.push(`unl+${unlocks.join(',')}`);
    }
    if (event.mutexEvents.length > 0) {
      const joined = this._joinIds(event.mutexEvents);
      bits.push(`ban+${joined.slice(1, -1)}`);
    }
    if (event.group !== null) {
      bits.push(`g=${event.group}`);
    }
    if (event.groupFallbackAge >= 0) {
      bits.push(`fb@${event.groupFallbackAge}`);
    }
    const delayedFlags = [];
    for (const item of event.flagsDelayed) {
      if (!isPlainObject(item)) {
        continue;
      }
      const delay = toInt(item.delay, 0);
      const patch = item.flags;
      if (delay < 1 || !isPlainObject(patch)) {
        continue;
      }
      const names = Object.keys(patch);
      if (names.length > 0) {
        delayedFlags.push(`${names.join(',')}@+${delay}`);
      }
    }
    if (delayedFlags.length > 0) {
      bits.push(`fd+${delayedFlags.join(',')}`);
    }
    return bits.join(' ');
  }

  _joinIds(ids) {
    if (!ids || ids.length === 0) {
      return '[]';
    }
    return `[${ids.map((id) => String(toInt(id, 0))).join(',')}]`;
  }

  _clip(text, maxLen) {
    const str = String(text);
    if (str.length <= maxLen) {
      return str;
    }
    return `${str.slice(0, maxLen)}…`;
  }

  _getEvent(eventId) {
    return this.catalog.get(eventId) || null;
  }
}
