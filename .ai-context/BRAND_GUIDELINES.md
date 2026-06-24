# Brand Guidelines (Post-MVP Polish Reference)

## Color Palette (Dark Mode Only for MVP)
- Primary: `#2563EB` (Blue 600) - Trust, intelligence
- Secondary: `#059669` (Emerald 600) - Growth, insight
- Background: `#0F172A` (Slate 950)
- Surface: `#1E293B` (Slate 800)
- Surface Hover: `#334155` (Slate 700)
- Text Primary: `#F8FAFC` (Slate 50)
- Text Secondary: `#CBD5E1` (Slate 300)
- Text Muted: `#94A3B8` (Slate 400)
- Border: `#334155` (Slate 700)
- Error: `#EF4444` (Red 500)
- Warning: `#F59E0B` (Amber 500)
- Success: `#22C55E` (Green 500)

## Session Type Badges
- Skill Development: `bg-blue-500/20 text-blue-400 border-blue-500/30`
- Applied Learning: `bg-emerald-500/20 text-emerald-400 border-emerald-500/30`
- Peer Collaboration: `bg-purple-500/20 text-purple-400 border-purple-500/30`
- Ambiguous: `bg-slate-500/20 text-slate-400 border-slate-500/30`
- Personal: `bg-amber-500/20 text-amber-400 border-amber-500/30`

## Typography
- Font Mono: `"JetBrains Mono", "Fira Code", monospace` (data, code, timestamps)
- Font UI: `"Inter", system-ui, sans-serif` (labels, buttons, nav)
- Base Size: 13px (0.8125rem)
- Scale: 12px / 13px / 14px / 16px / 18px / 24px
- Line Height: 1.5 (body), 1.2 (headings)

## Spacing
- Unit: 4px (0.25rem)
- Scale: 4, 8, 12, 16, 24, 32, 48, 64

## Components (shadcn/ui + Tailwind)
- Card: `rounded-xl border border-slate-700 bg-slate-800/50 hover:border-slate-600 transition-colors`
- Button Primary: `bg-blue-600 hover:bg-blue-500 text-white`
- Button Ghost: `hover:bg-slate-700 text-slate-100`
- Button Destructive: `bg-red-600 hover:bg-red-500 text-white`
- Input: `bg-slate-900 border-slate-700 focus:border-blue-500 focus:ring-blue-500/20`
- Badge: `px-2 py-0.5 text-xs font-medium rounded-full`
- Separator: `border-slate-700`

## Dashboard Layout (MVP)
```
Desktop (≥1024px):
┌─────────────────────────────────────────────────────┐
│ Sidebar (280px)          │ Main Content (flex-1)    │
│  - Logo                  │  - Session List (50%)    │
│  - Nav: Sessions         │  - Session Detail (50%)  │
│  - Nav: Analytics        │                          │
│  - Nav: Settings         │                          │
│  - User/Status           │                          │
└─────────────────────────────────────────────────────┘

Mobile (<1024px):
┌─────────────────────┐
│ Top Bar             │
│  Logo | Menu Btn    │
├─────────────────────┤
│ Session List        │
│ (full width)        │
├─────────────────────┤
│ Bottom Nav (4 items)│
└─────────────────────┘
```

## Session Detail View
- Header: Session type badge, time range, duration, status
- Intent Card: Type, goal, confidence, friction points, evidence
- Timeline: App switches, screenshots (thumbnails), input activity
- Raw Events: Expandable list (window_title, process, timestamp)

## Accessibility (MVP Minimum)
- Semantic HTML (`<nav>`, `<main>`, `<aside>`, `<section>`)
- ARIA labels on icon buttons
- Focus visible: `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500`
- Color contrast: AA (4.5:1) minimum
- Keyboard navigable: Tab order logical