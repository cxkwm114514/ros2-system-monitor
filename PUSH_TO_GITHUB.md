# 建库 + 推送命令清单

在 **Ubuntu 22.04（含 WSL）** 上执行。署名、邮箱、GitHub 用户名都已填好：
`蔡俊杰` / `3510173849@qq.com` / `cxkwm114514`。仓库名默认 `ros2-system-monitor`。

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
gh auth login                     # GitHub.com → HTTPS → Login with a web browser（显示设备码）
gh auth setup-git                 # 让 git 复用 gh 的凭据，之后 git push 不用再输密码
gh repo create ros2-system-monitor --public --source=. --remote=origin --push
```

## 2B. 不用 gh：网页建库再推送

1. 打开 <https://github.com/new>
2. Repository name 填 `ros2-system-monitor`，可见性选 **Public**
3. **不要**勾选 Add a README file / .gitignore / license（本地已经都有）
4. 点 Create repository
5. 回到终端：

```bash
git remote add origin https://github.com/cxkwm114514/ros2-system-monitor.git
git push -u origin main
```

> HTTPS 推送会问用户名和密码：用户名填 `cxkwm114514`，**"密码"必须填 Personal Access Token**——
> GitHub 从 2021 年起不再接受账号密码，只填账号密码会报
> `remote: Invalid username or token. Password authentication is not supported for Git operations.`
>
> 生成 Token：GitHub 右上头像 → Settings → Developer settings → Personal access tokens →
> **Tokens (classic)** → Generate new token (classic) → 勾选 **`repo`** → 生成后立刻复制（只显示一次）。
> 若用细粒度 token，权限要给 **Contents: Read and write**。

## 3. 推送报 Authentication failed 怎么办

先清掉可能已经缓存的错误密码：

```bash
git config --global --unset credential.helper 2>/dev/null
git credential-cache exit 2>/dev/null || true
```

**方式 1：改用 GitHub CLI（最省事，一次配置长期有效）**

```bash
sudo apt install -y gh
gh auth login          # GitHub.com → HTTPS → Login with a web browser（设备码）
gh auth setup-git      # 关键：让 git 复用 gh 的凭据
cd ~/ros2_ws/src/ros2-system-monitor
git push -u origin main
```

**方式 2：继续用 HTTPS + Token**

```bash
cd ~/ros2_ws/src/ros2-system-monitor
git push -u origin main
# Username: cxkwm114514
# Password: 粘贴刚生成的 Token（不是账号密码）
```

想以后不再输，可以缓存凭据（注意 Token 会明文存在 `~/.git-credentials`）：

```bash
git config --global credential.helper store
```

**方式 3：改走 SSH**

```bash
ssh-keygen -t ed25519 -C "3510173849@qq.com"   # 一路回车
cat ~/.ssh/id_ed25519.pub                       # 整行复制到 GitHub → Settings → SSH and GPG keys → New SSH key
ssh -T git@github.com                           # 出现 successfully authenticated 即成功
git remote set-url origin git@github.com:cxkwm114514/ros2-system-monitor.git
git push -u origin main
```

## 4. 验证

```bash
git remote -v
git log --oneline
gh repo view --web                # 或直接在浏览器打开仓库页面
```

## 5. 之后的日常提交

```bash
git add -A
git commit -m "描述这次改了什么"
git push
```

## 注意

- 仓库里应该只有 `src/`、`README.md`、`LICENSE`、`PUSH_TO_GITHUB.md`、`.gitignore`（共 16 个文件）；`build/`、`install/`、`log/` 是编译产物，不该出现在网页上。
- 如果 `git commit` 报 author 未配置，回到第 0 步。
