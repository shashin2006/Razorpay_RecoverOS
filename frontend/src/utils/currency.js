/**
 * Formats minor currency units (e.g. paise for INR: 100 paise = 1 INR) into human-readable INR format.
 * 
 * Example:
 * 50000 minor units -> ₹500
 * 500000 minor units -> ₹5,000
 * 12500000 minor units -> ₹1.25L
 */
export function formatMinorUnitsToINR(minorUnits, options = {}) {
  if (minorUnits === null || minorUnits === undefined || isNaN(minorUnits)) {
    return '₹0';
  }

  const { compact = false, showDecimals = false } = options;
  const majorUnits = Number(minorUnits) / 100;

  if (compact && Math.abs(majorUnits) >= 10000000) {
    const cr = majorUnits / 10000000;
    return `₹${cr.toFixed(2).replace(/\.00$/, '')}Cr`;
  }

  if (compact && Math.abs(majorUnits) >= 100000) {
    const lakhs = majorUnits / 100000;
    return `₹${lakhs.toFixed(2).replace(/\.00$/, '')}L`;
  }

  if (compact && Math.abs(majorUnits) >= 1000) {
    const k = majorUnits / 1000;
    return `₹${k.toFixed(1).replace(/\.0$/, '')}k`;
  }

  // Standard Indian Currency Number Formatting (en-IN)
  try {
    const formatted = new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: showDecimals ? 2 : (majorUnits % 1 === 0 ? 0 : 2),
      minimumFractionDigits: showDecimals ? 2 : 0,
    }).format(majorUnits);

    return formatted;
  } catch {
    return `₹${majorUnits.toLocaleString('en-IN')}`;
  }
}

/**
 * Formats percentage rates.
 * Handles both decimal fractions (0.425 -> 42.5%) and already multiplied percentages (42.5 -> 42.5%).
 */
export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined || isNaN(value)) {
    return '0.0%';
  }

  let num = Number(value);
  // If value is between 0 and 1 (exclusive of 1 unless exactly 1.0 representing 100%), treat as ratio
  if (num <= 1 && num > 0) {
    num = num * 100;
  }

  return `${num.toFixed(decimals)}%`;
}

/**
 * Formats count numbers with Indian grouping
 */
export function formatCount(value) {
  if (value === null || value === undefined || isNaN(value)) {
    return '0';
  }
  return Number(value).toLocaleString('en-IN');
}
