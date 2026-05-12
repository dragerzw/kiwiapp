# Cascading Style Sheets - CSS

## Part 1 — CSS Fundamentals

### 1. What is CSS and how does it work?

**Introduction:**
HTML gives a page its structure and content, but it has no opinion about how things look. CSS (Cascading Style Sheets) is the language that controls the visual presentation — colours, fonts, spacing, layout. Every property you set in CSS is a key-value pair called a *declaration*, and you group declarations together into *rules* that target specific HTML elements.

**How to link a CSS file:**
CSS lives in a separate `.css` file and is connected to HTML via a `<link>` tag in the `<head>`.

```html
<!-- index.html -->
<head>
  <link rel="stylesheet" href="styles.css">
</head>
```

Once linked, every rule in `styles.css` applies to that page.

---

### 2. Selectors

**Introduction:**
A selector tells CSS *which* HTML elements a rule applies to. There are three basic kinds you will use constantly.

| Selector | Syntax | Targets |
|---|---|---|
| Element | `p { }` | Every `<p>` tag on the page |
| Class | `.card { }` | Every element with `class="card"` |
| ID | `#submit-btn { }` | The single element with `id="submit-btn"` |

**Rule anatomy:**

```css
selector {
  property: value;
  property: value;
}
```

**Example:**

```css
/* element selector — targets every paragraph on the page */
p {
  color: #333333;   /* dark grey text colour */
}

/* class selector — targets every element with class="card" */
.card {
  background-color: #ffffff;   /* white background */
  border-radius: 8px;          /* slightly rounded corners */
}

/* id selector — targets the single element with id="logo" */
#logo {
  font-size: 1.5rem;   /* 1.5 × 16px = 24px */
}
```

**Tip:** Classes are the most common selector you will write. IDs are for JavaScript hooks — prefer classes for styling.

---

### 3. The Cascade and Specificity

**Introduction:**
"Cascading" in CSS means that multiple rules can target the same element and the browser must decide which one wins. The rule is: **more specific selectors win**. ID > class > element. If specificity is equal, the rule written later in the file wins.

**Example:**

```css
p {
  color: black;   /* element selector — lowest specificity, applied to all <p> */
}

.highlight {
  color: orange;   /* class selector — wins over the element selector above */
}

#special {
  color: red;   /* id selector — wins over both class and element selectors */
}
```

```html
<p>Black text</p>
<p class="highlight">Orange text</p>
<p id="special" class="highlight">Red text (ID wins)</p>
```

**Practical advice:** Keep specificity low by using classes. Avoid fighting the cascade with overly specific rules — it makes CSS hard to maintain.

---

### 4. Text Properties

**Introduction:**
Typography is the first thing users notice. CSS gives you full control over how text looks. These are the properties you will use in nearly every project.

**Properties to cover, in order:**

#### `color`

Sets the text colour. Accepts colour names, hex codes, or `rgb()`.

```css
.logo-text {
  color: #4ade80;   /* bright green — used in the app's login page logo */
}
```

#### `font-size`

Sets how large the text is. `rem` units are preferred (relative to the root font size, usually 16px).

```css
.headline {
  font-size: 2rem;   /* 2 × 16px = 32px — double the body text size */
}
```

#### `font-weight`

Controls how bold the text is. Values are 100–900, or keywords `normal` (400) and `bold` (700).

```css
.logo-text {
  font-weight: 700;   /* bold — makes text heavier and more prominent */
}
```

#### `font-family`

Sets the typeface. Provide fallbacks in case the first font is not available.

```css
body {
  font-family: system-ui, -apple-system, sans-serif;   /* uses the OS default font, with sans-serif as a final fallback */
}
```

Point to `src/index.css` line 9 — this is exactly what the app uses.

#### `line-height`

Sets the vertical space between lines of text. A value of `1.6`–`1.7` is comfortable for body text.

```css
.subline {
  line-height: 1.7;   /* 1.7× the font size — adds breathing room between lines */
}
```

#### `letter-spacing`

Adds or removes space between characters. Positive values spread letters apart; negative pulls them together.

```css
.logo-text {
  letter-spacing: 0.05em;   /* adds a small gap between each letter — used in the app logo */
}
```

#### `text-align`

Aligns text horizontally: `left`, `center`, `right`.

```css
.sign-in-card {
  text-align: center;   /* centres all text content inside the sign-in card */
}
```

#### `text-transform`

Changes capitalisation without editing the HTML.

```css
.logo-text {
  text-transform: lowercase;   /* forces all characters to lowercase regardless of how they are typed in HTML */
}
```

---

### 5. The Box Model

**Introduction:**
Every HTML element is a rectangle. The *box model* describes the four layers that make up that rectangle, from inside out:

1. **Content** — the actual text or image
2. **Padding** — transparent space *inside* the border
3. **Border** — a line around the padding
4. **Margin** — transparent space *outside* the border that pushes other elements away

Understanding the box model is the single most important CSS concept. Once you get it, layout clicks.

