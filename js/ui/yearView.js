import { ctx, PIXEL_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT, SAFE_AREA } from '../render';

const AUTO_INTERVAL_MS = 500;
const FONT_STACK = 'PingFang SC, Hiragino Sans GB, Heiti SC, sans-serif';
const COLORS = {
  bg: '#171412',
  title: '#eddcb8',
  subtitle: '#9e8f7a',
  age: '#f2e6c7',
  stats: '#d9ccb3',
  logPanel: '#241f1c',
  logText: '#e6d6bd',
  hint: '#8c8070',
  plus: '#8fba8a',
  minus: '#c98989',
  button: '#3a322c',
  buttonText: '#f2e6c7',
  buttonDisabled: '#2a2420',
  buttonDisabledText: '#6a5e54',
  end: '#c4b49a',
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

function wrapText(context, text, maxWidth) {
  const source = String(text || '');
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
    } else {
      current = test;
    }
  }
  if (current) {
    lines.push(current);
  }
  return lines.length > 0 ? lines : [''];
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

export default class YearView {
  constructor(engine, errorText = '', options = {}) {
    this.engine = engine;
    this.errorText = errorText;
    this.startAttrs = options.attrs || null;
    this.onRestart = options.onRestart || null;
    this.onSettle = options.onSettle || null;
    this.active = false;
    this.journal = [];
    this.autoplaying = false;
    this.autoplayToken = 0;
    this.autoTimer = 0;
    this.scroll = 0;
    this.stickBottom = true;
    this.logItems = [];
    this.logContentHeight = 0;
    this.buttons = {};
    this.logRect = { x: 0, y: 0, w: 0, h: 0 };
    this.touch = null;
    this.width = SCREEN_WIDTH;
    this.height = SCREEN_HEIGHT;
    this.pixelRatio = PIXEL_RATIO;
    this.safeArea = SAFE_AREA;
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
    if (this.errorText) {
      this._layout();
      this.render();
      return;
    }
    this._beginLife();
  }

  stop() {
    this.active = false;
    this._stopAutoplay(true);
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
    this._rebuildLogLayout();
    this.render();
  }

  _layout() {
    const w = this.width;
    const h = this.height;
    const safe = this.safeArea;
    const padX = 28;
    const padTop = Math.max(24, (safe.top || 0) + 10);
    const padBottom = Math.max(20, h - (safe.bottom || h) + 14);
    const titleH = 32;
    const subtitleH = 20;
    const statsH = 72;
    const hintH = 40;
    const buttonH = 44;
    const logTop = padTop + titleH + 8 + subtitleH + 12 + statsH + 12;
    const logBottom = h - padBottom - buttonH - 12 - hintH - 8;
    const logH = Math.max(140, logBottom - logTop);
    const innerW = w - padX * 2;
    const gap = 12;
    const btnW = (innerW - gap * 2) / 3;
    const btnY = logTop + logH + 8 + hintH + 12;

    this.layout = {
      padX,
      padTop,
      padBottom,
      titleY: padTop,
      subtitleY: padTop + titleH + 8,
      statsY: padTop + titleH + 8 + subtitleH + 12,
      statsH,
      hintY: logTop + logH + 8,
      hintH,
      innerW,
    };
    this.logRect = {
      x: padX,
      y: logTop,
      w: innerW,
      h: logH,
    };
    const restart = { x: padX + (btnW + gap) * 2, y: btnY, w: btnW, h: buttonH, id: 'restart' };
    if (this.engine && this.engine.state && this.engine.state.dead) {
      this.buttons = {
        settle: { x: padX, y: btnY, w: btnW * 2 + gap, h: buttonH, id: 'settle' },
        restart,
      };
    } else {
      this.buttons = {
        next: { x: padX, y: btnY, w: btnW, h: buttonH, id: 'next' },
        auto: { x: padX + btnW + gap, y: btnY, w: btnW, h: buttonH, id: 'auto' },
        restart,
      };
    }
  }

  _beginLife() {
    this._stopAutoplay(true);
    this.journal = [];
    this.engine.restart(this.startAttrs);
    this._appendYearToJournal();
    this.stickBottom = true;
    this._refresh();
  }

  _onNextYear() {
    if (this.engine.state.dead) {
      return;
    }
    this.engine.nextYear();
    this._appendYearToJournal();
    this._refresh();
  }

