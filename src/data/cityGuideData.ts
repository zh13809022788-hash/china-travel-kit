// Central city guide metadata for China cities page
// Add a new entry here + create a city guide post → auto appears on /cities/
// mapX/mapY use equirectangular projection (no borders, just geographic positions)

export interface CityGuideEntry {
  slug: string;
  name: string;
  nameZh: string;
  desc: string;
  days: string;
  bestSeason: string;
  difficulty: string;
  whyGo: string;
  next: string;
  nextLabel: string;
  mapX: number;
  mapY: number;
}

export const CITY_GUIDES: CityGuideEntry[] = [
  {
    slug: 'beijing-city-guide-for-foreigners',
    name: 'Beijing', nameZh: '北京',
    desc: 'Best for history, hutongs, the Great Wall, and first-time classic sightseeing.',
    days: '4-5 days', bestSeason: 'September-October', difficulty: 'Medium',
    whyGo: 'Imperial history, museums, and the easiest Great Wall access.',
    next: '/posts/beijing-daxing-airport-to-city-center-a-first-timer-s-guide/',
    nextLabel: 'Daxing airport transfer guide',
    mapX: 460, mapY: 208, // 116.4°E, 39.9°N
  },
  {
    slug: 'shanghai-city-guide-for-foreigners',
    name: 'Shanghai', nameZh: '上海',
    desc: 'Best for an easy landing, international food, skyline walks, and strong metro coverage.',
    days: '3-4 days', bestSeason: 'March-May, October-November', difficulty: 'Easy',
    whyGo: 'The smoothest first stop for metro, airports, food, and English-friendly services.',
    next: '/posts/shanghai-metro-for-foreigners-tickets-qr-codes-transfers/',
    nextLabel: 'Shanghai metro guide',
    mapX: 509, mapY: 324, // 121.5°E, 31.2°N
  },
  {
    slug: 'chengdu-city-guide-for-foreigners',
    name: 'Chengdu', nameZh: '成都',
    desc: 'Best for Sichuan food, teahouse pace, pandas, and a softer big-city rhythm.',
    days: '3-5 days', bestSeason: 'March-June, September-November', difficulty: 'Medium',
    whyGo: 'Pandas, Sichuan food, teahouses, lower costs, and western China side trips.',
    next: '/posts/chengdu-street-food-safety-spice-levels-what-to-order/',
    nextLabel: 'Chengdu street-food guide',
    mapX: 341, mapY: 332, // 104.1°E, 30.6°N
  },
  {
    slug: 'xian-city-guide-for-foreigners',
    name: "Xi'an", nameZh: '西安',
    desc: "Best for ancient history, the Terracotta Warriors, old city walls, and hands-on Chinese heritage.",
    days: '3-4 days', bestSeason: 'March-May, September-November', difficulty: 'Medium',
    whyGo: "Terracotta Warriors, ancient city wall, Muslim Quarter food street, and a deep sense of Chinese history.",
    next: '/posts/china-high-speed-rail-guide-foreigners/',
    nextLabel: "High-speed rail to Xi'an",
    mapX: 387, mapY: 283, // 108.9°E, 34.3°N
  },
  {
    slug: 'guangzhou-city-guide-for-foreigners',
    name: 'Guangzhou', nameZh: '广州',
    desc: "Best for Cantonese food, trade city energy, southern gateway, and easy Hong Kong access.",
    days: '3-4 days', bestSeason: 'October-December, March-April', difficulty: 'Medium',
    whyGo: 'Cantonese dim sum, Chen Clan Academy, Canton Tower, and a warmer southern alternative.',
    next: '/posts/ordering-food-in-china-without-chinese-meituan-ele-me/',
    nextLabel: 'Cantonese food guide',
    mapX: 430, mapY: 432, // 113.3°E, 23.1°N
  },
  {
    slug: 'chongqing-city-guide-for-foreigners',
    name: 'Chongqing', nameZh: '重庆',
    desc: 'Best for Sichuan hotpot, futuristic skyline, mountain-city terrain, and Yangtze River cruises.',
    days: '3-4 days', bestSeason: 'March-May, September-November', difficulty: 'Hard',
    whyGo: 'Chongqing hotpot, Hongya Cave, night skyline, Yangtze cable car, and a uniquely vertical city.',
    next: '/food/',
    nextLabel: 'Chongqing food guide',
    mapX: 364, mapY: 345, // 106.5°E, 29.6°N
  },
  {
    slug: 'hangzhou-city-guide-for-foreigners',
    name: 'Hangzhou', nameZh: '杭州',
    desc: 'Best for West Lake, green scenery, weekend pacing, and a polished city break.',
    days: '2-3 days', bestSeason: 'March-May, September-November', difficulty: 'Easy-medium',
    whyGo: 'West Lake, tea villages, temples, and a calm high-speed rail add-on from Shanghai.',
    next: '/transport/',
    nextLabel: 'Plan trains and local transport',
    mapX: 497, mapY: 336, // 120.2°E, 30.3°N
  },
  {
    slug: 'sanya-city-guide-for-foreigners',
    name: 'Sanya', nameZh: '三亚',
    desc: 'Best for warm winter weather, resort stays, beach time, and Hainan side trips.',
    days: '3-7 days', bestSeason: 'November-April', difficulty: 'Medium',
    whyGo: 'China beach time, winter sun, seafood, resorts, and longer seasonal stays.',
    next: '/posts/what-to-pack-for-china-a-season-by-season-checklist/',
    nextLabel: 'Seasonal packing guide',
    mapX: 393, mapY: 496, // 109.5°E, 18.3°N
  },
  {
    slug: 'nanjing-city-guide-for-foreigners',
    name: 'Nanjing', nameZh: '南京',
    desc: "Best for Ming dynasty history, Confucian temples, Qinhuai River nights, and a calmer cultural pace.",
    days: '2-3 days', bestSeason: 'March-May, September-November', difficulty: 'Easy-medium',
    whyGo: 'Ming Xiaoling Mausoleum, Sun Yat-sen Mausoleum, Confucius Temple, and a relaxed historical atmosphere.',
    next: '/posts/china-high-speed-rail-guide-foreigners/',
    nextLabel: 'High-speed rail to Nanjing',
    mapX: 483, mapY: 312, // 118.8°E, 32.1°N
  },
  {
    slug: 'guilin-city-guide-for-foreigners',
    name: 'Guilin', nameZh: '桂林',
    desc: "Best for karst landscapes, Li River cruise, Yangshuo countryside, and outdoor adventure.",
    days: '3-4 days', bestSeason: 'March-October', difficulty: 'Medium',
    whyGo: 'Li River, Yangshuo, Longji Rice Terraces, Reed Flute Cave, and China\'s most scenic landscapes.',
    next: '/posts/china-high-speed-rail-guide-foreigners/',
    nextLabel: 'High-speed rail to Guilin',
    mapX: 401, mapY: 403, // 110.3°E, 25.3°N
  },
];