```text
┌──────────────── margin ───────────────────┐
│  ┌─────────────── border ──────────────┐  │
│  │  ┌──────────── padding ──────────┐  │  │
│  │  │           content             │  │  │
│  │  └───────────────────────────────┘  │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

**`box-sizing: border-box`** — by default, `width` only measures the content area, which makes sizing confusing. Setting `box-sizing: border-box` makes `width` include padding and border, which is almost always what you want. Point to `src/index.css` lines 1–3 — the app applies this globally with `*, *::before, *::after`.

**Example:**

```css
/* Apply to everything — do this at the top of every project */
*, *::before, *::after {
  box-sizing: border-box;   /* width now includes padding and border, not just content */
}

.card {
  width: 300px;               /* total width of the card including padding and border */
  padding: 1.5rem;            /* 24px of space inside the card on all four sides */
  border: 1px solid #e2e8f0;  /* thin, light grey solid border */
  border-radius: 12px;        /* rounds all four corners with a 12px radius */
  margin-bottom: 1rem;        /* 16px of space below the card to separate it from the next element */
}
```

**Padding vs margin:** Padding is inside the box (affects background); margin is outside (always transparent). Use padding when you want the background to extend into the space; use margin to separate elements from each other.

---

### 6. Background and Borders

#### `background-color`

```css
body {
  background-color: #f8f9fa;   /* very light grey — a softer alternative to pure white for page backgrounds */
}
```

#### `border`

Shorthand for `border-width border-style border-color` in one declaration:

```css
.card {
  border: 1px solid #dee2e6;   /* 1px wide, solid line style, light grey colour */
}
```

#### `border-radius`

Rounds the corners of the box:

```css
.card {
  border-radius: 12px;   /* rounds all four corners with a 12px radius */
}

.avatar {
  border-radius: 50%;    /* makes the element a circle — only works when width equals height */
}
```

#### `box-shadow`

Adds a shadow under the element. The four values are: `x-offset y-offset blur spread color`.

```css
.sign-in-card {
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07),    /* close shadow: small blur, very light — gives a subtle lift */
              0 20px 60px -10px rgba(0,0,0,0.12);  /* distant shadow: large blur, slightly stronger — adds depth */
}
```

Point to `src/components/LoginPage.css` lines 138–140 — this is the exact shadow used on the login card.

---

### Part 1 Exercise — Style a Portfolio Card

**Objective:** Build a styled portfolio card that looks like the ones in the app.

**Step 1 — Create the files.**
Create two files in the same folder: `index.html` and `styles.css`.

**Step 2 — Write the HTML structure.**
Open `index.html` and write the skeleton of a card. We need a wrapper div, a title, a description, and a button.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Portfolio Card</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="card">
    <div class="card-body">
      <h3 class="card-title">Tech Growth Portfolio</h3>
      <p class="card-description">A diversified portfolio focused on technology sector growth stocks.</p>
    </div>
    <div class="card-footer">
      <button class="btn-view">View Holdings</button>
    </div>
  </div>
</body>
</html>
```

Open the file in a browser. The card is unstyled — everything stacks and uses browser defaults. Now we fix that.

**Step 3 — Add the global reset to `styles.css`.**
Always start every project with these two rules:

```css
*, *::before, *::after {
  box-sizing: border-box;   /* width includes padding and border, prevents sizing surprises */
}

body {
  margin: 0;                                         /* removes the browser's default 8px body margin */
  background-color: #f8f9fa;                         /* light grey page background */
  font-family: system-ui, -apple-system, sans-serif; /* uses the device's native system font */
}
```

Refresh. The page background turns light grey and the default margin around the body disappears.

**Step 4 — Style the card box.**
Give the card a white background, rounded corners, a border, and a shadow. Add padding inside it and constrain its width so it does not stretch full-screen.

```css
.card {
  width: 320px;                                       /* card is 320px wide */
  margin: 2rem auto;                                  /* 32px top/bottom, auto left/right — centres the card horizontally */
  background-color: #ffffff;                          /* white background to contrast the grey page */
  border: 1px solid #e2e8f0;                         /* thin light grey border */
  border-radius: 12px;                                /* rounded corners */
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07),       /* subtle close shadow */
              0 10px 30px -5px rgba(0,0,0,0.1);       /* softer distant shadow for depth */
}
```

Refresh. The card is now a white rounded rectangle floating on the grey background.

**Step 5 — Style the card body (title and description).**
Add padding inside the body, make the title bold and dark, and make the description smaller and grey.

```css
.card-body {
  padding: 1.25rem 1.5rem;   /* 20px top/bottom, 24px left/right — space inside the card around the text */
}

.card-title {
  margin: 0 0 0.5rem 0;   /* removes default heading margin, adds 8px below the title */
  font-size: 1.1rem;       /* slightly larger than body text */
  font-weight: 700;        /* bold — makes the portfolio name prominent */
  color: #0f172a;          /* very dark navy — near-black for high contrast */
}

.card-description {
  margin: 0;          /* removes default paragraph margin */
  font-size: 0.9rem;  /* slightly smaller than body text */
  color: #64748b;     /* medium grey — visually secondary to the title */
  line-height: 1.5;   /* 1.5× the font size — comfortable spacing between description lines */
}
```