  _appendYearToJournal() {
    this.journal.push({
      age: this.engine.state.age,
      lines: this.engine.state.yearLog.map((line) => ({
        event_id: line.event_id,
        desc: line.desc,
        effects: { ...line.effects },
      })),
    });
  }

  _refresh() {
    this._layout();
    this._rebuildLogLayout();
    if (this.stickBottom) {
      this._scrollToBottom();
    }
    this.render();
  }

  _hintText() {
    if (this.errorText) {
      return this.errorText;
    }
    if (this.engine.state.dead) {
      return '人生已结束。点「结算」查看本世属性最高值。';
    }
    if (this.autoplaying) {
      return '自动播放中。再点一次「停止播放」可停下。';
    }
    return '点「下一年」推进一岁，或用「自动播放」连年结算。';
  }

  _nextDisabled() {
    return this.engine.state.dead || this.autoplaying;
  }

  _autoDisabled() {
    return this.engine.state.dead;
  }

  _startAutoplay() {
    if (this.engine.state.dead) {
      this._stopAutoplay();
      return;
    }
    this.autoplaying = true;
    this.autoplayToken += 1;
    const token = this.autoplayToken;
    this._refresh();
    this._runAutoplay(token);
  }

  _stopAutoplay(skipRender = false) {
    this.autoplaying = false;
    this.autoplayToken += 1;
    if (this.autoTimer) {
      clearTimeout(this.autoTimer);
      this.autoTimer = 0;
    }
    if (!skipRender) {
      this._layout();
      this._rebuildLogLayout();
      this.render();
    }
  }

  _runAutoplay(token) {
    if (!this.autoplaying || this.engine.state.dead || token !== this.autoplayToken) {
      if (token === this.autoplayToken) {
        this._stopAutoplay();
      }
      return;
    }
    this._onNextYear();
    if (!this.autoplaying || this.engine.state.dead || token !== this.autoplayToken) {
      if (token === this.autoplayToken) {
        this._stopAutoplay();
      }
      return;
    }
    this.autoTimer = setTimeout(() => {
      this._runAutoplay(token);
    }, AUTO_INTERVAL_MS);
  }

  _mode() {
    return this.engine && this.engine.mode ? this.engine.mode : null;
  }

  _clockLabel() {
    const mode = this._mode();
    return mode && mode.clock ? mode.clock.label : '岁';
  }

  _titleText() {
    const mode = this._mode();
    return mode && mode.title ? mode.title : '异世岁记';
  }

  _subtitleText() {
    const mode = this._mode();
    return mode && mode.subtitle ? mode.subtitle : '';
  }

  _attrDefs() {
    const mode = this._mode();
    return mode && Array.isArray(mode.attrs) ? mode.attrs : [];
  }

  _eventSegments(line) {
    const segs = [{ text: String(line.desc || ''), color: COLORS.logText }];
    const effects = line.effects || {};
    for (const def of this._attrDefs()) {
      const v = Number(effects[def.key] || 0);
      if (!v) {
        continue;
      }
      const sign = v > 0 ? '+' : '';
      segs.push({
        text: `  ${def.label}${sign}${v}`,
        color: v > 0 ? COLORS.plus : COLORS.minus,
      });
    }
    return segs;
  }

  _rebuildLogLayout() {
    ctx.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
    ctx.font = `16px ${FONT_STACK}`;
    const pad = 16;
    const maxWidth = Math.max(40, this.logRect.w - pad * 2);
    const lineHeight = 24;
    const items = [];
    let y = 12;
    for (const year of this.journal) {
      items.push({
        type: 'header',
        text: `${year.age} ${this._clockLabel()}`,
        y,
        h: lineHeight,
      });
      y += lineHeight;
      if (!year.lines || year.lines.length === 0) {
        items.push({
          type: 'empty',
          text: '（无事发生）',
          y,
          h: lineHeight,
        });
        y += lineHeight;
      } else {
        for (const line of year.lines) {
          const rows = this._wrapSegments(this._eventSegments(line), maxWidth);
          const h = rows.length * lineHeight;
          items.push({
            type: 'event',
            rows,
            y,
            h,
          });
          y += h;
        }
      }
      y += 10;
    }
    if (this.engine && this.engine.state.dead) {
      items.push({
        type: 'end',
        text: '—— 人生结束 ——',
        y,
        h: lineHeight,
      });
      y += lineHeight;
    }
    this.logItems = items;
    this.logContentHeight = y + 8;
    this._clampScroll();
  }

