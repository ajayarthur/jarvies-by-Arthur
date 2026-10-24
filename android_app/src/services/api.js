import { StorageService } from "./storage";

export class ApiError extends Error {
  constructor(message, status = 0, isOffline = false) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.isOffline = isOffline;
  }
}

export const JarvisApi = {
  async _fetch(endpoint, options = {}, customTimeout = 8000) {
    const baseUrl = await StorageService.getHostUrl();
    const token = await StorageService.getAuthToken();

    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
      headers["X-Jarvis-Token"] = token;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), customTimeout);

    try {
      const url = `${baseUrl}${endpoint}`;
      const res = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const contentType = res.headers.get("content-type") || "";
      const isJson = contentType.includes("application/json");
      const data = isJson ? await res.json() : await res.text();

      if (!res.ok) {
        if (res.status === 401) {
          throw new ApiError("Authentication failed. Please re-pair with companion PC in Settings.", 401);
        }
        const errorMsg = (typeof data === "object" && data.error) || `Server error (${res.status})`;
        throw new ApiError(errorMsg, res.status);
      }

      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err instanceof ApiError) throw err;
      if (err.name === "AbortError") {
        throw new ApiError("Request timed out. Companion computer may be busy or offline.", 408, true);
      }
      throw new ApiError(`Cannot reach Jarvis companion at ${baseUrl}. Ensure both phone and PC are on the same Wi-Fi.`, 0, true);
    }
  },

  async checkHealth(targetUrl = null) {
    const baseUrl = targetUrl || (await StorageService.getHostUrl());
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3500);

    try {
      const res = await fetch(`${baseUrl}/api/health`, {
        method: "GET",
        signal: controller.signal
      });
      clearTimeout(timer);
      if (res.ok) {
        return await res.json();
      }
      return { status: "error", code: res.status };
    } catch (err) {
      clearTimeout(timer);
      return { status: "offline", error: err.message };
    }
  },

  async pairDevice(pairingCode, deviceName = "Android Mobile") {
    const data = await this._fetch("/api/auth/pair", {
      method: "POST",
      body: JSON.stringify({
        pairing_code: pairingCode.trim(),
        device_name: deviceName
      })
    }, 5000);

    if (data.success && data.token) {
      await StorageService.setAuthToken(data.token);
      return data;
    }
    throw new ApiError(data.error || "Pairing failed. Incorrect code.");
  },

  async sendCommand(message, voice = "en-IN-PrabhatNeural") {
    return await this._fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message: message.trim(),
        voice: voice,
        play_on_speaker: false
      })
    }, 15000);
  },

  async executeTool(action, param = "") {
    return await this._fetch("/api/execute_tool", {
      method: "POST",
      body: JSON.stringify({ action, param })
    }, 8000);
  },

  async confirmAction(actionId, confirmed = true) {
    return await this._fetch("/api/confirm_action", {
      method: "POST",
      body: JSON.stringify({
        action_id: actionId,
        confirmed: confirmed
      })
    }, 8000);
  },

  async getCapabilities() {
    return await this._fetch("/api/capabilities", { method: "GET" }, 5000);
  },

  async getSystemStats() {
    return await this._fetch("/api/system/stats", { method: "GET" }, 4000);
  }
};
