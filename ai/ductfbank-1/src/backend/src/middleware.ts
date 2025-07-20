import { Context, MiddlewareHandler, Next } from "hono"
import { getCookie } from "hono/cookie"
import { verify, VerifyOptions } from "jsonwebtoken"

interface JWTAuthOptions {
  cookieName?: string
  secret: string
  verifyOptions?: VerifyOptions
  loginPath?: string
};

/**
 * Middleware to validate JWT token stored in a cookie
 * @param options Configuration options for JWT validation
 * @returns Hono middleware handler
 */
export const jwtAuth = (options: JWTAuthOptions): MiddlewareHandler => {
  const {
    cookieName = 'bank-session',
    secret,
    verifyOptions = {},
    loginPath = '/login'
  } = options

  return async (c: Context, next: Next) => {
    // Get the JWT from the cookie
    const jwt = getCookie(c, cookieName)

    // If there's no JWT, redirect to login page
    if (!jwt) {
      return c.redirect(loginPath)
    }

    try {
      // Verify the JWT
      const payload = verify(jwt, secret, verifyOptions)

      // Store the decoded payload in the context for later use
      c.set('jwtPayload', payload)

      // Continue to the next middleware/handler
      await next()
    } catch (error) {
      // If JWT is invalid, redirect to login page
      return c.redirect(loginPath)
    }
  }
}