  _wrapSegments(segments, maxWidth) {
    const rows = [];
    let row = [];
    let x = 0;
    ctx.font = `16px ${FONT_STACK}`;
    for (const seg of segments) {
      let buf = '';
      for (const ch of String(seg.text)) {
        const test = buf + ch;
        const width = ctx.measureText(test).width;
        if (x + width > maxWidth && (x > 0 || buf.length > 0)) {
          if (buf) {
            row.push({ text: buf, color: seg.color });
            buf = '';
          }
          if (row.length > 0) {
            rows.push(row);
          }
          row = [];
          x = 0;
          buf = ch;
        } else {
          buf = test;
        }
      }
      if (buf) {
        row.push({ text: buf, color: seg.color });
        x += ctx.measureText(buf).width;
      }
    }
    if (row.length > 0) {
      rows.push(row);
    }
    return rows.length > 0 ? rows : [[{ text: '', color: COLORS.logText }]];
  }

  _maxScroll() {
    return Math.max(0, this.logContentHeight - this.logRect.h);
  }

  _clampScroll() {
    const maxScroll = this._maxScroll();
    if (this.scroll < 0) {
      this.scroll = 0;
    }
    if (this.scroll > maxScroll) {
      this.scroll = maxScroll;
    }
    if (maxScroll - this.scroll < 2) {
      this.stickBottom = true;
    }
  }

  _scrollToBottom() {
    this.scroll = this._maxScroll();
    this.stickBottom = true;
  }

  render() {
    this._layout();
    ctx.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, this.width, this.height);

    if (this.errorText) {
      this._drawError();
      return;
    }

