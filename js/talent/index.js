const GRADE_WEIGHT = [889, 100, 10, 1];
const DRAW_COUNT = 6;
const PICK_MAX = 3;
const RND_ATTRS = ['str', 'agi', 'int', 'wis', 'con', 'cha'];

let catalog = [];
let byId = {};

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

function parseExclusive(raw) {
  const src = Array.isArray(raw) ? raw : [];
  const out = [];
  const seen = {};
  for (let i = 0; i < src.length; i += 1) {
    const id = String(src[i] || '').trim();
    if (!id || seen[id]) {
      continue;
    }
    seen[id] = true;
    out.push(id);
  }
  return out;
}

function parseEventMods(raw) {
  const src = Array.isArray(raw) ? raw : [];
  const out = [];
  for (let i = 0; i < src.length; i += 1) {
    const row = src[i];
    if (!isPlainObject(row)) {
      continue;
    }
    const op = String(row.op || '').trim();
    if (op !== 'boost' && op !== 'nerf' && op !== 'block') {
      continue;
    }
    const mod = { op };
    if (row.group !== undefined && row.group !== null && String(row.group).trim()) {
      mod.group = String(row.group).trim();
    }
    if (row.tag !== undefined && row.tag !== null && String(row.tag).trim()) {
      mod.tag = String(row.tag).trim();
    }
    if (op !== 'block') {
      let mul = Number(row.mul);
      if (!Number.isFinite(mul) || mul < 0) {
        mul = 1;
      }
      mod.mul = mul;
    }
    if (!mod.group && !mod.tag) {
      continue;
    }
    out.push(mod);
  }
  return out;
}

function parseReplacement(raw) {
  if (!isPlainObject(raw)) {
    return null;
  }
  const out = {};
  if (raw.grade !== undefined && raw.grade !== null) {
    const g = toInt(raw.grade, -1);
    if (g >= 0 && g <= 3) {
      out.grade = g;
    }
  }
  if (Array.isArray(raw.ids)) {
    out.ids = parseExclusive(raw.ids);
  }
  if (Array.isArray(raw.weighted)) {
    const weighted = [];
    for (let i = 0; i < raw.weighted.length; i += 1) {
      const row = raw.weighted[i];
      if (Array.isArray(row) && row.length >= 2) {
        const id = String(row[0] || '').trim();
        const w = Number(row[1]);
        if (id && Number.isFinite(w) && w > 0) {
          weighted.push({ id, weight: w });
        }
      } else if (isPlainObject(row) && row.id) {
        const id = String(row.id).trim();
        const w = Number(row.weight);
        if (id && Number.isFinite(w) && w > 0) {
          weighted.push({ id, weight: w });
        }
      }
    }
    if (weighted.length) {
      out.weighted = weighted;
    }
  }
  if (out.grade === undefined && !out.ids && !out.weighted) {
    return null;
  }
  return out;
}

function parseCatalog(raw) {
  const rows = Array.isArray(raw)
    ? raw
    : raw && Array.isArray(raw.talents)
      ? raw.talents
      : [];
  const out = [];
  const seen = {};
  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i];
    if (!isPlainObject(row)) {
      continue;
    }
    const id = row.id === undefined || row.id === null ? '' : String(row.id).trim();
    if (!id || seen[id]) {
      continue;
    }
    seen[id] = true;
    const title = row.title === undefined || row.title === null ? id : String(row.title);
    const desc = row.desc === undefined || row.desc === null ? '' : String(row.desc);
    let grade = toInt(row.grade, 0);
    if (grade < 0) {
      grade = 0;
    }
    if (grade > 3) {
      grade = 3;
    }
    out.push({
      id,
      title,
      desc,
      grade,
      points: toInt(row.points, 0),
      effects: isPlainObject(row.effects) ? row.effects : {},
      flags: isPlainObject(row.flags) ? row.flags : {},
      exclusive: parseExclusive(row.exclusive),
      eventMods: parseEventMods(row.eventMods),
      replacement: parseReplacement(row.replacement),
      minAge: row.minAge === undefined || row.minAge === null ? 0 : toInt(row.minAge, 0),
      requiredAttrs: isPlainObject(row.requiredAttrs) ? row.requiredAttrs : {},
    });
  }
  return out;
}

function rebuildIndex() {
  byId = {};
  for (let i = 0; i < catalog.length; i += 1) {
    byId[catalog[i].id] = catalog[i];
  }
}

export function loadTalents(raw) {
  catalog = parseCatalog(raw);
  rebuildIndex();
  return catalog.length;
}

export function getTalent(id) {
  const key = String(id || '').trim();
  return byId[key] || null;
}

export function listTalents() {
  return catalog.slice();
}

export function extraPoints(ids) {
  const src = Array.isArray(ids) ? ids : [];
  let sum = 0;
  for (let i = 0; i < src.length; i += 1) {
    const def = getTalent(src[i]);
    if (def) {
      sum += def.points | 0;
    }
  }
  return sum;
}

