declare global {
  interface Window {
    grecaptcha?: {
      ready: (cb: () => void) => void;
      execute: (siteKey: string, options: { action: string }) => Promise<string>;
    };
  }
}

let scriptPromise: Promise<void> | null = null;

const ensureScript = (siteKey: string) => {
  if (scriptPromise) return scriptPromise;
  scriptPromise = new Promise((resolve, reject) => {
    if (window.grecaptcha) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = `https://www.google.com/recaptcha/api.js?render=${encodeURIComponent(siteKey)}`;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load reCAPTCHA script"));
    document.head.appendChild(script);
  });
  return scriptPromise;
};

export const getRecaptchaToken = async (action: string) => {
  const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY as string | undefined;
  if (!siteKey) {
    return "dev-bypass-token";
  }

  await ensureScript(siteKey);
  if (!window.grecaptcha) throw new Error("reCAPTCHA unavailable");

  return new Promise<string>((resolve, reject) => {
    window.grecaptcha?.ready(async () => {
      try {
        const token = await window.grecaptcha?.execute(siteKey, { action });
        if (!token) {
          reject(new Error("Failed to generate reCAPTCHA token"));
          return;
        }
        resolve(token);
      } catch (err) {
        reject(err);
      }
    });
  });
};
