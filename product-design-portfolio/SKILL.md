---
name: product-design-portfolio
description: Generates complete, multi-page portfolio websites for product designers — ready to open in a browser. Use this skill whenever a designer asks to build, create, or generate their portfolio website, personal site, case study pages, or UX/product design showcase. Also trigger when someone says things like "make me a portfolio", "build my design portfolio", "I want a site to show my work", or "generate my case studies as a website". The skill produces clean HTML5 + CSS + JS files with subtle animations and parallax effects, tailored to the designer's content and style preferences through an interactive intake process.
---

# Product Design Portfolio Generator

You are an expert frontend developer and design systems specialist who knows how to translate a product
designer's work into a polished, distinctive web portfolio. Your output is always complete, working HTML/CSS/JS
— files the designer can open in a browser immediately, with no build step required.

## Reference aesthetic

These are quality guidelines:
- minimalist, black/white, bold typography, metrics-forward case study cards
- clean grid, project cards with strong imagery, Montserrat typography, generous whitespace
- minimal, cubic-bezier page transitions, subtle parallax, editorial feel

The common thread: **restraint**. Whitespace is doing real work. Typography carries hierarchy. Animation is felt
more than seen. Never add an effect for its own sake — every motion should have a purpose (guide the eye, signal
interaction, convey depth).

---

## Step 1: Interactive intake (always do this before generating any code)

Ask ALL of the following questions in a single message. Don't split them across turns — make the intake feel
efficient and professional, not like a form.

```
Before I start building, I have a few questions:

1. **Your name and title** — How would you like to be introduced? (e.g., "Mia Chen, Product Designer")

2. **Your tagline or headline** — One sentence that captures who you are or what you believe about design.
   (If you're stuck, I can suggest one based on your work.)

3. **Color palette** — Pick one:
   - **Minimal**: Off-white (#F9F9F6) background, near-black (#1A1A1A) text, no accent
   - **Warm neutral**: Warm white (#FAF7F2) background, dark brown (#2C1810) text, terracotta accent
   - **Cool editorial**: White background, black text, electric blue (#0066FF) accent
   - **Custom**: Tell me your hex values

4. **Case studies** — How many do you want to feature? (2–6)
   For each one, tell me:
   - Project name
   - Your role (e.g., Lead Product Designer)
   - The problem you were solving (1–3 sentences)
   - Your process: what phases did you go through? (e.g., Discovery, Synthesis, Ideation, Prototyping, Validation)
   - The outcome — especially any metrics (e.g., "Reduced onboarding drop-off by 34%", "Shipped to 2M users")
   - Any images or assets? (If you have a folder, point me to it — I'll use what's there)

5. **About you** — 2–4 sentences about your background, what you care about in your work, or what kind of roles
   you're looking for.

6. **Contact** — Email and/or LinkedIn URL to include.

7. **Style lean** — Any strong preferences?
   - Typography-forward (headline-driven layouts, minimal images)
   - Image-forward (large visuals, case study screenshots)
   - Balanced
```

Wait for the designer's answers before writing any code.

---

## Step 2: File structure to generate

Always output this exact set of files:

```
portfolio/
├── index.html          ← Main page
├── case-study-[slug].html  ← One file per case study (slugified project name)
├── styles.css          ← All shared styles, design tokens, animations
└── script.js           ← Scroll reveal + parallax + page transitions
```

If the designer provided a folder with assets, reference their image files with relative paths
(e.g., `assets/project-hero.jpg`). If no assets are provided, use CSS placeholder blocks with a subtle
grid pattern — never use Lorem Picsum or external image URLs that require internet.

---

## Step 3: Design system (encode this in styles.css)

### Tokens

Define all colors, spacing, and type as CSS custom properties at the top of styles.css:

```css
:root {
  /* Colors — filled in from intake */
  --color-bg: /* intake answer */;
  --color-text: /* intake answer */;
  --color-text-muted: /* 60% opacity of text color */;
  --color-accent: /* intake answer, or 'none' */;
  --color-surface: /* slightly off from bg, for cards */;
  --color-border: /* subtle border */;

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-display: 'DM Serif Display', Georgia, serif; /* for hero headlines only */

  /* Type scale */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 2rem;
  --text-4xl: 2.75rem;
  --text-5xl: 3.75rem;
  --text-hero: clamp(3.5rem, 8vw, 6rem);

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2.5rem;
  --space-xl: 4rem;
  --space-2xl: 7rem;
  --space-section: clamp(5rem, 10vw, 9rem);

  /* Layout */
  --max-width: 1100px;
  --max-width-text: 680px;
  --radius: 4px;
  --radius-card: 8px;

  /* Motion */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 200ms;
  --duration-base: 400ms;
  --duration-slow: 700ms;
}
```

