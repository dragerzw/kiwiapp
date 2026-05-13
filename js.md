# JavaScript

## Part 1 — JavaScript Fundamentals

### 1. JavaScript vs Python — A Brief Orientation

**Introduction:**
You already know Python. JavaScript is the language that runs natively in every web browser — it is the only programming language browsers understand directly. Everything interactive you have ever seen on a web page (a button that reacts to a click, a list that updates without reloading the page) is powered by JavaScript.

Before diving in, here is a side-by-side map of the concepts you already know:

| Python | JavaScript | Notes |
| --- | --- | --- |
| `x = 5` | `let x = 5` | JS requires a keyword (`let` or `const`) |
| `# comment` | `// comment` | Single-line comment |
| `True / False` | `true / false` | Lowercase in JS |
| `None` | `null` / `undefined` | JS has two "nothing" values — explained below |
| `def greet():` | `function greet() {}` | Curly braces instead of indentation |
| `[1, 2, 3]` | `[1, 2, 3]` | Arrays work almost identically |
| `{"key": "value"}` | `{ key: "value" }` | Called an *object* in JS, not a dict |
| `f"Hello {name}"` | `` `Hello ${name}` `` | Template literals, same idea |
| `print(x)` | `console.log(x)` | Output goes to the browser's developer console |

**Key syntax differences to highlight:**

1. **Semicolons** — JS uses semicolons to end statements. They are technically optional (the engine inserts them automatically), but writing them avoids subtle bugs. The codebase omits trailing semicolons in JSX but uses them in regular JS logic.

2. **Curly braces, not indentation** — In Python, indentation defines code blocks. In JS, curly braces `{ }` define blocks. Indentation is just style.

3. **Strict equality** — Always use `===` (checks value *and* type). The `==` operator exists but does surprising automatic type conversions — avoid it.

```python
# Python
x = 10
if x == "10":   # True — Python raises a TypeError here actually, but == in JS would coerce
    print("equal")
```

```javascript
// JavaScript — always use ===
let x = 10
console.log(x === 10)    // true  — same value, same type (number)
console.log(x === "10")  // false — same value, different type (number vs string)
console.log(x == "10")   // true  — == coerces "10" to a number first — AVOID THIS
```

---

### 2. Variables: `let` and `const`

**Introduction:**
JavaScript has two variable keywords you will use: `const` and `let`. A third keyword `var` exists but is outdated — never use it in new code.

| Keyword | Can be reassigned? | When to use |
| --- | --- | --- |
| `const` | No | Default choice. Use whenever the variable will not be reassigned. |
| `let` | Yes | Use only when you know the value will change (e.g., a counter, a flag). |

**Why the distinction matters:** Defaulting to `const` makes your intentions explicit — a reader of your code immediately knows this value will not change. It also prevents accidental reassignment.

```javascript
// const — value is fixed after declaration
const portfolioName = 'Growth Fund'
portfolioName = 'Other Fund'   // TypeError: Assignment to constant variable

// let — value can change
let activeTab = 'portfolios'
activeTab = 'holdings'         // fine — let allows reassignment
console.log(activeTab)         // 'holdings'
```

```javascript
const newId = nextPortfolioId
```

`newId` is declared with `const` because its value is set once and never changed in that function — it is a snapshot of the current counter.

```javascript
const trimmedTicker = ticker.trim()
const qty = parseInt(quantity, 10)
```

Both are `const` — they are computed once at the top of the function and read thereafter.

**Practical rule:** Start with `const`. If the editor (or browser console) complains that you are reassigning it, switch to `let`.

---

### 3. Primitive Data Types

**Introduction:**
JavaScript has six primitive types. You will use four of them constantly.

#### `string`

Text, wrapped in single quotes, double quotes, or backticks.

```javascript
const ticker = 'AAPL'
const description = "Long-term growth picks"
const label = `Portfolio: ${ticker}`   // backtick = template literal — covered in Part 2
```

#### `number`

