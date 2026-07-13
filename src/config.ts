// Site-wide configuration.
//
// AdSense: after your AdSense account is approved, paste your publisher ID
// below (the "ca-pub-XXXXXXXXXXXXXXXX" value from your AdSense account).
// Leaving it empty keeps the dashed placeholder boxes and loads no ad script,
// which is the correct state while your account is still under review.
export const ADSENSE_PUBLISHER_ID = 'ca-pub-3673928456254144';

// Optional: per-format ad slot IDs from AdSense (the numeric "data-ad-slot"
// value you get when you create an ad unit). Fill these in once you have units.
export const ADSENSE_SLOTS: Record<string, string> = {
  banner: '',
  'in-article': '',
  sidebar: '',
};

// Microsoft Clarity project ID. Leave empty to disable Clarity tracking.
export const CLARITY_PROJECT_ID = 'xl5po1by2u';

// 填入真实联盟 https 链接后，全站对应 CTA 自动生效；留空则 CTA 隐藏
// （AffiliateCta 组件已处理 placeholder 非真链接时隐藏）。
export const AFFILIATE_LINKS: Record<string, string> = {
  esim: '',
  payment: '',
  transport: '',
};

// Interactive tools, shared between the homepage grid and the Tool Center.
// Order here controls display order; `featured` tools surface on the homepage.
export interface Tool {
  href: string;
  title: string;
  desc: string;
  icon: string;
  featured?: boolean;
}

export const TOOLS: Tool[] = [
  {
    href: '/tools/survival-kit/',
    title: 'China Survival Kit',
    desc: 'Use full-screen translation cards and saved checklists for arrival, restaurants, hotels, and local communication.',
    icon: 'KIT',
    featured: true,
  },
  {
    href: '/tools/show-to-driver/',
    title: 'Show to Driver',
    desc: 'Create a large Chinese address card for taxi drivers, hotel front desks, and asking directions on your phone.',
    icon: '🚕',
    featured: true,
  },
  {
    href: '/tools/visa-free-checker/',
    title: 'Visa-Free & Transit Checker',
    desc: 'See if you can enter China visa-free, use 240-hour transit, or need to apply — by nationality.',
    icon: '🛂',
    featured: true,
  },
  {
    href: '/tools/best-time-to-visit/',
    title: 'Best Time to Visit China',
    desc: 'See weather, crowds, and what to pack by city and month across major Chinese destinations.',
    icon: '🗓️',
    featured: true,
  },
  {
    href: '/tools/budget-cash-estimator/',
    title: 'Budget & Cash Estimator',
    desc: 'Estimate your total trip budget and how much cash to bring, by length, style, and city tier.',
    icon: '🧮',
    featured: true,
  },
  {
    href: '/tools/esim-comparison/',
    title: 'eSIM Plan Comparator',
    desc: 'Compare data allowance, validity, price, and network across the top China travel eSIMs.',
    icon: '📶',
    featured: true,
  },
  {
    href: '/tools/payment-checker/',
    title: 'Payment Compatibility Checker',
    desc: 'Check if your card works with Alipay and WeChat Pay, plus limits and fees, by nationality.',
    icon: '💳',
    featured: true,
  },
  {
    href: '/tools/app-availability-checker/',
    title: 'Will My Apps Work in China?',
    desc: 'Check if Google, WhatsApp, Instagram and more work without a VPN — with a local alternative for each.',
    icon: '📱',
    featured: true,
  },
  {
    href: '/tools/currency-converter/',
    title: 'RMB Currency Converter',
    desc: 'Convert your currency to yuan and back, and see what everyday things cost in China.',
    icon: '💱',
  },
  {
    href: '/tools/power-plug-checker/',
    title: 'Power Plug & Voltage Checker',
    desc: 'Find out if you need a plug adapter or voltage converter for China, based on your home country.',
    icon: '🔌',
  },
  {
    href: '/tools/clothing-size-converter/',
    title: 'Clothing & Shoe Size Converter',
    desc: 'Convert US, UK, and EU sizes to Chinese sizes for clothing and footwear before you shop.',
    icon: '👕',
  },
  {
    href: '/tools/essential-phrases/',
    title: 'Essential Chinese Phrases',
    desc: 'A printable list of must-know Mandarin phrases with pinyin — payment, transport, food, and help.',
    icon: '💬',
  },
];