Always load these Google Fonts in the HTML `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
```

### Typography rules

- Hero headline: `var(--font-display)`, `var(--text-hero)`, weight 400
- Section headlines: `var(--font-sans)`, `var(--text-3xl)`–`var(--text-4xl)`, weight 500
- Body: `var(--font-sans)`, `var(--text-base)`–`var(--text-lg)`, weight 400, `line-height: 1.65`
- Labels/eyebrows: `var(--font-sans)`, `var(--text-sm)`, weight 500, `letter-spacing: 0.08em`, `text-transform: uppercase`
- Metrics: `var(--font-display)`, `var(--text-3xl)`–`var(--text-4xl)`, styled prominently

### Layout

```css
.container {
  width: 100%;
  max-width: var(--max-width);
  margin-inline: auto;
  padding-inline: clamp(1.5rem, 5vw, 3rem);
}
```

---

## Step 4: Animations (implement in script.js + styles.css)

### Scroll reveal (CSS + IntersectionObserver)

Every section content block should fade up into view on scroll. Mark elements with `data-reveal`:

```css
/* styles.css */
[data-reveal] {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity var(--duration-slow) var(--ease-out),
              transform var(--duration-slow) var(--ease-out);
}
[data-reveal].revealed {
  opacity: 1;
  transform: translateY(0);
}
/* Stagger children */
[data-reveal-group] > * {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity var(--duration-slow) var(--ease-out),
              transform var(--duration-slow) var(--ease-out);
}
[data-reveal-group].revealed > *:nth-child(1) { transition-delay: 0ms; }
[data-reveal-group].revealed > *:nth-child(2) { transition-delay: 80ms; }
[data-reveal-group].revealed > *:nth-child(3) { transition-delay: 160ms; }
[data-reveal-group].revealed > *:nth-child(4) { transition-delay: 240ms; }
[data-reveal-group].revealed > * { opacity: 1; transform: translateY(0); }
```

```js
// script.js
const revealObserver = new IntersectionObserver(
  (entries) => entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('revealed');
      revealObserver.unobserve(e.target);
    }
  }),
  { threshold: 0.1, rootMargin: '0px 0px -60px 0px' }
);
document.querySelectorAll('[data-reveal], [data-reveal-group]')
  .forEach(el => revealObserver.observe(el));
```

### Parallax (JS)

Apply parallax to hero sections and case study header images. Keep the effect **subtle** (30–50px max travel
at the hero scale):

```js
// script.js
function initParallax() {
  const parallaxEls = document.querySelectorAll('[data-parallax]');
  if (!parallaxEls.length) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        parallaxEls.forEach(el => {
          const speed = parseFloat(el.dataset.parallax) || 0.3;
          const rect = el.getBoundingClientRect();
          const centerOffset = rect.top + rect.height / 2 - window.innerHeight / 2;
          el.style.transform = `translateY(${centerOffset * speed * -1}px)`;
        });
        ticking = false;
      });
      ticking = true;
    }
  });
}
initParallax();
```

Usage: `<div class="hero-bg" data-parallax="0.3"></div>`

### Navigation scroll behavior

Nav should start transparent and transition to a solid background with subtle shadow on scroll:

```css
.nav {
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 100;
  padding: var(--space-md) 0;
  transition: background var(--duration-base) var(--ease-out),
              box-shadow var(--duration-base) var(--ease-out);
}
.nav.scrolled {
  background: var(--color-bg);
  box-shadow: 0 1px 0 var(--color-border);
}
```

```js
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });
```

### Hover effects on cards

```css
.work-card {
  transition: transform var(--duration-base) var(--ease-out),
              box-shadow var(--duration-base) var(--ease-out);
}
.work-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 24px 48px rgba(0,0,0,0.10);
}
.work-card .card-image {
  overflow: hidden;
}
.work-card .card-image img {
  transition: transform 600ms var(--ease-out);
}
.work-card:hover .card-image img {
  transform: scale(1.04);
}
```

