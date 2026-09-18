import { ctx, PIXEL_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT, SAFE_AREA, contentTop, bindFrame, bindViewFrame } from '../render';
import {
  ALIGN_CELLS,
  ALIGN_COL_HEADERS,
  ALIGN_ROW_HEADERS,
  alignmentTitle,
  axisBand,
  axisToPos,
  cellIndex,
} from '../life/alignment';

const FONT_STACK = 'PingFang SC, Hiragino Sans GB, Heiti SC, sans-serif';
const COLORS = {
  bg: '#171412',
  title: '#eddcb8',
  subtitle: '#9e8f7a',
  label: '#f2e6c7',
  row: '#241f1c',
  gridLine: '#5a4e44',
  gridFill: '#1c1917',
  gridFillOn: '#322b26',
  cellText: '#8c8070',
  cellTextOn: '#eddcb8',
  header: '#c4b49a',
  dot: '#e8943a',
  dotStroke: '#2a1a08',
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
  constructor({ attrs, peaks, alignment, onRestart }) {
    this.attrDefs = Array.isArray(attrs) ? attrs : [];
    this.peaks = peaks && typeof peaks === 'object' ? peaks : {};
    this.alignment = alignment && typeof alignment === 'object'
      ? alignment
      : { order: 0, moral: 0 };
    this.onRestart = onRestart;
    this.active = false;
    this.width = SCREEN_WIDTH;
    this.height = SCREEN_HEIGHT;
    this.pixelRatio = PIXEL_RATIO;
    this.safeArea = SAFE_AREA;
    this.buttons = {};
    this.rows = [];
    this.grid = null;
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
    bindViewFrame(this);
    this.render();
  }

  stop() {
    this.active = false;
    bindFrame(null);
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

  _order() {
    return this.alignment.order | 0;
  }

  _moral() {
    return this.alignment.moral | 0;
  }

  _layout() {
    const w = this.width;
    const h = this.height;
    const safe = this.safeArea;
    const padX = 24;
    const padTop = contentTop();
    const padBottom = Math.max(20, h - (safe.bottom || h) + 16);
    const innerW = w - padX * 2;
    const restartH = 52;
    const titleH = 32;
    const subtitleH = 20;
    const headerBottom = padTop + titleH + 6 + subtitleH + 12;
    const conclusionH = 36;
    const valueH = 20;
    const gridGap = 10;
    const restartY = h - padBottom - restartH;
    const n = this.attrDefs.length;
    const colGap = 10;
    const rowGap = 8;
    const peakH = 36;
    const peakRows = Math.ceil(Math.max(1, n) / 2);
    const peaksH = n > 0 ? peakRows * peakH + Math.max(0, peakRows - 1) * rowGap : 0;
    const peaksBottom = headerBottom + peaksH;
    const gridTop = peaksBottom + (n > 0 ? 14 : 0);
    const gridBudget = Math.max(160, restartY - 16 - conclusionH - valueH - gridGap - gridTop);
    const rowLabelW = 36;
    const colHeaderH = 28;
    const plotMax = Math.min(innerW - rowLabelW, Math.max(0, gridBudget - colHeaderH));
    const plotSize = Math.max(96, plotMax);
    const colW = (innerW - colGap) / 2;
    const rows = [];
    for (let i = 0; i < this.attrDefs.length; i += 1) {
      const def = this.attrDefs[i];
      const col = i % 2;
      const row = Math.floor(i / 2);
      rows.push({
        key: def.key,
        label: def.label,
        x: padX + col * (colW + colGap),
        y: headerBottom + row * (peakH + rowGap),
        w: colW,
        h: peakH,
      });
    }
    this.layout = {
      padX,
      padTop,
      innerW,
      titleY: padTop,
      subtitleY: padTop + titleH + 6,
      conclusionY: gridTop + colHeaderH + plotSize + gridGap,
      valueY: gridTop + colHeaderH + plotSize + gridGap + conclusionH,
    };
    this.rows = rows;
    this.grid = {
      x: padX + rowLabelW,
      y: gridTop + colHeaderH,
      size: plotSize,
      rowLabelX: padX,
      colHeaderY: gridTop,
      rowLabelW,
      colHeaderH,
    };
    this.buttons = {
      restart: {
        x: padX,
        y: restartY,
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
    ctx.fillText('本世峰值，以及落点阵营', L.padX, L.subtitleY);

    for (const row of this.rows) {
      ctx.fillStyle = COLORS.row;
      roundRectPath(ctx, row.x, row.y, row.w, row.h, 8);
      ctx.fill();
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = COLORS.label;
      ctx.font = `15px ${FONT_STACK}`;
      ctx.fillText(row.label, row.x + 10, row.y + row.h / 2);

      const value = this._peakOf(row.key);
      const tier = peakTier(value);
      const badgeW = 44;
      const badgeH = 24;
      const bx = row.x + row.w - 8 - badgeW;
      const by = row.y + (row.h - badgeH) / 2;
      ctx.fillStyle = tier.fill;
      roundRectPath(ctx, bx, by, badgeW, badgeH, 6);
      ctx.fill();
      ctx.fillStyle = tier.text;
      ctx.font = `bold 15px ${FONT_STACK}`;
      ctx.textAlign = 'center';
      ctx.fillText(String(value), bx + badgeW / 2, by + badgeH / 2);
    }

    this._drawAlignmentGrid();

    const title = alignmentTitle(this._order(), this._moral());
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillStyle = COLORS.title;
    ctx.font = `bold 26px ${FONT_STACK}`;
    ctx.fillText(title, this.width / 2, L.conclusionY);
    ctx.fillStyle = COLORS.subtitle;
    ctx.font = `13px ${FONT_STACK}`;
    ctx.fillText(`序乱 ${this._order()}  ·  善恶 ${this._moral()}`, this.width / 2, L.valueY);

    this._drawButton(this.buttons.restart, '重开');
  }

  _drawAlignmentGrid() {
    const grid = this.grid;
    if (!grid) {
      return;
    }
    const order = this._order();
    const moral = this._moral();
    const colOn = cellIndex(axisBand(order));
    const rowOn = cellIndex(axisBand(moral));
    const cell = grid.size / 3;

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = COLORS.header;
    ctx.font = `13px ${FONT_STACK}`;
    for (let c = 0; c < 3; c += 1) {
      ctx.fillText(
        ALIGN_COL_HEADERS[c],
        grid.x + cell * c + cell / 2,
        grid.colHeaderY + grid.colHeaderH / 2,
      );
    }
    ctx.font = `13px ${FONT_STACK}`;
    for (let r = 0; r < 3; r += 1) {
      ctx.fillText(
        ALIGN_ROW_HEADERS[r],
        grid.rowLabelX + grid.rowLabelW / 2,
        grid.y + cell * r + cell / 2,
      );
    }

    for (let r = 0; r < 3; r += 1) {
      for (let c = 0; c < 3; c += 1) {
        const x = grid.x + cell * c;
        const y = grid.y + cell * r;
        const on = c === colOn && r === rowOn;
        ctx.fillStyle = on ? COLORS.gridFillOn : COLORS.gridFill;
        ctx.fillRect(x, y, cell, cell);
        ctx.strokeStyle = COLORS.gridLine;
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 0.5, y + 0.5, cell - 1, cell - 1);
        ctx.fillStyle = on ? COLORS.cellTextOn : COLORS.cellText;
        ctx.font = `12px ${FONT_STACK}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(ALIGN_CELLS[r][c], x + cell / 2, y + cell / 2);
      }
    }

    ctx.strokeStyle = COLORS.gridLine;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(grid.x + 0.5, grid.y + 0.5, grid.size - 1, grid.size - 1);

    const radius = Math.max(5, Math.min(8, cell * 0.12));
    const inner = Math.max(0, grid.size - radius * 2);
    const dx = grid.x + radius + axisToPos(order, inner);
    const dy = grid.y + radius + axisToPos(moral, inner);
    ctx.beginPath();
    ctx.arc(dx, dy, radius, 0, Math.PI * 2);
    ctx.fillStyle = COLORS.dot;
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = COLORS.dotStroke;
    ctx.stroke();
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
