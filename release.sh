#!/bin/bash
# aklog 版本发布脚本
# 自动递增 semver tag 并推送，触发 .github/workflows/release.yml
# 版本唯一来源：本脚本创建的 git tag（vX.Y.Z）；发版前 sync build_meta.py / pyproject.toml
# 版本格式：v1.0.0（严格遵循语义化版本）
# 
# 通过软链接在子项目根目录使用（见 scripts/release/setup-release-links.sh）
# 脚本会自动识别当前所在的 Git 仓库根目录
#
# 使用方法:
#   ./release.sh              # 非交互模式（默认，使用默认值）
#   ./release.sh -i           # 交互模式
#   ./release.sh --interactive # 交互模式

set -euo pipefail  # 安全模式：出错即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === 解析命令行参数 ===
INTERACTIVE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        -h|--help)
            echo "版本发布脚本"
            echo ""
            echo "使用方法:"
            echo "  $0 [选项]"
            echo ""
            echo "选项:"
            echo "  -i, --interactive  启用交互模式（默认：非交互模式）"
            echo "  -h, --help         显示此帮助信息"
            echo ""
            echo "非交互模式（默认）:"
            echo "  - 代码未变化时自动退出"
            echo "  - 版本号递增方式默认选择修订号 +1"
            echo "  - 自动创建并推送 tag，无需确认"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 未知参数: $1${NC}"
            echo "使用 $0 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 获取 Git 仓库根目录（无论脚本在哪里，都能找到实际的 git 仓库根目录）
# 如果当前目录不是 git 仓库，向上查找直到找到 .git 目录
PROJECT_ROOT=""
CURRENT_DIR="$(pwd)"

# 从当前目录开始向上查找 .git 目录
while [ "$CURRENT_DIR" != "/" ]; do
    if [ -d "$CURRENT_DIR/.git" ]; then
        PROJECT_ROOT="$CURRENT_DIR"
        break
    fi
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done

# 如果没找到 git 仓库，尝试使用脚本所在目录的父目录（向后兼容）
if [ -z "$PROJECT_ROOT" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
    echo -e "${YELLOW}⚠️  未找到 Git 仓库，使用脚本所在目录的父目录: ${PROJECT_ROOT}${NC}"
else
    echo -e "${GREEN}✓${NC} 找到 Git 仓库根目录: ${PROJECT_ROOT}"
fi

cd "$PROJECT_ROOT"

# 获取项目名称（从目录名或 git remote 推断）
PROJECT_NAME=$(basename "$PROJECT_ROOT")

# 显示脚本信息
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ${PROJECT_NAME} 版本发布脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# === 1. 检查 Git 状态 ===
echo -e "${YELLOW}[1/6] 检查 Git 状态...${NC}"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ 存在未提交的更改，请先提交或暂存${NC}"
    echo ""
    echo "未提交的文件："
    git status --short
    exit 1
fi

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${GREEN}✓${NC} 当前分支: ${CURRENT_BRANCH}"

# 检查是否在正确的分支（可选，可以根据需要调整）
# if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
#     echo -e "${YELLOW}⚠️  警告: 当前不在 main/master 分支${NC}"
#     read -p "是否继续? (y/N): " -n 1 -r
#     echo
#     if [[ ! $REPLY =~ ^[Yy]$ ]]; then
#         exit 1
#     fi
# fi

# === 2. 推送代码到远程分支 ===
echo ""
echo -e "${YELLOW}[2/6] 推送代码到远程分支...${NC}"

# 获取远程仓库名称（默认 origin）
REMOTE=${REMOTE:-origin}
echo "远程仓库: ${REMOTE}"

# 检查远程仓库是否存在
if ! git remote get-url "${REMOTE}" >/dev/null 2>&1; then
    echo -e "${RED}❌ 远程仓库 '${REMOTE}' 不存在${NC}"
    exit 1
fi

# 拉取最新代码
echo "拉取最新代码..."
if ! git fetch "${REMOTE}" "${CURRENT_BRANCH}"; then
    echo -e "${RED}❌ 拉取远程代码失败${NC}"
    exit 1
fi

# 检查本地分支与远程分支的关系
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse "${REMOTE}/${CURRENT_BRANCH}" 2>/dev/null || echo "")