export function isExclusiveWith(a, b) {
  const left = typeof a === 'string' ? getTalent(a) : a;
  const right = typeof b === 'string' ? getTalent(b) : b;
  if (!left || !right || left.id === right.id) {
    return false;
  }
  return left.exclusive.indexOf(right.id) >= 0 || right.exclusive.indexOf(left.id) >= 0;
}

export function pickBlockedBy(id, selected) {
  const src = Array.isArray(selected) ? selected : [];
  for (let i = 0; i < src.length; i += 1) {
    if (src[i] === id) {
      continue;
    }
    if (isExclusiveWith(id, src[i])) {
      const other = getTalent(src[i]);
      return other ? other.title : src[i];
    }
  }
  return '';
}

function pickFrom(list) {
  if (!list.length) {
    return null;
  }
  return list[Math.floor(Math.random() * list.length)];
}

function pickWeighted(items) {
  let total = 0;
  for (let i = 0; i < items.length; i += 1) {
    total += items[i].weight;
  }
  if (total <= 0) {
    return null;
  }
  let roll = Math.random() * total;
  for (let i = 0; i < items.length; i += 1) {
    roll -= items[i].weight;
    if (roll <= 0) {
      return items[i].id;
    }
  }
  return items[items.length - 1].id;
}

function rollGrade() {
  let roll = Math.random() * 1000;
  for (let g = GRADE_WEIGHT.length - 1; g >= 0; g -= 1) {
    roll -= GRADE_WEIGHT[g];
    if (roll <= 0) {
      return g;
    }
  }
  return 0;
}

export function drawTalents(count = DRAW_COUNT) {
  const buckets = [[], [], [], []];
  for (let i = 0; i < catalog.length; i += 1) {
    buckets[catalog[i].grade].push(catalog[i]);
  }
  const taken = {};
  const out = [];
  const n = Math.max(0, toInt(count, DRAW_COUNT));
  let guard = 0;
  while (out.length < n && out.length < catalog.length && guard < 80) {
    guard += 1;
    let grade = rollGrade();
    while (grade >= 0 && buckets[grade].filter((t) => !taken[t.id]).length === 0) {
      grade -= 1;
    }
    if (grade < 0) {
      const rest = catalog.filter((t) => !taken[t.id]);
      const pick = pickFrom(rest);
      if (!pick) {
        break;
      }
      taken[pick.id] = true;
      out.push(pick);
      continue;
    }
    const pool = buckets[grade].filter((t) => !taken[t.id]);
    const pick = pickFrom(pool);
    if (!pick) {
      continue;
    }
    taken[pick.id] = true;
    out.push(pick);
  }
  return out;
}

function allowedReplacement(id, def, used) {
  if (!id || id === def.id || !getTalent(id) || used[id]) {
    return false;
  }
  const others = Object.keys(used);
  for (let i = 0; i < others.length; i += 1) {
    const otherId = others[i];
    if (!used[otherId] || otherId === def.id) {
      continue;
    }
    if (isExclusiveWith(id, otherId)) {
      return false;
    }
  }
  return true;
}

function replacementCandidates(def, used) {
  const spec = def.replacement;
  if (!spec) {
    return [];
  }
  let rows = [];
  if (spec.weighted) {
    rows = spec.weighted.slice();
  } else if (spec.ids && spec.ids.length) {
    rows = spec.ids.map((id) => ({ id, weight: 1 }));
  } else if (spec.grade !== undefined) {
    for (let i = 0; i < catalog.length; i += 1) {
      const t = catalog[i];
      if (t.grade === spec.grade) {
        rows.push({ id: t.id, weight: 1 });
      }
    }
  }
  return rows.filter((row) => allowedReplacement(row.id, def, used));
}

export function resolvePicks(ids) {
  const src = Array.isArray(ids) ? ids : [];
  const used = {};
  for (let i = 0; i < src.length; i += 1) {
    used[String(src[i])] = true;
  }
  const out = [];
  const seen = {};
  for (let i = 0; i < src.length; i += 1) {
    const id = String(src[i] || '').trim();
    const def = getTalent(id);
    if (!def) {
      continue;
    }
    let nextId = id;
    if (def.replacement) {
      const cand = replacementCandidates(def, used);
      const picked = pickWeighted(cand);
      if (picked) {
        delete used[id];
        used[picked] = true;
        nextId = picked;
      }
    }
    if (seen[nextId]) {
      continue;
    }
    seen[nextId] = true;
    out.push(nextId);
  }
  return out;
}

export function collectEventMods(ids) {
  const src = Array.isArray(ids) ? ids : [];
  const out = [];
  for (let i = 0; i < src.length; i += 1) {
    const def = getTalent(src[i]);
    if (!def) {
      continue;
    }
    for (let j = 0; j < def.eventMods.length; j += 1) {
      out.push(def.eventMods[j]);
    }
  }
  return out;
}

export function rndAttrKeys() {
  return RND_ATTRS.slice();
}

export const TALENT_PICK_MAX = PICK_MAX;
export const TALENT_DRAW_COUNT = DRAW_COUNT;
export const BASE_POINTS = 30;
