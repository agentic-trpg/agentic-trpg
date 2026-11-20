# Linear 项目与 Issue 流程

DOC、Rules Engine（RE）和 State Machine（SM）共用一个 Linear Project。打开 [Agentic TRPG](https://linear.app/agentictrpg/project/agentic-trpg-50fd8e69ee42) 后，在 **Overview** 查看项目概况和当前重点，在 **Issues** 查看待办和进度。在 **My issues** 可以查看分配给自己的工作。

## 记录与讨论待办

1. 先在项目中查找已有 Issue。已有记录就补充现有事项，否则在项目下新建 Issue。
2. 写清要解决的问题、涉及的仓库、已知依据和可观察的验收条件。记录负责人、状态和已知依赖。范围待讨论时，把待决定的问题留在 Issue 中。
3. 开始前和负责人确认范围，再核对当前代码、测试及相关项目文档。架构和跨模块协议查 [Module Contracts](MODULE_CONTRACTS.md)，产品范围查 [MVP Scope](MVP_SCOPE.md)，当前行为以实际代码和验证证据为准。

## 更新进度与关闭

- 开始或阻塞时更新 Issue 状态。遇到依赖时写明阻塞项及继续条件。
- 验证后在 Issue 里记录结论，并关联相应的 PR、提交或测试证据，再按实际结果关闭。已完成的事项注明证据，决定不做的事项记录原因。
- 跨仓工作共用一个 Issue，关联各仓交付。可以独立实施或验收的部分可建子 Issue，并记录彼此依赖。
- 长期的职责、接口和设计决定回写对应的项目文档。Linear 保存执行状态、讨论和指向验收证据的链接。
