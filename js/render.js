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
