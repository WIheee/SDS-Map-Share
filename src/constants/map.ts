/**
 * 地图分类常量
 * CATEGORIES 与 src/data/map/json 下的文件一一对应
 */

export const CATEGORIES = ['对战', '观赏', '趣味', '跑酷', '其他'] as const

export type Category = (typeof CATEGORIES)[number]

/**
 * JSON 文件名 -> 分类名
 * 加载时按文件名自动注入分类，避免 JSON 数据手写 category 导致筛选失效
 */
export const FILE_CATEGORY: Record<string, string> = {
  battle: '对战',
  scenery: '观赏',
  fun: '趣味',
  parkour: '跑酷',
  other: '其他',
}
