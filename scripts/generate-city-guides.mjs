/**
 * generate-city-guides.mjs — Codex 运行
 * 生成：城市攻略 .md 文件 + 更新 cityGuideData.ts
 * 使用：node scripts/generate-city-guides.mjs
 */
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
const BASE = process.env.INIT_CWD || '.';

const CITIES = [
  // 现有城市（已存在，跳过）
  ...['beijing','shanghai','guangzhou','chengdu','xian','chongqing','hangzhou','sanya','nanjing','guilin'].map(s=>({slug:s+'-city-guide-for-foreigners',skip:true})),
  // 新城市 [slug, name, nameZh, lat, lon, desc, days, bestSeason, diff, whyGo, q1, a1, q2, a2]
  ['shenzhen','Shenzhen','深圳',22.5,114.1,'China tech hub with modern architecture, easy Hong Kong access.','2-3 days','Oct-Apr','Easy','Tech innovation, OCT Loft, seamless border from Hong Kong.','How to go HK→SZ?','HSR from HK West Kowloon to Futian: 14 min.','Shenzhen worth visiting?','Yes — OCT Loft, Dapeng beaches, innovative architecture.'],
  ['wuhan','Wuhan','武汉',30.6,114.3,'Central China hub on Yangtze, cherry blossoms, hot dry noodles.','3-4 days','Mar-Apr, Sep-Nov','Medium','Yellow Crane Tower, cherry blossoms, vibrant food scene.','Best time for cherry blossoms?','Late Mar-early Apr at Wuhan University.','Wuhan famous food?','Hot dry noodles (re gan mian), duck neck, doupi.'],
  ['kunming','Kunming','昆明',25.0,102.7,'Spring City with year-round mild weather, gateway to Yunnan.','3-5 days','Mar-Oct','Medium','Eternal spring, Stone Forest, Dianchi Lake.','Why Spring City?','Year-round 15-22°C due to low-latitude high-altitude.','Stone Forest distance?','80km SE, 1.5hr drive, doable as day trip.'],
  ['xiamen','Xiamen','厦门',24.5,118.1,'Coastal Fujian city with Gulangyu Island and Minnan culture.','3-4 days','Mar-May, Oct-Dec','Easy','Gulangyu Island, colonial architecture, seafood.','Gulangyu ferry?','Yes, book ahead on holidays. Car-free island.'],
  ['suzhou','Suzhou','苏州',31.3,120.6,'Classical gardens and canals — Venice of the East.','2-3 days','Mar-May, Sep-Nov','Easy','UNESCO gardens, Grand Canal, silk, day trip from SH.','Best garden?','Humble Administrator\'s Garden. Lingering Garden also great.'],
  ['dalian','Dalian','大连',38.9,121.6,'Russian/Japanese-influenced port with beaches and seafood.','3-4 days','May-Oct','Medium','Russian Street, Xinghai Square, beach resorts.'],
  ['qingdao','Qingdao','青岛',36.1,120.4,'German-colonial port famous for Tsingtao beer and beaches.','3-4 days','May-Oct','Easy','Tsingtao Brewery, German architecture, Laoshan.','Visit Tsingtao Brewery?','Yes, museum includes tour + tasting.'],
  ['changsha','Changsha','长沙',28.2,113.0,'Hunan capital known for spicy food and youth culture.','2-3 days','Apr-Oct','Medium','Hunan cuisine, Yuelu Academy, street food.'],
  ['harbin','Harbin','哈尔滨',45.8,126.6,'Ice festival capital with Russian architecture.','3-4 days','Dec-Feb (festival)','Hard (winter)','Ice Festival, Saint Sophia Cathedral, Tiger Park.','Ice festival dates?','Late Dec to late Feb. Best viewed at night.'],
  ['lhasa','Lhasa','拉萨',29.7,91.1,'Tibetan capital at 3,650m with Potala Palace.','4-6 days','Apr-Oct','Hard','Potala Palace, Jokhang Temple, Tibetan culture.','Permits needed?','Yes — Tibet Travel Permit + guided tour required.'],
  ['dali','Dali','大理',25.6,100.2,'Ancient town by Erhai Lake with Bai culture.','3-5 days','Mar-May, Sep-Nov','Easy-Med','Erhai Lake, Cangshan, old town, coffee scene.'],
  ['luoyang','Luoyang','洛阳',34.6,112.5,'Ancient capital with Longmen Grottoes.','2-3 days','Apr-May, Sep-Oct','Medium','Longmen Grottoes (UNESCO), White Horse Temple.','Longmen Grottoes time?','Half day minimum. West bank has largest caves.'],
  // Tier 2
  ['tianjin','Tianjin','天津',39.1,117.2,'Port city near Beijing with European concessions.','1-2 days','Mar-May, Sep-Nov','Easy','Five Great Avenues, Tianjin Eye, day trip from BJ.'],
  ['jinan','Jinan','济南',36.7,117.0,'City of Springs with natural artesian springs.','2-3 days','Mar-May, Sep-Nov','Medium','Baotu Spring, Daming Lake, gateway to Mount Tai.'],
  ['zhengzhou','Zhengzhou','郑州',34.8,113.7,'Transport hub and gateway to Shaolin Temple.','1-2 days','Mar-May, Sep-Nov','Easy','Shaolin Temple day trip, Henan Museum.'],
  ['huangshan','Huangshan (Mt. Huang)','黄山',29.7,118.3,'Iconic granite peaks, hot springs, and Xidi/Hongcun villages.','3-4 days','Mar-May, Sep-Oct','Medium','Yellow Mountain scenery, ancient Huizhou villages.'],
  ['zhangjiajie','Zhangjiajie','张家界',29.4,110.5,'Avatar-inspired sandstone pillars and glass bridge.','3-4 days','Apr-Jun, Sep-Oct','Medium','Avatar Hallelujah Mountain, glass bridge, Tianmen Mountain.'],
  ['dunhuang','Dunhuang','敦煌',40.1,94.7,'Silk Road outpost with Mogao Caves and desert dunes.','2-3 days','May-Oct','Medium','Mogao Caves, Singing Sand Dunes, Crescent Moon Spring.'],
  ['datong','Datong','大同',40.1,113.3,'Northern city with Yungang Grottoes and Hanging Temple.','2-3 days','May-Oct','Medium','Yungang Grottoes, Hanging Temple, ancient Great Wall.'],
  ['xishuangbanna','Xishuangbanna','西双版纳',22.0,100.8,'Tropical Dai minority region with rainforest and elephants.','3-5 days','Nov-Apr','Medium','Dai culture, tropical jungle, wild elephants, night markets.'],
  ['kashgar','Kashgar','喀什',39.5,76.0,'Silk Road oasis with Uyghur culture and Sunday Bazaar.','3-4 days','May-Oct','Hard','Old City, Sunday livestock market, Uyghur cuisine.'],
  ['jingdezhen','Jingdezhen','景德镇',29.3,117.2,'Porcelain capital of China with ceramic history.','2-3 days','Mar-May, Sep-Nov','Medium','Porcelain museums, pottery workshops, ancient kilns.'],
  ['guizhou','Guizhou (Guiyang)','贵阳',26.7,106.6,'Karst landscapes and Miao/Dong minority villages.','4-6 days','Mar-Oct','Hard','Huangguoshu Waterfall, Miao villages, Dong drum towers.'],
  ['lanzhou','Lanzhou','兰州',36.1,103.8,'Yellow River city, gateway to the Tibetan Plateau.','2-3 days','May-Oct','Medium','Yellow River, beef noodles, Bingling Temple Grottoes.'],
  ['xining','Xining','西宁',36.6,101.8,'Gateway to Qinghai Lake and Tibetan Amdo region.','2-3 days','Jun-Sep','Medium','Qinghai Lake, Ta\'er Monastery, Tibetan culture.'],
  ['urumqi','Urumqi','乌鲁木齐',43.8,87.6,'Capital of Xinjiang with Uyghur culture and mountain access.','3-4 days','May-Oct','Medium','Uyghur food, Heavenly Lake, Tianshan Mountains.'],
];

