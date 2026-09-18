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

export default class ModeDef {
  constructor() {
    this.id = '';
    this.title = '';
    this.subtitle = '';
    this.clock = {
      key: 'age',
      label: '岁',
      start: 0,
    };
    this.attrs = [];
    this.attrKeys = [];
    this.attrByKey = {};
  }

  isAttrKey(key) {
    return Object.prototype.hasOwnProperty.call(this.attrByKey, String(key));
  }

  isClockName(key) {
    const name = String(key);
    return name === this.clock.key || name === 'age';
  }

  attrMin(key) {
    const def = this.attrByKey[key];
    if (!def) {
      return 0;
    }
    if (def.min === undefined || def.min === null) {
      return null;
    }
    return def.min;
  }

  static parse(data) {
    if (!isPlainObject(data)) {
      return { error: 'mode.json 必须是对象' };
    }
    const mode = new ModeDef();
    mode.id = data.id === undefined || data.id === null ? '' : String(data.id);
    if (!mode.id) {
      return { error: 'mode.json 缺少 id' };
    }
    mode.title = data.title === undefined || data.title === null ? mode.id : String(data.title);
    mode.subtitle = data.subtitle === undefined || data.subtitle === null
      ? ''
      : String(data.subtitle);
    const clock = isPlainObject(data.clock) ? data.clock : {};
    const clockKey = clock.key === undefined || clock.key === null || String(clock.key) === ''
      ? 'age'
      : String(clock.key);
    mode.clock = {
      key: clockKey,
      label: clock.label === undefined || clock.label === null || String(clock.label) === ''
        ? '岁'
        : String(clock.label),
      start: toInt(clock.start, 0),
    };
    if (!Array.isArray(data.attrs) || data.attrs.length === 0) {
      return { error: `${mode.id} 未声明 attrs` };
    }
    const seen = {};
    for (const raw of data.attrs) {
      if (!isPlainObject(raw)) {
        continue;
      }
      const key = raw.key === undefined || raw.key === null ? '' : String(raw.key);
      if (!key) {
        return { error: `${mode.id} 存在空的属性 key` };
      }
      if (key === mode.clock.key) {
        return { error: `${mode.id} 属性 key 不能与时钟 ${mode.clock.key} 重名` };
      }
      if (seen[key]) {
        return { error: `${mode.id} 重复属性 key: ${key}` };
      }
      seen[key] = true;
      const label = raw.label === undefined || raw.label === null || String(raw.label) === ''
        ? key
        : String(raw.label);
      const short = raw.short === undefined || raw.short === null || String(raw.short) === ''
        ? label.slice(0, 1)
        : String(raw.short);
      const alloc = raw.alloc !== false;
      let min;
      if (raw.min === undefined || raw.min === null) {
        min = alloc ? 0 : null;
      } else {
        min = toInt(raw.min, 0);
      }
      const def = {
        key,
        label,
        short,
        initial: raw.initial === undefined || raw.initial === null ? 5 : toInt(raw.initial, 5),
        min,
        alloc,
      };
      mode.attrs.push(def);
      mode.attrKeys.push(key);
      mode.attrByKey[key] = def;
    }
    if (mode.attrs.length === 0) {
      return { error: `${mode.id} 没有有效属性` };
    }
    return { mode, error: '' };
  }
}

export function resolveModeEntry(index) {
  if (!isPlainObject(index)) {
    return { error: 'modes.json 必须是对象' };
  }
  const modes = Array.isArray(index.modes) ? index.modes : [];
  if (modes.length === 0) {
    return { error: 'modes.json 未声明任何模式' };
  }
  const defaultId = index.default === undefined || index.default === null
    ? ''
    : String(index.default);
  let entry = null;
  for (const item of modes) {
    if (!isPlainObject(item)) {
      continue;
    }
    if (defaultId && String(item.id) === defaultId) {
      entry = item;
      break;
    }
  }
  if (!entry) {
    entry = modes[0];
  }
  if (!isPlainObject(entry) || !entry.path) {
    return { error: '默认模式缺少 path' };
  }
  return {
    entry: {
      id: String(entry.id || ''),
      path: String(entry.path).replace(/\/$/, ''),
    },
    error: '',
  };
}
