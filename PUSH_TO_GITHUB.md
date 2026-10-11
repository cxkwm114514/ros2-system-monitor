# 建库 + 推送命令清单

在**你的 Ubuntu 22.04 机器上**执行。署名和邮箱已按 `蔡俊杰` / `3510173849@qq.com` 填好，
只剩 `<你的GitHub用户名>` 需要换成你自己的 GitHub 用户名。仓库名默认 `ros2-system-monitor`。

## 0. 准备工具与身份

```bash
sudo apt update && sudo apt install -y git
git config --global user.name "蔡俊杰"
git config --global user.email "3510173849@qq.com"
```

## 1. 在项目根目录初始化本地仓库并提交

```bash
cd ~/ros2-system-monitor          # 换成你实际存放本项目的路径
git init -b main
git add -A
git commit -m "Add ROS 2 system status monitor packages"
```

提交前确认里面**没有** `build/`、`install/`、`log/`（`.gitignore` 已排除，仍建议 `git status` 看一眼）。

## 2A. 用 GitHub CLI 建 public 仓库并推送（推荐，一步到位）

```bash
sudo apt install -y gh
gh auth login                     # 选 GitHub.com → HTTPS → 浏览器登录
gh repo create ros2-system-monitor --public --source=. --remote=origin --push
```

## 2B. 不用 gh：网页建库再推送

1. 打开 <https://github.com/new>
2. Repository name 填 `ros2-system-monitor`，可见性选 **Public**
3. **不要**勾选 Add a README file / .gitignore / license（本地已经都有）
4. 点 Create repository
5. 回到终端：

```bash
git remote add origin https://github.com/<你的GitHub用户名>/ros2-system-monitor.git
git push -u origin main
```

> HTTPS 推送时，密码栏要填 **Personal Access Token**（GitHub 已不支持账号密码）。
> 生成地址：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)，勾选 `repo` 权限。

## 3. 验证

```bash
git remote -v
git log --oneline
gh repo view --web                # 或直接在浏览器打开仓库页面
```

## 4. 之后的日常提交

```bash
git add -A
git commit -m "描述这次改了什么"
git push
```

## 注意

- 推送完仓库里不应出现 `src/`、`build/`、`install/`、`log/` 之外的中间产物。
- 如果 `git commit` 报 author 未配置，回到第 0 步。
