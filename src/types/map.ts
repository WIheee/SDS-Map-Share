export interface MapItem {
  id: number
  title: string
  description: string
  image: string
  file: string
  category: string[]
  author: string
  authorUrl?: string // 新增：作者社交媒体链接，可选
}
