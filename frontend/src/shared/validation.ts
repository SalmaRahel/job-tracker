const TYPO_DOMAINS: Record<string, string> = {
  "gmal.com": "gmail.com",
  "gmial.com": "gmail.com",
  "gamil.com": "gmail.com",
  "gmail.co": "gmail.com",
  "gmaill.com": "gmail.com",
  "gmai.com": "gmail.com",
  "hotmial.com": "hotmail.com",
  "hotmal.com": "hotmail.com",
  "hotnail.com": "hotmail.com",
  "outlok.com": "outlook.com",
  "outloook.com": "outlook.com",
  "yaho.com": "yahoo.com",
  "yahooo.com": "yahoo.com",
};

export const isValidPhone = (value: string) => {
  const phone = value.trim();
  if (!phone) return true;
  const digits = phone.replace(/[^0-9]/g, "").length;
  return /^\+?[0-9\s\-.()]+$/.test(phone) && digits >= 8 && digits <= 15;
};

export function isValidEmail(value: string) {
  const parts = value.trim().split("@");
  if (parts.length !== 2) return false;
  const [local, domain] = parts;
  const localOk = /^[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+$/.test(local) && !/^\.|\.$|\.\./.test(local);
  return localOk && /^([A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}$/.test(domain);
}

export function suggestEmail(value: string) {
  const [local, domain] = value.trim().split("@");
  const fixed = domain && TYPO_DOMAINS[domain.toLowerCase()];
  return fixed ? `${local}@${fixed}` : null;
}

export function emailError(value: string) {
  if (!isValidEmail(value)) return "Enter a valid email address";
  const suggestion = suggestEmail(value);
  return suggestion ? `Did you mean ${suggestion}?` : null;
}
