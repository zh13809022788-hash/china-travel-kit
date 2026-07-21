// Central city guide metadata for China cities page
// Add a new entry here + create a city guide post → auto appears on /cities/
// mapX/mapY use equirectangular projection (no borders, just geographic positions)

export interface CityGuideEntry {
  slug: string;
  name: string;
  nameZh: string;
  nameJa: string;
  nameKo: string;
  nameDe: string;
  nameEs: string;
  nameFr: string;
  nameRu: string;
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

export function cityName(guide: CityGuideEntry, locale: string): string {
  const map: Record<string, string> = {
    en: guide.name, 'zh-tw': guide.nameZh, ja: guide.nameJa,
    ko: guide.nameKo, de: guide.nameDe, es: guide.nameEs,
    fr: guide.nameFr, ru: guide.nameRu,
  };
  return map[locale] ?? guide.name;
}

export const CITY_GUIDES: CityGuideEntry[] = [
  {
    slug: 'beijing-city-guide-for-foreigners',
    name: 'Beijing', nameZh: '北京', nameJa: '北京', nameKo: '베이징', nameDe: 'Peking', nameEs: 'Pekín', nameFr: 'Pékin', nameRu: 'Пекин',
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
  {
    slug: 'shenzhen-city-guide-for-foreigners',
    name: 'Shenzhen', nameZh: '深圳',
    desc: 'China tech hub with modern architecture, easy Hong Kong access.',
    days: '2-3 days', bestSeason: 'Oct-Apr', difficulty: 'Easy',
    whyGo: 'Tech innovation, OCT Loft, seamless border from Hong Kong.',
    mapX: -520, mapY: -781,
  },
  {
    slug: 'wuhan-city-guide-for-foreigners',
    name: 'Wuhan', nameZh: '武汉',
    desc: 'Central China hub on Yangtze, cherry blossoms, hot dry noodles.',
    days: '3-4 days', bestSeason: 'Mar-Apr, Sep-Nov', difficulty: 'Medium',
    whyGo: 'Yellow Crane Tower, cherry blossoms, vibrant food scene.',
    mapX: -435, mapY: -784,
  },
  {
    slug: 'kunming-city-guide-for-foreigners',
    name: 'Kunming', nameZh: '昆明',
    desc: 'Spring City with year-round mild weather, gateway to Yunnan.',
    days: '3-5 days', bestSeason: 'Mar-Oct', difficulty: 'Medium',
    whyGo: 'Eternal spring, Stone Forest, Dianchi Lake.',
    mapX: -493, mapY: -629,
  },
  {
    slug: 'xiamen-city-guide-for-foreigners',
    name: 'Xiamen', nameZh: '厦门',
    desc: 'Coastal Fujian city with Gulangyu Island and Minnan culture.',
    days: '3-4 days', bestSeason: 'Mar-May, Oct-Dec', difficulty: 'Easy',
    whyGo: 'Gulangyu Island, colonial architecture, seafood.',
    mapX: -499, mapY: -834,
  },
  {
    slug: 'suzhou-city-guide-for-foreigners',
    name: 'Suzhou', nameZh: '苏州',
    desc: 'Classical gardens and canals — Venice of the East.',
    days: '2-3 days', bestSeason: 'Mar-May, Sep-Nov', difficulty: 'Easy',
    whyGo: 'UNESCO gardens, Grand Canal, silk, day trip from SH.',
    mapX: -427, mapY: -868,
  },
  {
    slug: 'dalian-city-guide-for-foreigners',
    name: 'Dalian', nameZh: '大连',
    desc: 'Russian/Japanese-influenced port with beaches and seafood.',
    days: '3-4 days', bestSeason: 'May-Oct', difficulty: 'Medium',
    whyGo: 'Russian Street, Xinghai Square, beach resorts.',
    mapX: -348, mapY: -881,
  },
  {
    slug: 'qingdao-city-guide-for-foreigners',
    name: 'Qingdao', nameZh: '青岛',
    desc: 'German-colonial port famous for Tsingtao beer and beaches.',
    days: '3-4 days', bestSeason: 'May-Oct', difficulty: 'Easy',
    whyGo: 'Tsingtao Brewery, German architecture, Laoshan.',
    mapX: -377, mapY: -865,
  },
  {
    slug: 'changsha-city-guide-for-foreigners',
    name: 'Changsha', nameZh: '长沙',
    desc: 'Hunan capital known for spicy food and youth culture.',
    days: '2-3 days', bestSeason: 'Apr-Oct', difficulty: 'Medium',
    whyGo: 'Hunan cuisine, Yuelu Academy, street food.',
    mapX: -460, mapY: -766,
  },
  {
    slug: 'harbin-city-guide-for-foreigners',
    name: 'Harbin', nameZh: '哈尔滨',
    desc: 'Ice festival capital with Russian architecture.',
    days: '3-4 days', bestSeason: 'Dec-Feb (festival)', difficulty: 'Hard (winter)',
    whyGo: 'Ice Festival, Saint Sophia Cathedral, Tiger Park.',
    mapX: -275, mapY: -948,
  },
  {
    slug: 'lhasa-city-guide-for-foreigners',
    name: 'Lhasa', nameZh: '拉萨',
    desc: 'Tibetan capital at 3,650m with Potala Palace.',
    days: '4-6 days', bestSeason: 'Apr-Oct', difficulty: 'Hard',
    whyGo: 'Potala Palace, Jokhang Temple, Tibetan culture.',
    mapX: -444, mapY: -474,
  },
  {
    slug: 'dali-city-guide-for-foreigners',
    name: 'Dali', nameZh: '大理',
    desc: 'Ancient town by Erhai Lake with Bai culture.',
    days: '3-5 days', bestSeason: 'Mar-May, Sep-Nov', difficulty: 'Easy-Med',
    whyGo: 'Erhai Lake, Cangshan, old town, coffee scene.',
    mapX: -487, mapY: -596,
  },
  {
    slug: 'luoyang-city-guide-for-foreigners',
    name: 'Luoyang', nameZh: '洛阳',
    desc: 'Ancient capital with Longmen Grottoes.',
    days: '2-3 days', bestSeason: 'Apr-May, Sep-Oct', difficulty: 'Medium',
    whyGo: 'Longmen Grottoes (UNESCO), White Horse Temple.',
    mapX: -393, mapY: -760,
  },
  {
    slug: 'tianjin-city-guide-for-foreigners',
    name: 'Tianjin', nameZh: '天津',
    desc: 'Port city near Beijing with European concessions.',
    days: '1-2 days', bestSeason: 'Mar-May, Sep-Nov', difficulty: 'Easy',
    whyGo: 'Five Great Avenues, Tianjin Eye, day trip from BJ.',
    mapX: -345, mapY: -822,
  },
  {
    slug: 'jinan-city-guide-for-foreigners',
    name: 'Jinan', nameZh: '济南',
    desc: 'City of Springs with natural artesian springs.',
    days: '2-3 days', bestSeason: 'Mar-May, Sep-Nov', difficulty: 'Medium',
    whyGo: 'Baotu Spring, Daming Lake, gateway to Mount Tai.',
    mapX: -371, mapY: -820,
  },
  {
    slug: 'zhengzhou-city-guide-for-foreigners',
    name: 'Zhengzhou', nameZh: '郑州',
    desc: 'Transport hub and gateway to Shaolin Temple.',
    days: '1-2 days', bestSeason: 'Mar-May, Sep-Nov', difficulty: 'Easy',
    whyGo: 'Shaolin Temple day trip, Henan Museum.',
    mapX: -391, mapY: -776,
  },
  {
    slug: 'huangshan-city-guide-for-foreigners',
    name: 'Huangshan (Mt. Huang)', nameZh: '黄山',
    desc: 'Iconic granite peaks, hot springs, and Xidi/Hongcun villages.',
    days: '3-4 days', bestSeason: 'Mar-May, Sep-Oct', difficulty: 'Medium',
    whyGo: 'Yellow Mountain scenery, ancient Huizhou villages.',
    mapX: -444, mapY: -837,
  },
  {
    slug: 'zhangjiajie-city-guide-for-foreigners',
    name: 'Zhangjiajie', nameZh: '张家界',
    desc: 'Avatar-inspired sandstone pillars and glass bridge.',
    days: '3-4 days', bestSeason: 'Apr-Jun, Sep-Oct', difficulty: 'Medium',
    whyGo: 'Avatar Hallelujah Mountain, glass bridge, Tianmen Mountain.',
    mapX: -447, mapY: -733,
  },
  {
    slug: 'dunhuang-city-guide-for-foreigners',
    name: 'Dunhuang', nameZh: '敦煌',
    desc: 'Silk Road outpost with Mogao Caves and desert dunes.',
    days: '2-3 days', bestSeason: 'May-Oct', difficulty: 'Medium',
    whyGo: 'Mogao Caves, Singing Sand Dunes, Crescent Moon Spring.',
    mapX: -335, mapY: -522,
  },
  {
    slug: 'datong-city-guide-for-foreigners',
    name: 'Datong', nameZh: '大同',
    desc: 'Northern city with Yungang Grottoes and Hanging Temple.',
    days: '2-3 days', bestSeason: 'May-Oct', difficulty: 'Medium',
    whyGo: 'Yungang Grottoes, Hanging Temple, ancient Great Wall.',
    mapX: -335, mapY: -770,
  },
  {
    slug: 'xishuangbanna-city-guide-for-foreigners',
    name: 'Xishuangbanna', nameZh: '西双版纳',
    desc: 'Tropical Dai minority region with rainforest and elephants.',
    days: '3-5 days', bestSeason: 'Nov-Apr', difficulty: 'Medium',
    whyGo: 'Dai culture, tropical jungle, wild elephants, night markets.',
    mapX: -525, mapY: -604,
  },
  {
    slug: 'kashgar-city-guide-for-foreigners',
    name: 'Kashgar', nameZh: '喀什',
    desc: 'Silk Road oasis with Uyghur culture and Sunday Bazaar.',
    days: '3-4 days', bestSeason: 'May-Oct', difficulty: 'Hard',
    whyGo: 'Old City, Sunday livestock market, Uyghur cuisine.',
    mapX: -341, mapY: -273,
  },
  {
    slug: 'jingdezhen-city-guide-for-foreigners',
    name: 'Jingdezhen', nameZh: '景德镇',
    desc: 'Porcelain capital of China with ceramic history.',
    days: '2-3 days', bestSeason: 'Mar-May, Sep-Nov', difficulty: 'Medium',
    whyGo: 'Porcelain museums, pottery workshops, ancient kilns.',
    mapX: -448, mapY: -822,
  },
  {
    slug: 'guizhou-city-guide-for-foreigners',
    name: 'Guizhou (Guiyang)', nameZh: '贵阳',
    desc: 'Karst landscapes and Miao/Dong minority villages.',
    days: '4-6 days', bestSeason: 'Mar-Oct', difficulty: 'Hard',
    whyGo: 'Huangguoshu Waterfall, Miao villages, Dong drum towers.',
    mapX: -476, mapY: -681,
  },
  {
    slug: 'lanzhou-city-guide-for-foreigners',
    name: 'Lanzhou', nameZh: '兰州',
    desc: 'Yellow River city, gateway to the Tibetan Plateau.',
    days: '2-3 days', bestSeason: 'May-Oct', difficulty: 'Medium',
    whyGo: 'Yellow River, beef noodles, Bingling Temple Grottoes.',
    mapX: -377, mapY: -644,
  },
  {
    slug: 'xining-city-guide-for-foreigners',
    name: 'Xining', nameZh: '西宁',
    desc: 'Gateway to Qinghai Lake and Tibetan Amdo region.',
    days: '2-3 days', bestSeason: 'Jun-Sep', difficulty: 'Medium',
    whyGo: 'Qinghai Lake, Ta\u2019er Monastery, Tibetan culture.',
    mapX: -372, mapY: -617,
  },
  {
    slug: 'urumqi-city-guide-for-foreigners',
    name: 'Urumqi', nameZh: '乌鲁木齐',
    desc: 'Capital of Xinjiang with Uyghur culture and mountain access.',
    days: '3-4 days', bestSeason: 'May-Oct', difficulty: 'Medium',
    whyGo: 'Uyghur food, Heavenly Lake, Tianshan Mountains.',
    mapX: -296, mapY: -428,
  },

];
