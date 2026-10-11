export const isValidPhone = (value: string) => {
  const phone = value.trim();
  if (!phone) return true;
  const digits = phone.replace(/[^0-9]/g, "").length;
  return /^\+?[0-9\s\-.()]+$/.test(phone) && digits >= 8 && digits <= 15;
};

export const isValidEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
