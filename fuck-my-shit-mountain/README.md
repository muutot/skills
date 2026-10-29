# Fuck My Shit Mountain

来源：[Fuck_My_Shit_Mountain](https://github.com/XiNian-dada/Fuck_My_Shit_Mountain)。项目无关的循证式多维代码库审计技能。

入口为 [SKILL.md](SKILL.md)，支持 26 个专项维度、全量与增量审计，以及 Markdown、HTML、JSON 和对话输出。

使用示例：

```text
使用 fuck-my-shit-mountain 全量审计当前仓库，输出中文 Markdown。

使用 fuck-my-shit-mountain 对 main...HEAD 做安全与数据完整性增量审计，输出 JSON。

使用 fuck-my-shit-mountain 审查当前未提交变更，在对话中给出结果。
```

语言默认跟随对话；一般审计默认全量，具体关注点自动映射专项维度；报告请求默认 Markdown，对话审查默认 stdout。审计本身不会修改应用代码或触发发布。

所有审计文件统一保存到本技能的 `result/`（本地生成输出，不进入 Git，不打入技能分发 ZIP），不写入项目根目录。

本地检查：

```powershell
python -X utf8 -B -m unittest discover -s fuck-my-shit-mountain/tests -v
python -X utf8 -B fuck-my-shit-mountain/scripts/project_inventory.py . --format text --language zh
python -X utf8 -B fuck-my-shit-mountain/scripts/report_lint.py --modes security fuck-my-shit-mountain/result/audit-report.json
python -X utf8 -B fuck-my-shit-mountain/scripts/package_skill.py --dry-run
```

测试使用临时目录和合成数据，不读取真实剪贴板数据。
