/**
 * Authentication Service
 * Handles JWT token management and secure storage
 */

import { jwtDecode } from 'jwt-decode';
import { API_BASE_URL } from './api';

interface TokenPayload {
  sub: string;
  exp: number;
  iat: number;
}

interface AuthTokens {
  access_token: string;
  refresh_token?: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'user' | 'admin';
  createdAt: string;
}

interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

interface SignupResponse {
  user: User;
  tokens: AuthTokens;
}

class AuthService {
  private readonly ACCESS_TOKEN_KEY = 'apollo_access_token';
  private readonly REFRESH_TOKEN_KEY = 'apollo_refresh_token';
  
  /**
   * Store tokens securely
   */
  setTokens(tokens: AuthTokens): void {
    // Store in sessionStorage for better security
    sessionStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access_token);
    if (tokens.refresh_token) {
      sessionStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refresh_token);
    }
  }
  
  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return sessionStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  /**
   * Get token (alias for getAccessToken)
   */
  getToken(): string | null {
    return this.getAccessToken();
  }
  
  /**
   * Get refresh token
   */
  getRefreshToken(): string | null {
    return sessionStorage.getItem(this.REFRESH_TOKEN_KEY);
  }
  
  /**
   * Check if token is valid
   */
  isTokenValid(token: string): boolean {
    try {
      const decoded = jwtDecode<TokenPayload>(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp > currentTime;
    } catch {
      return false;
    }
  }
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    return token ? this.isTokenValid(token) : false;
  }
  
  /**
   * Get user email from token
   */
  getUserEmail(): string | null {
    try {
      const token = this.getAccessToken();
      if (!token) return null;
      
      const decoded = jwtDecode<TokenPayload>(token);
      return decoded.sub;
    } catch {
      return null;
    }
  }
  
  /**
   * Clear all tokens
   */
  logout(): void {
    sessionStorage.removeItem(this.ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Remove token (alias for logout)
   */
  removeToken(): void {
    this.logout();
  }
  
  /**
   * Refresh access token
   */
  async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) return false;
      
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const tokens = await response.json();
        this.setTokens(tokens);
        return true;
      }
      
      return false;
    } catch {
      return false;
    }
  }

  /**
   * Login user
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    // Mock authentication for now - in production, this would call the backend
    if (email === 'demo@apollo.ai' && password === 'demo123') {
      const mockUser: User = {
        id: '1',
        email: email,
        name: 'Demo User',
        role: 'user',
        createdAt: new Date().toISOString(),
      };
      
      const mockTokens: AuthTokens = {
        access_token: 'mock_access_token_' + Date.now(),
        refresh_token: 'mock_refresh_token_' + Date.now(),
      };
      
      this.setTokens(mockTokens);
      return { user: mockUser, tokens: mockTokens };
    }
    
    throw new Error('Invalid credentials. Use demo@apollo.ai / demo123');
  }

  /**
   * Signup user
   */
  async signup(name: string, email: string, password: string): Promise<SignupResponse> {
    // Mock signup for now - in production, this would call the backend
    const mockUser: User = {
      id: Date.now().toString(),
      email: email,
      name: name,
      role: 'user',
      createdAt: new Date().toISOString(),
    };
    
    const mockTokens: AuthTokens = {
      access_token: 'mock_access_token_' + Date.now(),
      refresh_token: 'mock_refresh_token_' + Date.now(),
    };
    
    this.setTokens(mockTokens);
    return { user: mockUser, tokens: mockTokens };
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const token = this.getAccessToken();
    if (!token) {
      throw new Error('No token available');
    }

    // Mock user data for now
    return {
      id: '1',
      email: 'demo@apollo.ai',
      name: 'Demo User',
      role: 'user',
      createdAt: new Date().toISOString(),
    };
  }

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const token = this.getAccessToken();
    if (!token) {
      throw new Error('No token available');
    }

    // Mock profile update for now
    return {
      id: '1',
      email: 'demo@apollo.ai',
      name: data.name || 'Demo User',
      role: 'user',
      createdAt: new Date().toISOString(),
      ...data,
    };
  }
}

export const authService = new AuthService(); 