Refresh. Title is bold and dark; description is smaller and grey.

**Step 6 — Style the card footer and button.**
Add a top border to separate the footer, give it padding, and style the button with a green background.

```css
.card-footer {
  padding: 0.75rem 1.5rem;        /* 12px top/bottom, 24px left/right */
  border-top: 1px solid #e2e8f0;  /* thin divider line separating the footer from the card body */
}

.btn-view {
  background-color: #22c55e;   /* green background — signals a positive action */
  color: #ffffff;              /* white text — high contrast against green */
  border: none;                /* removes the browser's default button border */
  border-radius: 8px;          /* rounded corners on the button */
  padding: 0.5rem 1rem;        /* 8px top/bottom, 16px left/right — makes the button comfortably clickable */
  font-size: 0.9rem;           /* matches the description text size */
  font-weight: 600;            /* semi-bold — makes the button label clear */
  cursor: pointer;             /* shows a hand cursor on hover so users know it is clickable */
}
```

Refresh. The button is now green with white text. The footer has a top divider line.

**Step 7 — Add a hover effect on the button (bonus).**
Add a `:hover` rule to give users visual feedback when they move their mouse over the button.

```css
.btn-view:hover {
  background-color: #16a34a;   /* darker green on hover — shows the button responded to the mouse */
}
```

**Final result:** A clean portfolio card with white background, rounded corners, shadow, bold title, grey description, and a green "View Holdings" button — matching the app's card style.

---

## Part 2 — Layout with Flexbox

### 1. Normal Flow and the Display Property

**Introduction:**
Without any CSS layout rules, HTML elements stack in *normal flow*: block elements (like `<div>`, `<p>`) each take up a full line and stack vertically; inline elements (like `<span>`, `<a>`) flow horizontally within a line. Normal flow is rarely enough for real UI layouts. The `display` property changes how an element and its children are arranged.

```css
div        { display: block;  }   /* default — block elements stack vertically, each on its own line */
span       { display: inline; }   /* inline — elements sit side by side within a line of text */
.container { display: flex;   }   /* flexbox — children arrange in a row or column with flexible sizing */
```

---

### 2. `display: flex` — Activating Flexbox

**Introduction:**
Flexbox is a CSS layout mode designed for arranging items in a row or column, with control over spacing and alignment. You activate it on a *container* element, and all its direct children become *flex items*.

```css
.container {
  display: flex;   /* turns on flexbox — children now sit side by side in a row by default */
}
```

```html
<div class="container">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

Without `display: flex`, the three divs stack vertically. With it, they sit side by side.

---

### 3. `flex-direction`

**Introduction:**
Controls whether flex items are arranged in a row (horizontal, the default) or a column (vertical).

```css
.row-layout    { flex-direction: row;    }   /* → default: items go left to right */
.column-layout { flex-direction: column; }   /* ↓ items go top to bottom */
```

**Codebase example:** On mobile, the LoginPage stacks its two panels vertically by changing `flex-direction` to `column` — see `src/components/LoginPage.css` lines 194–195.

---

### 4. `justify-content` — Aligning Along the Main Axis

**Introduction:**
The *main axis* runs along the `flex-direction` (horizontal for `row`, vertical for `column`). `justify-content` distributes items along that axis.

```css
.container {
  display: flex;
  justify-content: flex-start;    /* items packed to the left (default) */
  justify-content: flex-end;      /* items packed to the right */
  justify-content: center;        /* items centred horizontally */
  justify-content: space-between; /* first item at left edge, last at right edge, rest evenly spaced */
  justify-content: space-around;  /* equal space on both sides of each item */
}
```

**Example — navigation bar:**

```css
.navbar {
  display: flex;                    /* puts brand and links in a row */
  justify-content: space-between;   /* brand goes to the left, nav links go to the right */
  align-items: center;              /* vertically centres both brand and links in the bar */
  padding: 1rem 2rem;               /* 16px top/bottom, 32px left/right */
}
```

---

### 5. `align-items` — Aligning Along the Cross Axis

**Introduction:**
The *cross axis* is perpendicular to the main axis. `align-items` aligns items on this axis (vertically when `flex-direction: row`).

```css
.container {
  display: flex;
  align-items: stretch;     /* items fill the full container height (default) */
  align-items: flex-start;  /* items aligned to the top */
  align-items: flex-end;    /* items aligned to the bottom */
  align-items: center;      /* items vertically centred */
}
```

**Example — vertically centred hero content:**

```css
.lp-hero {
  display: flex;
  align-items: center;      /* vertically centres the hero content within the panel */
  justify-content: center;  /* horizontally centres the hero content within the panel */
}
```

Point to `src/components/LoginPage.css` lines 13–14 — this is exactly how the hero panel works.

---

### 6. `gap`

**Introduction:**
Adds space *between* flex items without using margins. Cleaner than adding `margin-right` to every item manually.

```css
.feature-list {
  display: flex;
  flex-direction: column;   /* stack items vertically */
  gap: 0.75rem;             /* 12px of space between each list item — no margin needed on individual items */
}
```

Point to `src/components/LoginPage.css` line 107 — this is used in the app's feature checklist.

---

### 7. `flex` — How Items Grow, Shrink, and Build a Grid

**Introduction:**
By default, flex items only take up as much space as their content needs. The `flex` property on an *item* (not the container) controls how the item participates in distributing available space. It is shorthand for three separate properties:

| Property | What it controls | Default |
|---|---|---|
| `flex-grow` | How much the item grows to fill *extra* space | `0` (don't grow) |
| `flex-shrink` | How much the item shrinks when space is *tight* | `1` (can shrink) |
| `flex-basis` | The item's starting size before any growing or shrinking | `auto` |

The shorthand syntax is: `flex: [grow] [shrink] [basis]`

#### Part A — Understanding the three sub-properties

**`flex-grow`** — distributes leftover space proportionally. Think of it as "share of the pie":

```css
/* Both items grow equally — each gets half of any leftover space */
.sidebar { flex-grow: 1; }   /* claims 1 share of extra space */
.content { flex-grow: 1; }   /* claims 1 share of extra space */

