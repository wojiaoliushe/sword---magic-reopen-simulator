import { ctx, PIXEL_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT, SAFE_AREA } from '../render';
import { TALENT_PICK_MAX, pickBlockedBy } from '../talent/index';

const FONT_STACK = 'PingFang SC, Hiragino Sans GB, Heiti SC, sans-serif';
const GRADE_NAME = ['白', '蓝', '紫', '橙'];
const GRADE_COLOR = ['#c4b49a', '#7aa6c9', '#b392d4', '#d4925a'];
const COLORS = {
  bg: '#171412',
  title: '#eddcb8',
  subtitle: '#9e8f7a',
  card: '#241f1c',
  cardOn: '#322b26',
  cardDim: '#1c1917',
  desc: '#c4b49a',
  descDim: '#6a5e54',
  button: '#3a322c',
  buttonText: '#f2e6c7',
  buttonBorder: '#5a4e44',
  selectBorder: '#eddcb8',
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

function wrapText(context, text, maxWidth, maxLines) {
  const source = String(text || '');
  const limit = maxLines > 0 ? maxLines : 99;
  if (!source) {
    return [''];
  }
  const lines = [];
  let current = '';
  for (const ch of source) {
    const test = current + ch;
    if (current && context.measureText(test).width > maxWidth) {
      lines.push(current);
      current = ch;
      if (lines.length >= limit) {
        break;
      }
    } else {
      current = test;
    }
  }
  if (lines.length < limit && current) {
    lines.push(current);
  } else if (lines.length >= limit && current) {
    let last = lines[lines.length - 1];
    while (last.length && context.measureText(`${last}…`).width > maxWidth) {
      last = last.slice(0, -1);
    }
    lines[lines.length - 1] = `${last}…`;
  }
  return lines.length > 0 ? lines : [''];
}

export default class TalentView {
  constructor({ drawn, selected, onBack, onNext }) {
    this.drawn = Array.isArray(drawn) ? drawn : [];
    this.selected = Array.isArray(selected) ? selected.slice() : [];
    this.onBack = onBack;
    this.onNext = onNext;
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

  _layout() {
    const w = this.width;
    const h = this.height;
    const safe = this.safeArea;
    const padX = 24;
    const padTop = Math.max(20, (safe.top || 0) + 12);
    const padBottom = Math.max(20, h - (safe.bottom || h) + 16);
    const innerW = w - padX * 2;
    const backH = 40;
    const nextH = 52;
    const titleH = 32;
    const headerBottom = padTop + backH + 12 + titleH + 8;
    const listBottom = h - padBottom - nextH - 16;
    const listH = Math.max(120, listBottom - headerBottom);
    const colGap = 12;
    const rowGap = 12;
    const colW = (innerW - colGap) / 2;
    const cardH = 126;
    const cards = [];
    for (let i = 0; i < this.drawn.length; i += 1) {
      const col = i % 2;
      const row = Math.floor(i / 2);
      cards.push({
        talent: this.drawn[i],
        x: padX + col * (colW + colGap),
        y: row * (cardH + rowGap),
        w: colW,
        h: cardH,
      });
    }
    const rows = Math.ceil(this.drawn.length / 2);
    this.contentHeight = rows > 0 ? rows * cardH + Math.max(0, rows - 1) * rowGap : 0;
    this.listRect = { x: padX, y: headerBottom, w: innerW, h: listH };
    this.layout = {
      padX,
      padTop,
      innerW,
      titleY: padTop + backH + 12,
    };
    this.cards = cards;
    this.buttons = {
      back: { x: padX, y: padTop, w: 88, h: backH, id: 'back' },
      next: {
        x: padX,
        y: h - padBottom - nextH,
        w: innerW,
        h: nextH,
        id: 'next',
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

  _isSelected(id) {
    return this.selected.indexOf(id) >= 0;
  }

  _toggle(id) {
    const idx = this.selected.indexOf(id);
    if (idx >= 0) {
      this.selected.splice(idx, 1);
      this.render();
      return;
    }
    if (this.selected.length >= TALENT_PICK_MAX) {
      return;
    }
    if (pickBlockedBy(id, this.selected)) {
      return;
    }
    this.selected.push(id);
    this.render();
  }

  render() {
    this._layout();
    ctx.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, this.width, this.height);

    this._drawButton(this.buttons.back, '返回');

    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = COLORS.title;
    ctx.font = `bold 22px ${FONT_STACK}`;
    ctx.fillText('选择天赋', this.layout.padX, this.layout.titleY);

    ctx.textAlign = 'right';
    ctx.fillStyle = COLORS.subtitle;
    ctx.font = `15px ${FONT_STACK}`;
    ctx.fillText(
      `已选 ${this.selected.length}/${TALENT_PICK_MAX}`,
      this.layout.padX + this.layout.innerW,
      this.layout.titleY + 4,
    );

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
        continue;
      }
      this._drawCard(card);
    }
    ctx.restore();

    this._drawButton(this.buttons.next, '下一步');
  }

  _drawCard(card) {
    const talent = card.talent;
    const on = this._isSelected(talent.id);
    const blocked = !on && (
      this.selected.length >= TALENT_PICK_MAX || Boolean(pickBlockedBy(talent.id, this.selected))
    );
    ctx.fillStyle = on ? COLORS.cardOn : blocked ? COLORS.cardDim : COLORS.card;
    roundRectPath(ctx, card.x, card.y, card.w, card.h, 10);
    ctx.fill();
    ctx.strokeStyle = on ? COLORS.selectBorder : COLORS.buttonBorder;
    ctx.lineWidth = on ? 2 : 1;
    roundRectPath(ctx, card.x, card.y, card.w, card.h, 10);
    ctx.stroke();

    const pad = 10;
    const grade = talent.grade | 0;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = GRADE_COLOR[grade] || GRADE_COLOR[0];
    ctx.font = `12px ${FONT_STACK}`;
    ctx.fillText(GRADE_NAME[grade] || '', card.x + pad, card.y + 8);

    ctx.fillStyle = blocked ? COLORS.descDim : COLORS.title;
    ctx.font = `bold 16px ${FONT_STACK}`;
    ctx.fillText(talent.title, card.x + pad, card.y + 26);

    ctx.fillStyle = blocked ? COLORS.descDim : COLORS.desc;
    ctx.font = `12px ${FONT_STACK}`;
    const lines = wrapText(ctx, talent.desc, card.w - pad * 2, 4);
    let y = card.y + 50;
    for (let i = 0; i < lines.length; i += 1) {
      ctx.fillText(lines[i], card.x + pad, y);
      y += 16;
    }
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
    this._handleTap(point.x, point.y);
  }

  _handleTap(x, y) {
    if (hitRect(this.buttons.back, x, y)) {
      if (typeof this.onBack === 'function') {
        this.onBack();
      }
      return;
    }
    if (hitRect(this.buttons.next, x, y)) {
      if (typeof this.onNext === 'function') {
        this.onNext(this.selected.slice());
      }
      return;
    }
    if (!hitRect(this.listRect, x, y)) {
      return;
    }
    const localY = y - this.listRect.y + this.scroll;
    for (const card of this.cards) {
      if (hitRect({ x: card.x, y: card.y, w: card.w, h: card.h }, x, localY)) {
        this._toggle(card.talent.id);
        return;
      }
    }
  }
}
