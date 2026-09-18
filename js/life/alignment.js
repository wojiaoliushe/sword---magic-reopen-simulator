const ORDER_KEY = 'order';
const MORAL_KEY = 'moral';
const ALIGN_EDGE = 30;
const ALIGN_NEUTRAL = 10;

function toInt(value, fallback = 0) {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    return fallback;
  }
  return Math.trunc(n);
}

function clamp(value, lo, hi) {
  if (value < lo) {
    return lo;
  }
  if (value > hi) {
    return hi;
  }
  return value;
}

export function alignmentWeightMul(orderAttr, moralAttr, orderFx, moralFx) {
  let mul = 1;
  const k = 0.08;
  const clampF = (factor) => clamp(factor, 0.22, 3.2);
  if (orderFx) {
    const sign = orderFx > 0 ? 1 : -1;
    const mag = Math.abs(orderFx) > 2 ? 2 : Math.abs(orderFx);
    mul *= clampF(1 + orderAttr * sign * k * mag);
  }
  if (moralFx) {
    const sign = moralFx > 0 ? 1 : -1;
    const mag = Math.abs(moralFx) > 2 ? 2 : Math.abs(moralFx);
    mul *= clampF(1 + moralAttr * sign * k * mag);
  }
  return mul;
}

export function axisBand(value) {
  const n = toInt(value, 0);
  if (n >= ALIGN_NEUTRAL) {
    return 'pos';
  }
  if (n <= -ALIGN_NEUTRAL) {
    return 'neg';
  }
  return 'mid';
}

export function alignmentTitle(order, moral) {
  const o = axisBand(order);
  const m = axisBand(moral);
  if (o === 'mid' && m === 'mid') {
    return '绝对中立';
  }
  const left = o === 'pos' ? '守序' : o === 'neg' ? '混乱' : '中立';
  const right = m === 'pos' ? '善良' : m === 'neg' ? '邪恶' : '中立';
  return `${left}${right}`;
}

export function axisToPos(value, size) {
  const n = clamp(toInt(value, 0), -ALIGN_EDGE, ALIGN_EDGE);
  if (n >= ALIGN_NEUTRAL) {
    return (size / 3) * (ALIGN_EDGE - n) / (ALIGN_EDGE - ALIGN_NEUTRAL);
  }
  if (n <= -ALIGN_NEUTRAL) {
    return (size * 2) / 3 + (size / 3) * (-ALIGN_NEUTRAL - n) / (ALIGN_EDGE - ALIGN_NEUTRAL);
  }
  return size / 2 - (n * (size / 6)) / ALIGN_NEUTRAL;
}

export function cellIndex(band) {
  if (band === 'pos') {
    return 0;
  }
  if (band === 'neg') {
    return 2;
  }
  return 1;
}

export const ALIGN_ORDER_KEY = ORDER_KEY;
export const ALIGN_MORAL_KEY = MORAL_KEY;
export const ALIGN_EDGE_VALUE = ALIGN_EDGE;
export const ALIGN_NEUTRAL_VALUE = ALIGN_NEUTRAL;

export const ALIGN_CELLS = [
  ['守序善良', '中立善良', '混乱善良'],
  ['守序中立', '绝对中立', '混乱中立'],
  ['守序邪恶', '中立邪恶', '混乱邪恶'],
];

export const ALIGN_COL_HEADERS = ['守序', '中立', '混乱'];
export const ALIGN_ROW_HEADERS = ['善良', '中立', '邪恶'];
