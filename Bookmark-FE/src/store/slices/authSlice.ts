import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { User, ApiUser } from "@/types/user";
import type { UserRole } from "@/constants/roles";
import { getToken, removeToken } from "@/utils/cookie";
import { fetchProfileApi } from "@/network";

const transformApiUser = (apiUser: ApiUser): User => {
  return {
    id: apiUser.id,
    name: apiUser.name,
    email: apiUser.email,
    role: apiUser.role as UserRole,
    isActive: apiUser.is_active,
  };
};

export const fetchProfile = createAsyncThunk(
  "auth/fetchProfile",
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetchProfileApi();
      if (response.data.success) {
        return transformApiUser(response.data.data);
      }
      return rejectWithValue(response.data.message || "Failed to fetch profile");
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || "Something went wrong"
      );
    }
  }
);

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
  error: string | null;
  isSidebarCollapsed: boolean;
}

const token = getToken();

const initialState: AuthState = {
  user: null,
  isAuthenticated: !!token,
  isLoading: !!token,
  token: token || null,
  error: null,
  isSidebarCollapsed: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setAuth: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      state.isLoading = false;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.isLoading = false;
      state.error = null;
      removeToken();
    },
    clearError: (state) => {
      state.error = null;
    },
    initializeAuth: (state) => {
      const currentToken = getToken();
      if (currentToken) {
        state.token = currentToken;
        state.isAuthenticated = true;
      } else {
        state.token = null;
        state.isAuthenticated = false;
      }
      state.isLoading = false;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.isSidebarCollapsed = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchProfile.fulfilled, (state, action: PayloadAction<User>) => {
        state.user = action.payload;
        state.isAuthenticated = true;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
        state.user = null;
        removeToken();
      });
  },
});

export const { setAuth, logout, initializeAuth, clearError, setSidebarCollapsed } = authSlice.actions;
export default authSlice.reducer;
export { transformApiUser };
