import { ctx, PIXEL_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT, SAFE_AREA } from '../render';

const FONT_STACK = 'PingFang SC, Hiragino Sans GB, Heiti SC, sans-serif';
const COLORS = {
  bg: '#171412',
  title: '#eddcb8',
  subtitle: '#9e8f7a',
  label: '#f2e6c7',
  row: '#241f1c',
  button: '#3a322c',
  buttonText: '#f2e6c7',
  buttonBorder: '#5a4e44',
};

const TIER_STYLES = [
  { min: 0, max: 5, fill: '#3a3836', text: '#d8cfc2' },
  { min: 6, max: 10, fill: '#e4dfd6', text: '#2c2824' },
  { min: 11, max: 15, fill: '#3e9a5c', text: '#f4fff6' },
  { min: 16, max: 20, fill: '#3b7fd4', text: '#f0f6ff' },
  { min: 21, max: 25, fill: '#8a5ad4', text: '#f6f0ff' },
  { min: 26, max: 40, fill: '#e8943a', text: '#2a1a08' },
  { min: 41, max: Infinity, fill: '#e86ba8', text: '#fff5fa' },
];

function peakTier(value) {
  const n = Number(value);
  const v = Number.isFinite(n) ? n : 0;
  if (v < 0) {
    return TIER_STYLES[0];
  }
  for (const tier of TIER_STYLES) {
    if (v >= tier.min && v <= tier.max) {
      return tier;
    }
  }
  return TIER_STYLES[TIER_STYLES.length - 1];
}

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

export default class SettleView {
  constructor({ attrs, peaks, onRestart }) {
    this.attrDefs = Array.isArray(attrs) ? attrs : [];
    this.peaks = peaks && typeof peaks === 'object' ? peaks : {};
    this.onRestart = onRestart;
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

  _peakOf(key) {
    return this.peaks[key] | 0;
  }

  _layout() {
    const w = this.width;
    const h = this.height;
    const safe = this.safeArea;
    const padX = 28;
    const padTop = Math.max(20, (safe.top || 0) + 12);
    const padBottom = Math.max(20, h - (safe.bottom || h) + 16);
    const innerW = w - padX * 2;
    const restartH = 52;
    const titleH = 36;
    const subtitleH = 22;
    const headerBottom = padTop + titleH + 8 + subtitleH + 18;
    const listBottom = h - padBottom - restartH - 16;
    const listH = Math.max(120, listBottom - headerBottom);
    const n = Math.max(1, this.attrDefs.length);
    const gap = 10;
    const rowH = Math.min(64, Math.max(48, (listH - gap * (n - 1)) / n));
    const badgeW = 88;
    const badgeH = Math.min(36, rowH - 12);
    const rows = [];
    let y = headerBottom;
    for (const def of this.attrDefs) {
      rows.push({
        key: def.key,
        label: def.label,
        y,
        h: rowH,
        badge: {
          x: padX + innerW - 14 - badgeW,
          y: y + (rowH - badgeH) / 2,
          w: badgeW,
          h: badgeH,
        },
      });
      y += rowH + gap;
    }
    this.layout = { padX, padTop, innerW, titleY: padTop, subtitleY: padTop + titleH + 8 };
    this.rows = rows;
    this.buttons = {
      restart: {
        x: padX,
        y: h - padBottom - restartH,
        w: innerW,
        h: restartH,
        id: 'restart',
      },
    };
  }

  render() {
    this._layout();
    ctx.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, this.width, this.height);

    const L = this.layout;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = COLORS.title;
    ctx.font = `bold 28px ${FONT_STACK}`;
    ctx.fillText('结算', L.padX, L.titleY);
    ctx.fillStyle = COLORS.subtitle;
    ctx.font = `14px ${FONT_STACK}`;
    ctx.fillText('本世各属性达到过的最高值', L.padX, L.subtitleY);

    for (const row of this.rows) {
      ctx.fillStyle = COLORS.row;
      roundRectPath(ctx, L.padX, row.y, L.innerW, row.h, 10);
      ctx.fill();
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = COLORS.label;
      ctx.font = `17px ${FONT_STACK}`;
      ctx.fillText(row.label, L.padX + 18, row.y + row.h / 2);

      const value = this._peakOf(row.key);
      const tier = peakTier(value);
      const badge = row.badge;
      ctx.fillStyle = tier.fill;
      roundRectPath(ctx, badge.x, badge.y, badge.w, badge.h, 8);
      ctx.fill();
      ctx.fillStyle = tier.text;
      ctx.font = `bold 20px ${FONT_STACK}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(String(value), badge.x + badge.w / 2, badge.y + badge.h / 2);
    }

    this._drawButton(this.buttons.restart, '重开');
  }

  _drawButton(btn, label) {
    ctx.save();
    ctx.fillStyle = COLORS.button;
    roundRectPath(ctx, btn.x, btn.y, btn.w, btn.h, 10);
    ctx.fill();
    ctx.strokeStyle = COLORS.buttonBorder;
    ctx.lineWidth = 1;
    roundRectPath(ctx, btn.x, btn.y, btn.w, btn.h, 10);
    ctx.stroke();
    ctx.font = `18px ${FONT_STACK}`;
    ctx.fillStyle = COLORS.buttonText;
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
    if (this.buttons.restart && hitRect(this.buttons.restart, x, y)) {
      if (typeof this.onRestart === 'function') {
        this.onRestart();
      }
    }
  }
}
