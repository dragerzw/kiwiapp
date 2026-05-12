import React from 'react'
import ReactDOM from 'react-dom/client'
import { AuthProvider as OidcAuthProvider } from "react-oidc-context";
import { AuthProviderWrapper } from "./AuthContext";
import { BrowserRouter } from "react-router-dom";
import App from './App.jsx'
import './index.css'
import { oidcConfig } from "./authConfig";

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <OidcAuthProvider {...oidcConfig}>
      <AuthProviderWrapper>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AuthProviderWrapper>
    </OidcAuthProvider>
  </React.StrictMode>,
)
