import { ctx, PIXEL_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT, SAFE_AREA } from '../render';

const FONT_STACK = 'PingFang SC, Hiragino Sans GB, Heiti SC, sans-serif';
const TOTAL_POINTS = 30;
const COLORS = {
  bg: '#171412',
  title: '#eddcb8',
  subtitle: '#9e8f7a',
  value: '#f2e6c7',
  button: '#3a322c',
  buttonText: '#f2e6c7',
  buttonBorder: '#5a4e44',
  buttonDisabled: '#2a2420',
  buttonDisabledText: '#6a5e54',
  row: '#241f1c',
};

function roundRectPath(context, x, y, w, h, r) {
  const radius = Math.min(r, w / 2, h / 2);
  context.beginPath();
  if (typeof context.roundRect === 'function') {
    context.roundRect(x, y, w, h, radius);
    return;
  }
  context.moveTo(x + radius, y);
  context.arcTo(x + w, y, x + w, y + h, radius);
  context.arcTo(x + w, y + h, x, y + h, radius);
  context.arcTo(x, y + h, x, y, radius);
  context.arcTo(x, y, x + w, y, radius);
  context.closePath();
}

function hitRect(rect, x, y) {
  return x >= rect.x && x <= rect.x + rect.w && y >= rect.y && y <= rect.y + rect.h;
}

function touchPoint(touch) {
  if (!touch) {
    return null;
  }
  const x = touch.clientX !== undefined ? touch.clientX : touch.x;
  const y = touch.clientY !== undefined ? touch.clientY : touch.y;
  return { x, y };
}

export default class PrepareView {
  constructor({ attrs, onConfirm }) {
    this.attrDefs = Array.isArray(attrs) ? attrs : [];
    this.onConfirm = onConfirm;
    this.points = {};
    this._resetPoints();
    this.active = false;
    this.width = SCREEN_WIDTH;
    this.height = SCREEN_HEIGHT;
    this.pixelRatio = PIXEL_RATIO;
    this.safeArea = SAFE_AREA;
    this.buttons = {};
    this.rows = [];
    this.touch = null;
    this._onTouchStart = this._onTouchStart.bind(this);
    this._onTouchMove = this._onTouchMove.bind(this);
    this._onTouchEnd = this._onTouchEnd.bind(this);
    this._onResize = this._onResize.bind(this);
  }

  start() {
    this.active = true;
    this._resetPoints();
    wx.onTouchStart(this._onTouchStart);
    wx.onTouchMove(this._onTouchMove);
    wx.onTouchEnd(this._onTouchEnd);
    wx.onTouchCancel(this._onTouchEnd);
    if (typeof wx.onWindowResize === 'function') {
      wx.onWindowResize(this._onResize);
    }
    this._layout();
    this.render();
  }

  stop() {
    this.active = false;
    if (typeof wx.offTouchStart === 'function') {
      wx.offTouchStart(this._onTouchStart);
      wx.offTouchMove(this._onTouchMove);
      wx.offTouchEnd(this._onTouchEnd);
      wx.offTouchCancel(this._onTouchEnd);
    }
    if (typeof wx.offWindowResize === 'function') {
      wx.offWindowResize(this._onResize);
    }
  }

  _resetPoints() {
    this.points = {};
    for (const def of this.attrDefs) {
      this.points[def.key] = 0;
    }
  }

  _spent() {
    let sum = 0;
    for (const def of this.attrDefs) {
      sum += this.points[def.key] | 0;
    }
    return sum;
  }

  _remaining() {
    return TOTAL_POINTS - this._spent();
  }

  _onResize() {
    if (!this.active) {
      return;
    }
    const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();
    this.width = info.screenWidth;
    this.height = info.screenHeight;
    this.pixelRatio = info.pixelRatio || 1;
    this.safeArea = info.safeArea || {
      left: 0,
      top: 0,
      right: this.width,
      bottom: this.height,
    };
    canvas.width = Math.floor(this.width * this.pixelRatio);
    canvas.height = Math.floor(this.height * this.pixelRatio);
    this._layout();
    this.render();
  }

  _layout() {
    const w = this.width;
    const h = this.height;
    const safe = this.safeArea;
    const padX = 28;
    const padTop = Math.max(20, (safe.top || 0) + 12);
    const padBottom = Math.max(20, h - (safe.bottom || h) + 16);
    const innerW = w - padX * 2;
    const randomH = 40;
    const reincarnateH = 52;
    const headerBottom = padTop + randomH + 16;
    const listBottom = h - padBottom - reincarnateH - 16;
    const listH = Math.max(120, listBottom - headerBottom);
    const n = Math.max(1, this.attrDefs.length);
    const gap = 10;
    const rowH = Math.min(64, Math.max(48, (listH - gap * (n - 1)) / n));
    const rows = [];
    let y = headerBottom;
    for (const def of this.attrDefs) {
      const stepper = 44;
      rows.push({
        key: def.key,
        label: def.label,
        y,
        h: rowH,
        minus: { x: padX + 10, y: y + (rowH - stepper) / 2, w: stepper, h: stepper },
        plus: {
          x: padX + innerW - 10 - stepper,
          y: y + (rowH - stepper) / 2,
          w: stepper,
          h: stepper,
        },
      });
      y += rowH + gap;
    }
    this.layout = { padX, padTop, innerW, headerBottom };
    this.rows = rows;
    this.buttons = {
      random: { x: padX, y: padTop, w: 88, h: randomH, id: 'random' },
      reincarnate: {
        x: padX,
        y: h - padBottom - reincarnateH,
        w: innerW,
        h: reincarnateH,
        id: 'reincarnate',
      },
    };
  }

