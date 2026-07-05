import { createContext, useContext } from "react";
import { useAuth as useOidcAuth } from "react-oidc-context";

const CustomAuthContext = createContext(null);

export const AuthProviderWrapper = ({ children }) => {
  const oidcAuth = useOidcAuth();
  
  // Extract the token dynamically exactly how the components expect it
  const token = oidcAuth.user?.id_token || oidcAuth.user?.access_token || null;

  const value = {
    ...oidcAuth,
    token,
  };

  return <CustomAuthContext.Provider value={value}>{children}</CustomAuthContext.Provider>;
};

export const useAuth = () => useContext(CustomAuthContext);
