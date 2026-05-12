# ReactJS

## Background

### 1. The Document Object Model (DOM)

**Introduction:**
When a browser loads an HTML file, it does not just display the text — it builds a live, in-memory tree structure from the markup called the **Document Object Model**, or **DOM**. Every element in your HTML (`<div>`, `<p>`, `<button>`) becomes a *node* in this tree, and JavaScript can read and modify that tree at any time. When you change a node, the browser immediately reflects the change on screen — no page reload needed.

Think of it this way:

```text
HTML file (static text)  →  browser parses it  →  DOM (live tree in memory)
                                                        ↑
                                              JavaScript reads and writes here
```

The DOM is the bridge between your HTML and your JavaScript. Everything interactive you have ever seen on a web page — menus that open, lists that update, forms that validate — works by JavaScript manipulating the DOM.

---

**Querying elements:**

To do anything with the DOM you first have to find the element you want. The two most common methods are:

```javascript
// Find one element by its id attribute
const heading = document.getElementById('main-title')

// Find the first element that matches a CSS selector
const button = document.querySelector('.submit-btn')

// Find ALL elements that match a CSS selector (returns a NodeList, like an array)
const rows = document.querySelectorAll('tr.holding-row')
```

Once you have a reference to an element you can read its current value or write a new one.

---

**Reading and writing content:**

```javascript
// Read the current text inside an element
console.log(heading.textContent)   // e.g. "My Portfolio"

// Overwrite the text
heading.textContent = 'Growth Fund'

// Read and write the full HTML inside an element
const list = document.getElementById('portfolio-list')
console.log(list.innerHTML)        // the current HTML string
list.innerHTML = '<li>Growth Fund</li><li>Income Fund</li>'
```

`textContent` is safe and fast when you only deal with plain text. `innerHTML` lets you inject HTML but must never be built from untrusted user input (security risk).

---

**Changing styles and attributes:**

```javascript
const card = document.querySelector('.portfolio-card')

// CSS classes
card.classList.add('selected')
card.classList.remove('selected')
card.classList.toggle('selected')   // add if absent, remove if present

// Inline style
card.style.backgroundColor = 'lightyellow'

// Arbitrary attributes
const img = document.querySelector('img')
img.setAttribute('alt', 'Portfolio logo')
console.log(img.getAttribute('src'))
```

---

**Registering event listeners:**

An *event listener* is a function you tell the browser to call whenever something happens — a click, a key press, a form submission.

```javascript
const btn = document.getElementById('buy-btn')

btn.addEventListener('click', function(event) {
  console.log('Buy button clicked!')
  console.log(event.target)   // the element that was clicked
})
```

Arrow functions work just as well:

```javascript
btn.addEventListener('click', (event) => {
  console.log('clicked')
})
```

Common event names: `'click'`, `'input'`, `'change'`, `'submit'`, `'keydown'`.

---

**Putting it together — a worked example:**

Imagine a minimal portfolio tracker: a text input, a button, and a list. Every time the user types a name and clicks Add, a new item appears in the list.

```html
<!-- index.html -->
<input id="portfolio-name" type="text" placeholder="Portfolio name" />
<button id="add-btn">Add</button>
<ul id="portfolio-list"></ul>
```

```javascript
// main.js
const input = document.getElementById('portfolio-name')
const addBtn = document.getElementById('add-btn')
const list = document.getElementById('portfolio-list')

// Keep the data in a plain JS array
const portfolios = []

function renderList() {
  // Wipe the current list and rebuild it from the array
  list.innerHTML = ''
  portfolios.forEach(function(name) {
    const item = document.createElement('li')
    item.textContent = name
    list.appendChild(item)
  })
}

addBtn.addEventListener('click', function() {
  const name = input.value.trim()
  if (name === '') return            // ignore empty input
  portfolios.push(name)             // update the data
  renderList()                      // re-draw the DOM
  input.value = ''                  // clear the input
})
```

This works. But notice what `renderList` does every time it is called: it **deletes every DOM node and rebuilds the whole list from scratch**. For two or three items that is fine. For a large table with holdings, prices, and interactive buttons, wiping and rebuilding everything becomes slow and loses state (scroll position, focused inputs, etc.). You also have to remember to call `renderList()` every single place where `portfolios` might change — and you have to keep expanding that function as the UI grows.

This is the problem React is designed to solve, and we will come back to it in the next section.

---

### 2. Setting Up Your Development Environment

**Introduction:**
The sessions so far only needed a browser and a text editor — vanilla HTML, CSS, and JavaScript run directly without any tooling. React is different. React code uses JSX (HTML-like syntax inside `.jsx` files) and ES module imports that browsers cannot execute directly. A *build tool* compiles your source files into plain JavaScript the browser understands. This project uses **Vite**.

Vite runs on **Node.js**, so you need to install Node and its package manager **npm** before you can scaffold or run a React project.

---

#### Step 1 — Install Node.js and npm

Node.js and npm are installed together from the same installer.