if [ -n "$REMOTE_COMMIT" ] && [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    # 检查本地是否落后于远程（远程 commit 是本地 HEAD 的祖先）
    if git merge-base --is-ancestor HEAD "${REMOTE_COMMIT}" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  本地分支落后于远程，正在拉取...${NC}"
        git pull "${REMOTE}" "${CURRENT_BRANCH}" --no-edit || {
            echo -e "${RED}❌ 拉取失败，请手动解决冲突后重试${NC}"
            exit 1
        }
    # 检查本地是否领先于远程（本地 HEAD 是远程 commit 的祖先）
    elif git merge-base --is-ancestor "${REMOTE_COMMIT}" HEAD 2>/dev/null; then
        echo -e "${GREEN}✓${NC} 本地分支领先于远程，可以直接推送"
    # 否则说明已分叉
    else
        echo -e "${RED}❌ 本地分支与远程分支已分叉，请先合并或 rebase${NC}"
        exit 1
    fi
fi

# 推送代码
echo "推送代码到 ${REMOTE}/${CURRENT_BRANCH}..."
if ! git push "${REMOTE}" "${CURRENT_BRANCH}"; then
    echo -e "${RED}❌ 推送代码失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} 代码推送成功"

# === 3. 获取最新版本 tag ===
echo ""
echo -e "${YELLOW}[3/6] 获取最新版本 tag...${NC}"

# 拉取所有 tag
echo "拉取远程 tag..."
git fetch "${REMOTE}" --tags --force

# 获取所有符合 v*.*.* 格式的 tag
ALL_TAGS=$(git tag -l "v*.*.*" | sort -V)

if [ -z "$ALL_TAGS" ]; then
    echo -e "${YELLOW}⚠️  未找到任何版本 tag，将使用初始版本 v1.0.0${NC}"
    LATEST_TAG="v0.0.0"
else
    # 获取最新的 tag（按版本号排序）
    LATEST_TAG=$(echo "$ALL_TAGS" | tail -1)
    echo -e "${GREEN}✓${NC} 最新版本: ${LATEST_TAG}"
    
    # 显示所有 tag（可选）
    echo "所有版本 tag:"
    echo "$ALL_TAGS" | sed 's/^/  - /'
fi

# === 4. 校验版本 commit 是否改变 ===
echo ""
echo -e "${YELLOW}[4/6] 校验版本 commit 是否改变...${NC}"

# 获取当前 HEAD 的 commit ID
CURRENT_COMMIT=$(git rev-parse HEAD)
echo "当前 commit: ${CURRENT_COMMIT:0:8}"

# 如果存在最新 tag，检查它指向的 commit
if [ "$LATEST_TAG" != "v0.0.0" ]; then
    # 获取最新 tag 指向的 commit ID
    LATEST_TAG_COMMIT=$(git rev-parse "${LATEST_TAG}" 2>/dev/null || echo "")
    
    if [ -n "$LATEST_TAG_COMMIT" ]; then
        echo "最新 tag ${LATEST_TAG} 指向: ${LATEST_TAG_COMMIT:0:8}"
        
        # 比较 commit ID
        if [ "$CURRENT_COMMIT" = "$LATEST_TAG_COMMIT" ]; then
            echo -e "${YELLOW}⚠️  警告: 当前代码与最新版本 tag 指向相同的 commit${NC}"
            echo ""
            echo "这意味着："
            echo "  - 最新版本: ${LATEST_TAG}"
            echo "  - Commit: ${CURRENT_COMMIT:0:8}"
            echo "  - 代码内容没有变化"
            echo ""
            if [ "$INTERACTIVE" = true ]; then
                read -p "是否仍要创建新版本? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    echo -e "${YELLOW}已取消：代码未变化，无需发布新版本${NC}"
                    exit 0
                fi
                echo -e "${GREEN}✓${NC} 用户确认继续创建新版本"
            else
                echo -e "${YELLOW}非交互模式：代码未变化，自动取消发布${NC}"
                exit 0
            fi
        else
            echo -e "${GREEN}✓${NC} 代码已更新，可以创建新版本"
        fi
    else
        echo -e "${YELLOW}⚠️  无法获取 tag ${LATEST_TAG} 的 commit 信息${NC}"
    fi
else
    echo -e "${GREEN}✓${NC} 首次发布，无需校验"
fi

# === 5. 选择版本号递增方式 ===
echo ""
echo -e "${YELLOW}[5/6] 选择版本号递增方式...${NC}"

# 解析版本号（移除 'v' 前缀）
VERSION_NUM=${LATEST_TAG#v}

# 验证版本格式
if [[ ! "$VERSION_NUM" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    # 如果不是标准格式，使用默认版本
    if [ "$LATEST_TAG" = "v0.0.0" ]; then
        NEW_VERSION="v1.0.0"
        VERSION_TYPE="首次发布"
        echo -e "${GREEN}✓${NC} 首次发布，使用初始版本: ${NEW_VERSION}"
    else
        echo -e "${RED}❌ 版本格式错误: ${LATEST_TAG}${NC}"
        echo "   期望格式: v*.*.* (例如: v1.0.0)"
        exit 1
    fi
else
    # 解析主版本号、次版本号、修订号
    IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION_NUM"
    
    echo "当前版本: ${LATEST_TAG} (${MAJOR}.${MINOR}.${PATCH})"
    
    if [ "$INTERACTIVE" = true ]; then
        echo ""
        echo "请选择版本号递增方式:"
        echo "  1) 主版本号 +1 (${MAJOR}.${MINOR}.${PATCH} → $((MAJOR + 1)).0.0) - 重大更新"
        echo "  2) 次版本号 +1 (${MAJOR}.${MINOR}.${PATCH} → ${MAJOR}.$((MINOR + 1)).0) - 新功能"
        echo "  3) 修订号 +1  (${MAJOR}.${MINOR}.${PATCH} → ${MAJOR}.${MINOR}.$((PATCH + 1))) - 修复/补丁 [默认]"
        echo ""
        read -p "请选择 (1/2/3，直接回车使用默认): " -r VERSION_CHOICE
        
        # 默认选择修订号递增
        VERSION_CHOICE=${VERSION_CHOICE:-3}
    else
        # 非交互模式：默认使用修订号递增
        VERSION_CHOICE=3
        echo -e "${GREEN}✓${NC} 非交互模式：使用默认选项（修订号 +1）"
    fi
    
    case "$VERSION_CHOICE" in
        1)
            # 主版本号 +1，次版本号和修订号归零
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            VERSION_TYPE="主版本号"
            ;;
        2)
            # 次版本号 +1，修订号归零
            MINOR=$((MINOR + 1))
            PATCH=0
            VERSION_TYPE="次版本号"
            ;;
        3)
            # 修订号 +1
            PATCH=$((PATCH + 1))
            VERSION_TYPE="修订号"
            ;;
        *)
            echo -e "${RED}❌ 无效的选择，使用默认选项（修订号 +1）${NC}"
            PATCH=$((PATCH + 1))
            VERSION_TYPE="修订号"
            ;;
    esac
    
    # 生成新版本号
    NEW_VERSION="v${MAJOR}.${MINOR}.${PATCH}"
    if [ "$INTERACTIVE" = true ]; then
        echo -e "${GREEN}✓${NC} 选择: ${VERSION_TYPE} 递增"
    fi