/* Content claims twice as much extra space as sidebar */
.sidebar { flex-grow: 1; }   /* claims 1 share — gets 1/3 of extra space */
.content { flex-grow: 2; }   /* claims 2 shares — gets 2/3 of extra space */
```

If the container is 900px wide and both items have `flex-grow: 1`, each gets 450px. If sidebar is `flex-grow: 1` and content is `flex-grow: 2`, sidebar gets 300px and content gets 600px (3 total shares: sidebar = 1/3, content = 2/3).

**`flex-shrink`** — controls how items give up space when the container is too small:

```css
.sidebar { flex-shrink: 0; }  /* never shrinks below its flex-basis — stays fixed width */
.content { flex-shrink: 1; }  /* shrinks proportionally when container is too narrow (default) */
```

**`flex-basis`** — sets the starting width (for `flex-direction: row`) or height (for `column`) before growing/shrinking kicks in:

```css
.panel { flex-basis: 300px; }  /* starts at exactly 300px, then grows/shrinks from there */
.panel { flex-basis: 50%;    }  /* starts at 50% of the container width */
.panel { flex-basis: auto;   }  /* uses the element's natural content size (default) */
```

#### Part B — Common shorthand patterns

Memorise these four — they cover almost every situation:

```css
/* 1. Equal share — item takes an equal portion of all available space */
.item { flex: 1; }                 /* shorthand for flex: 1 1 0 — grows, shrinks, starts at 0 */

/* 2. Fixed size — item never grows or shrinks, stays exactly at the given width */
.sidebar { flex: 0 0 240px; }      /* don't grow (0), don't shrink (0), always 240px */

/* 3. Fixed percentage — same as fixed but uses a percentage of the container */
.sign-in-panel { flex: 0 0 45%; }  /* don't grow, don't shrink, always 45% of container */

/* 4. Flexible percentage — starts at a percentage but adapts when space changes */
.hero-panel { flex: 1 1 55%; }     /* start at 55%, grow if there is extra space, shrink if needed */
```

Point to `src/components/LoginPage.css` lines 10 and 124 — patterns 3 and 4 are used directly to split the login page 55/45.

#### Part C — Building a Grid with Flexbox

This is the bridge between Flexbox and Bootstrap's grid system.

By default, flex items all stay on one row — they shrink to fit rather than wrap to a new line. Adding `flex-wrap: wrap` changes this: when items run out of horizontal space they wrap onto the next row. Combined with a `flex-basis` that fixes each item's width, this creates a responsive multi-column grid using only Flexbox.

**A simple 3-column card grid:**

```css
/* Step 1 — the grid container */
.card-grid {
  display: flex;     /* turns on flexbox */
  flex-wrap: wrap;   /* items wrap to the next row instead of shrinking to fit one row */
  gap: 1rem;         /* 16px space between rows AND between columns */
}

/* Step 2 — each card */
.card-grid .card {
  flex: 0 0 calc(33.333% - 0.67rem);  /* don't grow, don't shrink, start at one third of the container */
                                        /* calc subtracts a share of the gap: 2 gaps ÷ 3 cards ≈ 0.67rem */
}
```

With 3 cards, each `flex-basis` is 33.333%, so exactly 3 fit per row. When they exceed the row width they wrap to a new row automatically.

**Visual result:**

```
┌──────────┐ ┌──────────┐ ┌──────────┐   ← row 1
│  Card 1  │ │  Card 2  │ │  Card 3  │
└──────────┘ └──────────┘ └──────────┘
┌──────────┐ ┌──────────┐               ← row 2 (wraps automatically)
│  Card 4  │ │  Card 5  │
└──────────┘ └──────────┘
```

**Making it responsive without media queries — `flex: 1 1 280px`:**

Instead of a fixed percentage, give items a minimum width and let the browser decide how many fit per row:

```css
.card-grid {
  display: flex;
  flex-wrap: wrap;   /* allow wrapping when items don't fit on one row */
  gap: 1rem;         /* 16px gap between rows and columns */
}

