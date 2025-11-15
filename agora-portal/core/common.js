// core/common.js
//
// Designed for the existing repo style (React via CDN + babel).
// Adds window.WWCommon = { UserContext, AgeGate, detectCrisis, ReflectionPrompt, helpers }
// Usage in pages:
// <script type="text/babel" src="/core/common.js"></script>
// Then inside page scripts: const { UserContext, AgeGate, ReflectionPrompt, detectCrisis } = WWCommon;

(() => {
  const React = window.React;
  const { createContext, useContext, useState, useEffect } = React;

  // ---- UserContext ----
  const UserContext = createContext();

  // simple mock factory (page-level code may replace with real auth)
  function createMockUser(opts = {}) {
    return {
      userId: opts.userId || "anon",
      username: opts.username || null,
      ageCategory: opts.ageCategory || "13-15", // "13-15" | "16-17" | "18+"
      birthYear: opts.birthYear || null,
      consentStatus: opts.consentStatus || { parentalConsent: false, consentDate: null, renewalDue: null, guardianEmail: null },
      pathProgress: opts.pathProgress || { currentPath: null, completedStations: [], activeQuests: [], reflectionJournal: [] },
      insights: opts.insights || { total: 0, breakdown: { biblical:0, theological:0, ethical:0, contemplative:0, comparative:0 }, depthScore: 0 },
      dailyUsageMinutes: opts.dailyUsageMinutes || 0,
      sabbathMode: opts.sabbathMode || { enabled: false, until: null },
      preferredLanguage: opts.preferredLanguage || "sv",
      accessibilitySettings: opts.accessibilitySettings || { fontSize: "medium", highContrast: false, screenReaderMode: false }
    };
  }

  // ---- Crisis detection (simple, extendable) ----
  function detectCrisis(text) {
    if (!text || typeof text !== "string") return null;
    const lower = text.toLowerCase();

    // Expandable keyword lists (in production use ML + human review)
    const selfHarm = ['suicide','kill myself','end my life','i will die','hurt myself'];
    const abuse = ['rape','raped','molest','molested','abuse','assault'];
    const identity = ['gay','lesbian','trans','same-sex','sexual orientation','queer'];

    if (selfHarm.some(k => lower.includes(k))) return { level: 'critical', type: 'self-harm' };
    if (abuse.some(k => lower.includes(k))) return { level: 'critical', type: 'abuse' };
    if (identity.some(k => lower.includes(k))) return { level: 'sensitive', type: 'identity' };
    // Add other sensitive categories as needed
    return null;
  }

  // ---- AgeGate component ----
  function AgeGate({ minimumAge = 13, children, fallback = null }) {
    // uses UserContext
    const ctx = useContext(UserContext);
    const user = ctx?.user || null;

    const ageMap = { "13-15": 13, "16-17": 16, "18+": 18 };
    const userAge = user?.ageCategory ? (ageMap[user.ageCategory] || 0) : 0;
    const hasConsent = user?.consentStatus?.parentalConsent === true;

    const allowed = user && userAge >= minimumAge && hasConsent;

    if (!allowed) {
      return fallback || (
        <div style={{ padding: 12, borderRadius: 6, background: "#fff6e6", border: "1px solid #f0d9b5" }}>
          <strong>Access restricted.</strong>
          <div style={{ marginTop: 6, color: "#444" }}>
            This content requires parental consent and age {minimumAge}+. Current status: ageCategory={user?.ageCategory ?? 'unknown'}, parentalConsent={String(user?.consentStatus?.parentalConsent ?? false)}.
          </div>
        </div>
      );
    }
    return React.createElement(React.Fragment, null, children);
  }

  // ---- ReflectionPrompt (reusable) ----
  function ReflectionPrompt({ prompts = [], onComplete = () => {}, minSeconds = 30 }) {
    // Minimal implementation as a common component; pages can style differently
    const [idx, setIdx] = useState(0);
    const [responses, setResponses] = useState({});
    const [seconds, setSeconds] = useState(0);

    useEffect(() => {
      setSeconds(0);
      const t = setInterval(() => setSeconds(s => s + 1), 1000);
      return () => clearInterval(t);
    }, [idx]);

    const canProceed = seconds >= minSeconds && (responses[idx] || "").trim().length > 0;

    return (
      React.createElement('div', { className: 'ww-reflection-prompt' },
        React.createElement('h4', null, 'Reflection'),
        React.createElement('p', { style: { color:'#555', fontSize: 13 } }, `Take your time — minimum ${minSeconds}s per prompt.`),
        React.createElement('p', null, React.createElement('strong', null, 'Prompt:'), ' ', prompts[idx] || ''),
        React.createElement('textarea', {
          rows: 5,
          style: { width: '100%' },
          value: responses[idx] || '',
          onChange: (e) => setResponses(Object.assign({}, responses, { [idx]: e.target.value }))
        }),
        React.createElement('div', { style: { marginTop: 8 } },
          idx > 0 && React.createElement('button', { onClick: () => setIdx(i => i - 1) }, 'Back'),
          !canProceed && React.createElement('button', { disabled: true, style: { marginLeft: 8 } }, `Please reflect ${Math.max(0, minSeconds - seconds)}s`),
          canProceed && idx < prompts.length - 1 && React.createElement('button', { onClick: () => setIdx(i => i + 1), style: { marginLeft: 8 } }, 'Next'),
          canProceed && idx === prompts.length - 1 && React.createElement('button', { onClick: () => onComplete(responses), style: { marginLeft: 8 } }, 'Complete Reflection')
        )
      )
    );
  }

  // ---- Small persistence helpers ----
  function persistLastActivity(keyBase = 'ww_last') {
    try { localStorage.setItem(keyBase, Date.now().toString()); } catch(e) {}
  }
  function loadPersistedProgress(key) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch(e) { return null; }
  }
  function savePersistedProgress(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch(e) {}
  }

  // Attach to window
  window.WWCommon = window.WWCommon || {};
  window.WWCommon.UserContext = UserContext;
  window.WWCommon.createMockUser = createMockUser;
  window.WWCommon.detectCrisis = detectCrisis;
  window.WWCommon.AgeGate = AgeGate;
  window.WWCommon.ReflectionPrompt = ReflectionPrompt;
  window.WWCommon.persistLastActivity = persistLastActivity;
  window.WWCommon.loadPersistedProgress = loadPersistedProgress;
  window.WWCommon.savePersistedProgress = savePersistedProgress;

  // helper for graceful import in modules
  try { Object.defineProperty(window.WWCommon, '__esModule', { value: true }); } catch(e) {}
})();
