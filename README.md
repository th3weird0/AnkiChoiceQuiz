# AnkiChoiceQuiz 🍱

一个基于 **[Anki]([https://github.com/ankitects/anki])** 的

~~深度定制~~Ai Vibe出来的交互式多选题系统。它将传统的“翻面记忆”逻辑重构为“点击-提交-反馈”的刷题体验，并适配了[thepeacemonk/Onigiri](https://github.com/thepeacemonk/Onigiri)界面。

<img width="1477" height="897" alt="5aaa46f778517f2d9821444ac433dff7" src="https://github.com/user-attachments/assets/00248215-0da0-4a24-b859-c60568dbdca0" />
<img width="1476" height="799" alt="e77adb9893380d27f12d754d2299f12e" src="https://github.com/user-attachments/assets/a8f98d90-e2a8-45a2-bb4b-9cf0d3b68bf4" />
<img width="1476" height="799" alt="2b11e40f3055e329c9e2c6d979f7be1f" src="https://github.com/user-attachments/assets/b251fdc2-6b0a-456a-950a-5c2bbbd7d39f" />
<img width="1476" height="856" alt="2c3ade0a4a7b7e97b6ec5d5e2622a0ea" src="https://github.com/user-attachments/assets/af99223e-d98a-46cb-bb36-1ddf03f089f5" />

*本质自用。欢迎PR。Issue已知是在我的电脑里有的时候studying界面会闪烁，懒得管了。反正功能能用=。=*

## ✒️ 致谢与声明 (Credits)

本项目的 UI 界面和看板系统主要依赖于 **[thepeacemonk/Onigiri](https://github.com/thepeacemonk/Onigiri)**。

> **Onigiri** 是一个极具实验性且前卫的 Anki 插件，彻底颠覆了 Anki 的原生界面。强烈建议前往原仓库支持原作者！

本项目在其基础上，通过自定义卡片模板（Note Type）和 JavaScript 逻辑，实现了深度集成的**交互式多选题（Interactive MCQ）**功能。

## 🌟 项目亮点

- **基于 Onigiri 的沉浸式看板**：继承了原项目的餐厅等级、XP 经验值及学习热力图。
- **全交互式 MCQ 体验**：选项即按钮，点击选中，提交即看对错。
- **对错反馈**：沿用Anki原评级等级，第一次作对与做错都会从蓝色新卡片阶段进入红色再练习阶段，再次作对才会消除。
- **混合题型兼容**：支持单选，多选，判断这类点击按钮即提交的类型。
- **视觉风格一致性**：**OnigiriStyleQuiz.7z** 提供完美契合 Onigiri 的玻璃拟态（Glassmorphism）配色方案。

## 🚀 快速开始 (Quick Start)

提供了两个版本：  **OnlyQuiz.7z** 和 **OnigiriStyleQuiz.7z**

**OnlyQuiz.7z**             - 不安装Onigiri也可以用，只是看起来比较单调。

**OnigiriStyleQuiz.7z**     - 最好配合Onigiri使用，因为引入了一些透明的元素。中文建议使用字体：**[香萃等粗宋](https://github.com/Miiiller/Xiangcui-Dengcusong)**


下载本仓库的压缩包后，选择好你的版本后，请按照以下步骤进行部署：

### 1. 环境准备

* **安装 Anki**：确保你的电脑已安装最新版的 [Anki Desktop](https://apps.ankiweb.net/)。
* **基础配置**：首次运行请完成 Anki 的基础设置（如语言选择、账号同步等）。
* **安装插件**：如果决定使用 **OnigiriStyleQuiz.7z** 最好先安装 [Onigiri 插件](https://github.com/thepeacemonk/Onigiri) 才能获得高颜值看板效果。如果没装插件只有单纯的题库交互功能。

### 2. 解压与部署 (具体步骤)

解压下载的 ZIP 文件，你会看到包含模板代码（.txt）和示例题库（.csv）的文件夹。

1. **创建笔记类型**：

   - 工具 → 管理笔记类型 → 复制“问答题”或“Basic”。
   - 名称改为：**可点击选择题**。
   - 打开“字段”，按顺序创建：`Stem`, `A`, `B`, `C`, `D`, `E`, `CorrectLetters`, `Answer`, `Type`, `Tags`。

2. **注入模板代码**：

   - 在“管理笔记类型”中选中“可点击选择题”，点击“卡片”。
   - 将 `正面模板.txt`、`背面模板.txt` 和 `样式.txt` 中的内容分别粘贴到对应的“正面”、“背面”和“样式”文本框中。

3. **仓库中提供了Vibe出来的简单小工具，都是python文件。**可以把word输出为txt的一些非字段化题目转为第一步描述的字段化csv。

   *这个小工具没迭代几个版本，所以我认为不太可用，如果你追求100%准确的字段文件，可能你还得自己开个excel或者numbers，自己创建好题库在输出为csv。*

   *我自己用的时候也是通过喂给LLM通用知识文档，让LLM帮我做数据提取。**建议你们也这么弄**，一些prompt已提供。*

4. **导入题库**：

   - 先新建好你的Deck牌组。
   - 文件 → 导入，选择配套的 CSV 文件。
   - 确保笔记模板选为“可点击选择题”，选对你新建的Deck牌组名称，字段映射从“列1 -> Stem”直到“列10 -> Tags”。

> 详细的字段顺序和操作细节，请参阅压缩包内的 `Anki_可点击选择题_使用说明.txt`。

## 🛠 技术实现细节

- **DOM 劫持**：在 Onigiri 渲染的 Web 视图中嵌入自定义按钮组，拦截默认事件。
- **状态流管理**：按钮包含 `Hover`、`Selected`、`Correct`、`Incorrect` 四种状态视觉反馈。
- **响应式设计**：适配桌面端布局。

## 📄 开源协议 (License)

本项目采用 **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** 协议。

- **署名 (BY)**：使用或转载请注明原作者。
- **非商业性使用 (NC)**：严禁将此模板或配套题库用于任何商业盈利目的。
- **相同方式共享 (SA)**：基于此项目的二次开发必须以相同协议开源。

*注：本项目使用的底层框架 Onigiri 遵循其原有的 [GPL-3.0 license](https://github.com/thepeacemonk/Onigiri?tab=GPL-3.0-1-ov-file#GPL-3.0-1-ov-file) 开源协议。*
