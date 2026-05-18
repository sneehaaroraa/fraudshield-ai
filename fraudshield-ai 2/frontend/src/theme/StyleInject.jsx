/**
 * src/theme/StyleInject.jsx
 * ──────────────────────────
 * Injects global CSS into the document: Google Fonts, keyframe animations,
 * and base resets used throughout the app.
 *
 * Why a component instead of a .css file?
 *   Keeps all theme config in one place (this + colors.js).
 *   Zero CSS modules or Tailwind config required.
 *   Easy to audit from one file.
 *
 * Usage: render <StyleInject /> once at the top of App.jsx.
 */

export function StyleInject() {
  return (
    <style>{`
      /* ── Google Fonts ───────────────────────────────────────────────── */
      @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

      /* ── Reset ─────────────────────────────────────────────────────── */
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

      html, body, #root {
        min-height: 100vh;
        background: #0f1117;
        color: #e2e8f0;
        font-family: 'Inter', system-ui, sans-serif;
        font-size: 14px;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }

      /* ── Scrollbar ──────────────────────────────────────────────────── */
      ::-webkit-scrollbar { width: 6px; height: 6px; }
      ::-webkit-scrollbar-track { background: #0f1117; }
      ::-webkit-scrollbar-thumb { background: #2a2d3e; border-radius: 3px; }
      ::-webkit-scrollbar-thumb:hover { background: #3a3d52; }

      /* ── Typography helpers ─────────────────────────────────────────── */
      .mono { font-family: 'Space Mono', monospace; }

      /* Used for the FraudShield brand label — subtle glow pulse */
      .orb {
        font-family: 'Space Mono', monospace;
        letter-spacing: 3px;
        text-transform: uppercase;
      }

      /* ── Keyframe animations ────────────────────────────────────────── */
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.6; }
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
      }

      @keyframes slideIn {
        from { opacity: 0; transform: translateX(-12px); }
        to   { opacity: 1; transform: translateX(0); }
      }

      @keyframes scanline {
        0%   { transform: translateY(-100%); }
        100% { transform: translateY(100vh); }
      }

      @keyframes blink {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0; }
      }

      @keyframes spin {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
      }

      @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position:  200% 0; }
      }

      /* ── Utility classes ────────────────────────────────────────────── */
      .fade-in   { animation: fadeIn  0.3s ease both; }
      .slide-in  { animation: slideIn 0.25s ease both; }

      /* ── Focus ring ─────────────────────────────────────────────────── */
      :focus-visible {
        outline: 2px solid #00d4ff;
        outline-offset: 2px;
        border-radius: 4px;
      }

      /* ── Selection ──────────────────────────────────────────────────── */
      ::selection {
        background: rgba(0, 212, 255, 0.25);
        color: #e2e8f0;
      }
    `}</style>
  );
}
