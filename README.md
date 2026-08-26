# 例胜残局

手机优先的中国象棋例胜残局练习：一点开局（不用摆子），**皮卡鱼**本地强力防守，可提示 / 正解 / 通关进度。

## 开发

```bash
npm install
npm run dev
```

电脑浏览器打开终端里的地址；手机同一局域网访问 `http://<电脑IP>:5173`。

首次进入对局会加载皮卡鱼引擎（约数 MB），建议 Wi‑Fi 下打开一次；之后可缓存离线使用。

## 引擎说明

- 对局/提示默认使用 [Pikafish](https://github.com/official-pikafish/Pikafish)（GPL-3.0）WebAssembly 版，本地计算、不连云端。
- 加载失败时回退到内置浅层搜索。

## 构建

```bash
npm run build
npm run preview
```
