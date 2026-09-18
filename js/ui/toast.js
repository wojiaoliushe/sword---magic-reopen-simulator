const SHOW_MS = 2000;
const GAP_MS = 240;

const queue = [];
let showing = false;
let timer = 0;

function pump() {
  if (showing || !queue.length) {
    return;
  }
  showing = true;
  const title = queue.shift();
  const text = `解锁成就:${title}`;
  try {
    if (typeof wx !== 'undefined' && typeof wx.showToast === 'function') {
      wx.showToast({
        title: text,
        icon: 'none',
        duration: SHOW_MS,
      });
    }
  } catch (err) {
    // ignore missing toast API
  }
  if (timer) {
    clearTimeout(timer);
  }
  timer = setTimeout(() => {
    timer = 0;
    showing = false;
    pump();
  }, SHOW_MS + GAP_MS);
}

/** Queue a native toast: 解锁成就:XXXX */
export function showUnlockToast(title) {
  const name = String(title || '').trim();
  if (!name) {
    return;
  }
  queue.push(name);
  pump();
}