fi

echo -e "${GREEN}✓${NC} 新版本: ${NEW_VERSION}"
echo "  从 ${LATEST_TAG} → ${NEW_VERSION}"

# === 显示完整发布信息摘要 ===
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  发布信息摘要${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 获取远程仓库 URL
REMOTE_URL=$(git remote get-url "${REMOTE}" 2>/dev/null || echo "未知")
# 简化显示远程仓库 URL（如果是 GitHub，只显示仓库名）
if [[ "$REMOTE_URL" =~ github\.com[:/]([^/]+/[^/]+)\.git ]]; then
    REPO_NAME="${BASH_REMATCH[1]}"
    REMOTE_DISPLAY="GitHub: ${REPO_NAME}"
elif [[ "$REMOTE_URL" =~ github\.com[:/]([^/]+/[^/]+) ]]; then
    REPO_NAME="${BASH_REMATCH[1]}"
    REMOTE_DISPLAY="GitHub: ${REPO_NAME}"
else
    REMOTE_DISPLAY="${REMOTE_URL}"
fi

# 获取当前分支的最新 commit 信息
CURRENT_COMMIT_SHORT=$(git rev-parse --short HEAD)
CURRENT_COMMIT_MSG=$(git log -1 --pretty=format:"%s" HEAD)

echo -e "${GREEN}📦 仓库信息:${NC}"
echo "  - 项目名称: ${PROJECT_NAME}"
echo "  - 远程仓库: ${REMOTE_DISPLAY}"
echo "  - 当前分支: ${CURRENT_BRANCH}"
echo "  - 当前 Commit: ${CURRENT_COMMIT_SHORT}"
if [ -n "$CURRENT_COMMIT_MSG" ]; then
    echo "  - Commit 信息: ${CURRENT_COMMIT_MSG}"
fi
echo ""

echo -e "${GREEN}🏷️  版本信息:${NC}"
echo "  - 远程最新版本: ${LATEST_TAG}"
if [ "$LATEST_TAG" != "v0.0.0" ]; then
    LATEST_TAG_COMMIT_SHORT=$(git rev-parse --short "${LATEST_TAG}" 2>/dev/null || echo "未知")
    echo "  - 最新版本 Commit: ${LATEST_TAG_COMMIT_SHORT}"
fi
echo "  - 本次发布版本: ${NEW_VERSION}"
echo "  - 版本类型: ${VERSION_TYPE:-首次发布}"
echo ""

echo -e "${GREEN}📋 操作摘要:${NC}"
echo "  1. 创建 tag: ${NEW_VERSION}"
echo "  2. 推送 tag 到远程: ${REMOTE}/${NEW_VERSION}"
echo "  3. sync-version.sh → commit build_meta.py"
echo "  4. 触发 GitHub Actions release.yml（quality → macOS 架构包 → GitHub Release → Homebrew）"
echo ""

# 确认是否继续
if [ "$INTERACTIVE" = true ]; then
    echo -e "${YELLOW}⚠️  请确认以上信息无误后继续${NC}"
    read -p "是否创建并推送 tag ${NEW_VERSION}? (Y/n): " -r
    # 支持回车确认：空字符串或 y/Y 都视为确认
    if [[ -z "$REPLY" ]] || [[ "$REPLY" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✓${NC} 确认发布"
    else
        echo -e "${YELLOW}已取消发布${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✓${NC} 非交互模式：自动确认发布"
fi

# === 6. 同步版本元数据并提交 ===
echo ""
echo -e "${YELLOW}[6/7] 同步版本元数据...${NC}"
if [ ! -x "${PROJECT_ROOT}/scripts/sync-version.sh" ]; then
    chmod +x "${PROJECT_ROOT}/scripts/sync-version.sh"
fi
"${PROJECT_ROOT}/scripts/sync-version.sh" "${NEW_VERSION}"
git add src/aklog/build_meta.py pyproject.toml
git commit -m "chore: release ${NEW_VERSION}"
git push "${REMOTE}" "${CURRENT_BRANCH}"
echo -e "${GREEN}✓${NC} 版本元数据已提交并推送"

# === 7. 创建并推送 tag ===
echo ""
echo -e "${YELLOW}[7/7] 创建并推送 tag...${NC}"

# 检查 tag 是否已存在
if git rev-parse "${NEW_VERSION}" >/dev/null 2>&1; then
    echo -e "${RED}❌ Tag ${NEW_VERSION} 已存在${NC}"
    exit 1
fi

# 创建 tag（带注释）
TAG_MESSAGE="Release ${NEW_VERSION}"
echo "创建 tag: ${NEW_VERSION}"
if ! git tag -a "${NEW_VERSION}" -m "${TAG_MESSAGE}"; then
    echo -e "${RED}❌ 创建 tag 失败${NC}"
    exit 1
fi

# 推送 tag
echo "推送 tag 到 ${REMOTE}..."
if ! git push "${REMOTE}" "${NEW_VERSION}"; then
    echo -e "${RED}❌ 推送 tag 失败${NC}"
    echo -e "${YELLOW}提示: 可以手动推送: git push ${REMOTE} ${NEW_VERSION}${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Tag 推送成功"

# === 可选：项目级发布后钩子（如 starai-deploy-cli 同步类型到公开仓库）===
if [ -f "${PROJECT_ROOT}/scripts/post-release.sh" ]; then
    echo ""
    echo -e "${YELLOW}[post-release] 执行 scripts/post-release.sh...${NC}"
    if "${PROJECT_ROOT}/scripts/post-release.sh"; then
        echo -e "${GREEN}✓${NC} post-release 完成"
    else
        echo -e "${RED}❌ post-release 失败${NC}"
        exit 1
    fi
fi

# === 完成 ===
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 版本发布成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "版本信息:"
echo "  - 旧版本: ${LATEST_TAG}"
echo "  - 新版本: ${NEW_VERSION}"
echo ""
echo "下一步:"
echo "  - release.yml：打包 lib/darwin/*（见 RELEASE_DARWIN_* 开关，默认仅 arm64）→ GitHub Release → homebrew-aklog Formula"
echo "  - 查看部署状态: https://github.com/$(git remote get-url ${REMOTE} | sed -E 's/.*[:/]([^/]+\/[^/]+)\.git/\1/')/actions"
echo ""

