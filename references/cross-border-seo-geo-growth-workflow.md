# 跨境独立站 SEO、GEO、分发、投流与 TikTok 关键词数据工作流

> 调研日期：2026-09-08  
> 范围：两周可上线的 MVP；GEO 指 Generative Engine Optimization（生成式搜索优化），不是地理分发。  
> 来源规则：功能与限制只引用平台官方文档；架构取舍标为“建议”或“推断”。

## 最快落地的首版

建议先用 **n8n Cloud + Apify TikTok Scraper + Google Sheets + n8n 模型节点**。已有 Dify 时，通过 Workflow API 调用它；未部署时，Dify 和 PostgreSQL 都可后加。TikTok 在此方案中用于关键词采集，不承担发布任务。

在站点和服务账号权限齐备、有一人能配置 API 的前提下，估计 3–5 个工作日可跑通采集和内容草稿，第二周接入分发与投放效果回流。这是实施估算，不是 SEO 排名或投放效果承诺。

1. 先用 2 个关键词、每词最多 50 条结果试跑，检查相关性、字段完整性和实际账单；通过后扩到 10 个关键词、每天每词最多 50 条。
2. n8n 使用 Schedule Trigger -> Google Sheets 读取关键词 -> Loop Over Items -> Apify Run Actor -> 等待对应 run 成功 -> Get Items（分页）-> Code 清洗 -> Google Sheets 写入。
3. 视频基础记录按 `video_id` 去重；关键词命中关系单独保留；指标按 `video_id + observation_date` 保存快照。缺失指标保留为空，不填成零；只有同一视频的连续快照才能计算增量。
4. AI 根据描述、标签和可用的评论样本输出选题及证据链接，结合商品真实资料生成站内文章、问答、渠道文案和广告素材草稿。未取得字幕或视频内容时，不推断画面、口播或前三秒钩子。
5. 先接现有的一个分发渠道和一个广告平台。投放日报核对 spend、purchase、revenue、归因窗口及币种后给建议，运营人员执行预算调整；API 权限未齐时支持平台导出文件导入。

Apify 输入示例，关键词仅为示例：

```json
{
  "searchQueries": ["dog grooming brush"],
  "searchSection": "/video",
  "resultsPerPage": 50,
  "shouldDownloadVideos": false
}
```

