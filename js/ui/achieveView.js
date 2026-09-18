import { ctx, PIXEL_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT, SAFE_AREA, contentTop, bindFrame, bindViewFrame } from '../render';
import { listAchievements } from '../achieve/index';

const FONT_STACK = 'PingFang SC, Hiragino Sans GB, Heiti SC, sans-serif';
const COLORS = {
  bg: '#171412',
  title: '#eddcb8',
  subtitle: '#9e8f7a',
  cardOn: '#2a241f',
  cardOff: '#1c1917',
  nameOn: '#eddcb8',
  nameOff: '#6a5e54',
  hintOn: '#c4b49a',
  hintOff: '#5a5048',
  button: '#3a322c',
  buttonText: '#f2e6c7',
  buttonBorder: '#5a4e44',
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

export default class AchieveView {
  constructor({ onBack }) {
    this.onBack = onBack;
    this.items = [];
    this.active = false;
    this.width = SCREEN_WIDTH;
    this.height = SCREEN_HEIGHT;
    this.pixelRatio = PIXEL_RATIO;
    this.safeArea = SAFE_AREA;
    this.buttons = {};
    this.cards = [];
    this.listRect = { x: 0, y: 0, w: 0, h: 0 };
    this.scroll = 0;
    this.contentHeight = 0;
    this.touch = null;
    this._onTouchStart = this._onTouchStart.bind(this);
    this._onTouchMove = this._onTouchMove.bind(this);
    this._onTouchEnd = this._onTouchEnd.bind(this);
    this._onResize = this._onResize.bind(this);
  }

  start() {
    this.active = true;
    this.items = listAchievements();
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

  _layout() {
    const w = this.width;
    const h = this.height;
    const safe = this.safeArea;
    const padX = 24;
    const padTop = contentTop();
    const padBottom = Math.max(20, h - (safe.bottom || h) + 16);
    const innerW = w - padX * 2;
    const backH = 52;
    const titleH = 36;
    const subtitleH = 22;
    const headerBottom = padTop + titleH + 8 + subtitleH + 16;
    const listBottom = h - padBottom - backH - 16;
    const listH = Math.max(120, listBottom - headerBottom);
    const colGap = 12;
    const rowGap = 12;
    const colW = (innerW - colGap) / 2;
    const cardH = 88;
    const cards = [];
    for (let i = 0; i < this.items.length; i += 1) {
      const col = i % 2;
      const row = Math.floor(i / 2);
      cards.push({
        item: this.items[i],
        x: padX + col * (colW + colGap),
        y: row * (cardH + rowGap),
        w: colW,
        h: cardH,
      });
    }
    const rows = Math.ceil(this.items.length / 2);
    this.contentHeight = rows > 0 ? rows * cardH + Math.max(0, rows - 1) * rowGap : 0;
    this.listRect = { x: padX, y: headerBottom, w: innerW, h: listH };
    this.layout = { padX, padTop, innerW, titleY: padTop, subtitleY: padTop + titleH + 8 };
    this.cards = cards;
    this.buttons = {
      back: {
        x: padX,
        y: h - padBottom - backH,
        w: innerW,
        h: backH,
        id: 'back',
      },
    };
    this._clampScroll();
  }

  _maxScroll() {
    return Math.max(0, this.contentHeight - this.listRect.h);
  }

  _clampScroll() {
    const maxScroll = this._maxScroll();
    if (this.scroll < 0) {
      this.scroll = 0;
    }
    if (this.scroll > maxScroll) {
      this.scroll = maxScroll;
    }
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
    ctx.fillText('成就', L.padX, L.titleY);
    ctx.fillStyle = COLORS.subtitle;
    ctx.font = `14px ${FONT_STACK}`;
    const unlocked = this.items.filter((it) => it.unlocked).length;
    ctx.fillText(`已解锁 ${unlocked} / ${this.items.length}`, L.padX, L.subtitleY);

    this._drawList();
    this._drawButton(this.buttons.back, '返回');
  }

  _drawList() {
    const rect = this.listRect;
    ctx.save();
    ctx.beginPath();
    ctx.rect(rect.x, rect.y, rect.w, rect.h);
    ctx.clip();
    ctx.translate(0, rect.y - this.scroll);
    for (const card of this.cards) {
      if (card.y + card.h < this.scroll - 8) {
        continue;
      }
      if (card.y > this.scroll + rect.h + 8) {
        break;
      }
      this._drawCard(card);
    }
    ctx.restore();
  }

  _drawCard(card) {
    const on = Boolean(card.item.unlocked);
    ctx.fillStyle = on ? COLORS.cardOn : COLORS.cardOff;
    roundRectPath(ctx, card.x, card.y, card.w, card.h, 10);
    ctx.fill();
    if (on) {
      ctx.strokeStyle = COLORS.buttonBorder;
      ctx.lineWidth = 1;
      roundRectPath(ctx, card.x, card.y, card.w, card.h, 10);
      ctx.stroke();
    }
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = on ? COLORS.nameOn : COLORS.nameOff;
    ctx.font = `bold 20px ${FONT_STACK}`;
    ctx.fillText(card.item.title, card.x + card.w / 2, card.y + card.h / 2 - 12);
    ctx.fillStyle = on ? COLORS.hintOn : COLORS.hintOff;
    ctx.font = `13px ${FONT_STACK}`;
    ctx.fillText(card.item.desc, card.x + card.w / 2, card.y + card.h / 2 + 16);
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
      dragging: hitRect(this.listRect, point.x, point.y),
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
    const dy = point.y - this.touch.y;
    if (Math.abs(point.x - this.touch.startX) + Math.abs(point.y - this.touch.startY) > 8) {
      this.touch.moved = true;
    }
    if (this.touch.dragging) {
      this.scroll -= dy;
      this._clampScroll();
      this.render();
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
    if (this.buttons.back && hitRect(this.buttons.back, point.x, point.y)) {
      if (typeof this.onBack === 'function') {
        this.onBack();
      }
    }
  }
}
