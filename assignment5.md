# Assignment 5 (Final): Frontend Application Development

Course: Financial Applications of Web Development  
Due Date: May 15, 2026 – 11:59 PM CST  
Weight: 40% of Final Grade  
Submission Method: Pull Request on the student's GitHub repository

---

## Overview

Throughout this course, you have built a full-featured portfolio management backend — starting from a command-line application, progressing through database integration, REST API design, authentication, and authorization. In this final assignment, you will complete the application by building a frontend web interface that connects to your backend API.

The result will be a fully integrated, end-to-end web application. A user will be able to open a browser, authenticate with their identity, and manage their investment portfolios entirely through the user interface you build.

---

## Objectives

By completing this assignment, you will:

1. Build a frontend web application using a React JavaScript framework.
2. Integrate your frontend with the REST API you developed in Assignments 3 and 4.
3. Implement browser-based user authentication using the OIDC Hosted UI provided by AWS Cognito.
4. Design a functional and organized user interface that supports all core portfolio management workflows.
5. Enforce frontend-level authorization so that UI elements and routes respect the user's identity and role.

---

## Application Requirements

Your frontend must support the following features. The implementation approach — component structure, state management, routing, styling — is left to your discretion as a developer. What matters is that the features work correctly and the user experience is coherent.

### Authentication

- The application must require users to authenticate before accessing any protected content.
- Authentication must be implemented using the **OIDC Authorization Code Flow** with your existing AWS Cognito User Pool (the same one used in Assignment 4).
- Upon successful authentication, the identity token (JWT) returned by Cognito must be stored client-side and attached to every subsequent API request as a `Bearer` token in the `Authorization` header.
- If a user's session expires or the token is missing, the application must redirect the user to the login page.
- The application must provide a way for the user to log out, which should clear the stored token and redirect to the login screen.

> Note: AWS Cognito provides a hosted UI that handles the login/signup screens for you. You are not required to build a custom login form — integrating with the Cognito Hosted UI redirect flow is sufficient.

### Portfolio Management

Once authenticated, the user must be able to:

- **View their portfolios** — Display a list of all portfolios belonging to the authenticated user. At minimum, each portfolio entry should show its name and description.
- **Create a new portfolio** — Provide a form or modal that allows the user to enter a portfolio name and description. Upon submission, the portfolio should be created via the API and the list should update accordingly.
- **Delete a portfolio** — Allow the user to delete a portfolio they own. The application should prevent deletion if the portfolio still contains holdings (consistent with the backend rule). Provide appropriate feedback to the user in either case.

### Holdings and Trading

Within a selected portfolio, the user must be able to:

- **View holdings** — Display all investment positions currently held in the portfolio. Each holding should show, at minimum, the ticker symbol and quantity.
- **Place a buy order** — Allow the user to purchase shares of a security by providing a ticker symbol and quantity. The application should display appropriate confirmation or error feedback based on the API response.
- **Place a sell order** — Allow the user to liquidate shares from a holding. The user should be able to specify the quantity to sell. Partial and full liquidations must both be supported.

### Transaction History

- Within a selected portfolio, the user must be able to **view all transactions** associated with that portfolio.
- Each transaction entry should display, at minimum: the ticker symbol, transaction type (BUY or SELL), quantity, price, and timestamp.

---

## Technical Requirements

- Your frontend must communicate exclusively with your own backend API (the Flask application from previous assignments).
- Authentication tokens must never be exposed in URLs or logged to the browser console.
- The application should handle API errors gracefully. If a backend call fails, the user should receive a meaningful message rather than a broken UI.
- The frontend project must live in a dedicated directory within your repository (e.g., `frontend/`), clearly separated from the backend code.

---

## General Guidance

- **Start with authentication.** Getting the OIDC flow working first will unblock everything else, since all API calls depend on a valid token.
- **Work feature by feature.** Implement and test one feature end-to-end before moving to the next. Trying to build everything at once makes debugging much harder.
- **Your backend is your source of truth.** If the UI is showing unexpected results, check what the API is returning first before debugging the frontend.
- **You are not graded on visual design.** A clean, functional interface is all that is expected. Do not spend excessive time on styling at the expense of functionality.
- **Test with real tokens.** Use Postman or the browser developer tools to inspect the tokens being sent and confirm they match what your backend expects.

---

## Submission Instructions

- Submit your work by creating a pull request (PR) from your feature branch (e.g., `assignment-5`) into your `main` branch on GitHub.
- **DO NOT** merge the PR or commit directly to the `main` branch. All code must go through the pull request.

Late submissions are subject to standard course penalties unless prior approval is obtained.

---

## Grading Rubric

| Criterion | Weight | Description |
| --- | --- | --- |
| Authentication (OIDC + AWS Cognito) | 25% | OIDC Authorization Code Flow is correctly implemented. Tokens are obtained, stored, attached to API requests, and cleared on logout. Unauthenticated users are redirected to login. |
| Portfolio Management Features | 25% | User can view, create, and delete portfolios. UI reflects backend state accurately and provides appropriate feedback on errors. |
| Holdings and Trading Features | 25% | User can view holdings, place buy orders, and place sell orders (partial and full). API errors are surfaced meaningfully to the user. |
| Transaction History | 10% | User can view the transaction history for a portfolio with relevant details displayed. |
| Code Quality and Project Structure | 10% | Frontend code is organized logically. The `frontend/` directory is clearly separated. A `README.md` with setup instructions is included. |
| Version Control and Submission Compliance | 5% | Work is submitted as a pull request from a feature branch. No code is committed directly to `main`. PR description is complete. |
