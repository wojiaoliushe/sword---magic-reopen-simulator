GameGlobal.canvas = wx.createCanvas();

const windowInfo = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();

export const PIXEL_RATIO = windowInfo.pixelRatio || 1;
export const SCREEN_WIDTH = windowInfo.screenWidth;
export const SCREEN_HEIGHT = windowInfo.screenHeight;
export const SAFE_AREA = windowInfo.safeArea || {
  left: 0,
  top: 0,
  right: SCREEN_WIDTH,
  bottom: SCREEN_HEIGHT,
  width: SCREEN_WIDTH,
  height: SCREEN_HEIGHT,
};

canvas.width = Math.floor(SCREEN_WIDTH * PIXEL_RATIO);
canvas.height = Math.floor(SCREEN_HEIGHT * PIXEL_RATIO);

export const ctx = canvas.getContext('2d');

function raf(fn) {
  if (typeof requestAnimationFrame === 'function') {
    return requestAnimationFrame(fn);
  }
  if (typeof wx !== 'undefined' && typeof wx.requestAnimationFrame === 'function') {
    return wx.requestAnimationFrame(fn);
  }
  return setTimeout(fn, 16);
}

function caf(id) {
  if (id === 0 || id === null || id === undefined) {
    return;
  }
  if (typeof cancelAnimationFrame === 'function') {
    cancelAnimationFrame(id);
    return;
  }
  if (typeof wx !== 'undefined' && typeof wx.cancelAnimationFrame === 'function') {
    wx.cancelAnimationFrame(id);
    return;
  }
  clearTimeout(id);
}

let framePaint = null;
let frameId = 0;

function tick() {
  frameId = 0;
  const paint = framePaint;
  if (typeof paint !== 'function') {
    return;
  }
  paint();
  frameId = raf(tick);
}

function kickFrame() {
  if (frameId || typeof framePaint !== 'function') {
    return;
  }
  frameId = raf(tick);
}

/** 绑定当前页绘制。微信真机需在 rAF 里画才会上屏。 */
export function bindFrame(paint) {
  framePaint = typeof paint === 'function' ? paint : null;
  if (framePaint) {
    kickFrame();
  }
}

export function bindViewFrame(view) {
  bindFrame(() => {
    if (view && view.active && typeof view.render === 'function') {
      view.render();
    }
  });
}

if (typeof wx !== 'undefined') {
  if (typeof wx.onHide === 'function') {
    wx.onHide(() => {
      caf(frameId);
      frameId = 0;
    });
  }
  if (typeof wx.onShow === 'function') {
    wx.onShow(() => {
      kickFrame();
    });
  }
}

function menuButtonRect() {
  try {
    if (typeof wx.getMenuButtonBoundingClientRect !== 'function') {
      return null;
    }
    const rect = wx.getMenuButtonBoundingClientRect();
    if (!rect || !Number.isFinite(rect.bottom) || rect.bottom <= 0) {
      return null;
    }
    return rect;
  } catch (err) {
    return null;
  }
}

/** 内容区顶部，避开微信关闭 / 互动胶囊按钮。 */
export function contentTop(gap = 12) {
  const info = (typeof wx.getWindowInfo === 'function'
    ? wx.getWindowInfo()
    : (typeof wx.getSystemInfoSync === 'function' ? wx.getSystemInfoSync() : {})) || {};
  const statusBar = Number(info.statusBarHeight) || 0;
  const safeTop = (info.safeArea && Number(info.safeArea.top)) || 0;
  const menu = menuButtonRect();
  const menuBottom = menu ? Number(menu.bottom) || 0 : 0;
  const fallback = Math.max(statusBar, safeTop) + 44;
  const base = Math.max(menuBottom, fallback, 64);
  const extra = Number(gap);
  return base + (Number.isFinite(extra) ? extra : 12);
}
