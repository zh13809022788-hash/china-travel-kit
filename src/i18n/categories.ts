// Central category label translations
// Use getCategoryLabel(category, locale) wherever post.data.category is rendered

export type LocaleCode = 'en' | 'zh-TW' | 'ja' | 'ko' | 'ru' | 'fr' | 'de' | 'es';

export const CATEGORY_LABELS: Record<string, Record<LocaleCode, string>> = {
  payment:    { en: 'Payment',     'zh-TW': '付款',     ja: '決済',       ko: '결제',     ru: 'Оплата',     fr: 'Paiement',    de: 'Bezahlung',   es: 'Pagos' },
  esim:       { en: 'eSIM',        'zh-TW': 'eSIM',    ja: 'eSIM',      ko: 'eSIM',    ru: 'eSIM',      fr: 'eSIM',        de: 'eSIM',        es: 'eSIM' },
  transport:  { en: 'Transport',   'zh-TW': '交通',     ja: '交通',       ko: '교통',     ru: 'Транспорт', fr: 'Transport',   de: 'Verkehr',     es: 'Transporte' },
  essentials: { en: 'Essentials',  'zh-TW': '行前準備', ja: '旅行準備',   ko: '여행 준비', ru: 'Подготовка', fr: 'Préparatifs', de: 'Vorbereitung', es: 'Preparativos' },
  food:       { en: 'Food',        'zh-TW': '美食',     ja: 'グルメ',     ko: '음식',     ru: 'Еда',       fr: 'Gastronomie', de: 'Essen',       es: 'Comida' },
};

export function getCategoryLabel(category: string, locale: string): string {
  const labels = CATEGORY_LABELS[category];
  if (!labels) return category;
  return labels[locale as LocaleCode] ?? labels.en;
}
