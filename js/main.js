import './render';
import { ctx } from './render';
import LifeEngine from './life/lifeEngine';
import ModeDef, { resolveModeEntry } from './life/modeDef';
import StartView from './ui/startView';
import TalentView from './ui/talentView';
import PrepareView from './ui/prepareView';
import YearView from './ui/yearView';
import SettleView from './ui/settleView';
import AchieveView from './ui/achieveView';
import { loadCatalog } from './achieve/index';
import { BASE_POINTS, extraPoints, loadTalents, drawTalents, resolvePicks } from './talent/index';

function parseJson(data) {
  const text = typeof data === 'string' ? data : data.toString();
  return JSON.parse(text);
}

function readJson(paths, failMessage) {
  const fs = wx.getFileSystemManager();
  return new Promise((resolve, reject) => {
    const tryRead = (index) => {
      if (index >= paths.length) {
        reject(new Error(failMessage));
        return;
      }
      fs.readFile({
        filePath: paths[index],
        encoding: 'utf8',
        success(res) {
          try {
            resolve(parseJson(res.data));
          } catch (err) {
            reject(new Error(`${failMessage}（JSON 解析失败）`));
          }
        },
        fail() {
          tryRead(index + 1);
        },
      });
    };
    tryRead(0);
  });
}

function packPaths(base, filename) {
  const rel = `${base}/${filename}`;
  return [rel, `/${rel}`];
}

function asEventList(raw) {
  if (Array.isArray(raw)) {
    return raw.slice();
  }
  if (raw && Array.isArray(raw.events)) {
    return raw.events.slice();
  }
  return [];
}

function loadDefaultPack() {
  return readJson(['data/modes.json', '/data/modes.json'], '无法读取 data/modes.json')
    .then((index) => {
      const resolved = resolveModeEntry(index);
      if (resolved.error) {
        throw new Error(resolved.error);
      }
      const base = resolved.entry.path;
      return Promise.all([
        readJson(packPaths(base, 'mode.json'), `无法读取 ${base}/mode.json`),
        readJson(packPaths(base, 'events.json'), `无法读取 ${base}/events.json`),
        readJson(packPaths(base, 'achievements.json'), `无法读取 ${base}/achievements.json`),
        readJson(packPaths(base, 'talents.json'), `无法读取 ${base}/talents.json`).catch(() => ({ talents: [] })),
        readJson(packPaths(base, 'talent_events.json'), `无法读取 ${base}/talent_events.json`).catch(() => ({ events: [] })),
      ]).then(([modeRaw, events, achievements, talents, talentEvents]) => {
        const parsed = ModeDef.parse(modeRaw);
        if (parsed.error) {
          throw new Error(parsed.error);
        }
        return {
          mode: parsed.mode,
          events: asEventList(events).concat(asEventList(talentEvents)),
          achievements,
          talents,
        };
      });
    });
}

function drawBootMessage(text) {
  const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();
  const pr = info.pixelRatio || 1;
  ctx.setTransform(pr, 0, 0, pr, 0, 0);
  ctx.fillStyle = '#171412';
  ctx.fillRect(0, 0, info.screenWidth, info.screenHeight);
  ctx.fillStyle = '#eddcb8';
  ctx.font = '20px PingFang SC, sans-serif';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.fillText(text, 28, Math.max(80, (info.safeArea && info.safeArea.top) || 0) + 24);
}

export default class Main {
  constructor() {
    this.engine = null;
    this.startView = null;
    this.talentView = null;
    this.prepView = null;
    this.view = null;
    this.settleView = null;
    this.achieveView = null;
    this.talentDrawn = [];
    this.talentSelected = [];
    this.talentResolved = [];
    drawBootMessage('正在加载…');
    loadDefaultPack()
      .then(({ mode, events, achievements, talents }) => {
        loadCatalog(achievements);
        loadTalents(talents);
        this.engine = new LifeEngine(mode);
        const err = this.engine.loadEvents(events);
        if (err) {
          this._enterGame(err);
          return;
        }
        this._showStart();
      })
      .catch((err) => {
        const message = err && err.message ? err.message : '模式包读取失败';
        this._enterGame(message);
      });
  }