.card-grid .card {
  flex: 1 1 280px;   /* start at 280px, grow to fill the row, wrap to next row when needed */
}
```

On a 1200px desktop: 4 cards of 280px fit per row (4 × 280 = 1120px).
On a 768px tablet: 2 cards fit per row.
On a 360px phone: 1 card per row.
**No media queries needed** — the layout adapts automatically.

**Why this matters — it is exactly what Bootstrap does under the hood:**

Bootstrap's grid is built on this exact flex-wrap pattern:

```css
/* This is (roughly) what Bootstrap's .row class does */
.row {
  display: flex;     /* flex container */
  flex-wrap: wrap;   /* items wrap to new rows when they run out of space */
  gap: 1.5rem;       /* Bootstrap's default gutter between columns */
}

/* This is (roughly) what Bootstrap's column classes do */
.col-4  { flex: 0 0 33.333%; }  /* 4 out of 12 columns = one third of the row */
.col-6  { flex: 0 0 50%;     }  /* 6 out of 12 columns = one half of the row */
.col-12 { flex: 0 0 100%;    }  /* 12 out of 12 columns = full row width */
```

When you write `class="col-12 col-md-6 col-lg-4"` in Bootstrap, you are telling the browser:

- Default (mobile): `flex-basis: 100%` — full width, 1 per row
- At `md` (≥768px): `flex-basis: 50%` — two per row
- At `lg` (≥992px): `flex-basis: 33.333%` — three per row

Bootstrap just adds media queries on top of flex-wrap and packages it as utility classes. By the time you reach part 3, flex-wrap will feel familiar because you have already built a grid yourself.

---

### 8. Nesting Flex Containers

**Introduction:**
A flex *item* can itself be a flex *container*. This is how complex layouts are built — you nest flexbox inside flexbox.

```css
/* Outer container: two panels side by side */
.lp-root {
  display: flex;           /* puts hero and sign-in panel side by side in a row */
}

/* Each panel is also a flex container to centre its own content */
.lp-hero {
  display: flex;
  align-items: center;     /* vertically centres the hero content within the panel */
  justify-content: center; /* horizontally centres the hero content within the panel */
}
```

`lp-root` and `lp-hero` are both flex containers. `lp-hero` is a flex *item* of `lp-root` at the same time — that is what nesting means.

---

### Part 2 Exercise — Build the Login Page Layout

**Objective:** Recreate the two-panel login page layout from the app using Flexbox.

**Step 1 — Create `index.html` and `styles.css`.**
Replace the body content in `index.html` with the two-panel login page structure.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Login</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="lp-root">

    <!-- Left: hero panel -->
    <div class="lp-hero">
      <div class="lp-hero-content">
        <div class="lp-logo">
          <span class="lp-logo-icon">🥝</span>
          <span class="lp-logo-text">kiwi</span>
        </div>
        <h1 class="lp-headline">Smart portfolio management for modern investors</h1>
        <p class="lp-subline">Track holdings, execute trades, and review your full transaction history in one place.</p>
        <ul class="lp-features">
          <li><span class="lp-check">✓</span> Real-time portfolio tracking</li>
          <li><span class="lp-check">✓</span> Buy and sell with instant updates</li>
          <li><span class="lp-check">✓</span> Full transaction history</li>
        </ul>
      </div>
    </div>

    <!-- Right: sign-in panel -->
    <div class="lp-panel">
      <div class="lp-card">
        <div class="lp-card-logo">🥝</div>
        <h2 class="lp-card-title">Welcome back</h2>
        <p class="lp-card-sub">Sign in to your account</p>
        <button class="lp-signin-btn">Sign in</button>
      </div>
    </div>

  </div>
</body>
</html>
```

Open in browser. Without CSS, everything stacks vertically. Now we add Flexbox to put the two panels side by side.

**Step 2 — Make `lp-root` a flex row.**

```css
*, *::before, *::after {
  box-sizing: border-box;   /* width includes padding and border */
}

body {
  margin: 0;                                         /* removes the browser's default body margin */
  font-family: system-ui, -apple-system, sans-serif; /* uses the device's native system font */
}

.lp-root {
  display: flex;        /* puts the hero and sign-in panel side by side */
  min-height: 100vh;    /* page fills the full viewport height */
}
```

Refresh. The two panels now sit side by side.

**Step 3 — Size the two panels.**

```css
.lp-hero {
  flex: 1 1 55%;   /* start at 55% of the page width, can grow or shrink */
}

.lp-panel {
  flex: 0 0 45%;   /* fixed at exactly 45% — does not grow or shrink */
}
```

Refresh. The split is now 55/45.

**Step 4 — Style the hero panel.**

```css
.lp-hero {
  flex: 1 1 55%;
  background: linear-gradient(135deg, #0b1120 0%, #0d2818 60%, #0a1f30 100%);  /* dark green-to-navy diagonal gradient */
  display: flex;
  align-items: center;      /* vertically centres the content block */
  justify-content: center;  /* horizontally centres the content block */
  padding: 3rem 4rem;       /* 48px top/bottom, 64px left/right — breathing room around the content */
}
```

**Step 5 — Style the hero text.**

