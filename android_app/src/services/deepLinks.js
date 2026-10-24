import { Linking } from "react-native";

export const DeepLinkService = {
  async openApp(appName) {
    const key = appName.toLowerCase().trim();
    const links = {
      whatsapp: { app: "whatsapp://", web: "https://web.whatsapp.com" },
      spotify: { app: "spotify://", web: "https://open.spotify.com" },
      youtube: { app: "vnd.youtube://", web: "https://youtube.com" },
      github: { app: "github://", web: "https://github.com" },
      linkedin: { app: "linkedin://", web: "https://linkedin.com" },
      chatgpt: { app: "chatgpt://", web: "https://chatgpt.com" }
    };

    const target = links[key];
    if (!target) return false;

    try {
      const canOpen = await Linking.canOpenURL(target.app);
      if (canOpen) {
        await Linking.openURL(target.app);
        return true;
      } else {
        await Linking.openURL(target.web);
        return true;
      }
    } catch {
      await Linking.openURL(target.web);
      return true;
    }
  }
};