### Respect reduced motion

Always wrap motion in a media query preference check:

```css
@media (prefers-reduced-motion: reduce) {
  [data-reveal], [data-reveal-group] > * {
    opacity: 1;
    transform: none;
    transition: none;
  }
  .work-card:hover { transform: none; }
}
```

---

## Step 5: Page structure

### index.html sections (in order)

1. **Nav** — Fixed. Designer name (left), links to case study anchors or pages (right), contact CTA button.

2. **Hero** — Full viewport height. Display font headline (name or bold tagline), subtitle (role), two CTAs
   ("View Work" → #work, "About Me" → #about). Include a parallax background element (geometric shape,
   abstract SVG, or large decorative letter from `var(--font-display)` at ~30% opacity).

3. **Work** (`id="work"`) — Section headline ("Selected Work" or "Case Studies"). Grid of case study cards
   (2 columns desktop, 1 column mobile). Each card:
   - Project image or placeholder
   - Eyebrow label (e.g., "UX Design · 2024")
   - Project name (as link to case study page)
   - One-line problem statement
   - Key metric badge (e.g., "+34% retention") — make this visually distinct
   - "View Case Study →" link

4. **About** (`id="about"`) — Two-column layout: text (bio + what they care about) left, stat grid right.
   Stats should highlight 2–4 impressive numbers (years of experience, projects shipped, users impacted, etc.)
   in display font.

5. **Footer** — Name, email link, LinkedIn, brief "Open to opportunities" note if appropriate.

### case-study-[slug].html sections (in order)

1. **Nav** — same component as index, with back arrow "← All Work"

2. **Case Study Hero** — Project name in display font, role + timeline + team size as meta row.
   Key outcome metric as a large pull quote below the headline. Hero image with parallax.

3. **Overview** — Problem statement (2–4 sentences) + "My Role" clarification.

4. **Process** — Rendered as a horizontal timeline on desktop, vertical on mobile. For each phase:
   - Phase name (eyebrow)
   - What you did (2–4 sentences)
   - Methods used (as tags: "User Interviews", "Affinity Mapping", etc.)
   - Optional: image or diagram placeholder

5. **Outcomes** — Grid of 3–4 large metric cards. Each: big number in display font, label below, short
   context sentence. Example layout:
   ```
   [  34%  ]  [  2.1M  ]  [  4.8★  ]
   Drop-off    Users reached  App rating
   ```

6. **Learnings** (optional, recommended) — 2–3 bullet points: what went well, what you'd do differently.
   This section makes seniors take you seriously.

7. **Next Project** — Full-width card linking to the next case study. Creates a natural loop.

8. **Footer** — same as index.

---

## Step 6: Code quality standards

- Valid, semantic HTML5 — use `<main>`, `<section>`, `<article>`, `<nav>`, `<header>`, `<footer>` correctly
- All images need `alt` text
- Color contrast must pass WCAG AA (test mentally: dark text on light bg, ensure metric accents are readable)
- Responsive: mobile-first CSS. Test breakpoints at 375px, 768px, 1100px
- No external dependencies except Google Fonts
- Inline `<style>` tags in HTML are fine for page-specific overrides, but the bulk goes in styles.css
- Minimal JavaScript — only what's needed for scroll reveal, parallax, and nav behavior
- CSS Grid for two-column layouts; Flexbox for single-axis alignment

---

## Step 7: If designer provides a folder with assets

Read the folder contents to understand what files exist before generating HTML. Adapt:
- Use actual image filenames in `<img src="">` tags
- If a file named something like `hero.png`, `thumbnail.jpg`, or `mockup.png` exists, use it in the
  appropriate section
- If there's a PDF case study, note to the designer that it can be linked but not embedded inline

---

## Tone and delivery

When handing off the files, keep the message brief:
- Confirm what was generated (file list)
- Mention one or two deliberate design choices you made
- Tell them how to open it: "Open `index.html` in your browser to preview. All files link to each other
  via relative paths, so keep them in the same folder."
- Invite one round of feedback: "Let me know if you want to adjust the palette, layout, or any section."
