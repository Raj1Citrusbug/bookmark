import { envConf } from "@/config/envConfig";
import Cookies from "js-cookie";

const TOKEN_KEY = "__bm_token";

/**
 * Sets the token cookie with expiration aligned to the token's own expiry timestamp.
 * Assumes token is a JWT with an 'exp' claim (expiration time in seconds).
 *
 * @param token - JWT access token string
 */
export function setTokenCookieWithExpiryFromToken(token: string) {
  try {
    const base64Payload = token.split(".")[1];
    const payload = JSON.parse(atob(base64Payload));

    if (!payload.exp) {
      throw new Error("Token does not contain 'exp' claim");
    }

    const expiryDate = new Date(payload.exp * 1000);

    Cookies.set(TOKEN_KEY, token, {
      expires: expiryDate,
      secure: Boolean(Number(envConf.cookieSecure)),
      sameSite: "Lax",
      path: "/",
    });
  } catch (error) {
    console.error("Failed to set token cookie with expiry from token:", error);
    Cookies.set(TOKEN_KEY, token, {
      secure: Boolean(Number(envConf.cookieSecure)),
      sameSite: "Lax",
      path: "/",
    });
  }
}

/**
 * Checks if the token cookie exists.
 * @returns {boolean} True if present
 */
export function isTokenPresent(): boolean {
  const token = Cookies.get(TOKEN_KEY);
  return !!token;
}

/**
 * Gets the token value from the cookie.
 * @returns {string | undefined} Token string if present
 */
export function getToken(): string | undefined {
  return Cookies.get(TOKEN_KEY);
}

/**
 * Removes the token cookie.
 */
export function removeToken(): void {
  Cookies.remove(TOKEN_KEY);
}
