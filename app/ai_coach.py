import os
import time

from .models import Todo

MAX_RETRIES = 3


def generate_coach_advice(todos: list[Todo]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

    if not api_key:
        return "⚠️ GEMINI_API_KEY が設定されていません。.env ファイルを確認してください。"

    if not todos:
        return "タスクがまだありません。まずはタスクを追加してみましょう！"

    # 入力トークン節約: 最大10件に制限
    task_summary = _build_task_summary(todos[:10])
    prompt = (
        f"タスク管理コーチとして以下を分析し、日本語で短いアドバイスを3つ書いて。\n"
        f"{task_summary}"
    )

    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import APIError

        client = genai.Client(api_key=api_key)

        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=256,
                        temperature=0.7,
                    ),
                )
                return response.text
            except APIError as e:
                if e.code == 429 and attempt < MAX_RETRIES - 1:
                    wait = 15 * (attempt + 1)
                    time.sleep(wait)
                    continue
                if e.code == 429:
                    return (
                        "⚠️ APIのレート制限に達しました。"
                        "しばらく待ってから再度お試しください。\n"
                        "（無料枠の場合、1分あたりのリクエスト数に制限があります）"
                    )
                raise
    except Exception as e:
        return f"⚠️ AI生成エラー: {e}"


def _build_task_summary(todos: list[Todo]) -> str:
    lines = []
    for t in todos:
        due = t.due_date.strftime("%Y-%m-%d") if t.due_date else "期限なし"
        lines.append(
            f"- {t.title} | 状態:{t.status} | 優先度:{t.priority} | "
            f"期限:{due} | 進捗:{t.progress}%"
        )
    return "\n".join(lines)