字段已按供应商当前 [输入文档](https://apify.com/clockworks/tiktok-scraper/input-schema) 核对；[Apify n8n 集成](https://docs.apify.com/platform/integrations/n8n) 提供 Run Actor、Get Run 和 Get Items。未调用付费采集任务，实际返回数据尚未验证。搜索结果数量和视频播放量都不是关键词搜索量；代理出口地区也不能证明受众所在地。

## 第二阶段架构与接口参考

数据量、语言和渠道增加后，建议采用 **n8n 做总编排，Dify 做 AI 内容与知识检索，PostgreSQL 做数据事实源**。以下是扩展参考，不是首版必须全部部署的清单：

- n8n 负责定时任务、Webhook、OAuth/API 调用、分页、限流重试、幂等写库、人工审批和告警。HTTP Request 节点支持通用 REST 与 OAuth2；官方也提供 Retry on Fail、批处理、Wait 与分页处理方式。[n8n HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest)；[n8n 限流处理](https://docs.n8n.io/integrations/builtin/handle-rate-limits)
- Dify 负责品牌/商品知识库检索、关键词聚类、内容 brief、多语言改写和结构化 JSON 输出。Dify Workflow 已支持 Schedule、Webhook 和集成触发器，但 Cloud 版触发次数受套餐配额约束；MVP 仍由 n8n 统一调度，减少双重状态机。[Dify Trigger](https://docs.dify.ai/en/cloud/use-dify/nodes/trigger/overview)；[Dify Knowledge Retrieval](https://docs.dify.ai/en/cloud/use-dify/nodes/knowledge-retrieval)；[Dify Workflow API](https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow)
- TikTok 关键词数据必须分来源处理。**TikTok 没有面向普通商业开发者、可搜索全站自然视频的通用公开 API**；这是根据官方公开产品边界得出的结论：Display API 只能读取授权用户资料/视频，Research API 仅面向合格的非商业研究，Commercial Content API 只覆盖商业内容/广告且目前数据先从 EU 开始。
- 首期投流只做“取数 + 规则建议 + 人工批准”，不自动改预算/出价。待归因、权限、预算上限和回滚机制验证后再开放写操作。

## 推荐架构

```text
商品/CMS/库存/毛利       GSC + GA4       Google Ads/Merchant       TikTok 合规数据源
        |                    |                    |                         |
        +--------------------+--------------------+-------------------------+
                                     |
                           n8n：采集、清洗、限流、审批
                                     |
                         PostgreSQL + 原始 JSON 对象存储
                                     |
                  +------------------+------------------+
                  |                                     |
         Dify：RAG/聚类/生成                     BI：漏斗、ROAS、机会榜
                  |
       SEO/GEO 草稿 -> 自动校验 -> 人工审批 -> CMS/渠道发布
```

建议至少保存五类实体：`product_snapshot`、`keyword_daily`、`content_item`、`channel_metric_daily`、`experiment`。所有写入使用稳定业务键，例如 `(source, account_id, date, keyword, country)`，工作流重跑时 UPSERT，避免重复数据。

## 四条 MVP 工作流

### WF-01：每日经营与搜索数据采集

每天固定时区运行：

1. n8n Schedule Trigger 生成 `run_id` 和目标日期；GSC、GA4 数据建议留 2–3 天回看窗口，再对最近 7 天做幂等回补。
2. 调用 Search Console Search Analytics API，按站点、日期、国家、设备、页面、query 分页；写入 `keyword_daily`。
3. 调用 GA4 Data API `runReport` 拉取 landing page、source/medium、country、purchase、revenue；写入 `channel_metric_daily`。
4. 拉取 Google Ads 报表；首期只读 campaign/ad group/search term、cost、click、conversion value。
5. 拉取 Merchant API 商品状态/问题，与库存、价格、毛利快照关联。
6. 每个 API 分支单独限流重试；429/5xx 指数退避，4xx 权限错误立即告警；最后输出缺数清单。

关键限制：

- Search Console 私有数据使用 OAuth 2.0，授权主体只能访问其有权限的资源；Search Analytics 返回的是“top rows”，不是完整明细，官方说明每天每种 search type 最多暴露 50,000 行。[授权](https://developers.google.com/webmaster-tools/v1/how-tos/authorizing)；[数据限制](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data#data_limits)；[配额](https://developers.google.com/webmaster-tools/limits)
- GA4 Data API 可用用户 OAuth 或 service account；service account 仍需被授予 GA4 property 权限。标准 property 的 Core 配额包括 200,000 tokens/property/day、40,000/property/hour、14,000/project/property/hour 与 10 个并发请求，实际消耗应从响应 quota 字段监控。[快速开始](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart-client-libraries)；[配额](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)
- GA4 Measurement Protocol 用于补充 server/offline 事件，不能替代 gtag/GTM/Firebase；每请求最多 25 个事件，生产收集端即使 payload 有误也可能返回 2xx，因此上线前必须调用 validation server。[Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)；[参考](https://developers.google.com/analytics/devguides/collection/protocol/ga4/reference)；[校验](https://developers.google.com/analytics/devguides/collection/protocol/ga4/validating-events)
- Google Ads API 同时需要 OAuth 2.0 和 developer token。Test、Explorer、Basic、Standard 权限层级决定生产可用性与日操作数；当前官方列出的 Explorer 为 2,880 operations/day，Basic 为 15,000/day，Standard 对多数服务不设日操作上限，但仍受审批、permissible use 和服务级配额约束。[OAuth](https://developers.google.com/google-ads/api/docs/oauth/overview)；[developer token](https://developers.google.com/google-ads/api/docs/api-policy/developer-token)；[访问级别](https://developers.google.com/google-ads/api/docs/api-policy/access-levels)
- Merchant Center 新接入必须使用 Merchant API。Content API for Shopping 已于 2026-08-18 sunset，并从 2026-09-01 起逐步返回错误。自营自动化可用加入 Merchant Center 的 service account；第三方/代理产品应走 OAuth。Cloud project 还需先通过 `registerGcp` 与一个 Merchant account 完成一次性注册。[Merchant API 总览](https://developers.google.com/merchant/api/overview)；[认证](https://developers.google.com/merchant/api/guides/quickstart/authentication)；[注册](https://developers.google.com/merchant/api/guides/quickstart/registration)

### WF-02：SEO/GEO 机会发现与内容生产

每周运行：

1. SQL 生成机会池：高展示低 CTR、排名 4–20、有站内转化、对应商品有库存且毛利达标的 query/page。
2. n8n 将商品事实、品牌规范、目标国家/语言、历史表现和候选 query 发给 Dify Workflow。
3. Dify 从“商品真相库”检索后输出固定 JSON：`intent`、`question_cluster`、`title`、`outline`、`claims_with_evidence`、`faq`、`internal_links`、`locale_notes`。禁止模型自行生成价格、认证、功效、库存或配送承诺。
4. n8n 做确定性校验：目标 query、canonical、hreflang、标题长度、内部链接、Product/Organization/Breadcrumb 结构化数据、禁词、证据字段、重复度。
5. 创建 CMS draft，经人工审批后发布；更新 sitemap，并用 Search Console Sitemaps API 提交。[Sitemaps submit](https://developers.google.com/webmaster-tools/v1/sitemaps/submit)
6. 7/14/28 天回写 impressions、clicks、conversion、revenue，形成 experiment 记录。

GEO 不应被包装成单独的“黑盒排名技巧”。Google 官方明确说明，出现在 AI Overviews/AI Mode **没有额外技术要求，也不需要特殊优化**，现有 SEO 基础仍适用。因此 GEO 的可执行重点是：可抓取的 HTML、稳定的实体与商品事实、清晰问答、第一方证据、作者/品牌信息、结构化数据一致性、可追踪的落地页。[Google AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)

不要对普通商品页调用 Google Indexing API；该 API 官方只允许带 `JobPosting` 或 `VideoObject` 中 `BroadcastEvent` 的页面。[Indexing API](https://developers.google.com/search/apis/indexing-api/v3/using-api)

### WF-03：多平台内容分发

以“已审批的站内主内容”为 canonical source，Dify 只做渠道适配：短视频脚本、邮件、Pinterest/Instagram 文案、广告素材 brief、多语言本地化。每份衍生内容保留 `source_content_id`、locale、渠道和 UTM。

MVP 发布规则：

- 网站/CMS 可在人工批准后自动发布；社媒只生成草稿或进入渠道排期工具。
- 价格、折扣、运费、交期从实时商品字段注入，不进入 Dify 长期知识文本。
- 每个国家维护本地禁限词、税费/退货政策与单位换算；翻译后仍做人工抽检。
- Dify API key 只保存在 n8n 凭证或 secrets manager，不放浏览器端；每次调用保存 prompt/version、知识文档版本和模型输出，便于追责与复现。

### WF-04：TikTok 按关键词的数据采集

先建立 `keyword_seed`：GSC queries、Google Ads search terms、商品类目/卖点、客服问题；Dify 负责同义词、口语表达和目标语言扩词。随后按以下优先级采集：

| 数据源 | 能得到什么 | 是否适合商业 MVP | 接入方式 |
|---|---|---:|---|
| TikTok Creative Center | 各地区热门 hashtag、内容/创意与 Top Ads，适合人工验证趋势 | 是 | 首期人工查询/记录；未找到官方通用导出 API，不使用网页私有接口 |
| Commercial Content API | 按 advertiser name 或 keyword 搜索广告/商业内容及元数据；公开说明当前先含 EU 广告数据 | 有条件 | 申请通过后由 n8n HTTP Request 调用 |
| 自有 TikTok Ads 数据 | 自己广告账户的报表；若账户/产品支持 Search Ads，可获取自己投放产生的搜索词维度 | 是 | TikTok for Business 开发者/广告主授权后，用 Marketing API 报表；以门户实际获批 scope/version 为准 |
| Display API | 被授权用户的 profile、近期或指定视频 | 否，不能做全站关键词搜索 | Login Kit + `user.info.basic`、`video.list`，仅用于自有/授权账号补充数据 |
| Research API | 公共账号/视频研究数据，可按获批研究用途查询 | 否 | 仅合格研究者；要求独立于商业利益并以非营利/非商业公共利益研究为目的 |
| 合规第三方数据商 / Apify Actor | 跨地区自然内容关键词/榜单数据 | 视合同与法务审查而定 | 要求其说明 TikTok 授权/数据来源、可商用权、地区覆盖、删除与留存机制，再接正式 API |

官方边界证据：

- Commercial Content API 明确支持按 advertiser name 或 keyword 搜索广告和其他商业内容；申请通过后提供 client key。官方当前说明数据先从 EU 广告开始，数据通常保留到广告最后展示后一年。[Commercial Content API](https://developers.tiktok.com/products/commercial-content-api/)；[Getting Started](https://developers.tiktok.com/doc/commercial-content-api-getting-started)
- Research Tools 只向符合条件的研究者开放；申请者需独立于商业利益，并以非营利/非商业方式开展公共利益研究。因此跨境电商选品或营销监控不应冒用该 API。[Research API](https://developers.tiktok.com/products/research-api/)；[Getting Started](https://developers.tiktok.com/doc/research-api-get-started)
- Display API 需要 Login Kit/TikTok API 产品获批以及 `user.info.basic`、`video.list` scope，文档用途是展示授权用户的资料和视频，不是关键词检索全站内容。[Display API](https://developers.tiktok.com/doc/display-api-get-started)
- Creative Center 可作为趋势人工入口：[Trend Discovery](https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en)；[Top Ads](https://ads.tiktok.com/business/creativecenter/topads/pc/en)。

Apify 的 Clockworks TikTok Scraper 是可快速接 n8n 的第三方采集候选，其上架和 API 可用性不代表 TikTok 官方授权：输入 schema 支持 `searchQueries`、`searchSection=/video`、结果数、MOST_RELEVANT/MOST_LIKED/LATEST 排序与时间窗口，部分筛选另计费；`proxyCountryCode` 只改变访问出口地区，**不等于受众所在地**。[Actor 输入 schema](https://apify.com/clockworks/tiktok-scraper/input-schema)；[Apify n8n 集成](https://docs.apify.com/platform/integrations/n8n)。接入前核对平台条款、数据使用权及供应商覆盖和稳定性，先小样本验证。

TikTok 采集工作流建议：

```text
keyword_seed
  -> Dify 扩词/语言归一化
  -> Switch(source: Commercial API / Ads API / licensed provider / manual import)
  -> 分页 + 429 退避 + 原始响应落对象存储
  -> 去重(content_id + source)
  -> 计算 velocity、engagement_rate、广告出现频次、国家/时间窗口
  -> 聚类 hook/卖点/痛点
  -> 进入选题榜，不直接触发广告或发布
```

采集仅针对业务所需的公开数据，不绕过访问控制。数据源不可用时，工作流应记录失败或缺数，保留人工录入/导入入口；不要把采集失败误记为没有相关内容。

## 投流闭环与安全门

首期日报生成三类建议：`scale`、`hold`、`stop-review`。规则输入必须同时包含 spend、conversion value、gross margin、stock、refund rate、数据新鲜度和最小样本量。Dify 只解释原因/生成摘要，不直接决定资金动作。

上线自动 mutate 前至少满足：

1. 连续两周只读建议与人工判断一致性达到团队设定阈值；
2. 单次、单日、单 campaign 预算变更上限已编码；
3. 所有写操作有审批人、旧值、新值、API response、rollback payload；
4. 数据延迟、归因窗口或 API 缺数时 fail closed；
5. 广告账户 token 使用最小 scope，可轮换，开发/生产分离。

## 两周上线计划

| 时间 | 交付 |
|---|---|
| Day 1–2 | PostgreSQL 表、对象存储、n8n/Dify 环境；完成 GSC、GA4、Ads、Merchant 权限清单与 token 生命周期 |
| Day 3–4 | WF-01：GSC + GA4 + 商品/订单入库，完成分页、UPSERT、缺数告警 |
| Day 5 | Google Ads/Merchant 只读接入；无权限时先用平台导出 CSV 保持数据模型不变 |
| Day 6–7 | Dify 商品真相库、固定 JSON 输出、SEO/GEO opportunity workflow |
| Day 8–9 | CMS draft、校验与人工审批；发布一个语言/一个国家的 3–5 个实验页 |
| Day 10–11 | TikTok `keyword_seed`、Creative Center 人工导入；并行提交 Commercial Content API/Marketing API 申请 |
| Day 12 | 只读投流日报与 Slack/邮件审批卡片，不启用自动预算修改 |
| Day 13–14 | 重跑/限流/过期 token/部分失败演练，仪表盘与 runbook，上线 MVP |

## 上线前需要准备

- 站点：CMS API、商品/订单/库存/毛利字段、国家/语言清单、GSC property、GA4 property。
- Google：Cloud project、OAuth consent、授权用户或 service account、Ads manager developer token、Merchant Center 用户授权与 GCP registration。
- TikTok：本次目标为自然视频关键词采集，首版评估第三方采集服务；EU 广告创意和自有广告搜索词分别是 Commercial Content API/Marketing API 的其他用途，不应混为同一个数据源。
- AI：品牌事实、商品合规材料、禁限词、语气、目标市场政策；这些是 Dify 知识库，不以互联网抓取内容替代。
- 运维：secret manager、token 到期告警、每源配额、数据保留期、删除请求处理、人工审批负责人。

## 扩展到更大规模

单机 n8n 足够支持 MVP。执行量增长后再用 queue mode：main 处理触发与 webhook，Redis 保存待执行队列，worker 执行任务，并共享数据库与加密 key。[n8n queue mode](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode)

先不要在第一期同时上多国家、多语言、Meta/TikTok/Google 全自动投放。最小验证单元应是“一个国家 + 一个语言 + 一个商品类目 + 一个广告平台 + TikTok 一个合规数据入口”，确认从关键词机会到内容/广告指标回流可以闭环后再复制。
