# AnkiChoiceQuiz 🍱

An interactive Multiple-Choice Question (MCQ) system based on **[Anki](https://github.com/ankitects/anki)**, ~~deeply customized~~ "vibe-ed" out by AI. It reconstructs the traditional "flip-to-memorize" logic into a "click-submit-feedback" experience and is specifically adapted for the **[thepeacemonk/Onigiri](https://github.com/thepeacemonk/Onigiri)** interface.

<img width="1477" height="897" alt="Dashboard Preview" src="https://github.com/user-attachments/assets/00248215-0da0-4a24-b859-c60568dbdca0" />
<img width="1476" height="799" alt="Question UI" src="https://github.com/user-attachments/assets/a8f98d90-e2a8-45a2-bb4b-9cf0d3b68bf4" />
<img width="1476" height="799" alt="Feedback Correct" src="https://github.com/user-attachments/assets/b251fdc2-6b0a-456a-950a-5c2bbbd7d39f" />
<img width="1476" height="856" alt="Completion Screen" src="https://github.com/user-attachments/assets/af99223e-d98a-46cb-bb36-1ddf03f089f5" />

*Essentially for personal use. PRs are welcome. Known issue: The study interface might flicker on some devices; I'm too lazy to fix it since the core functionality works fine. =.=*

---

## ✒️ Credits & Disclaimer

The UI and dashboard system of this project primarily rely on **[thepeacemonk/Onigiri](https://github.com/thepeacemonk/Onigiri)**.

> **Onigiri** is an experimental and avant-garde Anki add-on that completely transforms the native Anki interface. I highly recommend visiting the original repository to support the author!

Based on this framework, I implemented a deeply integrated **Interactive MCQ** functionality through custom Note Types and JavaScript logic.

---

## 🌟 Highlights

* **Onigiri-Powered Dashboard**: Inherits features like Restaurant Levels, XP systems, and GitHub-style contribution heatmaps.
* **Fully Interactive MCQ**: Options act as buttons. Click to select; submit to see immediate feedback.
* **Feedback Logic**: Follows Anki's native rating system. Correct/Incorrect answers move cards from the "New" (Blue) stage to "Relearn" (Red) until mastery.
* **Hybrid Question Support**: Supports Single-choice, Multiple-choice, and True/False questions with "click-to-submit" logic.
* **Visual Consistency**: **OnigiriStyleQuiz.7z** provides a Glassmorphism theme that fits perfectly with the Onigiri aesthetic.

---

## 🚀 Quick Start

Two versions are provided: **OnlyQuiz.7z** and **OnigiriStyleQuiz.7z**.

| Version | Description |
| :--- | :--- |
| **OnlyQuiz.7z** | Standalone version. No Onigiri required (looks simpler). |
| **OnigiriStyleQuiz.7z** | Best paired with the Onigiri add-on. Uses transparent elements. |

> **Note**: For Chinese text, the recommended font is **[Xiangcui-Dengcusong](https://github.com/Miiiller/Xiangcui-Dengcusong)** (Please follow its specific repository license).

### 1. Environment Setup

* **Install Anki**: Ensure you have the latest [Anki Desktop](https://apps.ankiweb.net/).
* **Basic Config**: Complete initial setup (language, sync, etc.).
* **Add-on**: If using **OnigiriStyleQuiz.7z**, install the [Onigiri add-on](https://github.com/thepeacemonk/Onigiri) first for the full visual experience.

### 2. Deployment Steps

After extracting your chosen ZIP, follow these steps:

1.  **Create Note Type**:
    * Tools → Manage Note Types → Add/Clone "Basic".
    * Rename to: **Clickable MCQ**.
    * Open "Fields" and create them in this exact order: `Stem`, `A`, `B`, `C`, `D`, `E`, `CorrectLetters`, `Answer`, `Type`, `Tags`.
2.  **Inject Template Code**:
    * Select your "Clickable MCQ" type → Cards.
    * Replace **Front Template**, **Back Template**, and **Styling** with the contents of the respective `.txt` files in the package.
3.  **Data Extraction Tools**:
    * The repository includes some simple Python scripts to convert Word/TXT files into formatted CSVs.
    * *Disclaimer*: These tools are "vibed" out and might not be 100% accurate. For perfect results, manual Excel creation or using LLMs to extract data from documents is recommended (prompts are provided in the repo).
4.  **Import Deck**:
    * Create your target Deck first.
    * File → Import → Select your `.csv` file.
    * Ensure the Note Type is set to "Clickable MCQ" and map fields correctly from Column 1 (`Stem`) to Column 10 (`Tags`).

---

## 🛠 Technical Details

* **DOM Injection**: Embeds custom button groups into the Onigiri web view and intercepts default "Show Answer" events.
* **State Management**: Buttons handle `Hover`, `Selected`, `Correct`, and `Incorrect` states via CSS/JS.
* **Responsive Design**: Optimized for desktop layouts.

---

## 📄 License

This project is licensed under **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)**.

* **Attribution (BY)**: You must give appropriate credit.
* **Non-Commercial (NC)**: You may not use the material for commercial purposes.
* **ShareAlike (SA)**: If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

*Note: Dependencies like Onigiri, Anki, and Xiangcui-Dengcusong follow their respective original licenses.*