```css
.lp-hero-content {
  max-width: 500px;   /* prevents the text from stretching too wide on large screens */
}

.lp-logo {
  display: flex;          /* puts icon and text in a row */
  align-items: center;    /* vertically aligns icon with text */
  gap: 0.5rem;            /* 8px between the emoji and the logo text */
  margin-bottom: 2.5rem;  /* 40px below the logo before the headline */
}

.lp-logo-icon {
  font-size: 2rem;   /* 32px emoji */
}

.lp-logo-text {
  font-size: 1.5rem;         /* 24px — prominent brand name */
  font-weight: 700;          /* bold */
  color: #4ade80;            /* green — the app's brand accent colour */
  letter-spacing: 0.05em;    /* slightly spaced letters */
  text-transform: lowercase; /* forces "kiwi" lowercase regardless of how it is typed */
}

.lp-headline {
  font-size: 2.5rem;      /* 40px — large, attention-grabbing headline */
  font-weight: 800;       /* extra bold */
  line-height: 1.15;      /* tight line spacing for large display text */
  color: #f1f5f9;         /* near-white — readable on dark background */
  margin-bottom: 1.25rem; /* 20px below the headline */
}

.lp-subline {
  font-size: 1rem;      /* body text size */
  color: #94a3b8;       /* light grey — secondary text on dark background */
  line-height: 1.7;     /* generous line spacing for readability */
  margin-bottom: 2rem;  /* 32px below the subline before the feature list */
}
```

**Step 6 — Style the features list.**

```css
.lp-features {
  list-style: none;       /* removes the default bullet points */
  padding: 0;             /* removes the default left indent on <ul> */
  margin: 0;              /* removes default margin */
  display: flex;
  flex-direction: column; /* stacks list items vertically */
  gap: 0.75rem;           /* 12px between each feature item */
}

.lp-features li {
  color: #cbd5e1;      /* light grey — secondary text colour */
  font-size: 0.95rem;  /* slightly smaller than body text */
  display: flex;
  align-items: center; /* vertically aligns the checkmark with the text */
  gap: 0.6rem;         /* 10px between checkmark and feature text */
}

.lp-check {
  color: #4ade80;    /* green checkmark — matches the brand accent colour */
  font-weight: 700;  /* bold so the checkmark is visually prominent */
}
```

**Step 7 — Style the right sign-in panel.**

```css
.lp-panel {
  flex: 0 0 45%;
  background: #f8fafc;      /* very light grey — slightly off-white background */
  display: flex;
  align-items: center;      /* vertically centres the sign-in card */
  justify-content: center;  /* horizontally centres the sign-in card */
  padding: 3rem 2rem;       /* 48px top/bottom, 32px left/right */
}
```

**Step 8 — Style the sign-in card.**

```css
.lp-card {
  width: 100%;           /* fills the panel width up to max-width */
  max-width: 380px;      /* caps width at 380px so it does not stretch on large panels */
  background: #ffffff;   /* white card on the light grey panel */
  border-radius: 20px;   /* generously rounded corners */
  padding: 2.5rem 2rem;  /* 40px top/bottom, 32px left/right */
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07),    /* close shadow — subtle lift */
              0 20px 60px -10px rgba(0,0,0,0.12);  /* distant shadow — depth */
  text-align: center;    /* centres all text in the card */
}

.lp-card-logo {
  font-size: 2.5rem;    /* 40px emoji */
  margin-bottom: 1rem;  /* 16px below the logo emoji */
}

.lp-card-title {
  font-size: 1.6rem;     /* 25.6px — heading size */
  font-weight: 700;      /* bold */
  color: #0f172a;        /* near-black */
  margin-bottom: 0.4rem; /* small gap between title and subtitle */
}

.lp-card-sub {
  color: #64748b;         /* medium grey — secondary text */
  font-size: 0.9rem;      /* smaller than heading */
  margin-bottom: 1.75rem; /* 28px space before the sign-in button */
}

.lp-signin-btn {
  width: 100%;                                           /* button stretches to fill the card */
  padding: 0.8rem 1.5rem;                                /* 13px top/bottom, 24px left/right */
  background: linear-gradient(135deg, #22c55e, #16a34a); /* green gradient — signals positive action */
  color: #ffffff;                                        /* white text on green */
  border: none;                                          /* removes default button border */
  border-radius: 10px;                                   /* rounded corners */
  font-size: 1rem;                                       /* body text size */
  font-weight: 600;                                      /* semi-bold label */
  cursor: pointer;                                       /* hand cursor on hover */
}
```

**Step 9 — Add the mobile media query.**
On screens 768px wide or narrower, stack the panels vertically.

```css
@media (max-width: 768px) {
  .lp-root {
    flex-direction: column;   /* changes the side-by-side row layout to a vertical stack */
  }

  .lp-hero {
    flex: none;          /* removes the flex-basis sizing — panel takes its natural height */
    padding: 3rem 2rem;  /* reduces horizontal padding on narrow screens */
  }

  .lp-panel {
    flex: none;           /* removes the flex-basis sizing */
    padding: 2rem 1.5rem; /* further reduces padding on very narrow screens */
  }
}
```

