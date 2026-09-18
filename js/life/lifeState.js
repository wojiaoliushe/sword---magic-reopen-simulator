export default class LifeState {
  constructor(mode) {
    this.age = mode && mode.clock ? mode.clock.start : 0;
    this.dead = false;
    this.attrs = {};
    this.attrPeak = {};
    if (mode && Array.isArray(mode.attrs)) {
      for (const def of mode.attrs) {
        this.attrs[def.key] = def.initial;
        this.attrPeak[def.key] = def.initial;
      }
    }
    this.flags = {};
    this.history = [];
    this.experienced = {};
    this.unlocked = {};
    this.disabled = {};
    this.triggerCount = {};
    this.lastTriggerAge = {};
    this.cooldownCount = {};
    this.cooldownLastAge = {};
    this.unlockWait = [];
    this.followWait = [];
    this.flagWait = [];
    this.yearQueue = [];
    this.yearGroups = {};
    this.yearFired = {};
    this.yearLog = [];
    this.yearDelay0 = {};
    this.talents = [];
    this.talentFired = {};
    this.talentMods = [];
  }

  clearYear() {
    this.yearQueue = [];
    this.yearGroups = {};
    this.yearFired = {};
    this.yearLog = [];
    this.yearDelay0 = {};
  }
}