  _randomize() {
    this._resetPoints();
    const keys = this.attrDefs.map((def) => def.key);
    if (keys.length === 0) {
      this.render();
      return;
    }
    for (let i = 0; i < TOTAL_POINTS; i += 1) {
      const key = keys[Math.floor(Math.random() * keys.length)];
      this.points[key] += 1;
    }
    this.render();
  }

  _adjust(key, delta) {
    const current = this.points[key] | 0;
    if (delta < 0 && current <= 0) {
      return;
    }
    if (delta > 0 && this._remaining() <= 0) {
      return;
    }
    this.points[key] = current + delta;
    this.render();
  }

  render() {
    this._layout();
    ctx.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, this.width, this.height);

    this._drawButton(this.buttons.random, '随机', false);
    const remain = this._remaining();
    ctx.font = `16px ${FONT_STACK}`;
    ctx.fillStyle = COLORS.subtitle;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(
      `剩余 ${remain}`,
      this.layout.padX + this.layout.innerW,
      this.buttons.random.y + this.buttons.random.h / 2,
    );

    for (const row of this.rows) {
      ctx.fillStyle = COLORS.row;
      roundRectPath(ctx, this.layout.padX, row.y, this.layout.innerW, row.h, 10);
      ctx.fill();
      const value = this.points[row.key] | 0;
      this._drawStepper(row.minus, '−', value <= 0);
      this._drawStepper(row.plus, '+', this._remaining() <= 0);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = COLORS.title;
      ctx.font = `17px ${FONT_STACK}`;
      ctx.fillText(row.label, this.width / 2, row.y + row.h / 2 - 11);
      ctx.fillStyle = COLORS.value;
      ctx.font = `bold 20px ${FONT_STACK}`;
      ctx.fillText(String(value), this.width / 2, row.y + row.h / 2 + 13);
    }

    this._drawButton(this.buttons.reincarnate, '轮回', false);
  }

  _drawButton(btn, label, disabled) {
    ctx.save();
    ctx.fillStyle = disabled ? COLORS.buttonDisabled : COLORS.button;
    roundRectPath(ctx, btn.x, btn.y, btn.w, btn.h, 10);
    ctx.fill();
    ctx.strokeStyle = COLORS.buttonBorder;
    ctx.lineWidth = 1;
    roundRectPath(ctx, btn.x, btn.y, btn.w, btn.h, 10);
    ctx.stroke();
    ctx.font = `18px ${FONT_STACK}`;
    ctx.fillStyle = disabled ? COLORS.buttonDisabledText : COLORS.buttonText;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, btn.x + btn.w / 2, btn.y + btn.h / 2);
    ctx.restore();
  }

  _drawStepper(btn, label, disabled) {
    ctx.save();
    ctx.fillStyle = disabled ? COLORS.buttonDisabled : COLORS.button;
    roundRectPath(ctx, btn.x, btn.y, btn.w, btn.h, 8);
    ctx.fill();
    ctx.font = `22px ${FONT_STACK}`;
    ctx.fillStyle = disabled ? COLORS.buttonDisabledText : COLORS.buttonText;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, btn.x + btn.w / 2, btn.y + btn.h / 2);
    ctx.restore();
  }

  _onTouchStart(event) {
    if (!this.active) {
      return;
    }
    const point = touchPoint(event.touches && event.touches[0]);
    if (!point) {
      return;
    }
    this.touch = {
      x: point.x,
      y: point.y,
      startX: point.x,
      startY: point.y,
      moved: false,
    };
  }

  _onTouchMove(event) {
    if (!this.active || !this.touch) {
      return;
    }
    const point = touchPoint(event.touches && event.touches[0]);
    if (!point) {
      return;
    }
    if (Math.abs(point.x - this.touch.startX) + Math.abs(point.y - this.touch.startY) > 8) {
      this.touch.moved = true;
    }
    this.touch.x = point.x;
    this.touch.y = point.y;
  }

  _onTouchEnd(event) {
    if (!this.active) {
      return;
    }
    const touchInfo = this.touch;
    this.touch = null;
    if (!touchInfo || touchInfo.moved) {
      return;
    }
    const point = touchPoint(event.changedTouches && event.changedTouches[0]) || {
      x: touchInfo.x,
      y: touchInfo.y,
    };
    this._handleTap(point.x, point.y);
  }

  _handleTap(x, y) {
    if (hitRect(this.buttons.random, x, y)) {
      this._randomize();
      return;
    }
    if (hitRect(this.buttons.reincarnate, x, y)) {
      if (typeof this.onConfirm === 'function') {
        const alloc = {};
        for (const def of this.attrDefs) {
          alloc[def.key] = this.points[def.key] | 0;
        }
        this.onConfirm(alloc);
      }
      return;
    }
    for (const row of this.rows) {
      if (hitRect(row.minus, x, y)) {
        this._adjust(row.key, -1);
        return;
      }
      if (hitRect(row.plus, x, y)) {
        this._adjust(row.key, 1);
        return;
      }
    }
  }
}