  _stopViews() {
    if (this.startView) {
      this.startView.stop();
      this.startView = null;
    }
    if (this.talentView) {
      this.talentView.stop();
      this.talentView = null;
    }
    if (this.prepView) {
      this.prepView.stop();
      this.prepView = null;
    }
    if (this.view) {
      this.view.stop();
      this.view = null;
    }
    if (this.settleView) {
      this.settleView.stop();
      this.settleView = null;
    }
    if (this.achieveView) {
      this.achieveView.stop();
      this.achieveView = null;
    }
  }

  _showStart() {
    const title = this.engine && this.engine.mode ? this.engine.mode.title : '异世岁记';
    const subtitle = this.engine && this.engine.mode ? this.engine.mode.subtitle : '再活一遍，从摇篮到墓碑';
    this._stopViews();
    this.startView = new StartView({
      title,
      subtitle,
      onStart: () => this._showTalent(true),
      onAchieve: () => this._showAchieve(),
    });
    this.startView.start();
  }

  _showTalent(fresh) {
    if (fresh) {
      this.talentDrawn = drawTalents();
      this.talentSelected = [];
      this.talentResolved = [];
    }
    this._stopViews();
    this.talentView = new TalentView({
      drawn: this.talentDrawn,
      selected: this.talentSelected,
      onBack: () => this._showStart(),
      onNext: (ids) => {
        this.talentSelected = Array.isArray(ids) ? ids : [];
        this.talentResolved = resolvePicks(this.talentSelected);
        this._showPrep();
      },
    });
    this.talentView.start();
  }

  _showPrep() {
    const all = this.engine && this.engine.mode ? this.engine.mode.attrs : [];
    const attrs = all.filter((def) => def && def.alloc !== false);
    const total = Math.max(0, BASE_POINTS + extraPoints(this.talentResolved));
    this._stopViews();
    this.prepView = new PrepareView({
      attrs,
      totalPoints: total,
      onBack: () => this._showTalent(false),
      onConfirm: (alloc) => this._enterGame('', alloc, this.talentResolved),
    });
    this.prepView.start();
  }

  _enterGame(errorText = '', attrs = null, talents = null) {
    this._stopViews();
    this.view = new YearView(this.engine, errorText, {
      attrs,
      talents: Array.isArray(talents) ? talents : [],
      onRestart: () => this._showStart(),
      onSettle: () => this._showSettle(),
    });
    this.view.start();
  }

  _showSettle() {
    const mode = this.engine && this.engine.mode ? this.engine.mode : null;
    const attrDefs = mode && Array.isArray(mode.attrs) ? mode.attrs : [];
    const peaks = {};
    const recorded = this.engine && this.engine.state ? this.engine.state.attrPeak : null;
    const nowAttrs = this.engine && this.engine.state ? this.engine.state.attrs : null;
    for (const def of attrDefs) {
      if (def.alloc === false) {
        continue;
      }
      const fromPeak = recorded && Object.prototype.hasOwnProperty.call(recorded, def.key)
        ? recorded[def.key]
        : 0;
      const fromNow = nowAttrs && Object.prototype.hasOwnProperty.call(nowAttrs, def.key)
        ? nowAttrs[def.key]
        : 0;
      peaks[def.key] = Math.max(fromPeak | 0, fromNow | 0);
    }
    const alignment = {
      order: nowAttrs && nowAttrs.order !== undefined ? nowAttrs.order | 0 : 0,
      moral: nowAttrs && nowAttrs.moral !== undefined ? nowAttrs.moral | 0 : 0,
    };
    this._stopViews();
    this.settleView = new SettleView({
      attrs: attrDefs.filter((def) => def && def.alloc !== false),
      peaks,
      alignment,
      onRestart: () => this._showStart(),
    });
    this.settleView.start();
  }

  _showAchieve() {
    this._stopViews();
    this.achieveView = new AchieveView({
      onBack: () => this._showStart(),
    });
    this.achieveView.start();
  }
}
