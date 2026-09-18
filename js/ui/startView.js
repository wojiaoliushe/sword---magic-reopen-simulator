import { ctx, PIXEL_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT, SAFE_AREA, contentTop, bindFrame, bindViewFrame } from '../render';

const FONT_STACK = 'PingFang SC, Hiragino Sans GB, Heiti SC, sans-serif';
const COLORS = {
  bg: '#171412',
  title: '#eddcb8',
  subtitle: '#9e8f7a',
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

export default class StartView {
  constructor({ title, subtitle, onStart, onAchieve }) {
    this.title = title || '异世岁记';
    this.subtitle = subtitle || '再活一遍，从摇篮到墓碑';
    this.onStart = onStart;
    this.onAchieve = onAchieve;
    this.active = false;
    this.width = SCREEN_WIDTH;
    this.height = SCREEN_HEIGHT;
    this.pixelRatio = PIXEL_RATIO;
    this.safeArea = SAFE_AREA;
    this.buttons = {};
    this.touch = null;
    this.icon = null;
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
    this._loadIcon();
    this._layout();
    bindViewFrame(this);
    this.render();
  }

  _loadIcon() {
    if (this.icon || typeof wx.createImage !== 'function') {
      return;
    }
    const img = wx.createImage();
    img.onload = () => {
      this.icon = img;
      if (this.active) {
        this.render();
      }
    };
    img.onerror = () => {};
    img.src = 'images/avatar.png';
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
    const padX = 40;
    const padTop = contentTop();
    const padBottom = Math.max(28, h - (safe.bottom || h) + 20);
    const innerW = Math.min(320, w - padX * 2);
    const btnX = (w - innerW) / 2;
    const btnH = 52;
    const gap = 16;
    const stackH = btnH * 2 + gap;
    const btnY = Math.min(h - padBottom - stackH, h * 0.58);

    const iconSize = 96;
    const titleY = padTop + iconSize + 28;
    this.layout = {
      padTop,
      innerW,
      iconSize,
      iconY: padTop,
      titleY,
      subtitleY: titleY + 48,
    };
    this.buttons = {
      start: { x: btnX, y: btnY, w: innerW, h: btnH, id: 'start' },
      achieve: { x: btnX, y: btnY + btnH + gap, w: innerW, h: btnH, id: 'achieve' },
    };
  }

  render() {
    this._layout();
    ctx.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, this.width, this.height);

    const L = this.layout;
    if (this.icon && L.iconSize) {
      const size = L.iconSize;
      const ix = (this.width - size) / 2;
      const iy = L.iconY;
      ctx.save();
      roundRectPath(ctx, ix, iy, size, size, 20);
      ctx.clip();
      ctx.drawImage(this.icon, ix, iy, size, size);
      ctx.restore();
      ctx.save();
      ctx.strokeStyle = COLORS.buttonBorder;
      ctx.lineWidth = 1;
      roundRectPath(ctx, ix, iy, size, size, 20);
      ctx.stroke();
      ctx.restore();
    }

    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillStyle = COLORS.title;
    ctx.font = `bold 34px ${FONT_STACK}`;
    ctx.fillText(this.title, this.width / 2, L.titleY);

    if (this.subtitle) {
      ctx.fillStyle = COLORS.subtitle;
      ctx.font = `15px ${FONT_STACK}`;
      ctx.fillText(this.subtitle, this.width / 2, L.subtitleY);
    }

    this._drawButton(this.buttons.start, '开始游戏');
    this._drawButton(this.buttons.achieve, '成就');
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
    if (hitRect(this.buttons.start, x, y)) {
      if (typeof this.onStart === 'function') {
        this.onStart();
      }
      return;
    }
    if (hitRect(this.buttons.achieve, x, y)) {
      if (typeof this.onAchieve === 'function') {
        this.onAchieve();
      }
    }
  }
}