    const L = this.layout;
    this._drawText(this._titleText(), L.padX, L.titleY, `bold 28px ${FONT_STACK}`, COLORS.title);
    this._drawText(this._subtitleText(), L.padX, L.subtitleY, `14px ${FONT_STACK}`, COLORS.subtitle);
    this._drawStats();
    this._drawLog();
    this._drawHint();
    if (this.buttons.settle) {
      this._drawButton(this.buttons.settle, '结算', false);
    } else {
      this._drawButton(this.buttons.next, '下一年', this._nextDisabled());
      this._drawButton(
        this.buttons.auto,
        this.autoplaying ? '停止播放' : '自动播放',
        this._autoDisabled(),
      );
    }
    this._drawButton(this.buttons.restart, '重开', false);
  }

  _drawError() {
    const L = this.layout || { padX: 28, titleY: 80 };
    this._drawText(this._titleText(), L.padX, L.titleY || 80, `bold 28px ${FONT_STACK}`, COLORS.title);
    ctx.font = `16px ${FONT_STACK}`;
    const lines = wrapText(ctx, this.errorText, this.width - 56);
    let y = (L.titleY || 80) + 56;
    for (const line of lines) {
      this._drawText(line, L.padX, y, `16px ${FONT_STACK}`, COLORS.minus);
      y += 24;
    }
  }

  _drawStats() {
    if (!this.engine) {
      return;
    }
    const s = this.engine.state;
    const L = this.layout;
    const items = [
      { text: `${s.age} ${this._clockLabel()}`, color: COLORS.age, font: `bold 20px ${FONT_STACK}` },
    ];
    for (const def of this._attrDefs()) {
      items.push({
        text: `${def.label} ${s.attrs[def.key] | 0}`,
        color: COLORS.stats,
        font: `16px ${FONT_STACK}`,
      });
    }
    let x = L.padX;
    let y = L.statsY;
    const maxX = L.padX + L.innerW;
    for (const item of items) {
      ctx.font = item.font;
      const width = ctx.measureText(item.text).width + 16;
      if (x + width > maxX && x !== L.padX) {
        x = L.padX;
        y += 24;
      }
      this._drawText(item.text, x, y, item.font, item.color);
      x += width;
    }
  }

  _drawLog() {
    const rect = this.logRect;
    ctx.save();
    ctx.fillStyle = COLORS.logPanel;
    roundRectPath(ctx, rect.x, rect.y, rect.w, rect.h, 8);
    ctx.fill();
    ctx.clip();

    const pad = 16;
    const lineHeight = 24;
    ctx.translate(rect.x + pad, rect.y - this.scroll);
    for (const item of this.logItems) {
      if (item.y + item.h < this.scroll - 8) {
        continue;
      }
      if (item.y > this.scroll + rect.h + 8) {
        break;
      }
      if (item.type === 'header') {
        this._drawText(item.text, 0, item.y, `bold 16px ${FONT_STACK}`, COLORS.age);
      } else if (item.type === 'empty') {
        this._drawText(item.text, 0, item.y, `16px ${FONT_STACK}`, COLORS.subtitle);
      } else if (item.type === 'end') {
        this._drawText(item.text, 0, item.y, `italic 16px ${FONT_STACK}`, COLORS.end);
      } else if (item.type === 'event') {
        let rowY = item.y;
        for (const row of item.rows) {
          let x = 0;
          ctx.font = `16px ${FONT_STACK}`;
          for (const seg of row) {
            ctx.fillStyle = seg.color;
            ctx.textAlign = 'left';
            ctx.textBaseline = 'top';
            ctx.fillText(seg.text, x, rowY);
            x += ctx.measureText(seg.text).width;
          }
          rowY += lineHeight;
        }
      }
    }
    ctx.restore();
  }

  _drawHint() {
    const L = this.layout;
    ctx.font = `13px ${FONT_STACK}`;
    const lines = wrapText(ctx, this._hintText(), L.innerW);
    let y = L.hintY;
    for (const line of lines.slice(0, 3)) {
      this._drawText(line, L.padX, y, `13px ${FONT_STACK}`, COLORS.hint);
      y += 16;
    }
  }

  _drawButton(btn, label, disabled) {
    ctx.save();
    ctx.fillStyle = disabled ? COLORS.buttonDisabled : COLORS.button;
    roundRectPath(ctx, btn.x, btn.y, btn.w, btn.h, 8);
    ctx.fill();
    ctx.font = `16px ${FONT_STACK}`;
    ctx.fillStyle = disabled ? COLORS.buttonDisabledText : COLORS.buttonText;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, btn.x + btn.w / 2, btn.y + btn.h / 2);
    ctx.restore();
  }

  _drawText(text, x, y, font, color) {
    ctx.font = font;
    ctx.fillStyle = color;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(text, x, y);
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
      dragging: hitRect(this.logRect, point.x, point.y),
      moved: false,
    };
  }

  _onTouchMove(event) {
    if (!this.active) {
      return;
    }
    if (!this.touch) {
      return;
    }
    const point = touchPoint(event.touches && event.touches[0]);
    if (!point) {
      return;
    }
    const dy = point.y - this.touch.y;
    const dx = point.x - this.touch.startX;
    const distY = point.y - this.touch.startY;
    if (Math.abs(dx) + Math.abs(distY) > 6) {
      this.touch.moved = true;
    }
    if (this.touch.dragging) {
      this.scroll -= dy;
      this.stickBottom = false;
      this._clampScroll();
      if (this.scroll >= this._maxScroll() - 1) {
        this.stickBottom = true;
      }
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
    if (!touchInfo || touchInfo.moved || this.errorText) {
      return;
    }
    const point = touchPoint(event.changedTouches && event.changedTouches[0]) || {
      x: touchInfo.x,
      y: touchInfo.y,
    };
    this._handleTap(point.x, point.y);
  }

  _handleTap(x, y) {
    if (this.buttons.settle && hitRect(this.buttons.settle, x, y)) {
      if (typeof this.onSettle === 'function') {
        this.onSettle();
      }
      return;
    }
    if (this.buttons.next && hitRect(this.buttons.next, x, y)) {
      if (!this._nextDisabled()) {
        this._onNextYear();
      }
      return;
    }
    if (this.buttons.auto && hitRect(this.buttons.auto, x, y)) {
      if (this._autoDisabled()) {
        return;
      }
      if (this.autoplaying) {
        this._stopAutoplay();
      } else {
        this._startAutoplay();
      }
      return;
    }
    if (this.buttons.restart && hitRect(this.buttons.restart, x, y)) {
      if (typeof this.onRestart === 'function') {
        this.onRestart();
      }
    }
  }
}