Resize the browser to narrow it. The panels stack vertically when the screen is small.

**Final result:** A full-screen two-panel login page matching the app's LoginPage, with responsive stacking on mobile.

---

## Part 3 — Responsive Design + Bootstrap

### 1. What is Responsive Design?

**Introduction:**
A responsive website adapts its layout to the screen size of the device. On a wide desktop screen you might show three columns side by side; on a phone those same three columns should stack vertically because there is not enough horizontal space.

Responsive design is not optional — more than 50% of web traffic is on mobile. You design for the smallest screen first (*mobile-first*) and then progressively enhance for larger screens.

---

### 2. Media Queries

**Introduction:**
A media query is a CSS rule that only applies when a condition about the screen is true — most commonly when the screen width is above or below a breakpoint.

```css
/* This rule applies ONLY when the screen is 768px wide or narrower */
@media (max-width: 768px) {
  .lp-root {
    flex-direction: column;   /* stacks panels vertically on mobile instead of side by side */
  }
}
```

Point to `src/components/LoginPage.css` lines 193–208 — the app uses a single media query to collapse the two-panel login layout into a single column on mobile.

**Common breakpoints:**

```css
@media (max-width: 576px)  { /* mobile */ }
@media (max-width: 768px)  { /* tablet */ }
@media (max-width: 992px)  { /* small desktop */ }
@media (max-width: 1200px) { /* large desktop */ }
```

**Example — hide the hero panel on very small screens:**

```css
.lp-hero {
  display: flex;   /* hero panel is visible by default */
}

@media (max-width: 576px) {
  .lp-hero {
    display: none;   /* completely hides the hero panel on phones — only shows the sign-in card */
  }
}
```

---

### 3. Introduction to Bootstrap

**Introduction:**
Bootstrap is a CSS framework — a large pre-written stylesheet that gives you ready-made, professionally designed styles and components. Instead of writing every style yourself, you apply Bootstrap *utility classes* to your HTML.

The KiwiUI app uses Bootstrap for almost all of its layout and components. Learning it will dramatically speed up your ability to build polished UIs.

**Adding Bootstrap via CDN** (no install needed for plain HTML):

```html
<head>
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
  >
</head>
```

---

### 4. The Bootstrap Grid System

**Introduction:**
Bootstrap's grid divides the page into 12 equal-width columns. You tell each element how many of those 12 columns it should occupy. Under the hood it uses exactly the flex-wrap technique from Part 2, Section 7.

**Three required layers:**

- `.container` — centres and constrains the content, adds horizontal padding
- `.row` — a flex row with `flex-wrap: wrap`; its children are columns
- `.col-*` — a column; `*` is how many of the 12 columns it takes up

```html
<div class="container">
  <div class="row">
    <div class="col-6">Left half</div>
    <div class="col-6">Right half</div>
  </div>
</div>
```

12 ÷ 6 = 2, so each column takes up half the width.

**Common column widths:**

```html
<div class="col-12">Full width (1 column)</div>
<div class="col-6">Half width (2 per row)</div>
<div class="col-4">One third (3 per row)</div>
<div class="col-3">One quarter (4 per row)</div>
```

---

### 5. Responsive Breakpoints in the Grid

**Introduction:**
Bootstrap has built-in responsive prefixes that let you specify different column widths at different screen sizes.

| Prefix | Minimum width | Typical device |
|---|---|---|
| (none) | any | all screens |
| `sm` | 576px | large phone |
| `md` | 768px | tablet |
| `lg` | 992px | small desktop |
| `xl` | 1200px | large desktop |

Stack multiple classes on the same element:

```html
<!-- 1 column on mobile, 2 on tablet, 3 on desktop -->
<div class="col-12 col-md-6 col-lg-4">Portfolio Card</div>
```

This is exactly how the portfolio card grid is built in the app — look at `src/components/PortfolioList.jsx`.

**Full example:**

```html
<div class="container">
  <div class="row g-3">
    <div class="col-12 col-md-6 col-lg-4">
      <div class="card">Portfolio A</div>
    </div>
    <div class="col-12 col-md-6 col-lg-4">
      <div class="card">Portfolio B</div>
    </div>
    <div class="col-12 col-md-6 col-lg-4">
      <div class="card">Portfolio C</div>
    </div>
  </div>
</div>
```

---

### 6. Bootstrap Utility Classes

**Introduction:**
Bootstrap ships hundreds of single-purpose utility classes so you can apply common styles directly in HTML without writing any CSS.

**Spacing (margin and padding):**
Pattern: `{property}{side}-{size}` — property is `m`/`p`, side is `t`/`b`/`s`/`e`/`x`/`y`/(none), size is 0–5.

```html
<p class="mb-3">Paragraph with 1rem bottom margin</p>
<div class="p-4">Div with 1.5rem padding on all sides</div>
<h2 class="mt-0 mb-2">No top margin, small bottom margin</h2>
```

**Display and flexbox:**

```html
<div class="d-flex justify-content-between align-items-center">
  <span>Left</span>
  <span>Right</span>
</div>
```

**Text:**

