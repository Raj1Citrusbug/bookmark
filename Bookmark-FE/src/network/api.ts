import { envConf } from "@/config/envConfig";
import { getToken } from "@/utils/cookie";
import type {
    AxiosInstance,
    AxiosResponse,
    InternalAxiosRequestConfig,
} from "axios";
import axios, { AxiosError } from "axios";

const apiInstance: AxiosInstance = axios.create({
    baseURL: envConf.baseApi,
    timeout: 150000,
    headers: {
        "Content-Type": "application/json",
    },
    responseType: "json",
});

// Request interceptor to inject JWT Token
apiInstance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        try {
            const token = getToken();
            config.headers = config.headers || {};
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        } catch (error) {
            console.error("Error while request interceptor", error);
            return config;
        }
    },
    (error) => Promise.reject(error)
);

// Response interceptor
apiInstance.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

export default apiInstance;
