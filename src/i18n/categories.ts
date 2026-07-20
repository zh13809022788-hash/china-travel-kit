// Central category label translations
// Use getCategoryLabel(category, locale) wherever post.data.category is rendered

export type LocaleCode = 'en' | 'zh-tw' | 'ja' | 'ko' | 'ru' | 'fr' | 'de' | 'es' | 'th' | 'ms' | 'vi';

export const CATEGORY_LABELS: Record<string, Record<LocaleCode, string>> = {
  payment:    { en: 'Payment',     'zh-tw': '付款',     ja: '決済',       ko: '결제',     ru: 'Оплата',     fr: 'Paiement',    de: 'Bezahlung',   es: 'Pagos',        th: 'การชำระเงิน', ms: 'Pembayaran',   vi: 'Thanh toán' },
  esim:       { en: 'eSIM',        'zh-tw': 'eSIM',    ja: 'eSIM',      ko: 'eSIM',    ru: 'eSIM',      fr: 'eSIM',        de: 'eSIM',        es: 'eSIM',         th: 'eSIM',        ms: 'eSIM',         vi: 'eSIM' },
  transport:  { en: 'Transport',   'zh-tw': '交通',     ja: '交通',       ko: '교통',     ru: 'Транспорт', fr: 'Transport',   de: 'Verkehr',     es: 'Transporte',   th: 'การเดินทาง',  ms: 'Pengangkutan', vi: 'Giao thông' },
  essentials: { en: 'Essentials',  'zh-tw': '行前準備', ja: '旅行準備',   ko: '여행 준비', ru: 'Подготовка', fr: 'Préparatifs', de: 'Vorbereitung', es: 'Preparativos', th: 'สิ่งจำเป็น',  ms: 'Persiapan',    vi: 'Chuẩn bị' },
  food:       { en: 'Food',        'zh-tw': '美食',     ja: 'グルメ',     ko: '음식',     ru: 'Еда',       fr: 'Gastronomie', de: 'Essen',       es: 'Comida',       th: 'อาหาร',        ms: 'Makanan',      vi: 'Ẩm thực' },
};

export function getCategoryLabel(category: string, locale: string): string {
  const labels = CATEGORY_LABELS[category];
  if (!labels) return category;
  return labels[locale as LocaleCode] ?? labels.en;
}