1. Go to [https://nodejs.org](https://nodejs.org) and download the **LTS** (Long-Term Support) release — this is the stable version recommended for most users.
2. Run the installer and follow the prompts. Accept all defaults.
3. When it finishes, open a new terminal window and verify both tools are available:

```bash
node --version    # should print something like v20.x.x
npm --version     # should print something like 10.x.x
```

If you see version numbers, Node and npm are installed correctly. If the command is not found, close and reopen your terminal, then try again.

> **What is npm?** npm (Node Package Manager) is the tool you use to install JavaScript libraries and run project scripts. When you run `npm install`, npm reads `package.json`, downloads all the listed libraries into a local `node_modules/` folder, and makes them available to your project. `node_modules/` is never committed to git — it can always be regenerated from `package.json`.

---

#### Step 2 — Verify your editor is ready

This project is built with **Visual Studio Code**. If you do not have it installed, download it from [https://code.visualstudio.com](https://code.visualstudio.com).

Recommended extensions for this project (install from the Extensions panel, `Ctrl+Shift+X` / `Cmd+Shift+X`):

| Extension | Why |
| --- | --- |
| **ES7+ React/Redux/React-Native snippets** | Shorthand snippets for React boilerplate |
| **Prettier - Code formatter** | Auto-formats JSX/JS on save |

---

#### Step 3 — Understand what npm does before you run it

Before running any npm command for the first time, glance at `package.json` in the project root. It lists:

- `dependencies` — libraries your app needs at runtime (React, React-Bootstrap, etc.)
- `devDependencies` — tools only needed during development (Vite, the React compiler plugin, etc.)
- `scripts` — shorthand commands (`npm run dev`, `npm run build`, etc.)

When you clone a project or scaffold a new one, the `node_modules/` folder does not exist yet. Running `npm install` downloads everything listed in `package.json` and creates `node_modules/`. You only need to do this once per machine (or after `package.json` changes).

---

With Node, npm, and VS Code in place, you are ready to scaffold and run a React project. The next section covers exactly that.

---

## Part 1 — Components and JSX

### 1. Why React? The Problem with Vanilla JavaScript

**Introduction:**
You have already built interactive web pages using vanilla JavaScript: you selected DOM elements with `document.getElementById`, updated their `innerHTML`, and wired up event listeners with `addEventListener`. That approach works fine for small, simple pages. But as an application grows — more data, more interactions, more pieces of UI that depend on the same data — it breaks down fast.

Consider what it would take to build the portfolio dashboard you have seen in this project using only vanilla JS. Every time the user selects a portfolio, you would have to:

1. Clear the holdings table manually
2. Loop through the new holdings and build HTML strings
3. Inject those strings into the DOM
4. Update any other part of the page that references the same portfolio

Now imagine the user also edits the portfolio name. You have to hunt down every place that name appears on the page and update each one individually. The more features you add, the harder it becomes to keep the DOM in sync with your data.

React solves this with a different mental model:

> **Instead of telling the browser how to update the DOM, you describe what the UI should look like for a given set of data — and React figures out the DOM changes.**

This shift is from *imperative* (step-by-step instructions) to *declarative* (a description of the desired result):

```javascript
// Vanilla JS — imperative: you manage the DOM yourself
const list = document.getElementById('portfolio-list')
list.innerHTML = ''
portfolios.forEach(p => {
  const card = document.createElement('div')
  card.textContent = p.name
  list.appendChild(card)
})
```

```jsx
// React — declarative: you describe what you want
function PortfolioList({ portfolios }) {
  return (
    <div>
      {portfolios.map(p => <div key={p.id}>{p.name}</div>)}
    </div>
  )
}
```

When the `portfolios` array changes, React automatically re-renders the component and updates only the parts of the DOM that changed. You never touch `document.getElementById` again.

---

### 2. Project Setup with Vite

**Introduction:**
Modern React code uses JSX (HTML-like syntax inside JavaScript files) and ES modules, which browsers cannot run directly. A build tool compiles your source code into plain JavaScript the browser understands. This project uses **Vite**.

**Scaffolding a new project:**

```bash
npm create vite@latest my-react-app
```

When prompted:

- **Framework:** React
- **Variant:** JavaScript (not TypeScript)

Then install dependencies and start the dev server:

```bash
cd my-react-app
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` by default. Every time you save a file, the browser updates instantly without a full page reload — this is called *Hot Module Replacement*.

**Project structure after scaffolding:**

```text
my-react-app/
├── index.html          ← the single HTML file — never edit this directly
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx        ← entry point — mounts the React app into index.html
    ├── App.jsx         ← root component — the top of your component tree
    ├── App.css
    └── index.css
```

**The entry point — `src/main.jsx`:**

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

`createRoot` finds the `<div id="root">` in `index.html` and hands it to React. From this point on, React owns everything inside that div. `StrictMode` is a development helper — it runs your components twice to help catch bugs, and you can ignore it for now.

**The `.jsx` extension:**
Any file that contains JSX must use the `.jsx` extension (not `.js`). This tells Vite to run the JSX compiler on it. Component files, the entry point, and `App.jsx` all use `.jsx`.

---

### 3. JSX — Writing HTML in JavaScript

**Introduction:**
JSX is a syntax extension for JavaScript that lets you write markup that looks like HTML directly inside a `.jsx` file. It is not a template language — it is compiled directly into JavaScript function calls.

```jsx
// What you write
const element = <h1 className="title">Hello, world</h1>

// What it compiles to (you never write this)
const element = React.createElement('h1', { className: 'title' }, 'Hello, world')
```

You write JSX; the compiler handles the rest.

**Embedding JavaScript expressions:**

Put any JavaScript expression inside `{ }` to include it in the output. An expression is anything that produces a value: a variable, arithmetic, a function call, a ternary, a method call.

```jsx
const portfolioName = 'Growth Fund'
const count = 3

// Variables
<h5>{portfolioName}</h5>

// Arithmetic
<p>You have {count} portfolio{count !== 1 ? 's' : ''}.</p>

// Method calls
<td className="fw-bold">{ticker.toUpperCase()}</td>
```

Statements (`if`, `for`, `while`) cannot go inside `{ }`. Use expressions instead — ternaries for conditionals, `.map()` for loops.

**Key differences from HTML:**

| HTML attribute | JSX equivalent | Why |
| --- | --- | --- |
| `class="..."` | `className="..."` | `class` is a reserved word in JavaScript |
| `for="..."` | `htmlFor="..."` | `for` is a reserved word in JavaScript |
| `<br>` | `<br />` | All tags must be closed or self-closing |
| `<img src="...">` | `<img src="..." />` | Same — all void elements need `/>` |
| `onclick="fn()"` | `onClick={fn}` | camelCase, and you pass a function reference |
| `style="color: red"` | `style={{ color: 'red' }}` | An object literal, not a string |

```jsx
// HTML
<div class="card" onclick="handleClick()">
  <img src="logo.png">
</div>

// JSX
<div className="card" onClick={handleClick}>
  <img src="logo.png" />
</div>
```

**A single root element:**

JSX must always return a single root element. If you need to return two sibling elements without adding an extra wrapper `<div>`, use a *Fragment*:

```jsx
// Error — two root elements
return (
  <h5>Growth Fund</h5>
  <p>Long-term growth picks</p>
)

// Correct — wrapped in a div
return (
  <div>
    <h5>Growth Fund</h5>
    <p>Long-term growth picks</p>
  </div>
)

// Correct — Fragment (renders no extra DOM element)
return (
  <>
    <h5>Growth Fund</h5>
    <p>Long-term growth picks</p>
  </>
)
```

---

### 4. Your First Component

**Introduction:**
A React component is a JavaScript function that returns JSX. That is all it is. The two rules:

1. The function name must start with a capital letter — React uses this to distinguish components from plain HTML tags.
2. The function must return JSX (or `null` if it renders nothing).

**A simple component:**

```jsx
function PortfolioCard() {
  return (
    <div className="card p-3">
      <h5>Growth Fund</h5>
      <p className="text-muted">Long-term growth picks</p>
    </div>
  )
}
```

**Using a component:**

Once defined, you use a component like an HTML tag — with a capital letter to signal it is a component, not a native HTML element:

```jsx
function App() {
  return (
    <div>
      <PortfolioCard />
      <PortfolioCard />
    </div>
  )
}
```

This renders two identical cards. To make components useful, you need to pass different data into each one — that is what props are for.

**Exporting and importing:**

Each component lives in its own file. Export the function at the bottom, import it where it is used:

```jsx
// src/components/PortfolioCard.jsx
function PortfolioCard() {
  return (
    <div className="card p-3">
      <h5>Growth Fund</h5>
    </div>
  )
}

export default PortfolioCard
```

```jsx
// src/App.jsx
import PortfolioCard from './components/PortfolioCard'

function App() {
  return <PortfolioCard />
}
```

**BEST PRACTICE**: one component per file, named export at the bottom, stored under `src/components/`.

---

### 5. Props — Passing Data into Components

**Introduction:**
A component that always renders the same thing is not very useful. Props (short for *properties*) are how you pass data into a component from its parent. They make components reusable.

**Passing props:**

You pass props like HTML attributes:

```jsx
<PortfolioCard name="Growth Fund" description="Long-term growth picks" />
<PortfolioCard name="Income Fund" description="Dividend-focused stocks" />
```

**Receiving props:**

The component receives all props as a single object. The idiomatic way is to destructure them directly in the function signature:

```jsx
function PortfolioCard({ name, description }) {
  return (
    <div className="card p-3">
      <h5>{name}</h5>
      <p className="text-muted">{description}</p>
    </div>
  )
}
```

Both cards above now render different content. The same component, two different outputs — this is reusability.

**Props are read-only:**

A component must never modify its props. Data flows one way: from parent to child. If the child needs to communicate something back to the parent (e.g., a button was clicked), it does so via a callback function — which is itself passed as a prop (covered in Part 3).

**Passing objects and other types:**

Props can be any JavaScript value: strings, numbers, booleans, arrays, objects, and functions.

```jsx
// Passing an object
<PortfolioCard portfolio={{ id: 1, name: 'Growth Fund', description: 'Long-term' }} />

// Receiving and using it
function PortfolioCard({ portfolio }) {
  return (
    <div>
      <h5>{portfolio.name}</h5>
      <p>{portfolio.description}</p>
    </div>
  )
}
```

```jsx
// Passing a function as a prop (a callback — covered in depth in Part 3)
<PortfolioCard portfolio={portfolio} onSelect={handleSelectPortfolio} />
```

---

### 6. Rendering Lists

**Introduction:**
Any time you have an array of data and want to render a UI element for each item, you use `.map()`. This is the most fundamental data rendering pattern in React.

**The basic pattern:**

```jsx
const portfolios = [
  { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' },
  { id: 2, name: 'Income Fund', description: 'Dividend-focused stocks' },
]

function PortfolioList() {
  return (
    <div>
      {portfolios.map(portfolio => (
        <div key={portfolio.id}>
          <h5>{portfolio.name}</h5>
          <p>{portfolio.description}</p>
        </div>
      ))}
    </div>
  )
}
```

The `.map()` call returns an array of JSX elements. React knows how to render an array of elements — it just outputs them one after another.

**The `key` prop:**

Every element in a rendered list must have a `key` prop. React uses the key to track which items have been added, removed, or reordered between renders — without it, React cannot update the list efficiently and will warn you.

Rules for keys:

- Must be unique within the list (not globally)
- Must be stable — do not use the array index if the order can change
- Use a unique identifier from your data, like `id`

```jsx
// Correct — uses a stable unique id from the data
portfolios.map(p => <PortfolioCard key={p.id} portfolio={p} />)

// Avoid — array index is unstable if the list can reorder or filter
portfolios.map((p, index) => <PortfolioCard key={index} portfolio={p} />)
```

**Wrapping in a container:**

Often the `.map()` is placed inside a container element. The container renders once; the mapped elements fill it:

```jsx
<Row xs={1} md={2} lg={3} className="g-3">
  {portfolios.map(portfolio => (
    <Col key={portfolio.id}>
      <PortfolioCard portfolio={portfolio} />
    </Col>
  ))}
</Row>
```

---

### 7. Conditional Rendering

**Introduction:**
React lets you include or exclude parts of the UI based on conditions using ordinary JavaScript expressions inside JSX.

#### The `&&` operator — render if truthy

If the condition is `true`, the element on the right is rendered. If it is `false` (or `null`, `0`, `undefined`), nothing is rendered.

```jsx
// Only show the description paragraph if a description exists
{portfolio.description && (
  <p className="text-muted">{portfolio.description}</p>
)}
```

```jsx
// Show an empty-state message only when there are no portfolios
{portfolios.length === 0 && (
  <p className="text-muted">No portfolios yet. Create one to get started.</p>
)}
```

**Pitfall:** If the condition is the number `0`, React will render `0` as text — it is truthy enough to evaluate the right side but falsy enough to... well, not quite. Be careful:

```jsx
// Bug — renders "0" if the array is empty
{portfolios.length && <p>...</p>}

// Correct — explicit boolean check
{portfolios.length > 0 && <p>...</p>}
// or
{portfolios.length === 0 && <p>No portfolios.</p>}
```

#### The ternary `? :` — render one of two things

```jsx
// Show a table if there are holdings, or a message if there are none
{holdings.length === 0 ? (
  <p className="text-muted">No holdings yet. Use the Trade tab to buy securities.</p>
) : (
  <table>...</table>
)}
```

#### Early return — return different JSX entirely

When a component's entire output changes based on a condition (not just a piece of it), return early from the function:

```jsx
function HoldingsPanel({ portfolio, holdings, onGoTrade }) {
  // No portfolio selected — return a completely different view
  if (!portfolio) {
    return (
      <Alert variant="info">
        Select a portfolio from the <strong>Portfolios</strong> tab to view its holdings.
      </Alert>
    )
  }

  // Portfolio is selected — return the full holdings view
  return (
    <div>
      <h5>{portfolio.name}</h5>
      ...
    </div>
  )
}
```

---

**Objective:** Scaffold a fresh Vite React project and build two components: a `PortfolioCard` that displays a single portfolio, and a `PortfolioList` that renders a list of them from static data.

---

**Step 1 — Scaffold the project.**

```bash
npm create vite@latest kiwi-lab
# Choose: React → JavaScript
cd kiwi-lab
npm install
npm run dev
```

Open `http://localhost:5173` and confirm the default Vite + React page loads. Leave the dev server running.

---

**Step 2 — Clean up the starter files.**

Open `src/App.jsx` and replace its entire contents with a minimal shell:

```jsx
function App() {
  return <div className="container mt-4">App</div>
}

export default App
```

Also open `src/App.css` and delete everything inside it (keep the file, just empty it). Save both files and confirm the browser now shows just "App".

---

**Step 3 — Create `src/components/PortfolioCard.jsx`.**

Create a `components` folder inside `src`, then create `PortfolioCard.jsx` inside it. The component should accept a `portfolio` object as a prop and render its name and description.

```jsx
function PortfolioCard({ portfolio }) {
  return (
    <div style={{ border: '1px solid #dee2e6', borderRadius: 8, padding: 16, marginBottom: 12 }}>
      <h5 style={{ margin: '0 0 4px' }}>{portfolio.name}</h5>
      <p style={{ margin: 0, color: '#6c757d' }}>
        {portfolio.description || 'No description.'}
      </p>
    </div>
  )
}

export default PortfolioCard
```

---

**Step 4 — Use `PortfolioCard` in `App.jsx` with a single hardcoded portfolio.**

Update `App.jsx` to import and render `PortfolioCard` with a hardcoded portfolio object:

```jsx
import PortfolioCard from './components/PortfolioCard'

function App() {
  const portfolio = { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' }

  return (
    <div className="container mt-4">
      <PortfolioCard portfolio={portfolio} />
    </div>
  )
}

export default App
```

Verify a card appears in the browser with the name and description.

---

**Step 5 — Create `src/components/PortfolioList.jsx`.**

Create `PortfolioList.jsx`. This component receives an array of portfolio objects as the `portfolios` prop and renders a `PortfolioCard` for each one using `.map()`.

```jsx
import PortfolioCard from './PortfolioCard'

function PortfolioList({ portfolios }) {
  return (
    <div>
      <h4>Your Portfolios</h4>
      {portfolios.length === 0 && (
        <p style={{ color: '#6c757d' }}>No portfolios yet. Create one to get started.</p>
      )}
      {portfolios.map(portfolio => (
        <PortfolioCard key={portfolio.id} portfolio={portfolio} />
      ))}
    </div>
  )
}

export default PortfolioList
```

---

**Step 6 — Wire `PortfolioList` into `App.jsx` with a static array.**

Update `App.jsx` to define a static array of portfolios and pass it to `PortfolioList`:

```jsx
import PortfolioList from './components/PortfolioList'

const portfolios = [
  { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' },
  { id: 2, name: 'Income Fund', description: 'Dividend-focused stocks' },
  { id: 3, name: 'Tech Fund', description: 'High-growth tech stocks' },
]

function App() {
  return (
    <div className="container mt-4">
      <PortfolioList portfolios={portfolios} />
    </div>
  )
}

export default App
```

Verify three cards appear in the browser.

---

**Step 7 — Test the empty-state.**

Temporarily change the `portfolios` array in `App.jsx` to an empty array:

```jsx
const portfolios = []
```

Verify the "No portfolios yet" message appears. Change it back to the three portfolios.

---

**Step 8 — Add conditional rendering for the description.**

Update `PortfolioCard` to only show the description paragraph if a description is present. Use the `&&` operator:

```jsx
function PortfolioCard({ portfolio }) {
  return (
    <div style={{ border: '1px solid #dee2e6', borderRadius: 8, padding: 16, marginBottom: 12 }}>
      <h5 style={{ margin: '0 0 4px' }}>{portfolio.name}</h5>
      {portfolio.description && (
        <p style={{ margin: 0, color: '#6c757d' }}>{portfolio.description}</p>
      )}
    </div>
  )
}
```

Test it by adding a portfolio to the array with no `description` property (or an empty string) and confirming no paragraph renders for that card.

---

**Checkpoint:** By the end of Part 1 you should have:

- A working Vite React project running locally
- A `PortfolioCard` component that renders a portfolio's name and description from props
- A `PortfolioList` component that renders an array of portfolios using `.map()` and `key`
- A conditional empty-state message when the array is empty
- Conditional rendering of the description using `&&`

---

## Part 2 — State and Events

### 8. The Problem with Regular Variables

**Introduction:**
Before introducing state, it is worth understanding exactly why regular variables do not work for interactive UI.

A React component is a function. Every time React needs to update what is displayed on screen, it *calls the function again* — this is called a *re-render*. When the function runs again, every local variable inside it is reset from scratch.

```jsx
// This does NOT work
function Counter() {
  let count = 0   // resets to 0 every time the component re-renders

  function handleClick() {
    count = count + 1
    console.log(count)   // logs the right number — but the screen never updates
  }

  return <button onClick={handleClick}>Clicked {count} times</button>
}
```

Two things go wrong here:

1. Changing `count` does nothing — React has no idea the variable changed, so it never re-renders the component.
2. Even if React did re-render, `count` would reset to `0`.

React needs a mechanism to:

- Store a value that **persists** across re-renders
- **Trigger a re-render** when that value changes

That mechanism is `useState`.

---

### 9. `useState`

**Introduction:**
`useState` is a React *hook* — a special function that connects your component to React's internal systems. You call it at the top of your component, and it gives you a stored value plus a function to update it.

**Basic syntax:**

```jsx
import { useState } from 'react'

const [value, setValue] = useState(initialValue)
```

- `value` — the current stored value. Read this in your JSX.
- `setValue` — the setter function. Call this to update the value.
- `initialValue` — the value on the very first render. Can be any type: a string, number, boolean, array, object, or `null`.

The square brackets are array destructuring — `useState` returns a two-element array and you name both elements in one line.

**How re-rendering works:**

```jsx
function Counter() {
  const [count, setCount] = useState(0)

  function handleClick() {
    setCount(count + 1)   // 1. update the stored value
                          // 2. React schedules a re-render
                          // 3. the function runs again with count = 1
                          // 4. the DOM updates to show the new count
  }

  return <button onClick={handleClick}>Clicked {count} times</button>
}
```

When you call `setCount`, React stores the new value, calls your function again, and updates only the DOM nodes that changed.

**State with different types:**

```jsx
// Boolean state — toggling a modal open/closed
const [showCreateModal, setShowCreateModal] = useState(false)

// Null state — nothing selected yet
const [selectedPortfolioId, setSelectedPortfolioId] = useState(null)

// String state — controlled input value
const [ticker, setTicker] = useState('')

// Array state — a list of data
const [portfolios, setPortfolios] = useState([
  { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' },
])
```

**Important: never mutate state directly.**

React detects changes by checking whether the value you passed to the setter is a *different reference* from the old value. If you mutate an array or object in place, the reference stays the same and React does not see a change.

```jsx
// Wrong — mutating the array in place
portfolios.push({ id: 2, name: 'Income Fund' })
setPortfolios(portfolios)   // same reference — React ignores this

// Correct — create a new array with the spread operator
setPortfolios([...portfolios, { id: 2, name: 'Income Fund' }])
```

This is why the JS guide covered the spread operator — it is essential for updating React state correctly.

---

### 10. Event Handlers

**Introduction:**
React handles DOM events through props like `onClick`, `onChange`, and `onSubmit`. These are named in camelCase, and you pass them a *function reference* — not a function call.

**`onClick`:**

```jsx
function handleClick() {
  console.log('button clicked')
}

// Correct — pass the function reference
<button onClick={handleClick}>Click me</button>

// Wrong — calls the function immediately during render, not on click
<button onClick={handleClick()}>Click me</button>
```

When you need to pass arguments to the handler, wrap it in an arrow function:

```jsx
// Without arguments — reference is fine
<button onClick={handleSelectPortfolio}>Select</button>

// With arguments — wrap in an arrow function
<button onClick={() => onSelect(portfolio.id)}>Select</button>
```

The arrow function is created fresh on each render but only called when the button is actually clicked.

**`onChange` for inputs:**

Every keystroke in an input fires an `onChange` event. The event object `e` has a `target` property that refers to the DOM input element, and `e.target.value` is its current string value.

```jsx
function handleTickerChange(e) {
  setTicker(e.target.value)
}

<input onChange={handleTickerChange} />

// Inline arrow function — the most common pattern in this codebase
<input onChange={e => setTicker(e.target.value)} />
```

**`onSubmit` for forms:**

```jsx
function handleSubmit(e) {
  e.preventDefault()   // prevent the browser from reloading the page (default form behaviour)
  // run your logic here
}

<form onSubmit={handleSubmit}>
  ...
</form>
```

Always call `e.preventDefault()` in form submit handlers. Without it, the browser will submit the form as an HTTP request and reload the page.

---

### 11. Controlled Inputs

**Introduction:**
In plain HTML, the browser owns the state of an input — the value lives in the DOM and you read it with JavaScript when you need it. In React, you can flip this around: you store the input's value in state and tell the input to display that state value. This is called a *controlled input*, and it is the standard React pattern for forms.

**The pattern:**

```jsx
const [ticker, setTicker] = useState('')

<input
  type="text"
  value={ticker}               // React drives the input's displayed value
  onChange={e => setTicker(e.target.value)}   // every keystroke updates state
/>
```

The data flow is circular:

1. User types a character
2. `onChange` fires → `setTicker` is called with the new string
3. React re-renders → the `value` prop is set to the new string
4. The input displays the new string

This means React always knows exactly what is in the input. You can read `ticker` at any time without touching the DOM.

**Resetting after submission:**

Because the input value is state, clearing the form after a successful submit is just a state reset:

```jsx
function handleTrade(type) {
  // ... do the trade ...
  setTicker('')      // clears the ticker input
  setQuantity('')    // clears the quantity input
}
```

---

### 12. Multiple State Variables

**Introduction:**
A component can call `useState` as many times as it needs. Each call manages one independent piece of state. Separate state variables that change independently — do not bundle unrelated values into a single object.

The `TradePanel` component has four state variables:

```jsx
const [ticker, setTicker]     = useState('')    // controlled input
const [quantity, setQuantity] = useState('')    // controlled input
const [error, setError]       = useState('')    // validation error message
const [success, setSuccess]   = useState('')    // success feedback message
```

`ticker` and `quantity` are form field values. `error` and `success` are feedback messages that appear or disappear based on what happened when the form was submitted. They are independent — changing one does not affect the others.

**Using state to show and hide feedback:**

Empty string is falsy in JavaScript, which pairs nicely with the `&&` operator for conditional rendering:

```jsx
{error   && <div className="alert alert-danger">{error}</div>}
{success && <div className="alert alert-success">{success}</div>}
```

When `error` is `''`, nothing renders. When it is `'Please enter a ticker symbol.'`, the alert appears.

**Clearing one message when the other appears:**

When a new trade attempt starts, clear both messages first:

```jsx
function handleTrade(type) {
  setError('')     // clear any previous error
  setSuccess('')   // clear any previous success

  // ... validation and trade logic ...
}
```

---

### 13. Updating State Based on Previous State

**Introduction:**
When a new state value depends on the current state value, use the *functional update* form of the setter. Instead of passing the new value directly, you pass a function that receives the current value and returns the new one.

**Why this matters:**

React may batch multiple state updates together. If you read `count` directly and call `setCount` twice, both calls might see the same old `count`:

```jsx
// Potentially buggy — both reads may see the same stale count
setCount(count + 1)
setCount(count + 1)   // count is still the old value here
```

The functional form always receives the most up-to-date value:

```jsx
// Correct — each call receives the result of the previous one
setCount(prev => prev + 1)
setCount(prev => prev + 1)   // prev is the result of the line above
```

---

## Part 3 — Component Composition, useEffect, and React-Bootstrap

### 14. Lifting State Up

**Introduction:**
As you build more components, you will encounter a situation where two sibling components need to read or change the same piece of data. For example, when the user selects a portfolio in `PortfolioList`, the `HoldingsPanel` needs to know which portfolio was selected so it can show the right holdings.

`PortfolioList` and `HoldingsPanel` are siblings — neither is the parent of the other. They cannot share state directly. The solution is to move the state *up* to their common parent — the `Dashboard` — which then passes it down to both siblings as props.

This is the central architectural principle of the `Dashboard` component:

```
Dashboard (owns all state)
├── PortfolioList  (reads portfolios, selectedPortfolioId; signals onSelect)
├── HoldingsPanel  (reads portfolio, holdings; signals onGoTrade)
├── TradePanel     (reads portfolio, holdings; signals onBuy, onSell)
└── TransactionLog (reads transactions, portfolios)
```

All state — `portfolios`, `holdings`, `transactions`, `selectedPortfolioId`, `activeTab`, `showCreateModal` — lives in `Dashboard`. The child components are *stateless display components*: they receive everything they need as props and report user actions back to `Dashboard` via callback props.

**The pattern:**

1. Identify which state needs to be shared between siblings
2. Move that state to the closest common parent
3. Pass the state value down as props to the children that need to read it
4. Pass setter or handler functions down as props to the children that need to change it

---

### 15. Callback Props — Events Flow Upward

**Introduction:**
Data flows downward through props (parent → child). When a child needs to signal something to the parent — "the user clicked this portfolio", "the user submitted the form" — it calls a function that the parent passed down as a prop. These are called *callback props*.

**Defining the callback in the parent:**

```jsx
// In Dashboard
function handleSelectPortfolio(id) {
  setSelectedPortfolioId(id)
  setActiveTab('holdings')
}
```

**Passing it down as a prop:**

```jsx
<PortfolioList
  portfolios={portfolios}
  selectedPortfolioId={selectedPortfolioId}
  onSelect={handleSelectPortfolio}   // pass the function as a prop
/>
```

**Calling it from the child:**

```jsx
// In PortfolioList — it does not know what handleSelectPortfolio does.
// It just calls whatever function was passed as onSelect.
<Card onClick={() => onSelect(portfolio.id)}>
  ...
</Card>
```

The child calls `onSelect(portfolio.id)`. The parent's `handleSelectPortfolio` runs. State updates in the parent. Both `PortfolioList` (to highlight the selected card) and `HoldingsPanel` (to show the right holdings) re-render with the new state — even though neither of them owns the state.

**The naming convention:**

By convention, callback props are named with the `on` prefix — `onSelect`, `onCreate`, `onBuy`, `onSell`, `onClose`, `onGoTrade`. This signals to readers that the prop is a function to be called in response to an event.

---

### 16. Component Composition — The Dashboard Pattern

**Introduction:**
React's power is in composing simple, single-purpose components into complex UIs. Each component does one thing well: `PortfolioList` displays a grid of portfolio cards, `HoldingsPanel` shows a holdings table, `TradePanel` handles the trade form. `Dashboard` is the coordinator — it holds the shared state and wires the components together.

**Tab-based navigation:**

The app uses tabs to switch between views. The active tab is tracked as a string in state (`'portfolios'`, `'holdings'`, `'trade'`, `'transactions'`). When the user clicks a different tab, the `onSelect` or `onTabChange` callback updates `activeTab`, which re-renders the layout showing the new tab's content.

The key insight: tabs are just a controlled UI mechanism on top of state. There is no page navigation, no URL change, no browser history — just `activeTab` changing and React re-rendering.

**How Dashboard assembles its children:**

```jsx
// src/components/Dashboard.jsx (simplified)
function Dashboard() {
  const [portfolios, setPortfolios] = useState([...])
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null)
  const [activeTab, setActiveTab] = useState('portfolios')

  const selectedPortfolio = portfolios.find(p => p.id === selectedPortfolioId) || null

  return (
    <Tabs activeKey={activeTab} onSelect={setActiveTab}>
      <Tab eventKey="portfolios" title="Portfolios">
        <PortfolioList
          portfolios={portfolios}
          selectedPortfolioId={selectedPortfolioId}
          onSelect={id => { setSelectedPortfolioId(id); setActiveTab('holdings') }}
        />
      </Tab>
      <Tab eventKey="holdings" title="Holdings">
        <HoldingsPanel
          portfolio={selectedPortfolio}
          holdings={holdings.filter(h => h.portfolioId === selectedPortfolioId)}
        />
      </Tab>
    </Tabs>
  )
}
```

Notice that `selectedPortfolio` is derived from `portfolios` and `selectedPortfolioId` — it is not stored as its own piece of state. Any value that can be computed from existing state should be computed, not stored separately.

---

### 17. `useEffect` — Side Effects in React

**Introduction:**
A React component is meant to be a pure function: given the same props and state, it returns the same JSX. That purity makes React's re-rendering efficient and predictable.

But real applications need to do things that are *outside* this pure function model:

- Fetch data from an API
- Read or write browser storage (`localStorage`, `sessionStorage`)
- Set up a timer or interval
- Subscribe to external events
- Manually interact with the DOM

These are called *side effects* — operations that reach outside the component and interact with the world beyond it. React provides `useEffect` as the dedicated place to run them.

**Basic syntax:**

```jsx
import { useEffect } from 'react'

useEffect(() => {
  // side effect code here
}, [/* dependency array */])
```

`useEffect` takes two arguments:

1. A function containing the side effect code
2. A dependency array that controls *when* the effect runs

---

#### The dependency array

**Empty array `[]` — run once on mount:**

The effect runs once, after the component first appears in the DOM. It does not run again on subsequent re-renders. Use this for setup that only needs to happen once: initial data fetches, reading from storage, checking for an auth token.

```jsx
useEffect(() => {
  console.log('Component mounted — runs once')
}, [])
```

This is the pattern in `src/App.jsx` — the auth check only needs to run once when the app first loads.

**No array — run after every render:**

Without a dependency array, the effect runs after every single render. This is rarely what you want and can cause infinite loops. Avoid it unless you have a specific reason.

```jsx
useEffect(() => {
  console.log('Runs after every render')
})
```

**With dependencies `[dep1, dep2]` — run when dependencies change:**

The effect runs after the first render, and then again any time one of the listed values changes. Use this to react to changes in props or state.

```jsx
useEffect(() => {
  // Runs when selectedPortfolioId changes
  console.log('Selected portfolio changed:', selectedPortfolioId)
}, [selectedPortfolioId])
```

When the backend is integrated with this app, `useEffect` with a dependency will be used to fetch holdings whenever the selected portfolio changes:

```jsx
useEffect(() => {
  if (!selectedPortfolioId) return
  // fetch holdings for the newly selected portfolio
  fetch(`/api/portfolios/${selectedPortfolioId}/investments`)
    .then(res => res.json())
    .then(data => setHoldings(data))
}, [selectedPortfolioId])
```

---

#### The cleanup function

Some effects need to clean up after themselves — subscriptions need to be cancelled, timers need to be cleared, event listeners need to be removed. Return a function from the effect to do this:

```jsx
useEffect(() => {
  const interval = setInterval(() => {
    console.log('tick')
  }, 1000)

  // Cleanup — runs when the component is removed from the DOM,
  // or just before the effect runs again (if dependencies changed)
  return () => clearInterval(interval)
}, [])
```

React calls the cleanup function automatically at the right time. You do not need to track whether to call it.

---

#### Running async code in `useEffect`

You cannot make the effect function itself `async` — React does not accept a function that returns a Promise. Instead, define an `async` function inside the effect and call it immediately:

```jsx
useEffect(() => {
  async function loadPortfolios() {
    try {
      const response = await fetch('/api/portfolios/user/alice')
      const data = await response.json()
      setPortfolios(data)
    } catch (err) {
      console.error('Failed to load portfolios:', err)
    }
  }

  loadPortfolios()   // call the async function — don't await it here
}, [])
```

This is the pattern you will use throughout this app once the backend integration is added. Every tab that loads data from the API will use a `useEffect` with this structure.

---

#### Rules of Hooks

`useState` and `useEffect` are both hooks. Hooks have two rules that you must follow:

1. **Only call hooks at the top level of your component** — never inside an `if`, a loop, or a nested function. React relies on hooks being called in the same order every time the component renders.
2. **Only call hooks from React function components** (or custom hooks) — not from regular JavaScript functions.

```jsx
// Wrong — conditional hook call
function MyComponent({ show }) {
  if (show) {
    const [value, setValue] = useState('')   // Error: can't call inside if
  }
}

// Correct — always call at the top level
function MyComponent({ show }) {
  const [value, setValue] = useState('')
  if (!show) return null
  return <div>{value}</div>
}
```

---

### 18. React-Bootstrap

**Introduction:**
React-Bootstrap is a library of pre-built UI components that wrap Bootstrap 5. Instead of writing `<div className="card">` and remembering the exact Bootstrap class names, you import and use React components like `<Card>`, `<Button>`, and `<Table>`.

**Installation:**

```bash
npm install react-bootstrap bootstrap
```

Import the Bootstrap CSS once, at the top of your entry point (`src/main.jsx`):

```jsx
import 'bootstrap/dist/css/bootstrap.min.css'
```

Then import individual components where you need them:

```jsx
import { Button, Card, Table } from 'react-bootstrap'
```

**Why use a component library?**

- Consistent, professional styling out of the box
- Responsive layout built in
- Accessible and well-tested components
- Much faster to build with than writing all styles from scratch

---

#### Layout — `Container`, `Row`, `Col`

Bootstrap's grid is a 12-column system. `Row` creates a horizontal row. `Col` divides the row into columns. `Container` provides horizontal padding and a max-width.

```jsx
import { Container, Row, Col } from 'react-bootstrap'

<Container className="mt-4">
  <Row xs={1} md={2} lg={3} className="g-3">
    <Col><Card>...</Card></Col>
    <Col><Card>...</Card></Col>
    <Col><Card>...</Card></Col>
  </Row>
</Container>
```

`xs={1}` — 1 column on small screens. `md={2}` — 2 columns on medium. `lg={3}` — 3 columns on large. `g-3` is a gap class.

---

#### `Card`

```jsx
import { Card, Button } from 'react-bootstrap'

<Card border="success" style={{ cursor: 'pointer' }} onClick={() => onSelect(portfolio.id)}>
  <Card.Body>
    <Card.Title>{portfolio.name}</Card.Title>
    <Card.Text className="text-muted">{portfolio.description}</Card.Text>
  </Card.Body>
  <Card.Footer className="text-end">
    <Button variant="outline-success" size="sm">View Holdings</Button>
  </Card.Footer>
</Card>
```

`border` accepts a Bootstrap variant name (`'success'`, `'danger'`, `'primary'`, etc.). `variant` on `Button` sets the colour style. `size="sm"` makes it smaller.

---

#### `Table`

```jsx
import { Table } from 'react-bootstrap'

<Table striped bordered hover responsive>
  <thead className="table-dark">
    <tr>
      <th>Ticker</th>
      <th>Quantity</th>
    </tr>
  </thead>
  <tbody>
    {holdings.map(h => (
      <tr key={h.id}>
        <td className="fw-bold">{h.ticker}</td>
        <td>{h.quantity}</td>
      </tr>
    ))}
  </tbody>
</Table>
```

`striped` — alternating row colours. `bordered` — borders on all cells. `hover` — highlight on mouse hover. `responsive` — wraps in a scrollable container on small screens.

---

#### `Alert`

```jsx
import { Alert } from 'react-bootstrap'

{error && (
  <Alert variant="danger" dismissible onClose={() => setError('')}>
    {error}
  </Alert>
)}

{success && (
  <Alert variant="success" dismissible onClose={() => setSuccess('')}>
    {success}
  </Alert>
)}
```

`dismissible` adds a close button. `onClose` is called when it is clicked — set the error/success state back to `''` to hide the alert.

---

#### `Form`

```jsx
import { Form, Row, Col } from 'react-bootstrap'

<Form onSubmit={handleSubmit}>
  <Form.Group className="mb-3" controlId="portfolioName">
    <Form.Label>Name</Form.Label>
    <Form.Control
      type="text"
      placeholder="e.g. Growth Fund"
      value={name}
      onChange={e => setName(e.target.value)}
    />
  </Form.Group>
  <Button type="submit" variant="success">Create</Button>
</Form>
```

`Form.Group` provides spacing and wires the label to the input via `controlId`. `Form.Control` is a styled input element. `Form.Select` is a styled `<select>`.

---

#### `Modal`

```jsx
import { Modal, Button } from 'react-bootstrap'

<Modal show={showCreateModal} onHide={() => setShowCreateModal(false)}>
  <Modal.Header closeButton>
    <Modal.Title>New Portfolio</Modal.Title>
  </Modal.Header>
  <Modal.Body>
    {/* form goes here */}
  </Modal.Body>
  <Modal.Footer>
    <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancel</Button>
    <Button variant="success" type="submit" form="my-form">Create</Button>
  </Modal.Footer>
</Modal>
```

`show` is a boolean — the modal is visible when `true`. `onHide` is called when the user clicks the backdrop or the close button. The `form` attribute on the submit button links it to a `<form>` in `Modal.Body` by matching the form's `id`.

---

#### `Tabs` and `Tab`

```jsx
import { Tabs, Tab } from 'react-bootstrap'

<Tabs activeKey={activeTab} onSelect={setActiveTab} className="mb-3">
  <Tab eventKey="portfolios" title="Portfolios">
    <PortfolioList ... />
  </Tab>
  <Tab eventKey="holdings" title="Holdings">
    <HoldingsPanel ... />
  </Tab>
</Tabs>
```

`activeKey` is the currently active tab. `onSelect` receives the `eventKey` of the clicked tab. Because `setActiveTab` is itself a setter function that takes a single value, you can pass it directly as `onSelect` — no wrapper needed.

---

#### `Navbar`

```jsx
import { Navbar, Container, Nav, Button } from 'react-bootstrap'

<Navbar bg="dark" variant="dark" expand="lg">
  <Container>
    <Navbar.Brand href="#">Kiwi</Navbar.Brand>
    <Navbar.Toggle aria-controls="main-nav" />
    <Navbar.Collapse id="main-nav">
      <Nav className="ms-auto">
        <Button variant="outline-light" size="sm" onClick={handleLogout}>
          Logout
        </Button>
      </Nav>
    </Navbar.Collapse>
  </Container>
</Navbar>
```

`bg="dark"` and `variant="dark"` — dark background with light text. `expand="lg"` — collapse the navbar into a hamburger menu on screens smaller than `lg`. `ms-auto` pushes the nav items to the right.

---

#### `Badge` and `Spinner`

```jsx
import { Badge, Spinner } from 'react-bootstrap'

// Colour-coded BUY/SELL label
<Badge bg={tx.type === 'buy' ? 'success' : 'danger'}>
  {tx.type.toUpperCase()}
</Badge>

// Loading spinner while data is being fetched
<Spinner animation="border" variant="success" />
```

---

**Objective:** Build a tabbed mini-dashboard using React-Bootstrap that ties together everything from all three Parts: component composition, lifted state, callback props, `useEffect`, and the React-Bootstrap component library. The result is a simplified version of the Kiwi dashboard.

Continue working in the `kiwi-lab` project from earlier Parts.

---

**Step 1 — Install React-Bootstrap.**

Stop the dev server if it is running, then install the packages:

```bash
npm install react-bootstrap bootstrap
```

Open `src/main.jsx` and add the Bootstrap CSS import as the first import:

```jsx
import 'bootstrap/dist/css/bootstrap.min.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

Restart the dev server with `npm run dev` and confirm your existing components now have Bootstrap styling applied (the font will change).

---

**Step 2 — Upgrade `PortfolioCard` to use Bootstrap `Card`.**

Replace the inline styles in `PortfolioCard.jsx` with React-Bootstrap components:

```jsx
import { Card, Button } from 'react-bootstrap'

function PortfolioCard({ portfolio, isSelected, onSelect }) {
  return (
    <Card
      className="h-100"
      border={isSelected ? 'success' : undefined}
      style={{ cursor: 'pointer' }}
      onClick={() => onSelect(portfolio.id)}
    >
      <Card.Body>
        <Card.Title>{portfolio.name}</Card.Title>
        {portfolio.description && (
          <Card.Text className="text-muted">{portfolio.description}</Card.Text>
        )}
      </Card.Body>
      <Card.Footer className="text-end">
        <Button
          variant="outline-success"
          size="sm"
          onClick={e => { e.stopPropagation(); onSelect(portfolio.id) }}
        >
          View Holdings
        </Button>
      </Card.Footer>
    </Card>
  )
}

export default PortfolioCard
```

The card now accepts `isSelected` (to show a green border) and `onSelect` (a callback).

---

**Step 3 — Upgrade `PortfolioList` to use Bootstrap grid and `Button`.**

```jsx
import { Row, Col, Button } from 'react-bootstrap'
import PortfolioCard from './PortfolioCard'

function PortfolioList({ portfolios, selectedPortfolioId, onSelect, onOpenCreate }) {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">Your Portfolios</h5>
        <Button variant="success" size="sm" onClick={onOpenCreate}>
          + New Portfolio
        </Button>
      </div>

      {portfolios.length === 0 && (
        <p className="text-muted">No portfolios yet. Create one to get started.</p>
      )}

      <Row xs={1} md={2} lg={3} className="g-3">
        {portfolios.map(portfolio => (
          <Col key={portfolio.id}>
            <PortfolioCard
              portfolio={portfolio}
              isSelected={portfolio.id === selectedPortfolioId}
              onSelect={onSelect}
            />
          </Col>
        ))}
      </Row>
    </div>
  )
}

export default PortfolioList
```

---

**Step 4 — Create `src/components/HoldingsPanel.jsx`.**

```jsx
import { Alert, Button, Table } from 'react-bootstrap'

function HoldingsPanel({ portfolio, holdings, onGoTrade }) {
  if (!portfolio) {
    return (
      <Alert variant="info">
        Select a portfolio from the <strong>Portfolios</strong> tab to view its holdings.
      </Alert>
    )
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">{portfolio.name}</h5>
        <Button variant="success" size="sm" onClick={onGoTrade}>
          Trade
        </Button>
      </div>

      {holdings.length === 0 ? (
        <p className="text-muted">No holdings yet. Use the Trade tab to buy securities.</p>
      ) : (
        <Table striped bordered hover responsive>
          <thead className="table-dark">
            <tr>
              <th>Ticker</th>
              <th>Quantity</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map(h => (
              <tr key={h.id}>
                <td className="fw-bold">{h.ticker}</td>
                <td>{h.quantity}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  )
}

export default HoldingsPanel
```

---

**Step 5 — Create `src/components/Dashboard.jsx` with lifted state.**

This is the core of the exercise. `Dashboard` owns all shared state and assembles the tabs.

```jsx
import { useState, useEffect } from 'react'
import { Container, Tabs, Tab } from 'react-bootstrap'
import PortfolioList from './PortfolioList'
import HoldingsPanel from './HoldingsPanel'

function Dashboard() {
  const [portfolios, setPortfolios] = useState([
    { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' },
    { id: 2, name: 'Income Fund', description: 'Dividend-focused stocks' },
  ])

  const [holdings, setHoldings] = useState([
    { id: 1, portfolioId: 1, ticker: 'AAPL', quantity: 10 },
    { id: 2, portfolioId: 1, ticker: 'MSFT', quantity: 5 },
  ])

  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null)
  const [activeTab, setActiveTab]                     = useState('portfolios')
  const [nextPortfolioId, setNextPortfolioId]         = useState(3)

  // Log a message every time the active tab changes — demonstrates useEffect with a dependency
  useEffect(() => {
    console.log('Active tab changed to:', activeTab)
  }, [activeTab])

  function handleSelectPortfolio(id) {
    setSelectedPortfolioId(id)
    setActiveTab('holdings')
  }

  function handleCreatePortfolio(name) {
    const newId = nextPortfolioId
    setPortfolios(prev => [...prev, { id: newId, name: name.trim(), description: '' }])
    setNextPortfolioId(prev => prev + 1)
    setSelectedPortfolioId(newId)
    setActiveTab('holdings')
  }

  const selectedPortfolio = portfolios.find(p => p.id === selectedPortfolioId) || null
  const selectedHoldings  = holdings.filter(h => h.portfolioId === selectedPortfolioId)

  return (
    <Container className="mt-4">
      <Tabs activeKey={activeTab} onSelect={setActiveTab} className="mb-3">

        <Tab eventKey="portfolios" title="Portfolios">
          <PortfolioList
            portfolios={portfolios}
            selectedPortfolioId={selectedPortfolioId}
            onSelect={handleSelectPortfolio}
            onOpenCreate={() => {
              const name = prompt('Enter portfolio name:')
              if (name && name.trim()) handleCreatePortfolio(name)
            }}
          />
        </Tab>

        <Tab eventKey="holdings" title="Holdings">
          <HoldingsPanel
            portfolio={selectedPortfolio}
            holdings={selectedHoldings}
            onGoTrade={() => setActiveTab('portfolios')}
          />
        </Tab>

      </Tabs>
    </Container>
  )
}

export default Dashboard
```

> Note: `prompt()` is used here as a quick stand-in for a real create form — it keeps this step focused on state lifting and composition. In the real app, this is replaced by the `CreatePortfolioModal` component.

Update `App.jsx` to render `Dashboard` instead of the individual components:

```jsx
import Dashboard from './components/Dashboard'

function App() {
  return <Dashboard />
}

export default App
```

---

**Step 6 — Verify the state flow manually.**

Walk through each of these interactions and verify the expected behaviour:

1. The app opens on the Portfolios tab showing two portfolio cards.
2. Click "Growth Fund" — the app switches to the Holdings tab and shows AAPL and MSFT.
3. Click back to Portfolios — the Growth Fund card has a green border.
4. Click "Income Fund" — the app switches to Holdings and shows the empty-holdings message.
5. Click "+ New Portfolio", enter a name → a new card appears, the app switches to Holdings for the new portfolio.
6. Open the browser console and verify the "Active tab changed to:" log fires each time you switch tabs — this confirms `useEffect` with the `[activeTab]` dependency is working.

---

**Step 7 — Add a `useEffect` that runs on mount.**

Inside `Dashboard`, add a `useEffect` that logs the initial portfolio count when the component first mounts. This simulates what a real data-fetch effect looks like before the API call is wired in.

```jsx
useEffect(() => {
  console.log(`Dashboard mounted with ${portfolios.length} portfolio(s).`)
  // In the real app, this is where you would fetch portfolios from the API:
  // fetch('/api/portfolios/user/<username>')
  //   .then(res => res.json())
  //   .then(data => setPortfolios(data))
}, [])   // empty array — runs once on mount
```

Reload the page and confirm the log fires exactly once in the console.

---

**Checkpoint:** By the end of Part 3 you should have:

- A `Dashboard` that owns all shared state and passes it down to children via props and callbacks
- `PortfolioList` and `HoldingsPanel` as stateless child components
- Callback props (`onSelect`, `onGoTrade`) wiring child events back to parent handlers
- React-Bootstrap components: `Container`, `Tabs`, `Tab`, `Card`, `Table`, `Alert`, `Button`, `Row`, `Col`
- A `useEffect` with an empty dependency array (runs on mount) and one with a dependency (runs when `activeTab` changes)
- A clear mental model of where to add API calls when the backend integration is added in a future Part
