# SDS-Map-Share
一个分享火柴人至高对决游戏的地图

---

# 如何上传地图?
1. 请进入`src/data/map/json`添加你的地图信息
2. 前往`/public/map/image`存放你的地图图片(需要分类)
3. 前往`public/map/fun`存放你的地图文件(需要分类)
4. 使用`tools/`下的工具进行压缩
5. 提交pr请求待我看到之后我会进行评估后添加  

Q: 我实在不会呀该怎么办呢?
A: 试着询问ai或者把你的fun地图文件发往到邮件bywihee [at] outlook.com 我会不定时的查看,或者提issue有标准格式

---

# 规范的地图提交格式
1. 压缩包内包含地图文件夹
2. 文件夹内包含,地图文件,图片,config.json文件
config.json文件内容
```json
{
  "title": "地图名称",
  "description": "地图描述",
  "category": ["对战", "观赏"],
  "author": "作者名",
  "authorUrl": "https://作者主页链接.com"
}
```  
category需要按照自己的地图类型自己填,authorUrl可选择删除不填  
源代码中有这个文件`Map_Upload_Sample_Archive.7z`这是一个示例

---

# 网址
> https://sds-map-share.pages.dev/