// Map 680x540, X≈(lon-72)*10.5, Y=-13.33*lat+740
function px(lon) { return Math.round((lon - 72) * 10.5); }
function py(lat) { return Math.round(-13.33 * lat + 740); }

function makeEntry(c) {
  const x = px(c[3]), y = py(c[4]); // lat=c[3], lon=c[4]
  // nameZh at index 2
  return `  {
    slug: '${c[0]}-city-guide-for-foreigners',
    name: '${c[1]}', nameZh: '${c[2]}',
    desc: '${c[5]}',
    days: '${c[6]}', bestSeason: '${c[7]}', difficulty: '${c[8]}',
    whyGo: '${c[9]}',
    mapX: ${x}, mapY: ${y},
  },`;
}

function makeMd(c) {
  const slug = c[0]+'-city-guide-for-foreigners';
  const name = c[1], nameZh = c[2];
  const tags = [slug.replace('-city-guide-for-foreigners',''), 'city guide', 'china travel', 'tourism'];
  let faqYaml = '';
  if (c[10]) faqYaml += `  - question: "${c[10]}"\n    answer: "${c[11]}"\n`;
  if (c[12]) faqYaml += `  - question: "${c[12]}"\n    answer: "${c[13]}"\n`;
  if (faqYaml) faqYaml = `faqs:\n${faqYaml}`;

  const body = `${name} (${nameZh}) is an increasingly popular stop for foreign travelers exploring China${c[0]==='lhasa'?', with its unique Tibetan Buddhist culture and stunning Himalayan setting':c[0]==='kashgar'?', offering a genuine Silk Road experience with strong Uyghur cultural identity':c[0]==='xishuangbanna'?', offering a tropical escape with Dai minority culture and lush jungle landscapes':c[0]==='dunhuang'?', offering a glimpse into the ancient Silk Road with remarkable Buddhist cave art':c[0]==='zhangjiajie'?', famous for the towering sandstone pillars that inspired the floating mountains in Avatar':c[0]==='huangshan'?', home to the iconic Yellow Mountain, one of China\'s most celebrated natural wonders':c[0]==='jingdezhen'?', known worldwide as the Porcelain Capital with a ceramic history spanning over a thousand years':c[0]==='guizhou'?', with its dramatic karst landscapes, waterfalls, and vibrant ethnic minority cultures':'. '}. This guide covers what you need to know before you go.

## Why Visit ${name}

${c[9]}

## Getting There

${name} is well-connected ${c[0] === 'lhasa' ? 'by air from major Chinese cities and by the Qinghai-Tibet Railway' : c[0] === 'kashgar' ? 'by air from Urumqi and other Xinjiang cities, and by road along the Karakoram Highway' : c[0] === 'dunhuang' ? 'by air from Lanzhou, Xi\'an, and Beijing, and by train from Lanzhou and Jiayuguan' : c[0] === 'xishuangbanna' ? 'by air from Kunming and other Chinese cities, and by road from Kunming' : c[0] === 'harbin' ? 'by air from major Chinese cities and by high-speed rail from Beijing' : 'by air, high-speed rail, and conventional rail from most major Chinese cities'}. For international travelers, flying into the nearest major hub and connecting by train or domestic flight is the most practical approach.

## Best Time to Visit

${c[7]}${c[0]==='harbin'?'. Note that winter temperatures can drop to -30°C for the Ice Festival':c[0]==='lhasa'?'. Summer is the peak tourist season with the highest oxygen levels':c[0]==='xishuangbanna'?'. The dry season (Nov-Apr) is most comfortable for travel':c[0]==='dunhuang'?'. Summer temperatures can exceed 35°C — carry plenty of water':' — the most comfortable weather for sightseeing'}.

## What to Do

- Explore the city's main sights and landmarks
- Try the local cuisine at food streets and night markets
- Visit nearby natural or cultural attractions
- Experience local culture and traditions

## Where to Stay

Most international travelers prefer hotels near the city center or train station area. ${name} has a range of options from international hotel chains to local boutique hotels. Book ahead during Chinese holidays and peak season.

## Food to Try

Each Chinese city has its own culinary identity. ${name}${c[0]==='wuhan'?' is famous for hot dry noodles (re gan mian)':c[0]==='changsha'?' is known for spicy Hunan cuisine':c[0]==='qingdao'?' is famous for seafood and Tsingtao beer':c[0]==='harbin'?' is known for Russian-influenced breads, sausages, and hearty stews':c[0]==='lhasa'?' features Tibetan momos, butter tea, and tsampa':c[0]==='kashgar'?' is famous for lamb kebabs, pilaf, and Uyghur naan bread':' offers a unique local food scene worth exploring'}.

## Practical Tips

- Download offline maps and translation apps before arriving
- Have a backup payment method (cash + Alipay/WeChat Pay)
- Check if your hotel offers English-speaking staff
- Register with the local police within 24 hours of arrival (your hotel will handle this)`;

  let frontmatter = `---
title: "${name} City Guide for Foreigners 2026: Complete Travel Guide"
description: "Complete 2026 travel guide to ${name} for foreign visitors — top attractions, local food, getting around, best time to visit, accommodation areas, and practical tips."
pubDate: 2026-07-21
category: essentials
tags: [${tags.join(', ')}]
featured: false
${faqYaml}
---
`;
  return frontmatter + '\n' + body;
}

// ── Generate cityGuideData.ts ──
const dataPath = 'D:/独立站/china-travel-kit/src/data/cityGuideData.ts';
const existingData = readFileSync(dataPath, 'utf8');
const insertPoint = existingData.indexOf('];') - 1;
const newData = existingData.slice(0, insertPoint) + '\n' + CITIES.filter(c=>!c.skip).map(makeEntry).join('\n') + '\n' + existingData.slice(insertPoint);
writeFileSync(dataPath, newData, 'utf8');
console.log(`✅ Updated cityGuideData.ts`);

// ── Generate .md files ──
let count = 0;
for (const c of CITIES) {
  if (c.skip) continue;
  const slug = c[0]+'-city-guide-for-foreigners';
  const mdPath = `D:/独立站/china-travel-kit/src/content/posts/${slug}.md`;
  if (existsSync(mdPath)) { console.log(`  SKIP: ${slug} (exists)`); continue; }
  writeFileSync(mdPath, makeMd(c), 'utf8');
  count++;
  console.log(`  ✅ ${slug}`);
}
console.log(`\nDone: ${count} city guides created.`);