JavaScript has a single number type for both integers and decimals (unlike Python's `int` vs `float`).

```javascript
const quantity = 10
const price = 182.50
```

#### `boolean`

`true` or `false` — lowercase, unlike Python's `True` / `False`.

```javascript
const isLoggedIn = false
const hasDuplicate = true
```

#### `null` and `undefined`

This is the one area where JS differs meaningfully from Python's single `None`.

- **`null`** — an explicitly assigned "empty" value. You set it on purpose to mean "no value here".
- **`undefined`** — a variable that exists but has never been assigned a value.

```javascript
let selectedPortfolioId = null       // null: explicitly "no portfolio selected yet"
let result                           // undefined: declared but never assigned
console.log(result)                  // undefined

// In practice: check for both with == null (the one valid use of ==)
if (selectedPortfolioId === null) {
  console.log('No portfolio selected')
}
```

```javascript
const [selectedPortfolioId, setSelectedPortfolioId] = useState(null)
```

`null` here means "the user has not selected any portfolio yet". This is used later in `HoldingsPanel.jsx` to decide whether to show a prompt or the actual holdings table.

**Tip:** Use `null` when *you* are choosing to represent "nothing". Reserve `undefined` as a signal that something was never set — do not assign it manually.

---

### 4. Objects

**Introduction:**
An object is JavaScript's equivalent of a Python dictionary — a collection of key-value pairs. But in JS, you access values with *dot notation* (not bracket notation) by default.

```javascript
// Python dict
portfolio = {"id": 1, "name": "Growth Fund", "description": "Long-term growth"}

// JavaScript object — same idea, different syntax
const portfolio = { id: 1, name: 'Growth Fund', description: 'Long-term growth' }
```

**Accessing values:**

```javascript
console.log(portfolio.name)          // 'Growth Fund'   — dot notation (preferred)
console.log(portfolio['name'])       // 'Growth Fund'   — bracket notation (same result)


let p = { id: 1, name: 'Growth Fund' }
p.name = 'Tech Fund'
console.log(p.name)   // 'Tech Fund'
```

Note: `const portfolio = { ... }` does NOT mean the object is frozen. You can still change its properties. `const` only prevents the variable from being *reassigned* to a different object entirely.

```javascript
const portfolio = { id: 1, name: 'Growth Fund' }
portfolio.name = 'Tech Fund'   // fine — mutating a property
portfolio = { id: 2 }          // TypeError — reassigning the variable is forbidden
```

**Nested objects and checking for a property:**

```javascript
const holding = { id: 1, portfolioId: 1, ticker: 'AAPL', quantity: 10 }

console.log(holding.ticker)       // 'AAPL'
console.log(holding.quantity)     // 10

// Checking if a property exists
console.log(holding.price)        // undefined — property does not exist, no error thrown
```

Every portfolio, holding, and transaction in this app is represented as a plain JavaScript object:

```javascript
{ id: 1, name: 'Growth Fund', description: 'Long-term growth picks' }
{ id: 1, portfolioId: 1, ticker: 'AAPL', quantity: 10 }
{ id: 1, portfolioId: 1, ticker: 'AAPL', type: 'buy', quantity: 10, date: '2026-03-01' }
```

Every React component in the app receives these objects as data and reads their properties using dot notation — `portfolio.name`, `holding.ticker`, `tx.date`.

---

### 5. Arrays

**Introduction:**
JavaScript arrays work almost identically to Python lists: ordered, zero-indexed, and they can hold any type of value — including objects.

```javascript
// Array of strings
const tickers = ['AAPL', 'MSFT', 'GOOG']

// Array of objects — the most common pattern in this codebase
const portfolios = [
  { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' },
  { id: 2, name: 'Income Fund', description: 'Dividend-focused' },
]
```

**Accessing elements:**

```javascript
console.log(tickers[0])         // 'AAPL'   — zero-indexed, same as Python
console.log(portfolios[1].name) // 'Income Fund' — index into array, then dot notation
console.log(tickers.length)     // 3 — number of items
```

**Adding items:**

```javascript
// push — adds to the end (mutates the array, like Python's .append())
const tickers = ['AAPL', 'MSFT']
tickers.push('GOOG')
console.log(tickers)   // ['AAPL', 'MSFT', 'GOOG']
```

> Note: In React you will almost never use `push` — instead you will build a *new* array using the spread operator (covered in Part 2). The reason will be clear once you see React state.

**Checking the length:**

```javascript
if (portfolios.length === 0) {
  console.log('No portfolios yet.')
}
```

```javascript
{portfolios.length === 0 && (
  <p className="text-muted">No portfolios yet. Create one to get started.</p>
)}
```

This checks whether the `portfolios` array is empty and shows a placeholder message if so.

---

### 6. Functions

**Introduction:**
JavaScript has two ways to write functions that you will use constantly: the classic *function declaration* and the more concise *arrow function*. Both do the same job — arrow functions are just a shorter syntax.

#### Function declarations

```python
# Python
def greet(name):
    return f"Hello, {name}"
```

```javascript
// JavaScript — function declaration
function greet(name) {
  return `Hello, ${name}`
}

console.log(greet('Alice'))   // 'Hello, Alice'
```

#### Arrow functions

Arrow functions are the shorthand form. They are especially common when passing a function as an argument (you will do this constantly with array methods in Part 2).

```javascript
// Same function as above, written as an arrow function
const greet = (name) => {
  return `Hello, ${name}`
}

// If the function body is a single expression, you can drop the braces and return keyword
const greet = (name) => `Hello, ${name}`

// If there is only one parameter, you can drop the parentheses around it
const greet = name => `Hello, ${name}`
```

All three versions above are identical. In this codebase you will see the short form frequently.

**Functions can receive other functions as arguments:**

This is the pattern behind every array method. A function passed as an argument is called a *callback*.

```javascript
function applyTwice(value, transform) {
  return transform(transform(value))
}

const result = applyTwice('aapl', s => s.toUpperCase())
console.log(result)   // 'AAPL' — toUpperCase was called twice, but it's idempotent
```

```javascript
const selectedPortfolio = portfolios.find(p => p.id === selectedPortfolioId) || null
```

`p => p.id === selectedPortfolioId` is an arrow function passed as a callback to `.find()`. It receives each portfolio object `p` and returns `true` or `false` — `.find()` uses that to locate the matching entry. This pattern is the foundation of Part 2.

---

### Part 1 Exercise — Portfolio Data Builder

**Objective:** Practice creating objects, arrays, and functions by modelling the portfolio data structures used in the app — using only a plain HTML file and a `<script>` tag.

**How to see output:** Open the browser's developer tools (`F12` or right-click → Inspect → Console). All `console.log()` output appears there.

---

**Step 1 — Create the file.**

Create a new file called `portfolio-lab.html` in any folder.

---

**Step 2 — Add the HTML shell with a script block.**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Portfolio Lab</title>
</head>
<body>
  <h1>Open the browser console to see output.</h1>

  <script>
    // All your JavaScript goes here

  </script>
</body>
</html>
```

Open the file in a browser and open the developer console. You should see no errors yet.

---

**Step 3 — Create two portfolio objects.**

Inside the `<script>` block, declare two portfolios using `const`. Each portfolio has an `id`, a `name`, and a `description`.

```javascript
const portfolio1 = { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' }
const portfolio2 = { id: 2, name: 'Income Fund', description: 'Dividend-focused stocks' }
```

Log both to the console and verify the output:

```javascript
console.log(portfolio1)
console.log(portfolio2.name)   // should print 'Income Fund'
```

Refresh the page and confirm both lines appear in the console.

---

**Step 4 — Put the portfolios in an array.**

Declare a `portfolios` array that holds both objects. Then log the number of portfolios and the name of the first one.

```javascript
const portfolios = [portfolio1, portfolio2]

console.log(portfolios.length)      // 2
console.log(portfolios[0].name)     // 'Growth Fund'
```

---

**Step 5 — Write a function that adds a new portfolio.**

The function takes a current array, an id, a name, and a description. It returns a **new** array with the new portfolio appended. Use `push` for now (the spread operator version comes in Part 2).

```javascript
function addPortfolio(currentPortfolios, id, name, description) {
  const newPortfolio = { id: id, name: name, description: description }
  const updated = [portfolio1, portfolio2]   // copy manually for now
  updated.push(newPortfolio)
  return updated
}

const updated = addPortfolio(portfolios, 3, 'Tech Fund', 'High-growth tech stocks')
console.log(updated.length)        // 3
console.log(updated[2].name)       // 'Tech Fund'
```

---

**Step 6 — Write a function that finds a portfolio by id.**

This mirrors `portfolios.find(...)` that the app uses to locate the selected portfolio. Write the lookup manually using a `for` loop first, then we will replace it with `.find()` in Part 2.

```javascript
function findById(portfoliosList, targetId) {
  for (let i = 0; i < portfoliosList.length; i++) {
    if (portfoliosList[i].id === targetId) {
      return portfoliosList[i]
    }
  }
  return null   // return null if no match — same convention the app uses
}

console.log(findById(portfolios, 1))     // { id: 1, name: 'Growth Fund', ... }
console.log(findById(portfolios, 99))    // null
```

---

**Step 7 — Rewrite the arrow function form.**

Rewrite `findById` as an arrow function stored in a `const`. The logic stays the same — only the syntax changes.

```javascript
const findById = (portfoliosList, targetId) => {
  for (let i = 0; i < portfoliosList.length; i++) {
    if (portfoliosList[i].id === targetId) {
      return portfoliosList[i]
    }
  }
  return null
}

console.log(findById(portfolios, 2))   // { id: 2, name: 'Income Fund', ... }
```

Verify the output is identical to Step 6. The two forms are interchangeable — arrow functions are not a different concept, just a shorter spelling.

---

**Checkpoint:** At the end of Part 1 you should have:

- Two portfolio objects and one array holding them
- A function that adds a new portfolio and returns a new array
- A function that finds a portfolio by id, written both ways (declaration and arrow)
- All output verified in the browser console

---

## Part 2 — Working with Data

### 7. String Methods and Template Literals

**Introduction:**
JavaScript strings come with built-in methods. The ones below are used throughout this codebase for cleaning user input and building readable messages.

#### `.trim()`

Removes whitespace from both ends of a string. Essential for cleaning up anything a user types.

```javascript
const raw = '  AAPL  '
console.log(raw.trim())   // 'AAPL' — leading and trailing spaces removed
```

The user may accidentally type spaces around a ticker symbol. `.trim()` ensures "  AAPL  " is treated the same as "AAPL".

#### `.toUpperCase()` and `.toLowerCase()`

```javascript
console.log('aapl'.toUpperCase())   // 'AAPL'
console.log('AAPL'.toLowerCase())   // 'aapl'
```

```javascript
const upperTicker = ticker.trim().toUpperCase()
```

Methods can be chained — `trim()` runs first, then `toUpperCase()` runs on the result. Ticker symbols are stored uppercase throughout the app for consistency.

#### `.includes()`

Returns `true` if a string contains a substring, `false` otherwise. Case-sensitive.

```javascript
console.log('AAPL'.includes('AA'))   // true
console.log('AAPL'.includes('aa'))   // false — case-sensitive
```

```javascript
tx.ticker.toLowerCase().includes(filterTicker.trim().toLowerCase())
```

Both the stored ticker and the user's filter input are lowercased before comparing so the search is case-insensitive.

#### Template literals

Template literals use backticks `` ` `` instead of quotes and embed expressions with `${ }` — exactly like Python's f-strings.

```python
# Python f-string
msg = f"Bought {qty} share(s) of {ticker}."
```

```javascript
// JavaScript template literal
const msg = `Bought ${qty} share(s) of ${ticker}.`
```

Any JavaScript expression can go inside `${ }`:

```javascript
const qty = 10
const ticker = 'aapl'
const msg = `Bought ${qty} share(s) of ${ticker.toUpperCase()}.`
console.log(msg)   // 'Bought 10 share(s) of AAPL.'
```

```javascript
setSuccess(`Bought ${qty} share(s) of ${trimmedTicker.toUpperCase()}.`)
```

---

### 8. Type Conversion

**Introduction:**
HTML form inputs always give you strings, even when the user types a number. JavaScript will not automatically convert `"10"` (string) to `10` (number) for arithmetic — you must convert explicitly.

#### `parseInt(string, radix)`

Converts a string to a whole number. Always pass `10` as the second argument (the *radix*) — it tells JS you want base-10 arithmetic.

```javascript
const raw = '10'               // string — came from a form input
const qty = parseInt(raw, 10)  // number — 10

console.log(raw + 5)    // '105' — string concatenation, not addition!
console.log(qty + 5)    // 15   — numeric addition
```

#### Checking for a valid number: `isNaN()`

`parseInt` returns the special value `NaN` (Not a Number) if the string cannot be parsed. Use `isNaN()` to guard against that.

```javascript
console.log(parseInt('abc', 10))    // NaN
console.log(parseInt('10', 10))     // 10
console.log(isNaN(parseInt('abc', 10)))   // true
console.log(isNaN(parseInt('10', 10)))    // false
```

---

### 9. Conditionals

**Introduction:**
JavaScript conditionals work the same as Python's. The only syntax differences are the curly braces and the absence of the `elif` keyword.

#### `if / else if / else`

```python
# Python
if qty <= 0:
    print("invalid")
elif qty > 1000:
    print("very large order")
else:
    print("valid")
```

```javascript
// JavaScript
if (qty <= 0) {
  console.log('invalid')
} else if (qty > 1000) {
  console.log('very large order')
} else {
  console.log('valid')
}
```

#### Ternary operator

A compact single-line `if/else` that evaluates to a value. Syntax: `condition ? valueIfTrue : valueIfFalse`.

```python
# Python one-liner
label = "buy" if type == "buy" else "sell"
```

```javascript
// JavaScript ternary
const label = type === 'buy' ? 'buy' : 'sell'
```

#### Logical operators: `&&`, `||`, `!`

These work the same as Python's `and`, `or`, `not`, but with symbol syntax.

| Python | JavaScript |
| --- | --- |
| `and` | `&&` |
| `or` | `\|\|` |
| `not x` | `!x` |

```javascript
const isValid = trimmedTicker !== '' && qty > 0   // both must be true

if (!isValid) {
  console.log('form is incomplete')
}
```

**Short-circuit evaluation — the `||` default pattern:**

`a || b` returns `a` if `a` is truthy, otherwise returns `b`. This is often used to provide a fallback value.

```javascript
const name = portfolio.name || 'Unnamed Portfolio'
// if portfolio.name is an empty string or null, 'Unnamed Portfolio' is used instead
```

---

### 10. Array Methods: `map`, `filter`, `find`, `some`

**Introduction:**
These four methods are the core of how data is processed throughout this codebase — and throughout virtually all React applications. Each method takes a *callback function* (usually an arrow function) that it calls once per item in the array. None of them modify the original array — they always return something new.

| Method | Returns | Use when you want to |
| --- | --- | --- |
| `.map()` | A new array of the same length | Transform every item |
| `.filter()` | A new array of only matching items | Keep items that pass a test |
| `.find()` | The first matching item (or `undefined`) | Get one specific item |
| `.some()` | `true` or `false` | Check if at least one item passes a test |

#### `.map()`

Transforms every item and returns a new array of the same length. The callback receives each item and returns its transformed version.

```javascript
const tickers = ['aapl', 'msft', 'goog']
const upper = tickers.map(t => t.toUpperCase())
console.log(upper)   // ['AAPL', 'MSFT', 'GOOG']
```

With an array of objects:

```javascript
const holdings = [
  { ticker: 'AAPL', quantity: 10 },
  { ticker: 'MSFT', quantity: 5  },
]

// Extract just the ticker symbols
const symbols = holdings.map(h => h.ticker)
console.log(symbols)   // ['AAPL', 'MSFT']

// Build a summary string for each holding
const summaries = holdings.map(h => `${h.ticker}: ${h.quantity} shares`)
console.log(summaries)   // ['AAPL: 10 shares', 'MSFT: 5 shares']
```

**Updating one item in an array with `.map()`:**

This is the standard React pattern for modifying a single item without mutating the original array. The callback returns the modified item for the match, and the unchanged original for everything else.

```javascript
const holdings = [
  { id: 1, ticker: 'AAPL', quantity: 10 },
  { id: 2, ticker: 'MSFT', quantity: 5  },
]

// Increase AAPL quantity by 3
const updated = holdings.map(h =>
  h.ticker === 'AAPL'
    ? { ...h, quantity: h.quantity + 3 }   // spread operator — covered in section 11
    : h
)

console.log(updated[0].quantity)   // 13
console.log(updated[1].quantity)   // 5 — unchanged
```

---

#### `.filter()`

Returns a new array containing only the items for which the callback returns `true`.

```javascript
const holdings = [
  { id: 1, portfolioId: 1, ticker: 'AAPL', quantity: 10 },
  { id: 2, portfolioId: 1, ticker: 'MSFT', quantity: 5  },
  { id: 3, portfolioId: 2, ticker: 'GOOG', quantity: 8  },
]

// Keep only holdings that belong to portfolio 1
const portfolioHoldings = holdings.filter(h => h.portfolioId === 1)
console.log(portfolioHoldings.length)   // 2
console.log(portfolioHoldings[0].ticker)   // 'AAPL'
```

Removing one item (the sell-to-zero case):

```javascript
// Remove AAPL from portfolio 1 entirely
const afterSell = holdings.filter(h => !(h.portfolioId === 1 && h.ticker === 'AAPL'))
console.log(afterSell.length)   // 2 — only MSFT and GOOG remain
```

---

#### `.find()`

Returns the *first* item for which the callback returns `true`, or `undefined` if nothing matches. Use it when you expect exactly one result.

```javascript
const portfolios = [
  { id: 1, name: 'Growth Fund' },
  { id: 2, name: 'Income Fund' },
]

const found = portfolios.find(p => p.id === 2)
console.log(found)         // { id: 2, name: 'Income Fund' }
console.log(found.name)    // 'Income Fund'

const missing = portfolios.find(p => p.id === 99)
console.log(missing)       // undefined — no match
```

Always guard against `undefined` when the match might not exist:

```javascript
const portfolio = portfolios.find(p => p.id === selectedId)
if (portfolio) {
  console.log(portfolio.name)
} else {
  console.log('Not found')
}
```

---

#### `.some()`

Returns `true` if *at least one* item in the array passes the test, `false` if none do. It stops as soon as it finds a match — it does not process the whole array.

```javascript
const portfolios = [
  { id: 1, name: 'Growth Fund' },
  { id: 2, name: 'Income Fund' },
]

const hasGrowth = portfolios.some(p => p.name === 'Growth Fund')
console.log(hasGrowth)   // true

const hasTech = portfolios.some(p => p.name === 'Tech Fund')
console.log(hasTech)     // false
```

---

### 11. The Spread Operator

**Introduction:**
The spread operator `...` copies the contents of an array (or object) into a new one. It is the standard way to add items to an array or update a property on an object *without mutating the original* — which is essential in React.

#### Spreading arrays

```javascript
const existing = [1, 2, 3]

// Add a new item to the end — creates a brand-new array
const updated = [...existing, 4]
console.log(updated)    // [1, 2, 3, 4]
console.log(existing)   // [1, 2, 3] — original is untouched
```

Compare this to `push`, which mutates in place:

```javascript
existing.push(4)        // modifies existing directly — never do this in React state
```

#### Spreading objects

`...obj` copies all properties of `obj` into a new object. You can then override specific properties after the spread.

```javascript
const holding = { id: 1, ticker: 'AAPL', quantity: 10 }

// Create a new object with quantity updated — original unchanged
const updated = { ...holding, quantity: 13 }
console.log(updated)    // { id: 1, ticker: 'AAPL', quantity: 13 }
console.log(holding)    // { id: 1, ticker: 'AAPL', quantity: 10 } — original unchanged
```

Properties after the spread override the copied ones. Properties not mentioned are preserved as-is.

---

### Part 2 Exercise — Mini Trade Logic

**Objective:** Implement a simplified version of the buy/sell logic using only vanilla JavaScript. This exercise gives you hands-on practice with all four array methods, the spread operator, string methods, and type conversion in a realistic context.

---

**Step 1 — Extend your file from Part 1.**

Open `portfolio-lab.html`. Below the existing code, add a separator comment and the starting data:

```javascript
// ─── Part 2 ────────────────────────────────────────────

const portfolios = [
  { id: 1, name: 'Growth Fund', description: 'Long-term growth picks' },
  { id: 2, name: 'Income Fund', description: 'Dividend-focused stocks' },
]

let holdings = [
  { id: 1, portfolioId: 1, ticker: 'AAPL', quantity: 10 },
  { id: 2, portfolioId: 1, ticker: 'MSFT', quantity: 5  },
]

let transactions = [
  { id: 1, portfolioId: 1, ticker: 'AAPL', type: 'buy', quantity: 10, date: '2026-03-01' },
  { id: 2, portfolioId: 1, ticker: 'MSFT', type: 'buy', quantity: 5,  date: '2026-03-10' },
]

let nextHoldingId    = 3
let nextTransactionId = 3
```

---

**Step 2 — Write `getHoldingsForPortfolio`.**

Use `.filter()` to return only the holdings that belong to a given portfolio id.

```javascript
function getHoldingsForPortfolio(portfolioId) {
  return holdings.filter(h => h.portfolioId === portfolioId)
}

console.log(getHoldingsForPortfolio(1))   // should show AAPL and MSFT
console.log(getHoldingsForPortfolio(2))   // should show an empty array []
```

Verify: portfolio 1 has 2 holdings, portfolio 2 has 0.

---

**Step 3 — Write `getPortfolioName`.**

Use `.find()` to look up a portfolio's name by its id. Return `'Unknown'` if no match is found.

```javascript
function getPortfolioName(portfolioId) {
  const p = portfolios.find(p => p.id === portfolioId)
  return p ? p.name : 'Unknown'
}

console.log(getPortfolioName(1))    // 'Growth Fund'
console.log(getPortfolioName(99))   // 'Unknown'
```

---

**Step 4 — Write `checkDuplicateName`.**

Use `.some()` to check whether a portfolio with the given name already exists (case-insensitive).

```javascript
function checkDuplicateName(name) {
  return portfolios.some(p => p.name.toLowerCase() === name.trim().toLowerCase())
}

console.log(checkDuplicateName('Growth Fund'))    // true
console.log(checkDuplicateName('growth fund'))    // true  — case-insensitive
console.log(checkDuplicateName('Tech Fund'))      // false
```

---

**Step 5 — Write `buy`.**

This is the core of the exercise. The `buy` function should:

1. Clean and convert the inputs: trim and uppercase the ticker; parse the quantity to an integer.
2. Validate: if the ticker is empty or the quantity is not a positive number, log an error and return early.
3. Check if the holding already exists using `.find()`.
4. If it does, update its quantity using `.map()` and the spread operator.
5. If it does not, add a new holding to the array using spread.
6. Add a transaction record to the `transactions` array using spread.

```javascript
function buy(portfolioId, ticker, quantity) {
  // Step 1 — clean inputs
  const upperTicker = ticker.trim().toUpperCase()
  const qty = parseInt(quantity, 10)

  // Step 2 — validate
  if (!upperTicker) {
    console.log('Error: ticker is required.')
    return
  }
  if (!qty || qty <= 0) {
    console.log('Error: quantity must be a positive number.')
    return
  }

  // Step 3 — check if the holding already exists
  const existing = holdings.find(
    h => h.portfolioId === portfolioId && h.ticker === upperTicker
  )

  // Step 4/5 — update or add holding
  if (existing) {
    holdings = holdings.map(h =>
      h.portfolioId === portfolioId && h.ticker === upperTicker
        ? { ...h, quantity: h.quantity + qty }
        : h
    )
  } else {
    const newHolding = { id: nextHoldingId, portfolioId, ticker: upperTicker, quantity: qty }
    holdings = [...holdings, newHolding]
    nextHoldingId++
  }

  // Step 6 — add a transaction record
  const newTx = {
    id: nextTransactionId,
    portfolioId,
    ticker: upperTicker,
    type: 'buy',
    quantity: qty,
    date: new Date().toISOString().slice(0, 10),
  }
  transactions = [...transactions, newTx]
  nextTransactionId++

  console.log(`Bought ${qty} share(s) of ${upperTicker}.`)
}
```

Test it with a few calls and check the arrays after each:

```javascript
buy(1, 'aapl', '5')      // should increase AAPL from 10 to 15
buy(1, 'goog', '8')      // should add a new GOOG holding
buy(1, '', '5')           // should log: Error: ticker is required.
buy(1, 'tsla', '-3')      // should log: Error: quantity must be a positive number.

console.log(holdings)      // inspect the result
console.log(transactions)  // should now have 4 transactions
```

---

**Step 6 — Write `sell`.**

The `sell` function is the mirror of `buy`. It should:

1. Clean and convert inputs (same as buy).
2. Validate inputs (same as buy).
3. Use `.find()` to check the holding exists and has enough shares.
4. If the sell quantity equals the existing quantity, remove the holding entirely with `.filter()`.
5. Otherwise, reduce the quantity with `.map()` and spread.
6. Add a sell transaction record.

```javascript
function sell(portfolioId, ticker, quantity) {
  // Step 1 — clean inputs
  const upperTicker = ticker.trim().toUpperCase()
  const qty = parseInt(quantity, 10)

  // Step 2 — validate
  if (!upperTicker) {
    console.log('Error: ticker is required.')
    return false
  }
  if (!qty || qty <= 0) {
    console.log('Error: quantity must be a positive number.')
    return false
  }

  // Step 3 — check sufficient holdings
  const existing = holdings.find(
    h => h.portfolioId === portfolioId && h.ticker === upperTicker
  )
  if (!existing || existing.quantity < qty) {
    console.log(`Error: insufficient holdings for ${upperTicker}.`)
    return false
  }

  // Step 4/5 — remove or reduce holding
  if (existing.quantity === qty) {
    holdings = holdings.filter(
      h => !(h.portfolioId === portfolioId && h.ticker === upperTicker)
    )
  } else {
    holdings = holdings.map(h =>
      h.portfolioId === portfolioId && h.ticker === upperTicker
        ? { ...h, quantity: h.quantity - qty }
        : h
    )
  }

  // Step 6 — add a transaction record
  const newTx = {
    id: nextTransactionId,
    portfolioId,
    ticker: upperTicker,
    type: 'sell',
    quantity: qty,
    date: new Date().toISOString().slice(0, 10),
  }
  transactions = [...transactions, newTx]
  nextTransactionId++

  console.log(`Sold ${qty} share(s) of ${upperTicker}.`)
  return true
}
```

Test the edge cases:

```javascript
sell(1, 'AAPL', '5')    // reduce AAPL from 10 to 5 (or from 15 to 10 if you ran buy first)
sell(1, 'MSFT', '5')    // sell all MSFT — should remove the holding entirely
sell(1, 'MSFT', '1')    // should log: Error: insufficient holdings (MSFT was just removed)
sell(1, 'NVDA', '1')    // should log: Error: insufficient holdings (never held)

console.log(holdings)
```

---

**Step 7 — Write `filterTransactions`.**

Use `.filter()` to implement the transaction search logic. The function takes optional filter strings for portfolio id and ticker. Empty strings mean "show all".

```javascript
function filterTransactions(portfolioIdFilter, tickerFilter) {
  return transactions.filter(tx => {
    const matchPortfolio =
      portfolioIdFilter === '' ||
      tx.portfolioId === parseInt(portfolioIdFilter, 10)

    const matchTicker =
      tickerFilter === '' ||
      tx.ticker.toLowerCase().includes(tickerFilter.trim().toLowerCase())

    return matchPortfolio && matchTicker
  })
}

console.log(filterTransactions('', ''))          // all transactions
console.log(filterTransactions('1', ''))         // all transactions for portfolio 1
console.log(filterTransactions('', 'aapl'))      // all AAPL transactions (case-insensitive)
console.log(filterTransactions('1', 'MSFT'))     // MSFT transactions in portfolio 1 only
```

---

**Step 8 — Write `printTransactions`.**

Use `.map()` to turn each transaction in the filtered results into a readable summary string using a template literal. Log each one.

```javascript
function printTransactions(portfolioIdFilter, tickerFilter) {
  const results = filterTransactions(portfolioIdFilter, tickerFilter)

  if (results.length === 0) {
    console.log('No transactions found.')
    return
  }

  const lines = results.map(tx =>
    `[${tx.date}] ${getPortfolioName(tx.portfolioId)} — ${tx.type.toUpperCase()} ${tx.quantity} ${tx.ticker}`
  )

  lines.forEach(line => console.log(line))
}

printTransactions('', '')        // print all transactions
printTransactions('1', 'AAPL')   // print only AAPL trades in portfolio 1
```

Expected output (dates will vary based on when you ran the buy/sell steps):

```text
[2026-03-01] Growth Fund — BUY 10 AAPL
[2026-03-10] Growth Fund — BUY 5 MSFT
[2026-04-05] Growth Fund — BUY 5 AAPL
...
```

---

**Checkpoint — what you built:**

| Function | Concepts used |
| --- | --- |
| `getHoldingsForPortfolio` | `.filter()` |
| `getPortfolioName` | `.find()`, ternary operator |
| `checkDuplicateName` | `.some()`, `.toLowerCase()`, `.trim()` |
| `buy` | `.find()`, `.map()`, spread, `parseInt`, template literal, validation |
| `sell` | `.find()`, `.filter()`, `.map()`, spread, `parseInt`, early return |
| `filterTransactions` | `.filter()`, `parseInt`, `.includes()`, `.toLowerCase()` |
| `printTransactions` | `.map()`, template literal, `forEach` |
