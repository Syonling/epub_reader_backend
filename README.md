# 📚 EPUB Reader Backend

日本語学習者（特に中国語ネイティブスピーカー）向けに特別に設計された、強力なEPUBリーダーバックエンドサービスです。複数のAIモデル、包括的な日本語辞書検索、動詞の活用解析をサポートしています。

> 📱 Frontend：[EPUB Reader （Flutter App）](https://github.com/Syonling/epub_reader_Androidfrontend#)

![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-blue)
![Python](https://img.shields.io/badge/Python-3.11.0+-brightgreen)
![Flutter](https://img.shields.io/badge/Flutter-3.35.6-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.2-orange)

## 🎬 デモンストレーション （1120夜　更新予定）

### 単語分析
**Debug中**
<!-- ![单词分析演示](assets/demos/word_analysis.gif) -->

### 長文解析 - AIによる構文解析
**準備中**
<!-- ![句子分析演示](assets/demos/sentence_analysis.gif) -->

[日本語](#日本語) | [English](#english-documentation)

---

## 日本語

### 🌟 概要

EPUB リーダー用のバックエンドサービスで、日本語学習者向けに特化した高度な機能を提供します。複数の AI モデルに対応し、包括的な日本語辞書検索と動詞活用分析を実現しています。

### ✨ 主な機能

#### 1. マルチ AI モデル対応

以下の主要な AI サービスとシームレスに統合：

- **OpenAI**
- **Anthropic Claude**
- **Google Gemini**
- **Ollama**
- ✅ **DeepSeek**
- ✅ **Echo**: テストモード仮想API（デバッグ用）

#### 2. 高度な日本語辞書機能

**辞書データベース：**
- Jim Breen 氏の JMdict（日本語多言語辞典）を採用
- 18 万語以上の包括的な語彙カバレッジ
- 読み仮名、品詞、語義を含む詳細な語彙情報

**動詞活用分析：**

本システムは日本語動詞の活用を自動的に識別し、生成します：

- **動詞分類の自動判定**：五段活用（一類）、一段活用（二類）、サ行変格活用、カ行変格活用
- **12 種類の活用形を完全生成**：
  ```
  辞書形          → 読む
  ます形(丁寧体)    → 読みます
  ない形(否定形)    → 読まない
  命令形          → 読め
  意志形(よう形)    → 読もう
  受身形          → 読まれる
  使役形          → 読ませる
  可能形          → 読める
  ば形(仮定形)     → 読めば
  て形(接続形)     → 読んで
  た形(過去形)     → 読んだ
  なかった形       → 読まなかった
  使役受身形       → 読ませられる
  ```

- **促音便・撥音便などの音便規則にも対応**

#### 3. インテリジェント・テキスト分析

**自動判定システム：**
- 短文（1〜10文字）→ 単語分析モード
- 長文（10文字以上）→ 文章・段落分析モード

**分析内容：**
- 翻訳
- 文法ポイントの解説
- JLPT レベル付き語彙リスト
- 動詞活用情報
- 特別なヒント：古い日本語など

### 🚀 セットアップ

#### インストール

```bash
# リポジトリをクローン
git clone < git@github.com:Syonling/epub_reader_backend.git >
cd epub_reader_backend

# Poetry を使用して依赖関係をインストール
poetry install
```

#### 設定

`.env` ファイルを作成：

```python
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=True 

# 少なくとも 1 つの API を設定してください
AI_PROVIDER=echo  #デフォルトモデルを設定する
# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=
# DeepSeek
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=
# Claude

# LLM 通用配置
MAX_TOKENS=1024
TEMPERATURE=0.7
TIMEOUT=30
```

#### 起動

```bash
# バックエンドサーバーを起動
poetry run python backend.py

# デフォルトで http://localhost:5001 で実行されます
```

### 🔧 API エンドポイント

#### `/api/analyze` - テキスト分析

**リクエスト：**
```json
{
  "text": "読む",
  "provider": "openai",
  "model": "gpt-4",  
}
```

**レスポンス例（単語分析）：**
```json
{
  "analysis": {
    "method": "word_parser",
    "result": {
      "translation": "read; peruse",
      "vocabulary": [{
        "word": "読む",
        "reading": "よむ",
        "meaning": "read; peruse",
        "level": "N2",
        "conjugation": {
          "has_conjugation": true,
          "verb_class": "五段動詞（一類動詞）",
          "all_forms": {
            "masu_form": "読みます",
            "te_form": "読んで",
            "ta_form": "読んだ",
            // ... その他の活用形
          }
        }
      }],
      "special_notes": [
        "✅ JMdict 完全辞書を使用（XML 直接解析）"
      ]
    }
  }
}
```

**レスポンス例（文章分析）：**
```json
{
  "analysis": {
    "method": "ai_analysis",
    "provider": "openai",
    "model": "gpt-4",
    "result": {
      "translation": "我每天都在学习日语。",
      "grammar_points": [
        {
          "pattern": "〜ています",
          "explanation": "表示动作的持续进行或习惯性动作",
          "example_in_sentence": "勉強しています",
          "level": "N5"
        }
      ],
      "vocabulary": [
        {
          "word": "毎日",
          "reading": "まいにち",
          "meaning": "每天",
          "level": "N5"
        },
        {
          "word": "勉強",
          "reading": "べんきょう",
          "meaning": "学习",
          "level": "N5"
        }
      ],
      "special_notes": [
        "这是一个表达日常习惯的句子"
      ]
    }
  }
}
```

#### `/api/health` - ヘルスチェック

バックエンドのステータスと利用可能な AI プロバイダーを返します。

### 🎯 技術スタック

- **バックエンドフレームワーク**：Flask 3.1.2
- **依存関係管理**：Poetry
- **日本語辞書**：JMdict（XML 直接解析）
- **AI 統合**：
  - OpenAI Python SDK
  - Anthropic Python SDK
  - Google Generative AI SDK
  - Ollama Python SDK
  - カスタム DeepSeek アダプター

### 📁 プロジェクト構造

```
epub_reader_backend/
├── app/
│   ├── middleware/          # ミドルウェア（リクエストロギング等）
│   ├── routes/              # API ルート
│   │   ├── analysis.py      # テキスト分析エンドポイント
│   │   ├── health.py        # ヘルスチェック
│   │   └── stats.py         # 統計情報
│   ├── services/            # コアサービス
│   │   ├── ai_service.py           # AI サービス管理
│   │   ├── japanese_word_parser.py # 日本語辞書解析
│   │   ├── verb_conjugator.py      # 動詞活用生成
│   │   ├── word_parser.py          # 単語解析器
│   │   └── text_analyzer.py        # テキスト分析器
│   └── utils/               # ユーティリティ関数
├── backend.py               # メインエントリーポイント
├── config.py                # 設定管理
└── pyproject.toml           # 依存関係定義
```

### 💡 技術的特徴

#### 学習者中心の設計

日本語学習者、特に中国語母語話者の実際のニーズを考慮した設計：

- **動詞活用の重点化**：日本語文法規則に基づいた独自の活用生成ロジックを実装。促音便、撥音便などの音便規則にも対応し、正確な活用形を生成します。
- **文法解析の最適化**：学習段階に応じた JLPT レベル表示と、詳細な文法ポイント解説を提供。
- **インテリジェント判定**：テキストの長さに基づいて単語分析と文章分析を自動選択。

#### コスト効率の高い設計

- **API 呼び出しの最適化**：単語分析はローカル辞書で処理し、AI API を使用しないため、コストを大幅に削減。
- **選択的 AI 利用**：文章や段落の分析時のみ AI API を呼び出し、不要な API 使用を回避。
- **複数プロバイダー対応**：ニーズに応じて最適な AI サービスを選択可能。

### 📄 ライセンス

CC BY-NC 4.0（非商用利用）

---

## English Documentation

### 🌟 Overview

A powerful backend service for an EPUB reader application, specifically designed for Japanese language learners. Supports multiple AI models, comprehensive Japanese dictionary lookups, and verb conjugation analysis.

### ✨ Key Features

#### 1. Multi-AI Model Support

Seamlessly integrated with major AI services:

- **OpenAI**: GPT-4, GPT-3.5, and other cutting-edge models
- **Anthropic Claude**: High-performance models including Claude 3.5 Sonnet
- **Google Gemini**: Gemini Pro, Gemini Flash
- **Ollama**: Privacy-focused local deployment
- **DeepSeek**: Cost-effective alternative

#### 2. Advanced Japanese Dictionary

**Dictionary Database:**
- Powered by Jim Breen's JMdict (Japanese-Multilingual Dictionary)
- 180,000+ comprehensive vocabulary coverage
- Custom implementation with direct XML parsing for fast and stable performance
- Detailed lexical information including readings, parts of speech, and definitions

**Verb Conjugation Analysis:**

The system automatically identifies and generates Japanese verb conjugations:

- **Automatic Verb Classification**: Godan (Type I), Ichidan (Type II), Suru-irregular, Kuru-irregular
- **12 Complete Conjugation Forms**:
  ```
  Dictionary Form        → 読む (yomu)
  Masu Form (polite)     → 読みます (yomimasu)
  Te Form (connective)   → 読んで (yonde)
  Ta Form (past)         → 読んだ (yonda)
  Nai Form (negative)    → 読まない (yomanai)
  Nakatta Form           → 読まなかった (yomanakatta)
  Ba Form (conditional)  → 読めば (yomeba)
  Command Form           → 読め (yome)
  Volitional Form        → 読もう (yomou)
  Passive Form           → 読まれる (yomareru)
  Causative Form         → 読ませる (yomaseru)
  Potential Form         → 読める (yomeru)
  Causative-Passive      → 読ませられる (yomaserareru)
  ```

- **Supports euphonic changes** (sound shifts in conjugation)

#### 3. Intelligent Text Analysis

**Automatic Detection:**
- Short text (1-3 characters) → Word analysis mode
- Long text (4+ characters) → Sentence/paragraph analysis mode

**Analysis Content:**
- Translation
- Grammar point explanations
- Vocabulary list with JLPT levels
- Verb conjugation information
- Learning tips

### 🚀 Setup

#### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd epub_reader_backend

# Install dependencies using Poetry
poetry install

# Download dictionary data (about 23MB, takes a few minutes)
poetry run python setup_dict.py
```

#### Configuration

Create a `.env` file:

```env
# Configure at least one API
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GEMINI_API_KEY=xxx
DEEPSEEK_API_KEY=sk-xxx

# For local Ollama usage
OLLAMA_BASE_URL=http://localhost:11434
```

#### Running

```bash
# Start the backend server
poetry run python backend.py

# Runs on http://localhost:5001 by default
```

### 🔧 API Endpoints

#### `/api/analyze` - Text Analysis

**Request:**
```json
{
  "text": "読む",
  "provider": "openai",
  "model": "gpt-4",
  "force_type": "word"  // Optional: force word or sentence analysis
}
```

**Response Example (Word Analysis):**
```json
{
  "analysis": {
    "method": "word_parser",
    "result": {
      "translation": "read; peruse",
      "vocabulary": [{
        "word": "読む",
        "reading": "よむ",
        "meaning": "read; peruse",
        "level": "N2",
        "conjugation": {
          "has_conjugation": true,
          "verb_class": "Godan Verb (Type I)",
          "all_forms": {
            "masu_form": "読みます",
            "te_form": "読んで",
            "ta_form": "読んだ",
            // ... more conjugations
          }
        }
      }],
      "special_notes": [
        "✅ Using complete JMdict dictionary (direct XML parsing)"
      ]
    }
  }
}
```

#### `/api/health` - Health Check

Returns backend status and available AI providers.

### 🎯 Tech Stack

- **Backend Framework**: Flask 3.1.2
- **Dependency Management**: Poetry
- **Japanese Dictionary**: JMdict (direct XML parsing)
- **AI Integration**:
  - OpenAI Python SDK
  - Anthropic Python SDK
  - Google Generative AI SDK
  - Ollama Python SDK
  - Custom DeepSeek adapter

### 📁 Project Structure

```
epub_reader_backend/
├── app/
│   ├── middleware/          # Middleware (request logging, etc.)
│   ├── routes/              # API routes
│   │   ├── analysis.py      # Text analysis endpoint
│   │   ├── health.py        # Health check
│   │   └── stats.py         # Statistics
│   ├── services/            # Core services
│   │   ├── ai_service.py           # AI service management
│   │   ├── japanese_word_parser.py # Japanese dictionary parser
│   │   ├── verb_conjugator.py      # Verb conjugation generator
│   │   ├── word_parser.py          # Word parser
│   │   └── text_analyzer.py        # Text analyzer
│   └── utils/               # Utility functions
├── backend.py               # Main entry point
├── config.py                # Configuration management
└── pyproject.toml           # Dependency definitions
```

### 💡 Technical Highlights

#### Direct XML Parsing for JMdict

To avoid issues with traditional SQLite import (UNIQUE constraint errors), we implemented custom XML parsing. This provides:
- Improved stability
- Simplified setup
- Fast search performance

#### Verb Conjugation Implementation

Custom conjugation logic based on Japanese grammar rules, with support for euphonic changes, producing accurate conjugation forms.

### 📄 License

CC BY-NC 4.0 (Non-Commercial Use)

---
