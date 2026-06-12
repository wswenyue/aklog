---
name: code-quality
description: >-
  在交付前确保 aklog 代码变更通过 lint、类型检查、测试与人工审查。
  在完成代码修改、汇报任务完成、用户要求质量审核或验证 CI 就绪时使用。
---

# 代码质量门禁

交付 aklog 代码变更前的最终质量检查。本地标准与发布流水线 **`.github/workflows/release.yml` → `quality` job** 对齐。

## 何时执行

每次代码修改任务结束前、向用户汇报完成之前，必须执行本 skill。

## 执行顺序总览

```
0. 范围检查（人工）
1. 安装依赖
2. Ruff lint
3. Ruff format check
4. Mypy
5. Pytest（覆盖率 ≥ 75%）
6. Smoke（CLI 与启动脚本）
7. 人工审查 diff
8. 修复循环 → 从失败步骤重跑
9. 汇报
```

**发布级全量检查**与 CI 一步对应：在仓库根目录执行 `make ci`（等价于步骤 1–6，顺序见下表）。

## 0. 范围检查

- 改动最小化，聚焦当前需求
- 不做无关重构、顺手修复或范围蔓延
- 注释仅用于解释非显而易见的业务逻辑

## 1–6. 自动化检查（与 release quality job 对齐）

在仓库根目录执行。若无 `python` 则使用 `python3`（Makefile 默认 `python3`）。

### 方式 A：一条命令（推荐，与发布一致）

```bash
make ci
```

`make ci` = `lint` → `typecheck` → `test-cov` → `smoke`，与 release workflow 步骤及顺序一致。

### 方式 B：分步执行（调试失败步骤时使用）

| 顺序 | release.yml step | 本地命令 |
|------|------------------|----------|
| 1 | Install dependencies | `make install-dev` 或 `python3 -m pip install -e ".[dev]"` |
| 2 | Ruff lint | `python3 -m ruff check src tests` |
| 3 | Ruff format check | `python3 -m ruff format --check src tests` |
| 4 | Mypy | `python3 -m mypy src/aklog` |
| 5 | Pytest with coverage | `python3 -m pytest tests --cov=aklog --cov-report=term-missing --cov-fail-under=75` |
| 6 | Smoke | 见下方 smoke 命令块 |

上述步骤 2–3 合并为 `make lint`；步骤 5 对应 `make test-cov`（**不是** `make test`，发布要求覆盖率 ≥ 75%）。

Smoke 命令（与 release 一致，`PYTHONPATH=src`）：

```bash
export PYTHONPATH=src
python3 -m aklog --version
python3 -m aklog -h
test -x aklog
bash -n aklog
python3 -c "from aklog.build_meta import __version__; assert __version__"
```

或：`make smoke`（Makefile 已设置 `PYTHONPATH=src`）。

### 按改动范围选择

| 场景 | 最低要求 | 说明 |
|------|----------|------|
| 交付 / 合入 / 发版前 | `make ci` | 与 release `quality` job 完全一致 |
| 仅改测试或文档 | `make lint` + `make test-cov` | 可跳过 smoke（未动 CLI/启动脚本时） |
| 改动 CLI 入口、`aklog` 脚本或打包 | `make ci` | smoke 必须跑 |

任一检查失败时，修复后**从失败步骤起重跑**（或重跑 `make ci`），直至全部通过。

## 7. 人工审查

对照 diff 审查：

- [ ] 逻辑正确，覆盖边界情况
- [ ] 新行为在适当时配有有意义的测试
- [ ] 命名、结构与 import 风格与周边代码一致
- [ ] 无密钥、凭证或调试残留
- [ ] 用户可见文案与 CLI 行为保持一致

## 8. 修复循环

对每个问题（自动化或人工发现）：

1. 修改代码
2. 从失败步骤重跑（或 `make ci`）
3. 重复直至通过

## 9. 汇报

向用户汇总：

- 已执行的检查及结果（注明是否跑了 `make ci`）
- 门禁过程中发现并修复的问题
- 剩余风险或未覆盖的测试范围

若在合理努力后仍无法通过检查，应明确说明阻塞原因，而非声称任务已完成。
