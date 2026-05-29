import apiInstance from "./api";
import { apiEndpoints } from "./endPointsConst";
import type { AxiosResponse } from "axios";
import type { ILoginRequest, IRegisterRequest } from "@/types/user";
import type { 
  IBookmarkCreateRequest, 
  IBookmarkUpdateRequest, 
  IBookmarkQueryParams 
} from "@/types/bookmark";
import type { ITagCreateRequest } from "@/types/tag";

// Auth
export const registerUser = (payload: IRegisterRequest): Promise<AxiosResponse<any>> => {
  return apiInstance.post(apiEndpoints.register, payload);
};

export const loginUser = (payload: ILoginRequest): Promise<AxiosResponse<any>> => {
  return apiInstance.post(apiEndpoints.login, payload);
};

export const fetchProfileApi = (): Promise<AxiosResponse<any>> => {
  return apiInstance.get(apiEndpoints.me);
};

// Bookmarks
export const getBookmarks = (params: IBookmarkQueryParams): Promise<AxiosResponse<any>> => {
  return apiInstance.get(apiEndpoints.bookmarks, { params });
};

export const getBookmark = (id: string): Promise<AxiosResponse<any>> => {
  return apiInstance.get(apiEndpoints.bookmarkDetail(id));
};

export const createBookmark = (payload: IBookmarkCreateRequest): Promise<AxiosResponse<any>> => {
  return apiInstance.post(apiEndpoints.bookmarks, payload);
};

export const updateBookmark = (id: string, payload: IBookmarkUpdateRequest): Promise<AxiosResponse<any>> => {
  return apiInstance.patch(apiEndpoints.bookmarkDetail(id), payload);
};

export const deleteBookmark = (id: string): Promise<AxiosResponse<any>> => {
  return apiInstance.delete(apiEndpoints.bookmarkDetail(id));
};

export const archiveBookmark = (id: string): Promise<AxiosResponse<any>> => {
  return apiInstance.patch(apiEndpoints.archiveBookmark(id));
};

export const refetchTitle = (id: string): Promise<AxiosResponse<any>> => {
  return apiInstance.post(apiEndpoints.refetchTitle(id));
};

// Tags
export const getTags = (): Promise<AxiosResponse<any>> => {
  return apiInstance.get(apiEndpoints.tags);
};

export const createTag = (payload: ITagCreateRequest): Promise<AxiosResponse<any>> => {
  return apiInstance.post(apiEndpoints.tags, payload);
};

export const getTagCloud = (): Promise<AxiosResponse<any>> => {
  return apiInstance.get(apiEndpoints.tagCloud);
};

// Admin
export const adminBrokenLinks = (params: any): Promise<AxiosResponse<any>> => {
  return apiInstance.get(apiEndpoints.adminBrokenLinks, { params });
};
