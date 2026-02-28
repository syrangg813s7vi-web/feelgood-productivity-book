# Claude 写作配置

## 项目写作工具决策

**决策时间**: 2026-02-28  
**决策**: 对于《Feel Good Productivity》书籍项目，**始终使用 Claude** 进行写作，**不使用 Codex**。

## 原因

1. **Claude Code 更适合书籍写作**
   - 更好的长文本生成能力
   - 更自然的中文表达
   - 更稳定的输出质量

2. **Codex 的限制**
   - 需要浏览器登录授权（难以自动化）
   - 沙箱模式限制文件写入
   - 更适合代码任务而非书籍写作

3. **项目历史经验**
   - 之前尝试 Codex 遇到认证和权限问题
   - Claude 更适合本项目的工作流

## 写作工具

### 使用 Claude Code

```bash
# 步骤1：加载 Claude API 配置（使用 Yes 提供者）
source ~/.claude-model-config

# 步骤2：派生 Claude writing agent
bash pty:true background:true command:"claude '写作任务'" \
  workdir:/root/clawd/github/active/feelgood-productivity-book
```

**重要**：必须先 source 配置文件，否则 Claude Code 会要求浏览器登录。

### API 配置说明

项目使用 Claude API（通过配置脚本管理）：
- 配置脚本: `/root/clawd/bin/switch-claude-model`
- 配置文件: `~/.claude-model-config`
- 当前提供者: Yes

查看当前配置：
```bash
/root/clawd/bin/switch-claude-model status
```

⚠️ **安全规则**：永远不要在文档或消息中输出 token、秘钥等敏感信息。

## 项目管理规则

- **PM Agent** 不自己写章节
- **PM Agent** 只负责协调和监控
- 所有写作任务通过派生 **Claude** agent 执行
- 保持 Trello 同步（每15分钟）

## 写作要求（传达给 Claude）

- 字数：10,000-15,000 字符/章
- 完整结构：概念/框架/案例/FAQ/行动清单/模板/误区/练习/要点
- 出版级质量
- 不要出现"视频/频道/订阅/从字幕提取"等词汇
- 完成后 git add/commit/push

## 相关文件

- `PM_AGENT_CONFIG.md` - PM Agent 约束配置
- `WRITING_WORKFLOW.md` - 写作工作流程（需要更新为 Claude）
- `.codex/config.json` - 旧配置（保留用于参考）

---

**最后更新**: 2026-02-28  
**版本**: 1.0  
**状态**: 强制执行
