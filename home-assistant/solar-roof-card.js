class SolarRoofCard extends HTMLElement {
  setConfig(config) {
    this.config = {
      title: "Live roof output",
      forecastEntity: "sensor.solar_forecast_now",
      totalEntity: "sensor.solar_power_total",
      sunEntity: "sun.sun",
      panels: [
        { name: "PV1", entity: "sensor.pv1_power", max: 2.0 },
        { name: "PV2", entity: "sensor.pv2_power", max: 6.0 },
        { name: "PV3", entity: "sensor.pv3_power", max: 3.0 },
      ],
      ...config,
    };
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 7;
  }

  value(entityId) {
    const raw = this._hass?.states?.[entityId]?.state;
    const value = Number.parseFloat(raw);
    return Number.isFinite(value) ? value : 0;
  }

  sun() {
    const attrs = this._hass?.states?.[this.config.sunEntity]?.attributes || {};
    const azimuth = Number.parseFloat(attrs.azimuth);
    const elevation = Number.parseFloat(attrs.elevation);
    return {
      azimuth: Number.isFinite(azimuth) ? azimuth : 180,
      elevation: Number.isFinite(elevation) ? elevation : 0,
    };
  }

  render() {
    if (!this.shadowRoot || !this._hass) return;

    const panels = this.config.panels.map((panel) => {
      const kw = this.value(panel.entity);
      const max = Number(panel.max) || 1;
      const ratio = Math.max(0, Math.min(1, kw / max));
      return { ...panel, kw, ratio, pct: Math.round(ratio * 100) };
    });
    const total = this.value(this.config.totalEntity);
    const forecast = this.value(this.config.forecastEntity) / 1000;
    const sun = this.sun();
    const isDaylight = sun.elevation > 0;
    const hasProduction = total > 0.03 || panels.some((panel) => panel.kw > 0.03);
    const hasUsefulForecast = forecast > 0.05;
    const showIrradiance = isDaylight && (hasProduction || hasUsefulForecast);
    const rayOpacity = showIrradiance
      ? Math.max(0.18, Math.min(0.82, Math.max(total / 6, forecast / 6)))
      : 0;
    const sunX = 55 + Math.max(0, Math.min(1, (sun.azimuth - 70) / 220)) * 490;
    const sunY = isDaylight
      ? 92 - Math.max(0, Math.min(1, sun.elevation / 65)) * 54
      : 104;
    const bestPanel = panels.reduce(
      (best, item) => (item.ratio > best.ratio ? item : best),
      panels[0],
    );
    const statusText = showIrradiance
      ? `Most active string: ${bestPanel.name} at ${bestPanel.kw.toFixed(2)} kW`
      : isDaylight
        ? "No measurable solar flow right now"
        : "Sun below horizon";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { overflow: hidden; padding: 16px; }
        .head {
          display: flex;
          align-items: start;
          justify-content: space-between;
          gap: 16px;
          margin-bottom: 12px;
        }
        .title { font-size: 20px; font-weight: 650; line-height: 1.15; }
        .meta { opacity: .72; font-size: 13px; margin-top: 4px; }
        .numbers {
          display: grid;
          grid-template-columns: repeat(2, minmax(92px, auto));
          gap: 8px;
          text-align: right;
          font-size: 13px;
        }
        .number {
          padding: 8px 10px;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          background: color-mix(in srgb, var(--card-background-color), var(--primary-background-color) 35%);
        }
        .number strong {
          display: block;
          font-size: 18px;
          color: var(--primary-text-color);
        }
        svg { width: 100%; height: auto; display: block; }
        .sun {
          filter: drop-shadow(0 0 14px rgba(255, 193, 7, .75));
          animation: sunPulse 2.6s ease-in-out infinite;
        }
        .ray {
          stroke: rgba(255, 198, 41, .62);
          stroke-width: 3;
          stroke-linecap: round;
          stroke-dasharray: 10 16;
          animation: rayMove 2.8s linear infinite;
          transition: opacity .8s ease;
        }
        .ray.off { animation: none; }
        .panel {
          stroke: rgba(255,255,255,.55);
          stroke-width: 2;
          transition: fill .8s ease, filter .8s ease;
        }
        .panel-glow { animation: panelGlow 3.2s ease-in-out infinite; }
        .label { fill: var(--primary-text-color); font: 700 18px sans-serif; }
        .small { fill: var(--secondary-text-color); font: 500 13px sans-serif; }
        .legend {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
          margin-top: 12px;
        }
        .item {
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: 10px;
          background: color-mix(in srgb, var(--card-background-color), var(--primary-background-color) 28%);
        }
        .item b {
          display: flex;
          justify-content: space-between;
          gap: 8px;
          margin-bottom: 8px;
        }
        .bar {
          height: 8px;
          border-radius: 99px;
          background: rgba(120,120,120,.22);
          overflow: hidden;
        }
        .fill {
          height: 100%;
          border-radius: inherit;
          background: linear-gradient(90deg, #f7c948, #ff8f00);
          transition: width .8s ease;
        }
        @media (max-width: 620px) {
          .head { display: block; }
          .numbers {
            grid-template-columns: repeat(2, 1fr);
            text-align: left;
            margin-top: 12px;
          }
          .legend { grid-template-columns: 1fr; }
        }
        @keyframes sunPulse {
          0%, 100% { opacity: .92; }
          50% { opacity: 1; }
        }
        @keyframes rayMove {
          from { stroke-dashoffset: 0; }
          to { stroke-dashoffset: -52; }
        }
        @keyframes panelGlow {
          0%, 100% { filter: drop-shadow(0 0 0 rgba(255, 193, 7, 0)); }
          50% { filter: drop-shadow(0 0 10px rgba(255, 193, 7, .35)); }
        }
      </style>
      <ha-card>
        <div class="head">
          <div>
            <div class="title">${this.config.title}</div>
            <div class="meta">Symbolic roof view from PV string power and sun position</div>
          </div>
          <div class="numbers">
            <div class="number">Actual total<strong>${total.toFixed(2)} kW</strong></div>
            <div class="number">Forecast<strong>${forecast.toFixed(2)} kW</strong></div>
            <div class="number">Azimuth<strong>${sun.azimuth.toFixed(0)} deg</strong></div>
            <div class="number">Elevation<strong>${sun.elevation.toFixed(1)} deg</strong></div>
          </div>
        </div>
        <svg viewBox="0 0 620 360" role="img" aria-label="Symbolic solar roof string view">
          <defs>
            <linearGradient id="sky" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stop-color="rgba(56, 132, 255, .26)" />
              <stop offset="100%" stop-color="rgba(56, 132, 255, .04)" />
            </linearGradient>
            <linearGradient id="roof" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0%" stop-color="rgba(82, 91, 104, .55)" />
              <stop offset="100%" stop-color="rgba(36, 42, 49, .75)" />
            </linearGradient>
          </defs>
          <rect x="0" y="0" width="620" height="360" rx="18" fill="url(#sky)" />
          <path d="M70 242 L310 118 L550 242 L504 272 L310 172 L116 272 Z" fill="url(#roof)" stroke="rgba(255,255,255,.18)" stroke-width="2" />
          <path class="ray ${showIrradiance ? "" : "off"}" style="opacity:${rayOpacity.toFixed(2)}" d="M${sunX.toFixed(1)} ${sunY.toFixed(1)} C420 130 386 162 348 191" />
          <path class="ray ${showIrradiance ? "" : "off"}" style="opacity:${rayOpacity.toFixed(2)}" d="M${sunX.toFixed(1)} ${sunY.toFixed(1)} C284 126 252 160 216 205" />
          <path class="ray ${showIrradiance ? "" : "off"}" style="opacity:${rayOpacity.toFixed(2)}" d="M${sunX.toFixed(1)} ${sunY.toFixed(1)} C500 152 454 191 408 224" />
          <g class="sun" style="transform: translate(${sunX.toFixed(1)}px, ${sunY.toFixed(1)}px); opacity:${isDaylight ? "1" : ".38"}">
            <circle r="21" fill="${isDaylight ? "#ffc928" : "#9aa4b2"}" />
            <circle r="31" fill="${isDaylight ? "rgba(255,201,40,.22)" : "rgba(154,164,178,.12)"}" />
          </g>
          ${this.panelSvg(panels[0], "M142 244 L259 186 L302 207 L188 272 Z", 198, 235)}
          ${this.panelSvg(panels[1], "M270 181 L310 161 L432 224 L390 248 Z", 342, 212)}
          ${this.panelSvg(panels[2], "M321 158 L365 135 L500 206 L454 233 Z", 410, 184)}
          <text x="310" y="306" text-anchor="middle" class="small">${statusText}</text>
        </svg>
        <div class="legend">
          ${panels.map((panel) => `
            <div class="item">
              <b><span>${panel.name}</span><span>${panel.kw.toFixed(2)} kW</span></b>
              <div class="bar"><div class="fill" style="width:${panel.pct}%"></div></div>
              <div class="meta">${panel.pct}% of configured range</div>
            </div>
          `).join("")}
        </div>
      </ha-card>
    `;
  }

  panelSvg(panel, points, x, y) {
    const alpha = 0.18 + panel.ratio * 0.68;
    const hue = 45 - panel.ratio * 14;
    const fill = `hsla(${hue}, 96%, 54%, ${alpha})`;
    const glow = panel.ratio > 0.08 ? "panel panel-glow" : "panel";
    return `
      <g>
        <path class="${glow}" d="${points}" fill="${fill}" />
        <text x="${x}" y="${y - 10}" text-anchor="middle" class="label">${panel.name}</text>
        <text x="${x}" y="${y + 12}" text-anchor="middle" class="small">${panel.kw.toFixed(2)} kW</text>
      </g>
    `;
  }
}

if (!customElements.get("solar-roof-card")) {
  customElements.define("solar-roof-card", SolarRoofCard);
}