```html
<p class="text-center">Centred text</p>
<p class="fw-bold">Bold text</p>
<p class="text-muted">Grey muted text</p>
```

**Buttons:**

```html
<button class="btn btn-success">Buy</button>             <!-- green -->
<button class="btn btn-danger">Sell</button>              <!-- red -->
<button class="btn btn-outline-secondary">Cancel</button>
```

---

### Part 3 Exercise — Responsive Portfolio Dashboard with Bootstrap

**Objective:** Build the portfolio list page using only Bootstrap classes — no custom CSS file needed.

**Step 1 — Create `index.html` with the Bootstrap CDN link.**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kiwi Portfolios</title>
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
  >
</head>
<body>

</body>
</html>
```

The `<meta name="viewport">` tag is required for Bootstrap's responsive classes to work on mobile. Open in browser — blank page for now.

**Step 2 — Add the navbar.**

```html
<nav class="navbar navbar-light bg-white border-bottom px-4">
  <span class="navbar-brand fw-bold">🥝 kiwi</span>
  <a href="#" class="nav-link text-muted">Log out</a>
</nav>
```

Refresh. A white navbar appears with the brand on the left and "Log out" on the right.

**Step 3 — Add the page heading and "New Portfolio" button.**

```html
<div class="container mt-4">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">My Portfolios</h4>
    <button class="btn btn-success btn-sm">+ New Portfolio</button>
  </div>
</div>
```

**Step 4 — Add the responsive card grid.**
Each column gets `col-12 col-md-6 col-lg-4`: full width on mobile, half on tablet, one-third on desktop.

```html
  <div class="row g-3">

    <div class="col-12 col-md-6 col-lg-4">
      <div class="card h-100 border-success">
        <div class="card-body">
          <h5 class="card-title">Tech Growth Portfolio</h5>
          <p class="card-text text-muted">A diversified portfolio focused on technology sector growth stocks.</p>
        </div>
        <div class="card-footer bg-white">
          <button class="btn btn-outline-success btn-sm">View Holdings</button>
        </div>
      </div>
    </div>

    <div class="col-12 col-md-6 col-lg-4">
      <div class="card h-100">
        <div class="card-body">
          <h5 class="card-title">Dividend Income Portfolio</h5>
          <p class="card-text text-muted">High-yield dividend stocks for steady passive income.</p>
        </div>
        <div class="card-footer bg-white">
          <button class="btn btn-outline-success btn-sm">View Holdings</button>
        </div>
      </div>
    </div>

    <div class="col-12 col-md-6 col-lg-4">
      <div class="card h-100">
        <div class="card-body">
          <h5 class="card-title">Index Fund Portfolio</h5>
          <p class="card-text text-muted">Low-cost index funds tracking the S&P 500 and global markets.</p>
        </div>
        <div class="card-footer bg-white">
          <button class="btn btn-outline-success btn-sm">View Holdings</button>
        </div>
      </div>
    </div>

  </div>
```

Refresh. Three cards appear. Narrow the browser: tablet shows 2-up, mobile shows 1-up.

**Step 5 — Observe what Bootstrap did for free.**


- `g-3` → gap between cards
- `h-100` → all cards stretch to the same height in a row
- `card`, `card-body`, `card-footer` → consistent padding and borders
- `btn btn-success` → green button with hover state
- `text-muted` → grey description text
- `border-success` → green border on the selected card
- `d-flex justify-content-between align-items-center` → the flex navbar layout from Part 2

**Final HTML (complete file):**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kiwi Portfolios</title>
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
  >
</head>
<body class="bg-light">

  <nav class="navbar navbar-light bg-white border-bottom px-4">
    <span class="navbar-brand fw-bold">🥝 kiwi</span>
    <a href="#" class="nav-link text-muted">Log out</a>
  </nav>

  <div class="container mt-4">

    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="mb-0">My Portfolios</h4>
      <button class="btn btn-success btn-sm">+ New Portfolio</button>
    </div>

    <div class="row g-3">

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card h-100 border-success">
          <div class="card-body">
            <h5 class="card-title">Tech Growth Portfolio</h5>
            <p class="card-text text-muted">A diversified portfolio focused on technology sector growth stocks.</p>
          </div>
          <div class="card-footer bg-white">
            <button class="btn btn-outline-success btn-sm">View Holdings</button>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Dividend Income Portfolio</h5>
            <p class="card-text text-muted">High-yield dividend stocks for steady passive income.</p>
          </div>
          <div class="card-footer bg-white">
            <button class="btn btn-outline-success btn-sm">View Holdings</button>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Index Fund Portfolio</h5>
            <p class="card-text text-muted">Low-cost index funds tracking the S&P 500 and global markets.</p>
          </div>
          <div class="card-footer bg-white">
            <button class="btn btn-outline-success btn-sm">View Holdings</button>
          </div>
        </div>
      </div>

    </div>
  </div>

</body>
</html>
```

**Final result:** A responsive portfolio dashboard — navbar, heading row, and three cards that reflow from 1 to 2 to 3 columns as the screen widens — matching the app's portfolio list view, built with zero custom CSS.

---
